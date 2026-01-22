"""
Tests for Django views.
"""
import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestBlogViews:
    """Tests for blog views."""

    def test_home_page_loads(self, client):
        """Home page should load successfully."""
        response = client.get(reverse('blog-home'))
        assert response.status_code == 200

    def test_home_page_shows_posts(self, client, multiple_posts):
        """Home page should display posts."""
        response = client.get(reverse('blog-home'))
        assert response.status_code == 200
        assert 'posts' in response.context
        # Pagination should limit to 5 posts per page
        assert len(response.context['posts']) == 5

    def test_post_detail_view(self, client, post):
        """Post detail view should show the post."""
        response = client.get(reverse('post-detail', kwargs={'pk': post.pk}))
        assert response.status_code == 200
        assert post.title in response.content.decode()

    def test_post_create_requires_login(self, client):
        """Creating a post should require login."""
        response = client.get(reverse('post-create'))
        assert response.status_code == 302  # Redirect to login

    def test_post_create_authenticated(self, client, user):
        """Authenticated users can create posts."""
        client.force_login(user)
        response = client.get(reverse('post-create'))
        assert response.status_code == 200

    def test_post_create_submission(self, client, user):
        """Authenticated users can submit new posts."""
        client.force_login(user)
        response = client.post(reverse('post-create'), {
            'title': 'New Post',
            'content': 'New content'
        })
        assert response.status_code == 302  # Redirect after creation
        assert user.post_set.filter(title='New Post').exists()

    def test_post_update_only_by_author(self, client, user, another_user, post):
        """Only the author can update their post."""
        client.force_login(another_user)
        response = client.get(reverse('post-update', kwargs={'pk': post.pk}))
        assert response.status_code == 403  # Forbidden

    def test_post_delete_only_by_author(self, client, user, another_user, post):
        """Only the author can delete their post."""
        client.force_login(another_user)
        response = client.post(reverse('post-delete', kwargs={'pk': post.pk}))
        assert response.status_code == 403  # Forbidden

    def test_about_page(self, client):
        """About page should load."""
        response = client.get(reverse('blog-about'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestUserViews:
    """Tests for user-related views."""

    def test_register_page_loads(self, client):
        """Registration page should load."""
        response = client.get(reverse('register'))
        assert response.status_code == 200

    def test_user_registration(self, client):
        """Users should be able to register."""
        response = client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!'
        })
        assert response.status_code == 302  # Redirect to login
        assert User.objects.filter(username='newuser').exists()

    def test_login_page_loads(self, client):
        """Login page should load."""
        response = client.get(reverse('login'))
        assert response.status_code == 200

    def test_user_login(self, client, user):
        """Users should be able to log in."""
        response = client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == 302  # Redirect after login

    def test_profile_requires_login(self, client):
        """Profile page should require login."""
        response = client.get(reverse('profile'))
        assert response.status_code == 302  # Redirect to login

    def test_profile_authenticated(self, client, user):
        """Authenticated users can view their profile."""
        client.force_login(user)
        response = client.get(reverse('profile'))
        assert response.status_code == 200

    def test_audiobook_search_requires_login(self, client):
        """Audiobook search should require login."""
        response = client.get(reverse('FindAudioBooks'))
        assert response.status_code == 302  # Redirect to login
