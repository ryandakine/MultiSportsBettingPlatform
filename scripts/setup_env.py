#!/usr/bin/env python3
"""
Setup environment file for MultiSportsBettingPlatform
"""

import os
import shutil

def setup_environment():
    """Set up the environment file."""
    print("🔧 Setting up environment configuration...")
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    # Check if env.example exists
    if os.path.exists('env.example'):
        try:
            # Copy env.example to .env
            shutil.copy('env.example', '.env')
            print("✅ Created .env file from env.example")
            print("📝 Edit .env file to add your API keys and configuration")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        # Create a basic .env file
        env_content = """# MultiSportsBettingPlatform Environment Configuration

# Application
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database (using SQLite for development)
DATABASE_URL=sqlite:///./multisports_betting.db

# Redis (optional for development)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (Add your actual keys here)
ANTHROPIC_API_KEY=sk-ant-api03-your-claude-key-here
PERPLEXITY_API_KEY=pplx-your-perplexity-key-here
OPENAI_API_KEY=sk-your-openai-key-here

# Sports APIs (Add your actual keys here)
ESPN_API_KEY=your-espn-api-key-here
SPORTS_DATA_API_KEY=your-sports-data-api-key-here
"""
        
        try:
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ Created basic .env file")
            print("📝 Edit .env file to add your API keys and configuration")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False

if __name__ == "__main__":
    success = setup_environment()
    if success:
        print("\n🎉 Environment setup complete!")
        print("Next steps:")
        print("1. Edit .env file to add your API keys")
        print("2. Run: py install_deps.py")
        print("3. Run: py run.py")
    else:
        print("\n❌ Environment setup failed.")
        print("Please create .env file manually from env.example") 