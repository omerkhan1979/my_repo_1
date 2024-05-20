from dataclasses import dataclass
from datetime import datetime

from src.config.constants import DEFAULT_USER_PASSWORD
from src.api.takeoff.auth_service import AuthService
from src.config.config import get_user_token, delete_user, get_firebase_key


@dataclass
class AuthServiceUser:
    email: str
    password: str
    id: str


def delete_test_user(retailer, env, email_id, password) -> None:
    firebase_key = get_firebase_key(retailer, env)
    delete_user(get_user_token(firebase_key, email_id, password), firebase_key)
    print(f"\nDeleted user: {email_id}")


def create_test_user(
    auth_service: AuthService, password: str = DEFAULT_USER_PASSWORD
) -> AuthServiceUser:
    user_identification = datetime.now().strftime("%Y%m%d%H%M%S")
    email = f"test_user+{user_identification}@takeoff.com"
    display_name = f"Test User RQT-{user_identification}"
    user = auth_service.create_user(email, password, display_name)
    print(f"\nCreated user: {email} ({user['user-id']})")
    return AuthServiceUser(
        email=user["user-email"], password=password, id=user["user-id"]
    )


def enable_test_user(
    auth_service: AuthService,
    user_email: str,
) -> None:
    # if we don't have a user, that's ok, it'll be made later
    try:
        user_id = auth_service.get_user_id(user_email)
    except Exception:
        return
    user_disabled = auth_service.get_user(user_id).get("is-disabled")
    if user_disabled:
        auth_service.update_user(user_id, {"is-disabled": False})
        print(f"\nEnabled user: {user_email} ({user_id})")


def get_or_create_user_token(
    auth_service: AuthService,
    retailer: str,
    env: str,
    location_id: str,
    user_email: str,
    role: str = "mfc-manager",
    delete_existing: bool = False,
) -> str:
    if delete_existing:
        delete_test_user(retailer, env, user_email, DEFAULT_USER_PASSWORD)
    firebase_key = get_firebase_key(retailer, env)
    enable_test_user(auth_service, user_email)
    try:
        return get_user_token(firebase_key, user_email, DEFAULT_USER_PASSWORD)
    except Exception as err:
        print(f"User {user_email} not found, will try to create. (error was {err})")
        # try to create
        try:
            auth_service.create_user(
                user_email, DEFAULT_USER_PASSWORD, f"Test User: {user_email}"
            )
            auth_service.set_user_role(
                auth_service.get_user_id(user_email), role, location_id
            )
            print(f"\nCreated user {user_email} and set role to {role}")
        except Exception as err:
            print(f"\nWas going to try to create but encountered: {err}")
    return get_user_token(firebase_key, user_email, DEFAULT_USER_PASSWORD)
