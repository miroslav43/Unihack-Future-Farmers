#!/usr/bin/env python3
"""
Simple test script to verify the backend setup
Run this after installing dependencies to ensure everything works
"""

import sys
import importlib

def test_imports():
    """Test if all required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'motor',
        'pymongo',
        'jose',
        'passlib',
        'pydantic',
        'pydantic_settings'
    ]
    
    print("🔍 Testing package imports...")
    all_good = True
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package} - NOT FOUND")
            all_good = False
    
    return all_good


def test_app_imports():
    """Test if app modules can be imported"""
    print("\n🔍 Testing app module imports...")
    
    try:
        from app.config import settings
        print(f"  ✅ Config loaded - Port: {settings.port}")
        
        from app.database import get_database
        print("  ✅ Database module imported")
        
        from app.services.auth_service import hash_password
        print("  ✅ Auth service imported")
        
        from app.services.contract_service import generate_contract_hash
        print("  ✅ Contract service imported")
        
        from app.dependencies import get_current_user
        print("  ✅ Dependencies imported")
        
        from app.routers import auth, farmers, buyers, inventory, contracts
        print("  ✅ All routers imported")
        
        return True
    except Exception as e:
        print(f"  ❌ Error importing app modules: {e}")
        return False


def test_password_hashing():
    """Test password hashing"""
    print("\n🔍 Testing password hashing...")
    
    try:
        from app.services.auth_service import hash_password, verify_password
        
        password = "test123"
        hashed = hash_password(password)
        
        if verify_password(password, hashed):
            print("  ✅ Password hashing works correctly")
            return True
        else:
            print("  ❌ Password verification failed")
            return False
    except Exception as e:
        print(f"  ❌ Error testing password hashing: {e}")
        return False


def test_jwt():
    """Test JWT token generation"""
    print("\n🔍 Testing JWT token generation...")
    
    try:
        from app.services.auth_service import create_access_token, verify_token
        
        data = {"user_id": "123", "email": "test@test.com", "role": "farmer"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        if payload and payload.get("user_id") == "123":
            print("  ✅ JWT token generation works correctly")
            return True
        else:
            print("  ❌ JWT token verification failed")
            return False
    except Exception as e:
        print(f"  ❌ Error testing JWT: {e}")
        return False


def test_contract_hash():
    """Test contract hash generation"""
    print("\n🔍 Testing contract hash generation...")
    
    try:
        from app.services.contract_service import generate_contract_hash
        
        data = {"buyer_id": "123", "farmer_id": "456", "total_amount": 1000}
        hash1 = generate_contract_hash(data)
        hash2 = generate_contract_hash(data)
        
        if hash1 == hash2 and len(hash1) == 64:  # SHA-256 produces 64 char hex
            print(f"  ✅ Contract hashing works (hash: {hash1[:16]}...)")
            return True
        else:
            print("  ❌ Contract hash generation inconsistent")
            return False
    except Exception as e:
        print(f"  ❌ Error testing contract hash: {e}")
        return False


def test_rsa_keys():
    """Test RSA key generation"""
    print("\n🔍 Testing RSA key generation...")
    
    try:
        from app.services.contract_service import generate_keys
        
        keys = generate_keys()
        
        if "private_key" in keys and "public_key" in keys:
            print("  ✅ RSA key generation works")
            return True
        else:
            print("  ❌ RSA key generation failed")
            return False
    except Exception as e:
        print(f"  ❌ Error testing RSA keys: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Future Farmers Backend - Setup Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("App Imports", test_app_imports),
        ("Password Hashing", test_password_hashing),
        ("JWT Tokens", test_jwt),
        ("Contract Hashing", test_contract_hash),
        ("RSA Key Generation", test_rsa_keys),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} - FAILED with exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\n🎯 {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Your backend is ready to run.")
        print("\n🚀 Start the server with:")
        print("   ./run.sh  (Unix/Mac)")
        print("   run.bat   (Windows)")
        print("   or: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("   Make sure you've installed all dependencies:")
        print("   pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())

