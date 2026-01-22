"""
Pytest configuration and fixtures for AudiFriends tests.
"""
import os
import pytest
from pathlib import Path
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from PIL import Image

from blog.models import Post


@pytest.fixture(scope='session', autouse=True)
def create_default_image():
    """Create a default profile image for tests."""
    media_root = Path(settings.MEDIA_ROOT)
    media_root.mkdir(parents=True, exist_ok=True)

    default_image_path = media_root / 'default.jpg'
    if not default_image_path.exists():
        # Create a simple 100x100 placeholder image
        img = Image.new('RGB', (100, 100), color='gray')
        img.save(default_image_path)

    yield

    # Cleanup after tests (optional)
    # if default_image_path.exists():
    #     default_image_path.unlink()


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
