# NCAA Playoff Research Plan

## Goal
Research and analyze NCAA playoff game patterns to find correlations and develop playoff-specific betting strategies, especially for parlays.

## Research Approach

### 1. Data Collection
- **Script**: `scripts/research_ncaa_playoff_patterns.py`
- **Data Sources**:
  - ESPN API (historical playoff games)
  - The Odds API (historical odds for playoff games)
  - Manual data collection if needed
- **Time Period**: Last 10 years (2014-2024+) of playoff data
- **Game Types**: 
  - College Football Playoff (CFP)
  - Bowl games (New Year's Six, etc.)
  - Conference championships
  - Final Four, March Madness (if applicable)

### 2. Patterns to Research

#### A. Win Patterns
- **Who wins**: Favorite vs underdog win rates
- **Ranking correlation**: Higher ranked teams win more often?
- **Conference dominance**: Do certain conferences perform better in playoffs?
- **Home field advantage**: Does home team advantage exist in neutral site games?

#### B. Game Characteristics
- **Margin of victory**: Blowouts vs close games frequency
- **Scoring patterns**: Over/under trends in playoff games
- **Round-by-round analysis**: Patterns differ by round (semifinal vs championship)?

#### C. "Scripted" Patterns
- **Cinderella stories**: Underdog upsets - when do they happen?
- **Favorite dominance**: Do favorites win as expected or do upsets occur?
- **Timing patterns**: Early vs late playoff rounds - different patterns?

### 3. Analysis Methods

1. **Statistical Analysis**:
   - Win rates by round
   - Average margins by round
   - Home/away performance
   - Conference performance

2. **Correlation Analysis**:
   - Rankings vs outcomes
   - Regular season performance vs playoff performance
   - Spread vs actual margin

3. **Pattern Recognition**:
   - Identify recurring patterns
   - Flag anomalies
   - Test for "scripted" behavior

### 4. Integration into System

#### A. Playoff Detection
- **Service**: `src/services/playoff_detector.py`
- **Features**:
  - Detects playoff games by name and date
  - Identifies playoff round
  - Provides playoff-specific adjustments

#### B. Parlay Strategy Adjustments
- **Location**: `src/services/parlay_builder.py`
- **Adjustments**:
  - Different confidence thresholds for playoff games
  - Adjusted edge requirements
  - Round-specific strategies
  - Playoff game prioritization in parlay selection

### 5. Running the Research

```bash
# Run the research script
cd /home/ryan/MultiSportsBettingPlatform
python3 scripts/research_ncaa_playoff_patterns.py
```

The script will:
1. Fetch historical playoff games from ESPN
2. Analyze patterns
3. Save results to `data/playoff_research/`
4. Generate a research report

### 6. Next Steps After Research

1. **Review Findings**: Analyze the generated report
2. **Refine Patterns**: Identify strongest correlations
3. **Update Strategies**: Integrate findings into betting logic
4. **Test**: Backtest playoff-specific strategies
5. **Deploy**: Use playoff strategies in live betting

### 7. Expected Outcomes

- **Pattern Documentation**: Clear patterns in playoff games
- **Strategy Adjustments**: Specific rules for playoff games
- **Confidence Levels**: How confident we can be in playoff patterns
- **Parlay Optimization**: Better parlay construction for playoff season

## Notes

- Research is data-driven - we need actual data to support any "scripted" claims
- Patterns should be statistically significant (sufficient sample size)
- Adjustments should be conservative until patterns are proven
- Focus on parlays as per user priority


