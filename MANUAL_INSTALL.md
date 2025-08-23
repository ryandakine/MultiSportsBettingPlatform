# Manual Installation Guide

Since the automated installation is being blocked, here's how to install dependencies manually:

## 🔧 Step 1: Install Python Dependencies

Open a new terminal/command prompt and run:

```bash
# Activate your virtual environment (if using one)
.venv\Scripts\activate

# Install the required packages
pip install python-dotenv
pip install fastapi
pip install uvicorn
pip install pydantic
pip install -r requirements.txt
```

## 🚀 Step 2: Run the Application

After installing dependencies, run:

```bash
py run.py
```

## 📋 Alternative: Install Individual Packages

If the above doesn't work, install these packages one by one:

```bash
pip install python-dotenv
pip install fastapi
pip install uvicorn
pip install pydantic
pip install httpx
pip install redis
pip install sqlalchemy
pip install pytest
```

## 🎯 Step 3: Test the Application

Once running, visit:
- http://localhost:8000/docs (API Documentation)
- http://localhost:8000/health (Health Check)
- http://localhost:8000/ (Root Endpoint)

## 🐛 Troubleshooting

If you get permission errors:
```bash
pip install --user python-dotenv
```

If you get SSL errors:
```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org python-dotenv
```

## ✅ Success Indicators

You'll know it's working when:
1. No more "ModuleNotFoundError" messages
2. The application starts and shows "Uvicorn running on http://0.0.0.0:8000"
3. You can access the API documentation at http://localhost:8000/docs 