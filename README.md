# MultiSportsBettingPlatform 🏈⚾🏀🏒

A cutting-edge multi-level betting platform with advanced AI features, real-time data integration, and specialized sub-agents for different sports.

## 🚀 Features

### Core Platform
- **Head Agent Coordination**: Centralized system managing specialized sub-agents
- **Multi-Sport Support**: MLB, NFL/CFL, Basketball, Hockey, and more
- **Real-time Data Integration**: Live odds, statistics, and market data
- **Advanced AI/ML**: Transformer models, ensemble learning, pattern recognition
- **User Dashboard**: Comprehensive betting interface and portfolio management
- **Social Features**: User interactions, leaderboards, and community features

### Advanced AI Features V4
- **Transformer Models**: Multi-head attention mechanisms for pattern recognition
- **Deep Learning**: Neural networks for prediction and analysis
- **Ensemble Learning**: Combined predictions from multiple models
- **Pattern Recognition**: Advanced AI pattern detection and analysis
- **Recommendation Engine**: AI-powered betting recommendations

### Technical Stack
- **Backend**: FastAPI, Python 3.12+
- **Database**: PostgreSQL, Redis, SQLite
- **AI/ML**: Custom transformer models, ensemble learning
- **Frontend**: React with Kendo UI components
- **Deployment**: Docker, Kubernetes, Nginx
- **Monitoring**: Prometheus, Grafana

## 🏗️ Architecture

```
MultiSportsBettingPlatform/
├── src/
│   ├── agents/           # Head agent and sub-agents
│   ├── api/             # FastAPI routes and models
│   ├── services/        # Business logic and integrations
│   └── utils/           # Utility functions
├── sub-agents/          # Specialized sports agents
├── sports-betting-kendo-react/  # Frontend application
├── k8s/                 # Kubernetes deployment
├── nginx/               # Reverse proxy configuration
└── monitoring/          # Prometheus configuration
```

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker and Docker Compose
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/MultiSportsBettingPlatform.git
   cd MultiSportsBettingPlatform
   ```

2. **Install Python dependencies**
   ```bash
   py -m pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   cd sports-betting-kendo-react
   npm install
   ```

4. **Start the platform**
   ```bash
   # Start backend services
   py src/main.py
   
   # Start frontend (in another terminal)
   cd sports-betting-kendo-react
   npm start
   ```

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🧠 AI Features

### Advanced AI Features V4
The platform includes cutting-edge AI capabilities:

- **Transformer Models**: Multi-head attention for sequence modeling
- **Ensemble Predictions**: Combined predictions from multiple models
- **Pattern Recognition**: Advanced pattern detection in betting data
- **Recommendation Engine**: AI-powered betting recommendations

### Testing AI Features
```bash
# Test advanced AI features
py advanced_ai_features_v4.py

# Test specific components
py test_advanced_ai_features_v4.py
```

## 📊 System Components

### Head Agent
- Coordinates all sub-agents
- Manages prediction aggregation
- Handles user requests and routing
- Provides system-wide analytics

### Sub-Agents
- **Baseball Agent**: MLB-specific predictions and analysis
- **Football Agent**: NFL/CFL betting strategies
- **Basketball Agent**: NBA/NCAAB analysis
- **Hockey Agent**: NHL predictions and insights

### Services
- **Real-time Data**: Live odds and statistics
- **User Management**: Authentication and preferences
- **Portfolio Management**: Bet tracking and performance
- **Notification System**: Real-time alerts and updates
- **Social Features**: User interactions and leaderboards

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```env
DATABASE_URL=postgresql://user:password@localhost/betting_platform
REDIS_URL=redis://localhost:6379
API_KEY=your_api_key
SECRET_KEY=your_secret_key
```

### Port Configuration
The system uses dynamic port management to avoid conflicts:
- Backend API: 8000-8100 (auto-assigned)
- Frontend: 3000
- Redis: 6379
- PostgreSQL: 5432

## 🧪 Testing

### Run All Tests
```bash
# Test core functionality
py test_complete_system.py

# Test AI features
py test_advanced_ai_features_v4.py

# Test specific components
py test_football_integration.py
py test_baseball_integration.py
```

### Performance Testing
```bash
# Test system performance
py test_performance_optimization.py

# Test scalability
py scalability_performance_system.py
```

## 📈 Monitoring

### System Health
- Real-time system status monitoring
- Performance metrics and analytics
- Error tracking and logging
- Health check endpoints

### Logging
The system uses comprehensive logging with:
- Emoji indicators for visual clarity
- Timestamps and detailed context
- Error tracking and debugging information
- Performance metrics

## 🚀 Deployment

### Production Deployment
```bash
# Deploy to production
py demo_production_deployment.py

# Kubernetes deployment
kubectl apply -f k8s/
```

### Docker Deployment
```bash
# Build production image
docker build -t multisports-betting-platform .

# Run with docker-compose
docker-compose -f docker-compose.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in the `/docs` folder
- Review the test files for usage examples

## 🎯 Roadmap

- [ ] Enhanced AI models with more sports
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Machine learning model training pipeline
- [ ] Real-time streaming improvements
- [ ] Additional sports integration

---

**Built with ❤️ using cutting-edge AI and modern web technologies** 