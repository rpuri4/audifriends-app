"""
Pytest configuration and fixtures for AudiFriends tests.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from blog.models import Post
from users.models import Profile


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create and return a test user."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    return user


@pytest.fixture
def another_user(db):
    """Create and return another test user."""
    user = User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpass123'
    )
    return user


@pytest.fixture
def authenticated_client(api_client, user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def post(db, user):
    """Create and return a test post."""
    return Post.objects.create(
        title='Test Post',
        content='This is test content for the post.',
        author=user
    )


@pytest.fixture
def multiple_posts(db, user):
    """Create multiple test posts."""
    posts = []
    for i in range(15):
        posts.append(Post.objects.create(
            title=f'Test Post {i}',
            content=f'Content for post {i}',
            author=user
        ))
    return posts
