import os
import requests
from dotenv import load_dotenv


from requests.exceptions import RequestException

load_dotenv()


USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
CONTENT_SERVICE_URL = os.getenv("CONTENT_SERVICE_URL")
JWT_KEY = os.getenv("JWT_KEY")

print(f"Using User Service URL: {USER_SERVICE_URL}")
print(f"Using Content Service URL: {CONTENT_SERVICE_URL}")
print("-" * 50)


def test_user_authentication():
    print("Testing user authentication...")

    login_data = {
        "email": "tsavsamuel@gmail.com",
        "password": "world2025",
    }

    try:
        response = requests.post(
            f"{USER_SERVICE_URL}/auth/jwt/create/", json=login_data, timeout=20
        )

        if response.status_code == 200:
            tokens = response.json()
            print("✅ Authentication successful")
            return tokens["access"]
        else:
            print(f"❌ Authentication failed: {response.text}")
            return None
    except RequestException as e:
        print(f"❌ Authentication request failed: {e}")
        return None


def test_user_token_validation(token):
    print("Testing user JWT validation...")

    try:
        response = requests.post(
            f"{USER_SERVICE_URL}/auth/jwt/verify/", json={"token": token}, timeout=20
        )

        if response.status_code == 200:
            print("✅ JWT token is valid")
            # Get user info
            headers = {"Authorization": f"Bearer {token}"}
            user_resp = requests.get(
                f"{USER_SERVICE_URL}/auth/users/me/", headers=headers, timeout=20
            )
            if user_resp.status_code == 200:
                user_data = user_resp.json()
                print(
                    f"User: {user_data.get('username', 'N/A')}, {user_data.get('email', 'N/A')}, {user_data.get('uid', 'N/A')}"
                )
                return user_data
            else:
                print(f"❌ Failed to get user info: {user_resp.text}")
                return None
        else:
            print(f"❌ JWT token is invalid: {response.text}")
            return None
    except RequestException as e:
        print(f"❌ Token validation request failed: {e}")
        return None


def test_service_to_service_auth():
    print("Testing service-to-service authentication...")

    try:
        response = requests.post(
            f"{USER_SERVICE_URL}/auth/service/validate-token/",
            json={"token": JWT_KEY},
            timeout=20,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                print("✅ Service-to-service authentication successful")
                return True
            else:
                print("❌ Service-to-service authentication failed")
                return False
        else:
            print(f"❌ Service-to-service request failed: {response.text}")
            return False
    except RequestException as e:
        print(f"❌ Service-to-service request failed: {e}")
        return False


def test_content_service_access(token=None):
    print("Testing content service access...")

    # Use JWT key if no token is provided
    auth_token = token or JWT_KEY
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    }

    url = f"{CONTENT_SERVICE_URL}/api/languages/"
    print(f"Using URL: {url}")
    print(f"Token preview: {auth_token[:20]}...")

    try:
        response = requests.get(url, headers=headers, timeout=10)

        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")

        if response.status_code == 200:
            print("✅ Content service access successful")
            languages = response.json()
            print(f"Found {len(languages.get('results', []))} languages")
            return True
        else:
            print("❌ Content service access failed")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except RequestException as e:
        print(f"❌ Content service request failed: {e}")
        return False


def test_admin_permissions(token):
    print("Testing admin permissions...")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    language_data = {
        "name": "test_language",
        "display_name": "Test Language",
        "description": "A test language for verification",
    }

    try:
        response = requests.post(
            f"{CONTENT_SERVICE_URL}/api/languages/",
            json=language_data,
            headers=headers,
            timeout=20,
        )

        if response.status_code == 201:
            print("✅ Admin permissions working - language created")
            language_id = response.json()["id"]
            delete_response = requests.delete(
                f"{CONTENT_SERVICE_URL}/api/languages/{language_id}/",
                headers=headers,
                timeout=10,
            )
            if delete_response.status_code == 204:
                print("✅ Test language cleaned up")
            return True
        elif response.status_code == 403:
            print("❌ Admin permissions not working - access denied")
            return False
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
    except RequestException as e:
        print(f"❌ Admin permissions request failed: {e}")
        return False


def main():
    print("🚀 Starting service communication tests...")
    print("-" * 50)

    # Step 1: User authentication
    token = test_user_authentication()
    if not token:
        print("❌ Cannot proceed without valid token")
        return 1

    print("-" * 50)

    # Step 2: User token validation + get user info
    user_data = test_user_token_validation(token)
    if not user_data:
        print("❌ Cannot proceed without valid user data")
        return 1

    print("-" * 50)

    # Step 3: Service-to-service authentication
    if not test_service_to_service_auth():
        print("❌ Service-to-service authentication failed")
        return 1

    print("-" * 50)

    # Step 4: Content service access
    if not test_content_service_access(token):
        print("❌ Content service access failed")
        return 1

    print("-" * 50)

    # Step 5: Admin permissions
    if user_data.get("is_staff") or user_data.get("is_superuser"):
        test_admin_permissions(token)
    else:
        print("ℹ️ User is not admin, skipping admin permission tests")

    print("-" * 50)
    print("🎉 All tests completed successfully!")
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
