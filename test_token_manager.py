#!/usr/bin/env python3
"""
Test script for the refactored token manager functionality.
This script tests the token manager independently and then tests the integration with main.py.
"""

import os
from dotenv import load_dotenv
from token_manager import get_token_manager, TokenManager


def test_token_manager_standalone():
    """Test the token manager as a standalone component."""
    print("=" * 60)
    print("TESTING TOKEN MANAGER STANDALONE")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    client_id = os.getenv('AIRBYTE_CLIENT_ID')
    client_secret = os.getenv('AIRBYTE_CLIENT_SECRET')
    workspace_id = os.getenv('AIRBYTE_WORKSPACE_ID')
    
    if not all([client_id, client_secret, workspace_id]):
        print("❌ Missing required environment variables")
        return False
    
    try:
        # Test singleton behavior
        print("1. Testing singleton behavior...")
        manager1 = get_token_manager()
        manager2 = get_token_manager()
        manager3 = TokenManager()
        
        if manager1 is manager2 is manager3:
            print("✅ Singleton pattern working correctly")
        else:
            print("❌ Singleton pattern failed")
            return False
        
        # Test configuration
        print("2. Testing configuration...")
        manager1.configure(client_id, client_secret, workspace_id)
        
        if manager1.is_configured():
            print("✅ Token manager configured successfully")
        else:
            print("❌ Token manager configuration failed")
            return False
        
        # Test token info before getting token
        print("3. Testing token info (before token creation)...")
        info = manager1.get_token_info()
        print(f"   Has token: {info['has_token']}")
        print(f"   Is configured: {info['is_configured']}")
        print(f"   Is valid: {info['is_valid']}")
        
        # Test token creation
        print("4. Testing token creation...")
        token = manager1.get_token()
        
        if token:
            print(f"✅ Token created successfully: {token[:20]}...")
        else:
            print("❌ Token creation failed")
            return False
        
        # Test auth header
        print("5. Testing auth header...")
        auth_header = manager1.get_auth_header()
        
        if 'Authorization' in auth_header and auth_header['Authorization'].startswith('Bearer '):
            print("✅ Auth header created successfully")
        else:
            print("❌ Auth header creation failed")
            return False
        
        # Test token info after getting token
        print("6. Testing token info (after token creation)...")
        info = manager1.get_token_info()
        print(f"   Has token: {info['has_token']}")
        print(f"   Token type: {info['token_type']}")
        print(f"   Expires at: {info['expires_at']}")
        print(f"   Is valid: {info['is_valid']}")
        
        # Test token reuse (should not create new token)
        print("7. Testing token reuse...")
        token2 = manager1.get_token()
        
        if token == token2:
            print("✅ Token reuse working correctly")
        else:
            print("❌ Token reuse failed - new token created unnecessarily")
            return False
        
        # Test token invalidation
        print("8. Testing token invalidation...")
        manager1.invalidate_token()
        info = manager1.get_token_info()
        
        if not info['has_token']:
            print("✅ Token invalidation working correctly")
        else:
            print("❌ Token invalidation failed")
            return False
        
        print("✅ All token manager tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Token manager test failed with error: {e}")
        return False


def test_main_integration():
    """Test the integration with main.py."""
    print("\n" + "=" * 60)
    print("TESTING MAIN.PY INTEGRATION")
    print("=" * 60)
    
    try:
        # Import and test the StripeAnalyzer initialization
        from main import StripeAnalyzer
        
        print("1. Testing StripeAnalyzer initialization...")
        analyzer = StripeAnalyzer()
        
        if hasattr(analyzer, 'token_manager') and analyzer.token_manager.is_configured():
            print("✅ StripeAnalyzer initialized with configured token manager")
        else:
            print("❌ StripeAnalyzer initialization failed")
            return False
        
        print("2. Testing token manager access from analyzer...")
        token_info = analyzer.token_manager.get_token_info()
        
        if token_info['is_configured']:
            print("✅ Token manager accessible from StripeAnalyzer")
        else:
            print("❌ Token manager not properly accessible")
            return False
        
        print("3. Testing auth header generation...")
        auth_header = analyzer.token_manager.get_auth_header()
        
        if 'Authorization' in auth_header:
            print("✅ Auth header generation working from StripeAnalyzer")
        else:
            print("❌ Auth header generation failed")
            return False
        
        print("✅ All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        return False


def main():
    """Run all tests."""
    print("TESTING REFACTORED TOKEN MANAGEMENT")
    print("=" * 60)
    
    # Test standalone functionality
    standalone_success = test_token_manager_standalone()
    
    # Test integration
    integration_success = test_main_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if standalone_success and integration_success:
        print("🎉 ALL TESTS PASSED! Refactoring successful.")
        print("\nThe token management has been successfully extracted from main.py")
        print("into a standalone, reusable token_manager.py module.")
        return 0
    else:
        print("❌ SOME TESTS FAILED! Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit(main())
