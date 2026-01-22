from rest_framework import serializers
from django.contrib.auth.models import User
from blog.models import Post
from users.models import Profile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with profile info."""
    profile_image = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'profile_image', 'posts_count']
        read_only_fields = ['date_joined']

    def get_profile_image(self, obj):
        if hasattr(obj, 'profile') and obj.profile.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.image.url)
            return obj.profile.image.url
        return None

    def get_posts_count(self, obj):
        if hasattr(obj, 'post_set'):
            return obj.post_set.count()
        return 0


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'image']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model."""
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='author',
        write_only=True,
        required=False
    )

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'date_posted', 'author', 'author_id']
        read_only_fields = ['date_posted']


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts."""

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'date_posted']
        read_only_fields = ['date_posted']


class AudiobookSerializer(serializers.Serializer):
    """Serializer for audiobook search results from Spotify."""
    title = serializers.CharField()
    authors = serializers.ListField(child=serializers.CharField())
    narrators = serializers.ListField(child=serializers.CharField())
    description = serializers.CharField()
    image = serializers.URLField(allow_null=True)
    url = serializers.URLField(allow_null=True)


class AudiobookSearchSerializer(serializers.Serializer):
    """Serializer for audiobook search request."""
    query = serializers.CharField(min_length=1, max_length=200)
