from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, OpenApiParameter

from blog.models import Post
from users.models import Profile
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    ProfileSerializer,
    PostSerializer,
    PostCreateSerializer,
    AudiobookSerializer,
    AudiobookSearchSerializer,
)
from .spotify import SpotifyClient
from .permissions import IsOwnerOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users.

    list: Get all users
    retrieve: Get a specific user
    create: Register a new user
    me: Get current authenticated user
    """
    queryset = User.objects.all().order_by('-date_joined')
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticatedOrReadOnly()]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get the current authenticated user's details."""
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for user profiles."""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get or update the current user's profile."""
        profile = request.user.profile

        if request.method == 'GET':
            serializer = ProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)

        serializer = ProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for blog posts.

    Supports filtering, searching, and ordering.
    """
    queryset = Post.objects.all().order_by('-date_posted')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author', 'author__username']
    search_fields = ['title', 'content']
    ordering_fields = ['date_posted', 'title']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='username', type=str, description='Filter by author username')
        ]
    )
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get posts by a specific user."""
        username = request.query_params.get('username')
        if not username:
            return Response(
                {'error': 'username parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        posts = Post.objects.filter(author__username=username).order_by('-date_posted')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class AudiobookSearchView(APIView):
    """
    Search for audiobooks using the Spotify API.

    Requires authentication. Returns a list of audiobooks matching the search query.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AudiobookSearchSerializer,
        responses={200: AudiobookSerializer(many=True)},
        description='Search for audiobooks on Spotify'
    )
    def post(self, request):
        serializer = AudiobookSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data['query']
        spotify = SpotifyClient()

        try:
            results = spotify.search_audiobooks(query)
            output_serializer = AudiobookSerializer(results, many=True)
            return Response(output_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @extend_schema(
        parameters=[
            OpenApiParameter(name='q', type=str, description='Search query', required=True)
        ],
        responses={200: AudiobookSerializer(many=True)},
        description='Search for audiobooks on Spotify'
    )
    def get(self, request):
        query = request.query_params.get('q')
        if not query:
            return Response(
                {'error': 'q parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        spotify = SpotifyClient()

        try:
            results = spotify.search_audiobooks(query)
            output_serializer = AudiobookSerializer(results, many=True)
            return Response(output_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
