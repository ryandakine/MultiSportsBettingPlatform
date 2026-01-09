# How Confidence & Probability Percentages Are Calculated

## Overview

The system calculates probabilities at two levels:
1. **Individual Leg Probabilities** - Each bet in the parlay
2. **Combined Probability** - The probability that ALL legs win (for the parlay)

## Step-by-Step Calculation

### 1. Individual Leg Probability (for each bet)

For each leg in the parlay:

```python
# Step 1: Get odds from The Odds API (real betting odds)
american_odds = -110  # Example: -110 means bet $110 to win $100

# Step 2: Convert American odds to implied probability
if american_odds > 0:
    implied_prob = 100 / (american_odds + 100)
else:
    implied_prob = abs(american_odds) / (abs(american_odds) + 100)

# Example: -110 odds → implied_prob = 110 / (110 + 100) = 0.5238 (52.38%)

# Step 3: Get edge from prediction
edge = 0.05  # Example: 5% edge (model thinks we have 5% advantage)

# Step 4: Calculate model probability (what we think the TRUE probability is)
model_prob = implied_prob + edge
model_prob = max(0.01, min(0.99, model_prob))  # Cap between 1% and 99%

# Example: 0.5238 + 0.05 = 0.5738 (57.38% - our model thinks it's more likely than the odds suggest)
```

**Where edge comes from:**
- Currently in `generate_predictions_with_betting_metadata.py`:
  ```python
  model_probability = 0.65  # Assumes model thinks 65% chance
  probability = implied_probability_from_odds  # What odds say
  edge = model_probability - probability  # Difference = edge
  ```
- **ISSUE**: This assumes 65% for everything, which is simplistic

### 2. Combined Probability (for the parlay)

Once we have model probabilities for each leg:

```python
# Multiply all individual probabilities together
combined_prob = model_prob_leg1 * model_prob_leg2 * model_prob_leg3 * ... * model_prob_leg6

# Example for 6-leg parlay:
# Leg 1: 57.38% (0.5738)
# Leg 2: 60.00% (0.6000)
# Leg 3: 55.00% (0.5500)
# Leg 4: 58.00% (0.5800)
# Leg 5: 56.00% (0.5600)
# Leg 6: 59.00% (0.5900)
# Combined: 0.5738 * 0.6000 * 0.5500 * 0.5800 * 0.5600 * 0.5900 = 0.0347 (3.47%)
```

**Why multiply?** Because ALL legs must win for the parlay to win. The probability of multiple independent events all occurring is the product of their individual probabilities.

### 3. Confidence Level (for 6-leg parlays)

Based on the combined probability:

```python
if combined_prob > 0.10:      # > 10%
    confidence_level = "HIGH"
elif combined_prob > 0.05:     # 5-10%
    confidence_level = "MEDIUM"
else:                          # < 5%
    confidence_level = "LOW"
```

## Current Issues

### 1. **Simplistic Edge Calculation**
The edge is currently calculated as:
```python
model_probability = 0.65  # Fixed 65% for everything
edge = model_probability - probability_from_odds
```

**Problem**: This assumes every bet has a 65% chance, regardless of:
- Team strength
- Historical performance
- Actual model predictions
- Game context

**Should be**: Edge should come from actual model predictions that analyze:
- Team statistics
- Recent performance
- Head-to-head records
- Injury reports
- etc.

### 2. **No Real Model Integration**
The system doesn't actually use ML/AI models to predict probabilities. It just:
- Gets odds from The Odds API
- Assumes 65% model probability
- Calculates edge as the difference

### 3. **Confidence vs Probability Confusion**
- **Confidence** (0-1): How confident the model is in its prediction
- **Probability** (0-1): The actual chance of winning
- Currently these are being conflated

## What Should Happen

1. **Real Model Predictions**: Use actual ML models to predict win probabilities
2. **Dynamic Edge Calculation**: Edge = model_predicted_prob - implied_prob_from_odds
3. **Better Confidence Metrics**: Separate confidence (model certainty) from probability (actual chance)

## Example Calculation Flow

```
Game: Lakers vs Celtics
Odds: Lakers -150 (bet $150 to win $100)
Implied Prob: 150 / (150 + 100) = 0.60 (60%)

Model Analysis:
- Lakers recent form: Strong
- Head-to-head: Lakers 3-1
- Injuries: Celtics missing key player
- Model predicts: 70% chance Lakers win

Edge = 0.70 - 0.60 = 0.10 (10% edge)
Model Prob = 0.60 + 0.10 = 0.70 (70%)

For 6-leg parlay:
Leg 1: 70% (0.70)
Leg 2: 65% (0.65)
Leg 3: 68% (0.68)
Leg 4: 62% (0.62)
Leg 5: 70% (0.70)
Leg 6: 64% (0.64)

Combined: 0.70 * 0.65 * 0.68 * 0.62 * 0.70 * 0.64 = 0.087 (8.7%)
Confidence: MEDIUM (between 5% and 10%)
```

## Recommendations

1. **Integrate Real Model Predictions**: Replace the fixed 65% assumption with actual model outputs
2. **Track Model Performance**: Compare predicted probabilities to actual outcomes to improve models
3. **Separate Confidence from Probability**: Use confidence as a measure of model certainty, not win probability
4. **Calibrate Models**: Ensure predicted probabilities match actual win rates over time


