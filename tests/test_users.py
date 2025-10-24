import pytest
from httpx import AsyncClient

from features.common.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


class TestUserEndpoints:
    """Test suite for user endpoints."""

    @pytest.mark.asyncio
    async def test_create_user(self, client: AsyncClient):
        """Test POST /users/ - Create a new user."""
        user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "full_name": "Test User",
            "is_active": True,
        }

        response = await client.post("/users/", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] == user_data["is_active"]
        assert "id" in data
        assert isinstance(data["id"], int)

    @pytest.mark.asyncio
    async def test_create_user_conflict(self, client: AsyncClient):
        """Creating two users with the same username/email should fail."""
        user_data = {
            "username": "dupeuser",
            "email": "dupe@example.com",
            "full_name": "Dup E",
            "is_active": True,
        }

        first_response = await client.post("/users/", json=user_data)
        assert first_response.status_code == 201

        second_response = await client.post("/users/", json=user_data)
        assert second_response.status_code == 400
        assert second_response.json()["detail"] == "Username or email already exists"

    @pytest.mark.asyncio
    async def test_get_user(self, client: AsyncClient):
        """Test GET /users/{user_id} - Get a specific user."""
        # First create a user
        user_data = {
            "username": "getuser",
            "email": "getuser@example.com",
            "full_name": "Get User",
            "is_active": True,
        }
        create_response = await client.post("/users/", json=user_data)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Now get the user
        response = await client.get(f"/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] == user_data["is_active"]

    @pytest.mark.asyncio
    async def test_list_users(self, client: AsyncClient):
        """Test GET /users/ - List all users."""
        # Create multiple users
        users_data = [
            {
                "username": "listuser1",
                "email": "listuser1@example.com",
                "full_name": "List User 1",
                "is_active": True,
            },
            {
                "username": "listuser2",
                "email": "listuser2@example.com",
                "full_name": "List User 2",
                "is_active": False,
            },
        ]

        for user_data in users_data:
            await client.post("/users/", json=user_data)

        # Get all users
        response = await client.get("/users/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data["total"] >= 2  # At least the two we just created
        assert data["page"] == 1
        assert data["page_size"] == DEFAULT_PAGE_SIZE
        items = data["items"]
        assert isinstance(items, list)

        # Verify our users are in the list
        usernames = [user["username"] for user in items]
        assert "listuser1" in usernames
        assert "listuser2" in usernames

    @pytest.mark.asyncio
    async def test_list_users_filters_and_sorting(self, client: AsyncClient):
        """Filtering and sorting parameters should alter the response."""
        users_data = [
            {
                "username": "inactive-one",
                "email": "inactive1@example.com",
                "full_name": "Inactive One",
                "is_active": False,
            },
            {
                "username": "inactive-two",
                "email": "inactive2@example.com",
                "full_name": "Inactive Two",
                "is_active": False,
            },
            {
                "username": "active-three",
                "email": "active3@example.com",
                "full_name": "Active Three",
                "is_active": True,
            },
        ]

        for user_data in users_data:
            await client.post("/users/", json=user_data)

        response = await client.get(
            "/users/?is_active=false&username=inactive&sort_by=username&sort_order=desc"
        )

        assert response.status_code == 200
        data = response.json()
        usernames = [user["username"] for user in data["items"]]
        assert usernames == ["inactive-two", "inactive-one"]

        email_filter_response = await client.get("/users/?email=active3@example.com")

        assert email_filter_response.status_code == 200
        email_data = email_filter_response.json()
        assert email_data["total"] == 1
        assert email_data["items"][0]["username"] == "active-three"

    @pytest.mark.asyncio
    async def test_list_users_page_size_too_large(self, client: AsyncClient):
        """Requesting a page size above the maximum should fail validation."""
        response = await client.get(f"/users/?page_size={MAX_PAGE_SIZE + 1}")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_user(self, client: AsyncClient):
        """Test PATCH /users/{user_id} - Update a user."""
        # First create a user
        user_data = {
            "username": "updateuser",
            "email": "updateuser@example.com",
            "full_name": "Update User",
            "is_active": True,
        }
        create_response = await client.post("/users/", json=user_data)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Update the user
        update_data = {"full_name": "Updated Full Name", "is_active": False}
        response = await client.patch(f"/users/{user_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == user_data["username"]  # Unchanged
        assert data["email"] == user_data["email"]  # Unchanged
        assert data["full_name"] == update_data["full_name"]  # Updated
        assert data["is_active"] == update_data["is_active"]  # Updated

    @pytest.mark.asyncio
    async def test_delete_user(self, client: AsyncClient):
        """Test DELETE /users/{user_id} - Delete a user."""
        # First create a user
        user_data = {
            "username": "deleteuser",
            "email": "deleteuser@example.com",
            "full_name": "Delete User",
            "is_active": True,
        }
        create_response = await client.post("/users/", json=user_data)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Delete the user
        response = await client.delete(f"/users/{user_id}")

        assert response.status_code == 204
        assert response.content == b""  # No content in response

        # Verify the user is deleted by trying to get it
        get_response = await client.get(f"/users/{user_id}")
        assert get_response.status_code == 404  # Should not be found
