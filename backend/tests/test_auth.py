"""
文件路径: /backend/tests/test_auth.py
功能描述: 认证模块测试用例
主要功能:
    - 测试登录功能
    - 测试 token 刷新
    - 测试权限验证
"""
import pytest

from core.jwt import decode_token


@pytest.mark.asyncio
async def test_login_success(test_client):
    """测试登录成功"""
    response = await test_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "accessToken" in data["data"]
    assert "refreshToken" in data["data"]

    access_payload = decode_token(data["data"]["accessToken"])
    refresh_payload = decode_token(data["data"]["refreshToken"])
    assert access_payload is not None
    assert refresh_payload is not None
    assert access_payload["type"] == "access"
    assert refresh_payload["type"] == "refresh"
    assert access_payload["jti"]
    assert refresh_payload["jti"]


@pytest.mark.asyncio
async def test_login_wrong_password(test_client):
    """测试密码错误"""
    response = await test_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "wrongpassword"
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_user_not_found(test_client):
    """测试用户不存在"""
    response = await test_client.post("/api/v1/auth/login", json={
        "username": "nonexistent",
        "password": "password123"
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(test_client):
    """测试无 token 访问受保护端点"""
    response = await test_client.get("/api/v1/users")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_token(test_client):
    """测试带 token 访问受保护端点"""
    login_response = await test_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })

    token = login_response.json()["data"]["accessToken"]

    response = await test_client.get("/api/v1/users", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_refresh_with_refresh_token_success(test_client):
    """测试 refresh token 可以刷新访问令牌"""
    login_response = await test_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    refresh_token = login_response.json()["data"]["refreshToken"]

    response = await test_client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })

    assert response.status_code == 200
    data = response.json()["data"]
    assert decode_token(data["accessToken"])["type"] == "access"
    assert decode_token(data["refreshToken"])["type"] == "refresh"


@pytest.mark.asyncio
async def test_refresh_with_access_token_rejected(test_client):
    """测试 access token 不能用于刷新"""
    login_response = await test_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    access_token = login_response.json()["data"]["accessToken"]

    response = await test_client.post("/api/v1/auth/refresh", json={
        "refresh_token": access_token
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_refresh_token_rejected(test_client):
    """测试 refresh token 不能访问普通业务接口"""
    login_response = await test_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    refresh_token = login_response.json()["data"]["refreshToken"]

    response = await test_client.get("/api/v1/plans", headers={
        "Authorization": f"Bearer {refresh_token}"
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_blacklists_access_token(test_client):
    """测试登出后原 access token 失效"""
    login_response = await test_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    access_token = login_response.json()["data"]["accessToken"]
    headers = {"Authorization": f"Bearer {access_token}"}

    logout_response = await test_client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 200

    response = await test_client.get("/api/v1/plans", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout_blacklists_refresh_token_when_provided(test_client):
    """测试登出时携带 refresh token 会同步撤销刷新能力"""
    login_response = await test_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    login_data = login_response.json()["data"]
    access_token = login_data["accessToken"]
    refresh_token = login_data["refreshToken"]

    logout_response = await test_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"refresh_token": refresh_token},
    )
    assert logout_response.status_code == 200

    response = await test_client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_user_duplicate_username_returns_business_error(test_client, auth_headers):
    """测试重复用户名返回稳定业务错误码"""
    response = await test_client.post("/api/v1/users", headers=auth_headers, json={
        "username": "admin",
        "password": "admin123",
        "name": "Duplicate Admin",
        "role": "operator",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 400
    assert data["errorCode"] == "username_already_exists"


@pytest.mark.asyncio
async def test_create_admin_user_returns_business_error(test_client, auth_headers):
    """测试禁止通过用户管理接口创建管理员"""
    response = await test_client.post("/api/v1/users", headers=auth_headers, json={
        "username": "new_admin",
        "password": "admin123",
        "name": "New Admin",
        "role": "admin",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 403
    assert data["errorCode"] == "cannot_create_admin"


@pytest.mark.asyncio
async def test_delete_self_returns_business_error(test_client, auth_headers):
    """测试禁止删除当前登录用户"""
    me_response = await test_client.get("/api/v1/auth/me", headers=auth_headers)
    user_id = me_response.json()["data"]["id"]

    response = await test_client.delete(f"/api/v1/users/{user_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 403
    assert data["errorCode"] == "cannot_delete_self"


@pytest.mark.asyncio
async def test_update_current_user_profile_only_changes_safe_fields(test_client, auth_headers):
    """测试当前用户只能通过自助接口修改基础资料"""
    response = await test_client.patch(
        "/api/v1/auth/me",
        headers=auth_headers,
        json={
            "username": "renamed-admin",
            "name": "Admin Profile",
            "phone": "13800000000",
            "email": "admin@example.com",
            "role": "operator",
            "status": "inactive",
            "isActive": False,
            "password": "Leaked123",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["username"] == "admin"
    assert data["name"] == "Admin Profile"
    assert data["phone"] == "13800000000"
    assert data["email"] == "admin@example.com"
    assert data["role"] == "admin"
    assert data["isActive"] is True
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_change_current_user_password_requires_old_password_and_updates_login(test_client, auth_headers):
    """测试当前用户改密必须校验旧密码并更新登录密码"""
    missing_old_password = await test_client.patch(
        "/api/v1/auth/me/password",
        headers=auth_headers,
        json={"newPassword": "Admin4567"},
    )
    wrong_old_password = await test_client.patch(
        "/api/v1/auth/me/password",
        headers=auth_headers,
        json={"oldPassword": "wrong-password", "newPassword": "Admin4567"},
    )
    invalid_password = await test_client.patch(
        "/api/v1/auth/me/password",
        headers=auth_headers,
        json={"oldPassword": "admin123", "newPassword": "short"},
    )
    success = await test_client.patch(
        "/api/v1/auth/me/password",
        headers=auth_headers,
        json={"oldPassword": "admin123", "newPassword": "Admin4567"},
    )

    assert missing_old_password.status_code == 200
    assert missing_old_password.json()["errorCode"] == "old_password_required"
    assert wrong_old_password.status_code == 200
    assert wrong_old_password.json()["errorCode"] == "old_password_incorrect"
    assert invalid_password.status_code == 200
    assert invalid_password.json()["errorCode"] == "invalid_password_policy"
    assert success.status_code == 200
    assert success.json()["data"]["requiresRelogin"] is True

    old_login = await test_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    new_login = await test_client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin4567",
    })

    assert old_login.status_code == 401
    assert new_login.status_code == 200
