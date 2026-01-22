"""
Tests for REST API endpoints.
"""
import pytest
from rest_framework import status

from blog.models import Post


@pytest.mark.django_db
class TestPostAPI:
    """Tests for Post API endpoints."""

    def test_list_posts(self, api_client, multiple_posts):
        """GET /api/v1/posts/ should list posts."""
        response = api_client.get('/api/v1/posts/')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 10  # Default pagination

    def test_list_posts_pagination(self, api_client, multiple_posts):
        """Posts API should be paginated."""
        response = api_client.get('/api/v1/posts/')
        assert 'count' in response.data
        assert 'next' in response.data
        assert response.data['count'] == 15

    def test_retrieve_post(self, api_client, post):
        """GET /api/v1/posts/{id}/ should return a single post."""
        response = api_client.get(f'/api/v1/posts/{post.pk}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Post'

    def test_create_post_unauthenticated(self, api_client):
        """Unauthenticated users cannot create posts."""
        response = api_client.post('/api/v1/posts/', {
            'title': 'New Post',
            'content': 'Content'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_post_authenticated(self, authenticated_client, user):
        """Authenticated users can create posts."""
        response = authenticated_client.post('/api/v1/posts/', {
            'title': 'New API Post',
            'content': 'Created via API'
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(title='New API Post').exists()
        assert Post.objects.get(title='New API Post').author == user

    def test_update_own_post(self, authenticated_client, post):
        """Users can update their own posts."""
        response = authenticated_client.patch(f'/api/v1/posts/{post.pk}/', {
            'title': 'Updated Title'
        })
        assert response.status_code == status.HTTP_200_OK
        post.refresh_from_db()
        assert post.title == 'Updated Title'

    def test_delete_own_post(self, authenticated_client, post):
        """Users can delete their own posts."""
        post_id = post.pk
        response = authenticated_client.delete(f'/api/v1/posts/{post_id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Post.objects.filter(pk=post_id).exists()

    def test_cannot_update_others_post(self, api_client, another_user, post):
        """Users cannot update others' posts."""
        api_client.force_authenticate(user=another_user)
        response = api_client.patch(f'/api/v1/posts/{post.pk}/', {
            'title': 'Hacked Title'
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_search_posts(self, api_client, post):
        """Posts can be searched by title/content."""
        response = api_client.get('/api/v1/posts/', {'search': 'Test'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1


@pytest.mark.django_db
class TestUserAPI:
    """Tests for User API endpoints."""

    def test_list_users(self, api_client, user):
        """GET /api/v1/users/ should list users."""
        response = api_client.get('/api/v1/users/')
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_user(self, api_client, user):
        """GET /api/v1/users/{id}/ should return user details."""
        response = api_client.get(f'/api/v1/users/{user.pk}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'

    def test_create_user(self, api_client):
        """POST /api/v1/users/ should create a new user."""
        response = api_client.post('/api/v1/users/', {
            'username': 'apiuser',
            'email': 'api@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_me_endpoint_authenticated(self, authenticated_client, user):
        """GET /api/v1/users/me/ should return current user."""
        response = authenticated_client.get('/api/v1/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username

    def test_me_endpoint_unauthenticated(self, api_client):
        """GET /api/v1/users/me/ requires authentication."""
        response = api_client.get('/api/v1/users/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestJWTAuthentication:
    """Tests for JWT token authentication."""

    def test_obtain_token(self, api_client, user):
        """Users can obtain JWT tokens."""
        response = api_client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_refresh_token(self, api_client, user):
        """Users can refresh their tokens."""
        # First obtain tokens
        token_response = api_client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = token_response.data['refresh']

        # Then refresh
        response = api_client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_invalid_credentials(self, api_client, user):
        """Invalid credentials should be rejected."""
        response = api_client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAPIDocumentation:
    """Tests for API documentation endpoints."""

    def test_swagger_ui(self, api_client):
        """Swagger UI should be accessible."""
        response = api_client.get('/api/v1/docs/')
        assert response.status_code == status.HTTP_200_OK

    def test_openapi_schema(self, api_client):
        """OpenAPI schema should be accessible."""
        response = api_client.get('/api/v1/schema/')
        assert response.status_code == status.HTTP_200_OK
