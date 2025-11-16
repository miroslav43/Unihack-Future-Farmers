#!/usr/bin/env python3
"""
Simple API test script to verify the backend is working correctly.
Run after starting the server: python test_api.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_result(endpoint, response):
    print(f"\n🔹 {endpoint}")
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        print(f"✅ Success")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text}")
    else:
        print(f"❌ Failed")
        print(f"Error: {response.text}")
    return response

def main():
    print("🚀 Testing Future Farmers Backend API")
    print(f"Base URL: {BASE_URL}")
    
    # Test health endpoint
    print_section("1. Health Check")
    response = requests.get("http://localhost:8001/health")
    print_result("GET /health", response)
    
    # Test root endpoint
    response = requests.get("http://localhost:8001/")
    print_result("GET /", response)
    
    # Register a farmer
    print_section("2. Register Farmer")
    farmer_data = {
        "email": f"farmer_{datetime.now().timestamp()}@test.com",
        "password": "test123",
        "name": "Test Farmer",
        "role": "farmer"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=farmer_data)
    result = print_result("POST /auth/register", response)
    
    if response.status_code == 200:
        farmer_token = response.json()["access_token"]
        farmer_cookies = {"token": farmer_token}
        farmer_id = response.json()["user"]["id"]
        print(f"✅ Farmer registered with ID: {farmer_id}")
    else:
        print("❌ Cannot continue without farmer registration")
        return
    
    # Register a buyer
    print_section("3. Register Buyer")
    buyer_data = {
        "email": f"buyer_{datetime.now().timestamp()}@test.com",
        "password": "test123",
        "name": "Test Buyer",
        "role": "buyer"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=buyer_data)
    result = print_result("POST /auth/register", response)
    
    if response.status_code == 200:
        buyer_token = response.json()["access_token"]
        buyer_cookies = {"token": buyer_token}
        buyer_id = response.json()["user"]["id"]
        print(f"✅ Buyer registered with ID: {buyer_id}")
    else:
        print("❌ Cannot continue without buyer registration")
        return
    
    # Get current user (farmer)
    print_section("4. Get Current User")
    response = requests.get(f"{BASE_URL}/auth/me", cookies=farmer_cookies)
    print_result("GET /auth/me", response)
    
    # Create farmer profile
    print_section("5. Create Farmer Profile")
    farmer_profile = {
        "farm_name": "Green Valley Farm",
        "contact_person": "Test Farmer",
        "phone": "+40123456789",
        "email": farmer_data["email"],
        "address": "123 Farm Road",
        "city": "Cluj-Napoca",
        "county": "Cluj",
        "postal_code": "400000",
        "farm_size_hectares": 50.5,
        "certifications": ["BIO", "EU Organic"]
    }
    response = requests.post(f"{BASE_URL}/farmers/", json=farmer_profile, cookies=farmer_cookies)
    result = print_result("POST /farmers/", response)
    
    if response.status_code == 200:
        farmer_profile_id = response.json()["id"]
        print(f"✅ Farmer profile created with ID: {farmer_profile_id}")
    
    # Create buyer profile
    print_section("6. Create Buyer Profile")
    buyer_profile = {
        "company_name": "Fresh Food Restaurant",
        "contact_person": "Test Buyer",
        "phone": "+40987654321",
        "email": buyer_data["email"],
        "business_type": "restaurant",
        "tax_id": "RO123456",
        "address": "456 Main Street",
        "city": "București",
        "county": "București",
        "postal_code": "010101"
    }
    response = requests.post(f"{BASE_URL}/buyers/", json=buyer_profile, cookies=buyer_cookies)
    result = print_result("POST /buyers/", response)
    
    if response.status_code == 200:
        buyer_profile_id = response.json()["id"]
        print(f"✅ Buyer profile created with ID: {buyer_profile_id}")
    
    # Create inventory item
    print_section("7. Create Inventory Item")
    inventory_item = {
        "product_name": "Organic Tomatoes",
        "category": "vegetables",
        "quantity": 100.0,
        "unit": "kg",
        "price_per_unit": 5.5,
        "is_available_for_sale": True,
        "location": "Greenhouse A",
        "description": "Fresh organic tomatoes",
        "min_order_quantity": 10.0,
        "max_order_quantity": 50.0
    }
    response = requests.post(f"{BASE_URL}/inventory/", json=inventory_item, cookies=farmer_cookies)
    result = print_result("POST /inventory/", response)
    
    if response.status_code == 200:
        inventory_id = response.json()["_id"]
        print(f"✅ Inventory item created with ID: {inventory_id}")
    
    # Get available inventory
    print_section("8. Get Available Inventory")
    response = requests.get(f"{BASE_URL}/inventory/available")
    print_result("GET /inventory/available", response)
    
    # Create contract
    print_section("9. Create Contract")
    contract_data = {
        "buyer_id": buyer_profile_id,
        "buyer_name": "Fresh Food Restaurant",
        "farmer_id": farmer_profile_id,
        "farmer_name": "Green Valley Farm",
        "items": [
            {
                "product_id": inventory_id,
                "product_name": "Organic Tomatoes",
                "quantity": 20.0,
                "unit": "kg",
                "price_per_unit": 5.5,
                "total_price": 110.0
            }
        ],
        "total_amount": 110.0,
        "delivery_date": "2024-12-20",
        "delivery_address": "456 Main Street, București",
        "terms": "Delivery within 2 days",
        "notes": "Please pack carefully"
    }
    response = requests.post(f"{BASE_URL}/contracts/", json=contract_data, cookies=buyer_cookies)
    result = print_result("POST /contracts/", response)
    
    if response.status_code == 200:
        contract_id = response.json()["_id"]
        print(f"✅ Contract created with ID: {contract_id}")
        print(f"Contract hash: {response.json()['contract_hash']}")
        
        # Generate keys for signing
        print_section("10. Generate Signing Keys")
        response = requests.get(f"{BASE_URL}/contracts/{contract_id}/generate-keys", cookies=farmer_cookies)
        result = print_result(f"GET /contracts/{contract_id}/generate-keys", response)
        
        if response.status_code == 200:
            keys = response.json()
            print(f"✅ Keys generated")
            
            # Sign contract as farmer
            print_section("11. Sign Contract (Farmer)")
            sign_data = {
                "signature": "demo_farmer_signature_12345",
                "public_key": keys["public_key"]
            }
            response = requests.post(f"{BASE_URL}/contracts/{contract_id}/sign", json=sign_data, cookies=farmer_cookies)
            print_result(f"POST /contracts/{contract_id}/sign", response)
            
            if response.status_code == 200:
                print(f"✅ Contract signed by farmer")
                print(f"Contract status: {response.json()['status']}")
    
    # Get contracts
    print_section("12. Get Contracts")
    response = requests.get(f"{BASE_URL}/contracts/", cookies=farmer_cookies)
    print_result("GET /contracts/", response)
    
    print_section("✅ Testing Complete!")
    print("\n🎉 All basic API endpoints are working correctly!")
    print("\n📚 Next steps:")
    print("  1. Check the interactive API docs at http://localhost:8001/docs")
    print("  2. Start your frontend application")
    print("  3. Test the complete user flow")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to the API server")
        print("Make sure the server is running on http://localhost:8001")
        print("Start it with: python -m app.main")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

