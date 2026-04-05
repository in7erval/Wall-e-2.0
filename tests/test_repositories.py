"""
Tests for UserRepository
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import UserRepository


@pytest.mark.asyncio
async def test_create_user(user_repository: UserRepository) -> None:
    """Test creating a new user"""
    user = await user_repository.create(
        user_id=123456,
        name="Test User",
        is_admin=False
    )

    assert user.id == 123456
    assert user.name == "Test User"
    assert user.is_admin is False


@pytest.mark.asyncio
async def test_get_user(user_repository: UserRepository) -> None:
    """Test getting a user by ID"""
    # Create user first
    await user_repository.create(
        user_id=789012,
        name="Get User",
        is_admin=False
    )

    # Get user
    user = await user_repository.get(789012)

    assert user is not None
    assert user.id == 789012
    assert user.name == "Get User"


@pytest.mark.asyncio
async def test_get_nonexistent_user(user_repository: UserRepository) -> None:
    """Test getting a nonexistent user"""
    user = await user_repository.get(999999)
    assert user is None


@pytest.mark.asyncio
async def test_update_admin(user_repository: UserRepository) -> None:
    """Test updating admin status"""
    # Create user
    await user_repository.create(
        user_id=345678,
        name="Admin User",
        is_admin=False
    )

    # Update admin status
    updated_user = await user_repository.update_admin(345678, is_admin=True)

    assert updated_user is not None
    assert updated_user.is_admin is True


@pytest.mark.asyncio
async def test_add_or_update_existing(user_repository: UserRepository) -> None:
    """Test add_or_update with existing user"""
    # Create user first
    await user_repository.create(
        user_id=567890,
        name="Original Name",
        is_admin=False
    )

    # Update existing
    user = await user_repository.add_or_update(
        user_id=567890,
        name="Updated Name",
        is_admin=True
    )

    assert user.name == "Updated Name"
    assert user.is_admin is True


@pytest.mark.asyncio
async def test_delete_user(user_repository: UserRepository) -> None:
    """Test deleting a user"""
    # Create user
    await user_repository.create(
        user_id=111222,
        name="Delete Me",
        is_admin=False
    )

    # Delete user
    result = await user_repository.delete(111222)
    assert result is True

    # Verify deletion
    user = await user_repository.get(111222)
    assert user is None


@pytest.mark.asyncio
async def test_get_all_admins(user_repository: UserRepository) -> None:
    """Test getting all admins"""
    # Create users
    await user_repository.create(user_id=1, name="Admin 1", is_admin=True)
    await user_repository.create(user_id=2, name="User 1", is_admin=False)
    await user_repository.create(user_id=3, name="Admin 2", is_admin=True)

    # Get admins
    admins = await user_repository.get_all_admins()

    assert len(admins) == 2
    assert all(user.is_admin for user in admins)
