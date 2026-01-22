"""
Tests for Django models.
"""
import pytest
from django.contrib.auth.models import User

from blog.models import Post
from users.models import Profile


@pytest.mark.django_db
class TestUserProfile:
    """Tests for the Profile model."""

    def test_profile_created_on_user_creation(self):
        """Profile should be automatically created when a user is created."""
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        assert hasattr(user, 'profile')
        assert isinstance(user.profile, Profile)

    def test_profile_str_representation(self, user):
        """Profile string should include username."""
        assert str(user.profile) == f'{user.username} Profile'

    def test_profile_default_image(self, user):
        """New profiles should have default image."""
        assert user.profile.image.name == 'default.jpg'


@pytest.mark.django_db
class TestPost:
    """Tests for the Post model."""

    def test_post_creation(self, user):
        """Test creating a post."""
        post = Post.objects.create(
            title='My Test Post',
            content='Some content here',
            author=user
        )
        assert post.title == 'My Test Post'
        assert post.author == user
        assert post.date_posted is not None

    def test_post_str_representation(self, post):
        """Post string should be its title."""
        assert str(post) == 'Test Post'

    def test_post_get_absolute_url(self, post):
        """Post should have a valid absolute URL."""
        url = post.get_absolute_url()
        assert f'/post/{post.pk}/' in url

    def test_post_ordering(self, multiple_posts):
        """Posts should be ordered by date (newest first) by default."""
        posts = Post.objects.all().order_by('-date_posted')
        assert posts[0].title == 'Test Post 14'

    def test_post_author_cascade_delete(self, user, post):
        """Deleting a user should delete their posts."""
        user_id = user.id
        post_id = post.id
        user.delete()
        assert not Post.objects.filter(id=post_id).exists()
        assert not User.objects.filter(id=user_id).exists()
