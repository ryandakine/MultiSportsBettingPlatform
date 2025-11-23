#!/usr/bin/env python3
"""
NHL Betting System - Local Predictions with Odds API
Run this locally after training model in Colab
"""

import requests
import pickle
import pandas as pd
import numpy as np
from datetime import datetime

# =============================================================
# CONFIGURATION
# =============================================================

# Get your free API key at https://the-odds-api.com/
ODDS_API_KEY = "78c0a858acc5bfdefb7e0abe02d0c744"

# Betting parameters
BANKROLL = 1000
MIN_EDGE = 0.03  # 3% minimum edge to bet
MIN_CONFIDENCE = 0.55

# Model file (downloaded from Colab)
MODEL_PATH = "nhl_model.pkl"

# =============================================================
# LOAD MODEL
# =============================================================

print("="*60)
print("🏒 NHL BETTING SYSTEM - LIVE PREDICTIONS")
print("="*60)

try:
    with open(MODEL_PATH, 'rb') as f:
        model_data = pickle.load(f)

    model = model_data['model']
    scaler = model_data['scaler']
    team_stats = model_data['stats']
    ELITE_HOME = model_data['elite_home']
    ROAD_WARRIORS = model_data['road_warriors']
    HIGH_SCORING = model_data['high_scoring']
    LOW_SCORING = model_data['low_scoring']

    print(f"✅ Model loaded from {MODEL_PATH}")
    print(f"   Teams in database: {len(team_stats)}")
except FileNotFoundError:
    print(f"❌ Model file not found: {MODEL_PATH}")
    print("   Run training in Colab and download nhl_model.pkl first")
    exit(1)

# =============================================================
# ODDS API FUNCTIONS
# =============================================================

