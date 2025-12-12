import requests

def get_user(user_service_url, clerk_jwt):
    r = requests.get(
        f"{user_service_url}/api/users/me/",  # or user_id
        headers={"Authorization": f"Bearer {clerk_jwt}"},
        timeout=5,
    )
    r.raise_for_status()
    return r.json()
