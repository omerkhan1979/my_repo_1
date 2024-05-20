from pytest import mark
from src.api.takeoff.auth_service import AuthService


@mark.rq
@mark.smoke
@mark.users
@mark.parametrize("change_role", ["mfc-manager"])
@mark.testrail("123600")
# user_role goes as a parameter to user_with_particular_role fixture
# the coverage may be extended further with other user roles
def test_create_user_with_particular_role(
    auth_service: AuthService, user_with_particular_role, change_role
):
    user = auth_service.get_user(user_with_particular_role.id)
    assert user["user-email"] == user_with_particular_role.email
    assert user["roles"][0]["role"] == change_role