def fetch_nhl_odds():
    """Fetch NHL games and odds from The Odds API"""
    url = "https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds"
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american'
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            # Show remaining requests
            remaining = resp.headers.get('x-requests-remaining', 'N/A')
            print(f"   API requests remaining: {remaining}")
            return data
        elif resp.status_code == 401:
            print("❌ Invalid API key")
            return None
        else:
            print(f"❌ API Error: {resp.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def american_to_implied_prob(odds):
    """Convert American odds to implied probability"""
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

def american_to_decimal(odds):
    """Convert American odds to decimal"""
    if odds > 0:
        return (odds / 100) + 1
    else:
        return (100 / abs(odds)) + 1

# =============================================================
# PREDICTION FUNCTION
# =============================================================

def predict_game(home_team, away_team):
    """Predict a single game using the trained model"""

    # Try to match team names
    def find_team(name):
        # Exact match
        if name in team_stats:
            return name
        # Partial match (city or team name)
        for team in team_stats:
            if name.split()[-1] in team or team.split()[-1] in name:
                return team
        return None

    home = find_team(home_team)
    away = find_team(away_team)

    if not home or not away:
        return None

    hs = team_stats[home]
    ast = team_stats[away]

    # Build feature vector
    feat = {
        'h_gf': hs['gf'], 'h_ga': hs['ga'],
        'a_gf': ast['gf'], 'a_ga': ast['ga'],
        'h_wpct': hs['wpct'], 'a_wpct': ast['wpct'],
        'h_home_pct': hs['home_pct'], 'a_away_pct': ast['away_pct'],
        'h_l5': hs['l5'], 'a_l5': ast['l5'],
        'h_l10': hs['l10'], 'a_l10': ast['l10'],
        'h_games': hs['games'], 'a_games': ast['games'],
        'h_diff': hs['diff'], 'a_diff': ast['diff'],
        'h_elite_home': 1 if home in ELITE_HOME else 0,
        'a_road_warrior': 1 if away in ROAD_WARRIORS else 0,
        'h_high_scoring': 1 if home in HIGH_SCORING else 0,
        'a_high_scoring': 1 if away in HIGH_SCORING else 0,
        'h_low_scoring': 1 if home in LOW_SCORING else 0,
        'a_low_scoring': 1 if away in LOW_SCORING else 0,
        'is_february': 1 if datetime.now().month == 2 else 0,
        'h_b2b': 0,  # Would need schedule data
        'a_b2b': 0,
    }

    X_pred = pd.DataFrame([feat])
    X_pred_s = scaler.transform(X_pred)
    prob = model.predict_proba(X_pred_s)[0][1]

    return prob

# =============================================================
# MAIN PREDICTION LOOP
# =============================================================

print(f"\n📡 Fetching NHL odds...")
games = fetch_nhl_odds()

if not games:
    print("\n❌ No games found or API error")
    exit(1)

print(f"✅ Found {len(games)} games")
print(f"\n📅 {datetime.now().strftime('%A, %B %d, %Y')}")

# Analyze each game
print("\n" + "-"*80)
print(f"{'Game':<42} {'Model':<8} {'Book':<8} {'Edge':<8} {'Pick':<15} {'Action'}")
print("-"*80)

value_bets = []

for game in games:
    home_team = game['home_team']
    away_team = game['away_team']
    game_time = game.get('commence_time', '')

    # Get best odds
    best_home_odds = -9999
    best_away_odds = -9999
    best_home_book = ""
    best_away_book = ""

    for book in game.get('bookmakers', []):
        for market in book.get('markets', []):
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    if outcome['name'] == home_team:
                        if outcome['price'] > best_home_odds:
                            best_home_odds = outcome['price']
                            best_home_book = book['title']
                    else:
                        if outcome['price'] > best_away_odds:
                            best_away_odds = outcome['price']
                            best_away_book = book['title']

    if best_home_odds == -9999:
        continue

    # Get model prediction
    prob = predict_game(home_team, away_team)

    if prob is None:
        continue

    # Calculate implied probabilities
    home_implied = american_to_implied_prob(best_home_odds)
    away_implied = american_to_implied_prob(best_away_odds)

    # Find value
    home_edge = prob - home_implied
    away_edge = (1 - prob) - away_implied

    if home_edge >= MIN_EDGE and prob >= MIN_CONFIDENCE:
        pick = home_team
        model_prob = prob
        book_prob = home_implied
        edge = home_edge
        odds = best_home_odds
        book = best_home_book
        action = "✅ BET"
    elif away_edge >= MIN_EDGE and (1 - prob) >= MIN_CONFIDENCE:
        pick = away_team
        model_prob = 1 - prob
        book_prob = away_implied
        edge = away_edge
        odds = best_away_odds
        book = best_away_book
        action = "✅ BET"
    else:
        pick = "-"
        model_prob = max(prob, 1 - prob)
        book_prob = min(home_implied, away_implied)
        edge = max(home_edge, away_edge)
        odds = 0
        book = ""
        action = "❌ PASS"

    game_str = f"{away_team} @ {home_team}"
    print(f"{game_str:<42} {model_prob:.1%}   {book_prob:.1%}   {edge:+.1%}   {pick:<15} {action}")

    if action == "✅ BET":
        value_bets.append({
            'game': game_str,
            'pick': pick,
            'model_prob': model_prob,
            'book_prob': book_prob,
            'edge': edge,
            'odds': odds,
            'book': book,
            'decimal': american_to_decimal(odds)
        })

print("-"*80)

# =============================================================
# BETTING RECOMMENDATIONS
# =============================================================

if value_bets:
    print(f"\n💰 VALUE BETS ({len(value_bets)})")
    print("="*60)

    total_risk = 0

    for bet in sorted(value_bets, key=lambda x: -x['edge']):
        # Calculate bet sizes
        kelly = (bet['model_prob'] * bet['decimal'] - 1) / (bet['decimal'] - 1)
        kelly = max(0, min(kelly, 0.15)) * 0.25  # Quarter Kelly
        kelly_bet = BANKROLL * kelly
        flat_bet = BANKROLL * 0.02

        print(f"\n🎯 {bet['pick']}")
        print(f"   Game: {bet['game']}")
        print(f"   Edge: {bet['edge']:+.1%} (Model {bet['model_prob']:.1%} vs Book {bet['book_prob']:.1%})")
        print(f"   Odds: {bet['odds']:+d} @ {bet['book']}")
        print(f"   Flat bet: ${flat_bet:.2f}")
        print(f"   Kelly bet: ${kelly_bet:.2f}")

        total_risk += flat_bet

    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"   Total bets: {len(value_bets)}")
    print(f"   Total risk (flat): ${total_risk:.2f}")
    print(f"   Bankroll: ${BANKROLL:.2f}")
else:
    print("\n❌ No value bets found today")

print(f"\n{'='*60}")
print("📝 PAPER TRADING LOG")
print("Record: Date | Game | Pick | Odds | Bet | Result | P/L")
print("="*60)
