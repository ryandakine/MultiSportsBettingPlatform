"""
Database Verification Script
===========================
Verifies that the database connection works, tables can be created,
and models can be queried.
"""
import sys
import os
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.db.database import engine, SessionLocal, Base
from src.db.models.user import User
from src.db.models.prediction import Prediction

def verify_db():
    print("🔄 Initializing verification...")
    
    # 1. Create Tables (Bypassing Alembic for logical verification)
    print("🛠️  Creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully via SQLAlchemy")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

    # 2. Test User CRUD
    print("👤 Testing User CRUD...")
    db = SessionLocal()
    try:
        # Create
        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            username=f"test_user_{int(datetime.now().timestamp())}",
            email=f"test_{int(datetime.now().timestamp())}@example.com",
            password_hash="hashed_secret",
            role="admin",
            preferences={"theme": "dark"}
        )
        db.add(new_user)
        db.commit()
        
        # Read
        fetched_user = db.query(User).filter(User.id == user_id).first()
        if fetched_user and fetched_user.username == new_user.username:
            print("✅ User created and fetched successfully")
            print(f"   ID: {fetched_user.id}")
            print(f"   Prefs: {fetched_user.preferences}")
        else:
            print("❌ User fetch failed or mismatch")
            return False
            
    except Exception as e:
        print(f"❌ User CRUD failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

    # 3. Test Prediction CRUD
    print("🎲 Testing Prediction CRUD...")
    db = SessionLocal()
    try:
        # Create
        pred_id = f"pred_{int(datetime.now().timestamp())}"
        new_prediction = Prediction(
            id=pred_id,
            sport="football",
            prediction_text="Team A wins",
            confidence="high",
            timestamp=datetime.utcnow(),
            metadata_json={"weather": "sunny"}
        )
        db.add(new_prediction)
        db.commit()
        
        # Read
        fetched_pred = db.query(Prediction).filter(Prediction.id == pred_id).first()
        if fetched_pred and fetched_pred.prediction_text == "Team A wins":
            print("✅ Prediction created and fetched successfully")
        else:
            print("❌ Prediction fetch failed")
            return False
            
    except Exception as e:
        print(f"❌ Prediction CRUD failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

    print("🎉 All database verification tests passed!")
    return True

if __name__ == "__main__":
    if verify_db():
        sys.exit(0)
    else:
        sys.exit(1)
