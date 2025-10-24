import pytest
from httpx import AsyncClient

from features.common.pagination import DEFAULT_PAGE_SIZE


class TestTodoEndpoints:
    """Test suite for todo endpoints."""

    @pytest.mark.asyncio
    async def test_create_todo(self, client: AsyncClient):
        """Test POST /todos/ - Create a new todo."""
        todo_data = {
            "title": "Test Todo",
            "description": "This is a test todo",
            "completed": False,
            "user_id": None,
        }

        response = await client.post("/todos/", json=todo_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == todo_data["title"]
        assert data["description"] == todo_data["description"]
        assert data["completed"] == todo_data["completed"]
        assert data["user_id"] == todo_data["user_id"]
        assert "id" in data
        assert isinstance(data["id"], int)

    @pytest.mark.asyncio
    async def test_create_todo_with_missing_user(self, client: AsyncClient):
        """Creating a todo with a nonexistent user should surface 404."""
        todo_data = {
            "title": "Invalid User Todo",
            "description": "This should fail",
            "completed": False,
            "user_id": 9999,
        }

        response = await client.post("/todos/", json=todo_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    @pytest.mark.asyncio
    async def test_get_todo(self, client: AsyncClient):
        """Test GET /todos/{todo_id} - Get a specific todo."""
        # First create a todo
        todo_data = {
            "title": "Get Todo Test",
            "description": "Todo to be retrieved",
            "completed": False,
            "user_id": None,
        }
        create_response = await client.post("/todos/", json=todo_data)
        created_todo = create_response.json()
        todo_id = created_todo["id"]

        # Now get the todo
        response = await client.get(f"/todos/{todo_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == todo_data["title"]
        assert data["description"] == todo_data["description"]
        assert data["completed"] == todo_data["completed"]
        assert data["user_id"] == todo_data["user_id"]

    @pytest.mark.asyncio
    async def test_list_todos(self, client: AsyncClient):
        """Test GET /todos/ - List all todos."""
        # Create multiple todos
        todos_data = [
            {
                "title": "First Todo",
                "description": "First test todo",
                "completed": False,
                "user_id": None,
            },
            {
                "title": "Second Todo",
                "description": "Second test todo",
                "completed": True,
                "user_id": None,
            },
        ]

        for todo_data in todos_data:
            await client.post("/todos/", json=todo_data)

        # Get all todos
        response = await client.get("/todos/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data["total"] >= 2  # At least the two we just created
        assert data["page"] == 1
        assert data["page_size"] == DEFAULT_PAGE_SIZE
        items = data["items"]
        assert isinstance(items, list)

        # Verify our todos are in the list
        titles = [todo["title"] for todo in items]
        assert "First Todo" in titles
        assert "Second Todo" in titles

    @pytest.mark.asyncio
    async def test_list_todos_with_users(self, client: AsyncClient):
        """Test GET /todos/with-users - List all todos with user information."""
        # First create a user
        user_data = {
            "username": "todouser",
            "email": "todouser@example.com",
            "full_name": "Todo User",
            "is_active": True,
        }
        user_response = await client.post("/users/", json=user_data)
        created_user = user_response.json()
        user_id = created_user["id"]

        # Create todos with and without user_id
        todo_with_user = {
            "title": "User's Todo",
            "description": "Todo with user",
            "completed": False,
            "user_id": user_id,
        }
        todo_without_user = {
            "title": "Unassigned Todo",
            "description": "Todo without user",
            "completed": False,
            "user_id": None,
        }

        await client.post("/todos/", json=todo_with_user)
        await client.post("/todos/", json=todo_without_user)

        # Get all todos with users
        response = await client.get("/todos/with-users")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data["total"] >= 2
        assert data["page"] == 1
        assert data["page_size"] == DEFAULT_PAGE_SIZE
        items = data["items"]
        assert isinstance(items, list)

        # Find the todo with user and verify user data is included
        user_todo = next(
            (todo for todo in items if todo["title"] == "User's Todo"), None
        )
        assert user_todo is not None
        assert user_todo["user"] is not None
        assert user_todo["user"]["id"] == user_id
        assert user_todo["user"]["username"] == user_data["username"]

        # Find the todo without user
        unassigned_todo = next(
            (todo for todo in items if todo["title"] == "Unassigned Todo"), None
        )
        assert unassigned_todo is not None
        assert unassigned_todo["user"] is None

    @pytest.mark.asyncio
    async def test_update_todo(self, client: AsyncClient):
        """Test PATCH /todos/{todo_id} - Update a todo."""
        # First create a todo
        todo_data = {
            "title": "Original Title",
            "description": "Original description",
            "completed": False,
            "user_id": None,
        }
        create_response = await client.post("/todos/", json=todo_data)
        created_todo = create_response.json()
        todo_id = created_todo["id"]

        # Update the todo
        update_data = {
            "title": "Updated Title",
            "completed": True,
        }
        response = await client.patch(f"/todos/{todo_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == update_data["title"]  # Updated
        assert data["description"] == todo_data["description"]  # Unchanged
        assert data["completed"] == update_data["completed"]  # Updated
        assert data["user_id"] == todo_data["user_id"]  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_todo(self, client: AsyncClient):
        """Test DELETE /todos/{todo_id} - Delete a todo."""
        # First create a todo
        todo_data = {
            "title": "Todo to Delete",
            "description": "This todo will be deleted",
            "completed": False,
            "user_id": None,
        }
        create_response = await client.post("/todos/", json=todo_data)
        created_todo = create_response.json()
        todo_id = created_todo["id"]

        # Delete the todo
        response = await client.delete(f"/todos/{todo_id}")

        assert response.status_code == 204
        assert response.content == b""  # No content in response

        # Verify the todo is deleted by trying to get it
        get_response = await client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 404  # Should not be found
