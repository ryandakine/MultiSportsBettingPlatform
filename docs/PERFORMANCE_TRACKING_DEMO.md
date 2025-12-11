# 🚀 Performance Tracking API Demo - YOLO MODE!

## 🎯 Overview
The new **Multidimensional Performance Tracking Service** is now live on both Basketball (Port 8006) and Hockey (Port 8005) systems! This advanced analytics engine provides comprehensive betting performance analysis, ROI calculations, streak analysis, and AI-generated insights.

## 🏀 Basketball System (Port 8006)
### New Performance Tracking Endpoints:

#### 1. **Track Betting Performance**
```bash
POST http://localhost:8006/api/v1/performance/track
```
**Request Body:**
```json
{
  "user_id": "user123",
  "bet_data": {
    "bet_type": "moneyline",
    "teams": ["Lakers", "Celtics"],
    "prediction": "Lakers ML",
    "actual_result": "Lakers Win",
    "bet_amount": 100.0,
    "payout": 150.0,
    "odds": 1.5,
    "confidence": 0.75,
    "council_analysis": [
      {"member": "offensive_specialist", "confidence": 0.8},
      {"member": "defensive_analyst", "confidence": 0.7}
    ],
    "yolo_factor": 1.2
  }
}
```

#### 2. **Get Performance Summary**
```bash
GET http://localhost:8006/api/v1/performance/summary?user_id=user123
```

#### 3. **Get ROI Analysis**
```bash
GET http://localhost:8006/api/v1/performance/roi?user_id=user123
```

#### 4. **Get Performance Insights**
```bash
GET http://localhost:8006/api/v1/performance/insights?user_id=user123
```

#### 5. **Get System Performance Stats**
```bash
GET http://localhost:8006/api/v1/performance/stats
```

## 🏒 Hockey System (Port 8005)
### Same Performance Tracking Endpoints:

#### 1. **Track Betting Performance**
```bash
POST http://localhost:8005/api/v1/performance/track
```
**Request Body:**
```json
{
  "user_id": "hockey_user",
  "bet_data": {
    "bet_type": "moneyline",
    "teams": ["Bruins", "Lightning"],
    "prediction": "Bruins ML",
    "actual_result": "Bruins Win",
    "bet_amount": 75.0,
    "payout": 120.0,
    "odds": 1.6,
    "confidence": 0.85,
    "council_analysis": [
      {"member": "goalie_expert", "confidence": 0.9},
      {"member": "offensive_specialist", "confidence": 0.8}
    ],
    "yolo_factor": 1.3
  }
}
```

#### 2. **Get Performance Summary**
```bash
GET http://localhost:8005/api/v1/performance/summary?user_id=hockey_user
```

#### 3. **Get ROI Analysis**
```bash
GET http://localhost:8005/api/v1/performance/roi?user_id=hockey_user
```

#### 4. **Get Performance Insights**
```bash
GET http://localhost:8005/api/v1/performance/insights?user_id=hockey_user
```

#### 5. **Get System Performance Stats**
```bash
GET http://localhost:8005/api/v1/performance/stats
```

## 🧠 Advanced Features

### **ROI Analysis**
- Overall ROI calculation
- ROI by bet type (moneyline, spread, totals)
- ROI by team performance
- Historical ROI trends

### **Streak Analysis**
- Current win/loss streaks
- Longest winning streaks
- Pattern recognition
- Streak-based recommendations

### **AI-Generated Insights**
- Risk assessment levels
- Performance recommendations
- Strength identification
- Improvement suggestions

### **Real-time Analytics**
- Live performance tracking
- Instant ROI calculations
- Dynamic confidence adjustments
- Council performance analysis

## 🎯 Example Usage Scenarios

### **Scenario 1: Track a Winning Bet**
```python
import requests

# Track a successful basketball bet
bet_data = {
    "user_id": "pro_trader",
    "bet_data": {
        "bet_type": "moneyline",
        "teams": ["Lakers", "Celtics"],
        "prediction": "Lakers ML",
        "actual_result": "Lakers Win",
        "bet_amount": 200.0,
        "payout": 300.0,
        "odds": 1.5,
        "confidence": 0.85,
        "council_analysis": [
            {"member": "offensive_specialist", "confidence": 0.9},
            {"member": "defensive_analyst", "confidence": 0.8}
        ],
        "yolo_factor": 1.2
    }
}

response = requests.post("http://localhost:8006/api/v1/performance/track", json=bet_data)
result = response.json()
print(f"ROI: {result['roi']:.2f}%")
```

### **Scenario 2: Get Performance Summary**
```python
# Get comprehensive performance summary
response = requests.get("http://localhost:8006/api/v1/performance/summary?user_id=pro_trader")
summary = response.json()
metrics = summary['performance_summary']['performance_metrics']
print(f"Total Bets: {metrics['total_bets']}")
print(f"Win Rate: {metrics['win_rate']:.1f}%")
print(f"Overall ROI: {metrics['overall_roi']:.2f}%")
```

### **Scenario 3: Get AI Insights**
```python
# Get AI-generated performance insights
response = requests.get("http://localhost:8006/api/v1/performance/insights?user_id=pro_trader")
insights = response.json()
print(f"Risk Level: {insights['insights']['risk_assessment']}")
print(f"Recommendations: {insights['insights']['recommendations']}")
```

## 🚀 YOLO MODE Features

### **Maximum Confidence Tracking**
- Real-time confidence adjustments
- YOLO factor integration
- Council consensus analysis
- Dynamic risk assessment

### **Advanced Analytics Engine**
- Pattern recognition algorithms
- Streak analysis
- Performance correlation
- Predictive modeling

### **Comprehensive Reporting**
- Detailed performance metrics
- ROI breakdowns
- Trend analysis
- AI-powered insights

## 🎉 Success Metrics

✅ **Performance Tracking**: Real-time bet tracking with ROI calculations  
✅ **Streak Analysis**: Advanced pattern recognition and streak identification  
✅ **AI Insights**: Machine learning-powered recommendations  
✅ **ROI Analysis**: Comprehensive return on investment calculations  
✅ **System Stats**: Real-time system performance monitoring  
✅ **Council Integration**: 5 AI Council performance analysis  
✅ **YOLO Mode**: Maximum confidence features with dynamic adjustments  

## 🔧 Technical Implementation

### **Data Structures**
- `BettingPerformance`: Individual bet tracking
- `UserPerformanceMetrics`: Comprehensive user statistics
- `PerformanceInsights`: AI-generated insights
- `StreakAnalysis`: Advanced streak and pattern analysis
- `ROIAnalysis`: Comprehensive ROI calculations

### **API Endpoints**
- `POST /api/v1/performance/track`: Track individual bets
- `GET /api/v1/performance/summary`: Get user performance summary
- `GET /api/v1/performance/roi`: Get detailed ROI analysis
- `GET /api/v1/performance/insights`: Get AI-generated insights
- `GET /api/v1/performance/stats`: Get system performance statistics

### **Real-time Features**
- Live performance monitoring
- Instant calculations
- Dynamic updates
- Real-time analytics

---

## 🎯 Ready to Test!

Both Basketball (Port 8006) and Hockey (Port 8005) systems now have full **Multidimensional Performance Tracking** capabilities! 

**Next Steps:**
1. Start both systems
2. Run performance tracking tests
3. Explore the new API endpoints
4. Analyze performance data
5. Get AI-generated insights

The enhanced systems are ready for maximum confidence betting with advanced analytics! 🚀 