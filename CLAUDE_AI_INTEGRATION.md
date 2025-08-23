# Claude AI Integration Documentation

## Overview

The MultiSportsBettingPlatform now includes Claude AI integration to enhance prediction capabilities across all sub-agents. Claude AI provides intelligent analysis, reasoning, and predictions based on comprehensive sports data.

## Features

### 🤖 AI-Enhanced Predictions
- **Intelligent Analysis**: Claude AI analyzes team statistics, player performance, weather conditions, and historical data
- **Natural Language Reasoning**: Provides detailed, human-like explanations for predictions
- **Confidence Assessment**: AI-determined confidence levels with explanations
- **Multi-Sport Intelligence**: Sport-specific knowledge and analysis patterns

### 🔄 Fallback System
- **Graceful Degradation**: If Claude AI is unavailable, agents fall back to traditional statistical analysis
- **Error Handling**: Robust error handling ensures system reliability
- **Performance Monitoring**: Real-time monitoring of Claude AI connection status

## Configuration

### API Key Setup
1. **Get Claude API Key**: Obtain an API key from [Anthropic](https://console.anthropic.com/)
2. **Environment Variable**: Set `ANTHROPIC_API_KEY` in your environment:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
   ```
3. **Configuration File**: Add to your `.env` file:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
   ```

### Automatic Detection
- The system automatically detects if Claude AI is available
- Sub-agents show Claude AI status in health checks
- No manual configuration required - works out of the box

## How It Works

### 1. Prediction Flow
```
User Query → Sport Analysis → Claude AI Enhancement → Final Prediction
```

### 2. Claude AI Processing
1. **Data Analysis**: Comprehensive analysis of team/player statistics
2. **Context Building**: Sport-specific context and recent performance
3. **AI Reasoning**: Claude AI generates predictions with detailed reasoning
4. **Confidence Assessment**: AI-determined confidence levels
5. **Response Formatting**: Structured JSON response with prediction details

### 3. Sport-Specific Intelligence
Each sport agent uses specialized prompts:

#### Baseball (MLB)
- Pitching matchup analysis
- Weather and ballpark factors
- Bullpen strength evaluation
- Recent form and head-to-head history

#### Basketball (NBA/NCAAB)
- Team offensive/defensive efficiency
- Player matchups and star power
- Pace of play analysis
- Conference-specific insights

#### Football (NFL/NCAAF)
- Weather impact analysis
- Home field advantage calculations
- Quarterback and key player performance
- Recent form and historical data

#### Hockey (NHL)
- Goalie matchup analysis
- Special teams evaluation
- Home ice advantage factors
- Recent performance trends

## API Integration

### Claude Service
```python
from src.services.claude_service import ClaudeService

# Initialize service
claude_service = ClaudeService()

# Get enhanced prediction
result = await claude_service.get_enhanced_prediction(
    sport="baseball",
    analysis=analysis_data,
    query_text="Dodgers vs Yankees prediction"
)
```

### Sub-Agent Integration
```python
from src.agents.sub_agents import BaseballAgent

# Create agent (Claude AI automatically enabled if API key available)
agent = BaseballAgent()

# Get prediction (automatically uses Claude AI if available)
prediction = await agent.get_prediction({"query_text": "Dodgers vs Yankees"})
```

## Testing

### Test Claude Integration
```bash
py test_claude_integration.py
```

### Test Individual Agents
```bash
py test_sub_agents.py
```

### API Testing
```bash
py run.py
# Visit http://localhost:8000/docs
```

## Health Monitoring

### Claude AI Status
Each sub-agent provides Claude AI status in health checks:

```json
{
  "claude_ai": {
    "enabled": true,
    "status": "connected"
  }
}
```

### Status Types
- **connected**: Claude AI is working properly
- **error**: Claude AI encountered an error
- **disabled**: Claude AI is not configured

## Performance

### Response Times
- **Claude AI Enhanced**: 2-5 seconds (includes API call)
- **Traditional Fallback**: <1 second
- **Error Recovery**: Automatic fallback to traditional analysis

### Rate Limits
- Claude AI has rate limits based on your API plan
- System gracefully handles rate limit errors
- Automatic retry logic for transient failures

## Error Handling

### Common Issues
1. **Missing API Key**: System falls back to traditional analysis
2. **Network Issues**: Automatic retry with exponential backoff
3. **Rate Limits**: Graceful degradation to traditional methods
4. **API Errors**: Detailed error logging and fallback

### Logging
- All Claude AI interactions are logged
- Error details are captured for debugging
- Performance metrics are tracked

## Benefits

### Enhanced Predictions
- **Intelligent Analysis**: AI-powered pattern recognition
- **Natural Language**: Human-like reasoning and explanations
- **Context Awareness**: Sport-specific knowledge and insights
- **Adaptive Learning**: Improves over time with more data

### User Experience
- **Detailed Reasoning**: Clear explanations for predictions
- **Confidence Levels**: AI-assessed confidence with explanations
- **Professional Quality**: High-quality, professional analysis
- **Consistent Format**: Structured, reliable responses

## Future Enhancements

### Phase 1 (Current)
- ✅ Basic Claude AI integration
- ✅ Sport-specific prompts
- ✅ Fallback system
- ✅ Health monitoring

### Phase 2 (Planned)
- Advanced prompt engineering
- Multi-model support (Claude + other AI models)
- Learning from prediction outcomes
- Personalized AI responses

### Phase 3 (Future)
- Real-time data integration
- Advanced statistical modeling
- Cross-sport pattern recognition
- Automated strategy optimization

## Troubleshooting

### Claude AI Not Working
1. **Check API Key**: Verify `ANTHROPIC_API_KEY` is set correctly
2. **Test Connection**: Run `test_claude_integration.py`
3. **Check Logs**: Look for error messages in application logs
4. **Network Issues**: Ensure internet connectivity for API calls

### Performance Issues
1. **Rate Limits**: Check your Anthropic API plan limits
2. **Network Latency**: Monitor API response times
3. **System Resources**: Ensure adequate CPU/memory for processing

### Fallback Behavior
- System automatically falls back to traditional analysis
- No user intervention required
- Predictions continue to work without Claude AI
- Health status shows fallback mode

## Support

For issues with Claude AI integration:
1. Check the logs for detailed error messages
2. Verify API key configuration
3. Test with `test_claude_integration.py`
4. Review this documentation for troubleshooting steps

The Claude AI integration enhances the platform's prediction capabilities while maintaining reliability through robust fallback mechanisms. 