from django.db import models
from django.contrib.auth.models import User


class FriendRequest(models.Model):
    """Model for friend requests between users."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    from_user = models.ForeignKey(
        User,
        related_name='friend_requests_sent',
        on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        User,
        related_name='friend_requests_received',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"

    def accept(self):
        """Accept the friend request and create friendship."""
        self.status = 'accepted'
        self.save()
        # Create bidirectional friendship
        Friendship.objects.get_or_create(user=self.from_user, friend=self.to_user)
        Friendship.objects.get_or_create(user=self.to_user, friend=self.from_user)

    def decline(self):
        """Decline the friend request."""
        self.status = 'declined'
        self.save()


class Friendship(models.Model):
    """Model for established friendships (bidirectional)."""

    user = models.ForeignKey(User, related_name='friendships', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friends_with', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ↔ {self.friend.username}"


class AudiobookFavorite(models.Model):
    """Model for user's favorite audiobooks from Spotify."""

    user = models.ForeignKey(User, related_name='audiobook_favorites', on_delete=models.CASCADE)
    spotify_id = models.CharField(max_length=255)  # Spotify audiobook ID from URL
    title = models.CharField(max_length=500)
    authors = models.JSONField(default=list)  # List of author names
    narrators = models.JSONField(default=list)  # List of narrator names
    image_url = models.URLField(max_length=500, blank=True)
    spotify_url = models.URLField(max_length=500)
    description = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'spotify_id')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class UserActivity(models.Model):
    """Model for tracking user activity for the feed."""

    ACTIVITY_TYPES = [
        ('favorite_added', 'Added favorite'),
        ('friend_added', 'Became friends'),
        ('post_created', 'Created post'),
    ]

    user = models.ForeignKey(User, related_name='activities', on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=500)
    related_user = models.ForeignKey(
        User,
        related_name='mentioned_in_activities',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    metadata = models.JSONField(default=dict, blank=True)  # Extra data like audiobook info
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User activities'

    def __str__(self):
        return f"{self.user.username}: {self.activity_type}"
