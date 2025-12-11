# Quick Setup Guide

## 🚀 Get MultiSportsBettingPlatform Running in 3 Steps

### Step 1: Install Dependencies
```bash
py install_deps.py
```

### Step 2: Run the Application
```bash
py run.py
```

### Step 3: Test the Application
Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root Endpoint**: http://localhost:8000/

## 🔧 What Each Script Does

### `install_deps.py`
- Installs all required Python packages from `requirements.txt`
- Ensures `python-dotenv`, `fastapi`, `uvicorn`, and `pydantic` are available
- Provides clear feedback on installation progress

### `run.py`
- Starts the FastAPI application with auto-reload
- Automatically installs missing dependencies if needed
- Shows helpful startup messages with API documentation links

## 🎯 Next Steps After Setup

1. **Configure Environment**: Copy `env.example` to `.env` and add your API keys
2. **Start Development**: Begin working on Task 2 (Head Agent Architecture)
3. **Test Features**: Use the API documentation to test endpoints

## 🐛 Troubleshooting

If you encounter issues:

1. **Module not found errors**: Run `py install_deps.py` again
2. **Port already in use**: Change the port in `run.py` or kill the existing process
3. **Environment issues**: Make sure you're in the correct virtual environment

## 📚 Available Commands

```bash
# Install dependencies
py install_deps.py

# Start the application
py run.py

# Run tests
py -m pytest tests/

# Format code
py -m black src/ tests/

# Lint code
py -m flake8 src/ tests/
``` 