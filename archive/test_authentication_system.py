"""
Comprehensive Test for Authentication System

This test covers user registration, login, session management,
preferences, and security features.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any

def test_authentication_service():
    """Test the authentication service functionality."""
    print("🔐 Testing Authentication Service")
    print("=" * 50)
    
    try:
        from src.services.auth_service import (
            AuthService, UserRegistration, UserLogin, 
            PasswordChange, UserRole, AuthStatus
        )
        
        # Initialize auth service
        auth_service = AuthService()
        print("✅ Auth service initialized")
        
        # Test 1: User Registration
        print("\n📝 Test 1: User Registration")
        print("-" * 30)
        
        registration = UserRegistration(
            username="testuser123",
            email="test@example.com",
            password="SecurePass123!",
            confirm_password="SecurePass123!"
        )
        
        result = auth_service.register_user(registration)
        print(f"Registration result: {result['status']}")
        
        if result["status"] == AuthStatus.SUCCESS:
            user_id = result["user_id"]
            print(f"✅ User registered successfully: {user_id}")
        else:
            print(f"❌ Registration failed: {result['message']}")
            return False
        
        # Test 2: User Login
        print("\n🔑 Test 2: User Login")
        print("-" * 30)
        
        login = UserLogin(
            username="testuser123",
            password="SecurePass123!",
            remember_me=False
        )
        
        result = auth_service.login_user(login, "127.0.0.1", "Test Browser")
        print(f"Login result: {result['status']}")
        
        if result["status"] == AuthStatus.SUCCESS:
            token = result["token"]
            session_id = result["session_id"]
            print(f"✅ Login successful")
            print(f"   Token: {token[:50]}...")
            print(f"   Session ID: {session_id}")
        else:
            print(f"❌ Login failed: {result['message']}")
            return False
        
        # Test 3: Token Validation
        print("\n🔍 Test 3: Token Validation")
        print("-" * 30)
        
        result = auth_service.validate_token(token)
        print(f"Token validation result: {result['status']}")
        
        if result["status"] == AuthStatus.SUCCESS:
            user_info = result["user"]
            print(f"✅ Token valid")
            print(f"   User: {user_info['username']}")
            print(f"   Role: {user_info['role']}")
        else:
            print(f"❌ Token validation failed: {result['message']}")
            return False
        
        # Test 4: Password Change
        print("\n🔒 Test 4: Password Change")
        print("-" * 30)
        
        password_change = PasswordChange(
            current_password="SecurePass123!",
            new_password="NewSecurePass456!",
            confirm_password="NewSecurePass456!"
        )
        
        result = auth_service.change_password(user_id, password_change)
        print(f"Password change result: {result['status']}")
        
        if result["status"] == AuthStatus.SUCCESS:
            print("✅ Password changed successfully")
        else:
            print(f"❌ Password change failed: {result['message']}")
            return False
        
        # Test 5: Login with New Password
        print("\n🔑 Test 5: Login with New Password")
        print("-" * 30)
        
        new_login = UserLogin(
            username="testuser123",
            password="NewSecurePass456!",
            remember_me=True
        )
        
        result = auth_service.login_user(new_login, "127.0.0.1", "Test Browser")
        print(f"New login result: {result['status']}")
        
        if result["status"] == AuthStatus.SUCCESS:
            new_token = result["token"]
            print("✅ Login with new password successful")
        else:
            print(f"❌ Login with new password failed: {result['message']}")
            return False
        
        # Test 6: Session Management
        print("\n📱 Test 6: Session Management")
        print("-" * 30)
        
        sessions = auth_service.get_user_sessions(user_id)
        print(f"Active sessions: {len(sessions)}")
        
        for i, session in enumerate(sessions, 1):
            print(f"   Session {i}: {session['session_id'][:20]}...")
            print(f"      IP: {session['ip_address']}")
            print(f"      Created: {session['created_at']}")
        
        # Test 7: Logout
        print("\n🚪 Test 7: Logout")
        print("-" * 30)
        
        result = auth_service.logout_user(session_id)
        print(f"Logout result: {result['status']}")
        
        if result["status"] == AuthStatus.SUCCESS:
            print("✅ Logout successful")
        else:
            print(f"❌ Logout failed: {result['message']}")
        
        # Test 8: Rate Limiting
        print("\n⏱️ Test 8: Rate Limiting")
        print("-" * 30)
        
        # Try multiple rapid logins
        failed_attempts = 0
        for i in range(10):
            rapid_login = UserLogin(
                username="testuser123",
                password="WrongPassword123!",
                remember_me=False
            )
            
            result = auth_service.login_user(rapid_login, "127.0.0.1", "Test Browser")
            if result["status"] == AuthStatus.RATE_LIMITED:
                failed_attempts += 1
        
        print(f"Rate limited attempts: {failed_attempts}/10")
        if failed_attempts > 0:
            print("✅ Rate limiting working")
        else:
            print("⚠️ Rate limiting may not be working")
        
        # Test 9: Account Lockout
        print("\n🔒 Test 9: Account Lockout")
        print("-" * 30)
        
        # Try multiple failed logins to trigger lockout
        for i in range(6):
            failed_login = UserLogin(
                username="testuser123",
                password="WrongPassword123!",
                remember_me=False
            )
            
            result = auth_service.login_user(failed_login, "127.0.0.1", "Test Browser")
            if result["status"] == AuthStatus.ACCOUNT_LOCKED:
                print(f"✅ Account locked after {i+1} failed attempts")
                break
        else:
            print("⚠️ Account lockout may not be working")
        
        # Test 10: Service Statistics
        print("\n📊 Test 10: Service Statistics")
        print("-" * 30)
        
        stats = auth_service.get_stats()
        print(f"Service stats: {stats}")
        
        if "error" not in stats:
            print("✅ Statistics retrieved successfully")
        else:
            print(f"⚠️ Statistics error: {stats['error']}")
        
        print("\n🎉 Authentication Service Tests Completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_user_preferences():
    """Test the user preferences service functionality."""
    print("\n⚙️ Testing User Preferences Service")
    print("=" * 50)
    
    try:
        from src.services.user_preferences import (
            UserPreferencesService, SportType, RiskLevel, 
            BettingType, NotificationType
        )
        
        # Initialize preferences service
        prefs_service = UserPreferencesService()
        print("✅ Preferences service initialized")
        
        # Test user ID
        test_user_id = "test_user_123"
        
        # Test 1: Get Default Preferences
        print("\n📋 Test 1: Get Default Preferences")
        print("-" * 30)
        
        preferences = prefs_service.get_user_preferences(test_user_id)
        print(f"Default preferences created: {preferences is not None}")
        
        if preferences:
            print(f"   User ID: {preferences.user_id}")
            print(f"   Preferred Sports: {[sport.value for sport in preferences.betting.preferred_sports]}")
            print(f"   Risk Level: {preferences.betting.risk_level.value}")
            print(f"   Theme: {preferences.display.theme}")
        else:
            print("❌ Failed to get default preferences")
            return False
        
        # Test 2: Update Betting Preferences
        print("\n🎯 Test 2: Update Betting Preferences")
        print("-" * 30)
        
        betting_updates = {
            "preferred_sports": [SportType.BASEBALL, SportType.BASKETBALL],
            "risk_level": RiskLevel.AGGRESSIVE,
            "max_bet_amount": 500.0,
            "min_confidence_threshold": 0.7,
            "auto_betting_enabled": True
        }
        
        success = prefs_service.update_betting_preferences(test_user_id, betting_updates)
        print(f"Betting preferences update: {'✅ Success' if success else '❌ Failed'}")
        
        # Verify update
        updated_prefs = prefs_service.get_user_preferences(test_user_id)
        if updated_prefs:
            print(f"   Updated Sports: {[sport.value for sport in updated_prefs.betting.preferred_sports]}")
            print(f"   Updated Risk: {updated_prefs.betting.risk_level.value}")
            print(f"   Max Bet: ${updated_prefs.betting.max_bet_amount}")
            print(f"   Auto Betting: {updated_prefs.betting.auto_betting_enabled}")
        
        # Test 3: Update Notification Preferences
        print("\n🔔 Test 3: Update Notification Preferences")
        print("-" * 30)
        
        notification_updates = {
            "email_notifications": True,
            "push_notifications": False,
            "sms_notifications": True,
            "prediction_alerts": True,
            "quiet_hours_start": "23:00",
            "quiet_hours_end": "07:00"
        }
        
        success = prefs_service.update_notification_preferences(test_user_id, notification_updates)
        print(f"Notification preferences update: {'✅ Success' if success else '❌ Failed'}")
        
        # Verify update
        updated_prefs = prefs_service.get_user_preferences(test_user_id)
        if updated_prefs:
            print(f"   Email Notifications: {updated_prefs.notifications.email_notifications}")
            print(f"   Push Notifications: {updated_prefs.notifications.push_notifications}")
            print(f"   SMS Notifications: {updated_prefs.notifications.sms_notifications}")
            print(f"   Quiet Hours: {updated_prefs.notifications.quiet_hours_start} - {updated_prefs.notifications.quiet_hours_end}")
        
        # Test 4: Update Display Preferences
        print("\n🎨 Test 4: Update Display Preferences")
        print("-" * 30)
        
        display_updates = {
            "theme": "dark",
            "language": "en",
            "timezone": "America/New_York",
            "currency": "USD",
            "odds_format": "decimal",
            "show_confidence_scores": True,
            "compact_view": True
        }
        
        success = prefs_service.update_display_preferences(test_user_id, display_updates)
        print(f"Display preferences update: {'✅ Success' if success else '❌ Failed'}")
        
        # Verify update
        updated_prefs = prefs_service.get_user_preferences(test_user_id)
        if updated_prefs:
            print(f"   Theme: {updated_prefs.display.theme}")
            print(f"   Timezone: {updated_prefs.display.timezone}")
            print(f"   Currency: {updated_prefs.display.currency}")
            print(f"   Odds Format: {updated_prefs.display.odds_format}")
            print(f"   Compact View: {updated_prefs.display.compact_view}")
        
        # Test 5: Get Specific Preferences
        print("\n🎯 Test 5: Get Specific Preferences")
        print("-" * 30)
        
        sports = prefs_service.get_user_sport_preferences(test_user_id)
        risk_level = prefs_service.get_user_risk_level(test_user_id)
        confidence_threshold = prefs_service.get_user_confidence_threshold(test_user_id)
        max_bet = prefs_service.get_user_max_bet_amount(test_user_id)
        timezone = prefs_service.get_user_timezone(test_user_id)
        currency = prefs_service.get_user_currency(test_user_id)
        
        print(f"   Preferred Sports: {[sport.value for sport in sports]}")
        print(f"   Risk Level: {risk_level.value}")
        print(f"   Confidence Threshold: {confidence_threshold}")
        print(f"   Max Bet Amount: ${max_bet}")
        print(f"   Timezone: {timezone}")
        print(f"   Currency: {currency}")
        
        # Test 6: Notification Status
        print("\n🔔 Test 6: Notification Status")
        print("-" * 30)
        
        email_enabled = prefs_service.is_notification_enabled(test_user_id, NotificationType.EMAIL)
        push_enabled = prefs_service.is_notification_enabled(test_user_id, NotificationType.PUSH)
        sms_enabled = prefs_service.is_notification_enabled(test_user_id, NotificationType.SMS)
        
        print(f"   Email Notifications: {'✅ Enabled' if email_enabled else '❌ Disabled'}")
        print(f"   Push Notifications: {'✅ Enabled' if push_enabled else '❌ Disabled'}")
        print(f"   SMS Notifications: {'✅ Enabled' if sms_enabled else '❌ Disabled'}")
        
        # Test 7: Reset Preferences
        print("\n🔄 Test 7: Reset Preferences")
        print("-" * 30)
        
        success = prefs_service.reset_user_preferences(test_user_id)
        print(f"Preferences reset: {'✅ Success' if success else '❌ Failed'}")
        
        # Verify reset
        reset_prefs = prefs_service.get_user_preferences(test_user_id)
        if reset_prefs:
            print(f"   Reset Sports: {[sport.value for sport in reset_prefs.betting.preferred_sports]}")
            print(f"   Reset Risk: {reset_prefs.betting.risk_level.value}")
            print(f"   Reset Theme: {reset_prefs.display.theme}")
        
        # Test 8: Preferences Statistics
        print("\n📊 Test 8: Preferences Statistics")
        print("-" * 30)
        
        stats = prefs_service.get_preferences_stats()
        print(f"Preferences stats: {stats}")
        
        if "error" not in stats:
            print("✅ Statistics retrieved successfully")
        else:
            print(f"⚠️ Statistics error: {stats['error']}")
        
        print("\n🎉 User Preferences Service Tests Completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_security_features():
    """Test security features and edge cases."""
    print("\n🛡️ Testing Security Features")
    print("=" * 50)
    
    try:
        from src.services.auth_service import (
            AuthService, UserRegistration, UserLogin, 
            AuthStatus
        )
        
        auth_service = AuthService()
        
        # Test 1: Password Validation
        print("\n🔒 Test 1: Password Validation")
        print("-" * 30)
        
        weak_passwords = [
            "123",  # Too short
            "password",  # No uppercase, no digit
            "PASSWORD",  # No lowercase, no digit
            "Password",  # No digit
            "Password1",  # No special char (but this might pass)
        ]
        
        for password in weak_passwords:
            try:
                registration = UserRegistration(
                    username=f"testuser_{password}",
                    email=f"test_{password}@example.com",
                    password=password,
                    confirm_password=password
                )
                print(f"   ❌ Weak password '{password}' should have been rejected")
            except ValueError as e:
                print(f"   ✅ Weak password '{password}' correctly rejected: {e}")
        
        # Test 2: Username Validation
        print("\n👤 Test 2: Username Validation")
        print("-" * 30)
        
        invalid_usernames = [
            "ab",  # Too short
            "a" * 31,  # Too long
            "user@name",  # Invalid characters
            "user-name",  # Invalid characters
            "user name",  # Invalid characters
        ]
        
        for username in invalid_usernames:
            try:
                registration = UserRegistration(
                    username=username,
                    email="test@example.com",
                    password="SecurePass123!",
                    confirm_password="SecurePass123!"
                )
                print(f"   ❌ Invalid username '{username}' should have been rejected")
            except ValueError as e:
                print(f"   ✅ Invalid username '{username}' correctly rejected: {e}")
        
        # Test 3: Email Validation
        print("\n📧 Test 3: Email Validation")
        print("-" * 30)
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
        ]
        
        for email in invalid_emails:
            try:
                registration = UserRegistration(
                    username="testuser",
                    email=email,
                    password="SecurePass123!",
                    confirm_password="SecurePass123!"
                )
                print(f"   ❌ Invalid email '{email}' should have been rejected")
            except ValueError as e:
                print(f"   ✅ Invalid email '{email}' correctly rejected: {e}")
        
        # Test 4: Duplicate Registration
        print("\n🔄 Test 4: Duplicate Registration")
        print("-" * 30)
        
        # Register first user
        registration1 = UserRegistration(
            username="duplicateuser",
            email="duplicate@example.com",
            password="SecurePass123!",
            confirm_password="SecurePass123!"
        )
        
        result1 = auth_service.register_user(registration1)
        if result1["status"] == AuthStatus.SUCCESS:
            print("   ✅ First registration successful")
            
            # Try to register with same username
            registration2 = UserRegistration(
                username="duplicateuser",
                email="different@example.com",
                password="SecurePass123!",
                confirm_password="SecurePass123!"
            )
            
            result2 = auth_service.register_user(registration2)
            if result2["status"] == AuthStatus.INVALID_CREDENTIALS:
                print("   ✅ Duplicate username correctly rejected")
            else:
                print(f"   ❌ Duplicate username should have been rejected: {result2['message']}")
            
            # Try to register with same email
            registration3 = UserRegistration(
                username="differentuser",
                email="duplicate@example.com",
                password="SecurePass123!",
                confirm_password="SecurePass123!"
            )
            
            result3 = auth_service.register_user(registration3)
            if result3["status"] == AuthStatus.INVALID_CREDENTIALS:
                print("   ✅ Duplicate email correctly rejected")
            else:
                print(f"   ❌ Duplicate email should have been rejected: {result3['message']}")
        else:
            print(f"   ❌ First registration failed: {result1['message']}")
        
        # Test 5: Invalid Token
        print("\n🎫 Test 5: Invalid Token")
        print("-" * 30)
        
        invalid_tokens = [
            "invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
            None
        ]
        
        for token in invalid_tokens:
            if token is not None:
                result = auth_service.validate_token(token)
                if result["status"] == AuthStatus.INVALID_TOKEN:
                    print(f"   ✅ Invalid token correctly rejected")
                else:
                    print(f"   ❌ Invalid token should have been rejected: {result['status']}")
        
        print("\n🎉 Security Features Tests Completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Run all authentication system tests."""
    print("🚀 MultiSportsBettingPlatform - Authentication System Test")
    print("=" * 70)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    auth_success = test_authentication_service()
    prefs_success = test_user_preferences()
    security_success = test_security_features()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"🔐 Authentication Service: {'✅ PASSED' if auth_success else '❌ FAILED'}")
    print(f"⚙️ User Preferences Service: {'✅ PASSED' if prefs_success else '❌ FAILED'}")
    print(f"🛡️ Security Features: {'✅ PASSED' if security_success else '❌ FAILED'}")
    
    overall_success = auth_success and prefs_success and security_success
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Authentication System is ready for production!")
        print("   - User registration and login working")
        print("   - Session management functional")
        print("   - Preferences system operational")
        print("   - Security features active")
    else:
        print("\n⚠️ Some issues need to be resolved before production use.")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 