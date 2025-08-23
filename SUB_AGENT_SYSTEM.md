# Sub-Agent System Documentation

## Overview

The Sub-Agent System is a core component of the MultiSportsBettingPlatform that provides sport-specific prediction capabilities. Each sub-agent specializes in a particular sport and provides detailed analysis, predictions, and reasoning.

## Architecture

### Base Sub-Agent (`BaseSubAgent`)
- Abstract base class that all sport-specific agents inherit from
- Implements the `SubAgentInterface` protocol
- Provides common functionality for prediction generation, outcome reporting, and health monitoring
- Includes learning capabilities and accuracy tracking

### Sport-Specific Agents

#### 1. Baseball Agent (`BaseballAgent`)
- **Sport**: MLB (Major League Baseball)
- **Key Features**:
  - Team statistics (wins, losses, runs per game, ERA)
  - Pitcher statistics (ERA, WHIP, K/9)
  - Weather factor analysis
  - Pitching matchup analysis
  - Betting types: moneyline, run line, total runs, first 5 innings, player props

#### 2. Basketball Agent (`BasketballAgent`)
- **Sports**: NBA and NCAAB
- **Key Features**:
  - Team offensive/defensive statistics
  - Player statistics and star power analysis
  - Pace analysis
  - Conference-specific insights
  - Betting types: moneyline, spread, total points, first half, player props

#### 3. Football Agent (`FootballAgent`)
- **Sports**: NFL and NCAAF
- **Key Features**:
  - Team offensive/defensive statistics
  - Passing and rushing analysis
  - Weather impact analysis
  - Home field advantage calculations
  - Betting types: moneyline, spread, total points, first half, player props

#### 4. Hockey Agent (`HockeyAgent`)
- **Sport**: NHL
- **Key Features**:
  - Team offensive/defensive statistics
  - Goalie analysis and statistics
  - Special teams analysis (power play, penalty kill)
  - Ice conditions and home ice advantage
  - Betting types: moneyline, puck line, total goals, first period, player props

## Key Features

### 1. Sport-Specific Analysis
Each agent provides comprehensive analysis including:
- Team matchup analysis
- Player statistics and impact
- Historical data and recent form
- Weather/environmental factors
- Key performance metrics

### 2. Prediction Generation
- Sport-specific prediction algorithms
- Confidence level calculation
- Detailed reasoning generation
- Multiple betting type support

### 3. Learning and Improvement
- Outcome tracking and reporting
- Accuracy history maintenance
- Learning model updates
- Performance monitoring

### 4. Health Monitoring
- Agent health status tracking
- Performance metrics
- Uptime monitoring
- Error handling and recovery

## Usage

### Basic Usage
```python
from src.agents.sub_agents import BaseballAgent, BasketballAgent

# Create agents
baseball_agent = BaseballAgent()
basketball_agent = BasketballAgent()

# Get predictions
prediction = await baseball_agent.get_prediction({"query_text": "Dodgers vs Yankees"})
```

### Integration with Head Agent
```python
from src.agents.head_agent import HeadAgent
from src.agents.sub_agents import BaseballAgent, BasketballAgent

# Initialize Head Agent
head_agent = HeadAgent()

# Register sub-agents
await head_agent.register_sub_agent(SportType.BASEBALL, BaseballAgent())
await head_agent.register_sub_agent(SportType.BASKETBALL, BasketballAgent())

# Get aggregated predictions
result = await head_agent.aggregate_predictions(user_query)
```

## Testing

### Individual Agent Testing
```bash
py test_sub_agents.py
```

### API Testing
```bash
py run.py
# Then visit http://localhost:8000/docs for API documentation
```

## Data Sources

### Current Implementation
- **Simulated Data**: Uses realistic but simulated team and player statistics
- **Historical Data**: Simulated head-to-head records and recent form
- **Weather Data**: Simulated weather conditions and impact

### Future Enhancements
- **Real-time APIs**: Integration with sports data providers
- **Live Statistics**: Real-time team and player statistics
- **Weather APIs**: Real weather data integration
- **News and Injury Data**: Latest team news and injury reports

## Configuration

### Agent Configuration
Each agent can be configured with:
- Custom team databases
- Player statistics
- Betting type preferences
- Analysis parameters

### Performance Tuning
- Confidence calculation algorithms
- Prediction weighting factors
- Learning rate adjustments
- Accuracy thresholds

## Monitoring and Maintenance

### Health Checks
- Agent availability monitoring
- Performance metrics tracking
- Error rate monitoring
- Response time analysis

### Updates and Maintenance
- Regular data updates
- Algorithm improvements
- New team/player additions
- Betting type expansions

## Future Roadmap

### Phase 1 (Current)
- ✅ Basic sub-agent implementation
- ✅ Sport-specific analysis
- ✅ Prediction generation
- ✅ Health monitoring

### Phase 2 (Planned)
- Real-time data integration
- Advanced machine learning models
- Cross-sport pattern recognition
- User preference learning

### Phase 3 (Future)
- AI-powered prediction refinement
- Advanced statistical modeling
- Real-time market analysis
- Automated betting recommendations 