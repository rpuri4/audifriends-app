from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from django.core.paginator import Paginator
import random

from .models import FriendRequest, Friendship, AudiobookFavorite, UserActivity


# Mock AI recommendations - pre-written for demo purposes
MOCK_RECOMMENDATIONS = [
    {
        'title': 'Atomic Habits',
        'author': 'James Clear',
        'reason': 'Based on your interest in self-improvement audiobooks, this bestseller offers practical strategies for building good habits and breaking bad ones. Perfect for your productivity-focused library.',
    },
    {
        'title': 'Deep Work',
        'author': 'Cal Newport',
        'reason': 'Your library shows a pattern of focus and productivity titles. This book dives into the art of concentrated work in a distracted world - a natural next step.',
    },
    {
        'title': 'Project Hail Mary',
        'author': 'Andy Weir',
        'reason': 'Given your appreciation for engaging narratives, this sci-fi thriller combines humor, science, and heart. The audiobook narration by Ray Porter is exceptional.',
    },
    {
        'title': 'The Psychology of Money',
        'author': 'Morgan Housel',
        'reason': 'Your collection suggests an interest in understanding systems and behavior. This book explores the emotional side of finance through compelling stories.',
    },
    {
        'title': 'Sapiens',
        'author': 'Yuval Noah Harari',
        'reason': 'For someone who enjoys thought-provoking content, this sweeping history of humankind will challenge your perspective on civilization and progress.',
    },
    {
        'title': 'The Midnight Library',
        'author': 'Matt Haig',
        'reason': 'Your eclectic taste suggests you appreciate books that make you think. This novel explores parallel lives and the choices that define us.',
    },
    {
        'title': 'Educated',
        'author': 'Tara Westover',
        'reason': 'Based on your memoir selections, this powerful story of self-invention and the pursuit of knowledge will resonate deeply.',
    },
    {
        'title': 'The Art of War',
        'author': 'Sun Tzu',
        'reason': 'Your strategy-focused picks indicate you appreciate timeless wisdom. This classic offers insights applicable to modern challenges.',
    },
]


@login_required
def dashboard(request):
    """User dashboard with stats, activity feed, and quick actions."""
    user = request.user

    # Get user stats
    stats = {
        'posts_count': user.post_set.count(),
        'friends_count': user.friendships.count(),
        'favorites_count': user.audiobook_favorites.count(),
    }

    # Get pending friend requests
    pending_requests = FriendRequest.objects.filter(
        to_user=user,
        status='pending'
    ).select_related('from_user', 'from_user__profile')[:5]

    # Get recent favorites
    recent_favorites = user.audiobook_favorites.all()[:4]

    # Get activity feed (user's activities + friends' activities)
    friend_ids = user.friendships.values_list('friend_id', flat=True)
    activities = UserActivity.objects.filter(
        Q(user=user) | Q(user_id__in=friend_ids)
    ).select_related('user', 'user__profile', 'related_user')[:10]

    # Suggested friends (users with similar favorites)
    user_favorite_titles = set(user.audiobook_favorites.values_list('title', flat=True))
    suggested_users = []

    if user_favorite_titles:
        # Find users with similar favorites who are not already friends
        existing_friend_ids = list(friend_ids) + [user.id]
        potential_friends = User.objects.exclude(
            id__in=existing_friend_ids
        ).annotate(
            shared_favorites=Count(
                'audiobook_favorites',
                filter=Q(audiobook_favorites__title__in=user_favorite_titles)
            )
        ).filter(shared_favorites__gt=0).order_by('-shared_favorites')[:5]
        suggested_users = potential_friends

    context = {
        'stats': stats,
        'pending_requests': pending_requests,
        'recent_favorites': recent_favorites,
        'activities': activities,
        'suggested_users': suggested_users,
    }
    return render(request, 'friends/dashboard.html', context)


@login_required
def friends_list(request):
    """List all friends with search functionality."""
    user = request.user
    query = request.GET.get('q', '')

    friends = User.objects.filter(
        id__in=user.friendships.values_list('friend_id', flat=True)
    ).select_related('profile')

    if query:
        friends = friends.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    paginator = Paginator(friends, 12)
    page = request.GET.get('page', 1)
    friends_page = paginator.get_page(page)

    context = {
        'friends': friends_page,
        'query': query,
    }
    return render(request, 'friends/friends_list.html', context)


@login_required
def discover_users(request):
    """Discover new users to connect with."""
    user = request.user
    query = request.GET.get('q', '')

    # Exclude self and existing friends
    friend_ids = list(user.friendships.values_list('friend_id', flat=True)) + [user.id]

    users = User.objects.exclude(
        id__in=friend_ids
    ).select_related('profile').annotate(
        favorites_count=Count('audiobook_favorites'),
        posts_count=Count('post')
    )

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    # Get pending requests sent by current user
    pending_sent = set(FriendRequest.objects.filter(
        from_user=user,
        status='pending'
    ).values_list('to_user_id', flat=True))

    paginator = Paginator(users, 12)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)

    context = {
        'users': users_page,
        'query': query,
        'pending_sent': pending_sent,
    }
    return render(request, 'friends/discover.html', context)


@login_required
@require_POST
def send_friend_request(request, user_id):
    """Send a friend request to another user."""
    to_user = get_object_or_404(User, id=user_id)

    if to_user == request.user:
        return JsonResponse({'error': 'Cannot send friend request to yourself'}, status=400)

    # Check if already friends
    if Friendship.objects.filter(user=request.user, friend=to_user).exists():
        return JsonResponse({'error': 'Already friends'}, status=400)

    # Check if request already exists
    existing = FriendRequest.objects.filter(
        from_user=request.user,
        to_user=to_user
    ).first()

    if existing:
        if existing.status == 'pending':
            return JsonResponse({'error': 'Request already sent'}, status=400)
        elif existing.status == 'declined':
            existing.status = 'pending'
            existing.save()
            return JsonResponse({'success': True, 'message': 'Friend request sent!'})

    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return JsonResponse({'success': True, 'message': 'Friend request sent!'})


@login_required
@require_POST
def respond_friend_request(request, request_id):
    """Accept or decline a friend request."""
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        to_user=request.user,
        status='pending'
    )

    action = request.POST.get('action')

    if action == 'accept':
        friend_request.accept()
        # Create activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='friend_added',
            description=f'Became friends with {friend_request.from_user.username}',
            related_user=friend_request.from_user
        )
        UserActivity.objects.create(
            user=friend_request.from_user,
            activity_type='friend_added',
            description=f'Became friends with {request.user.username}',
            related_user=request.user
        )
        return JsonResponse({'success': True, 'message': 'Friend request accepted!'})
    elif action == 'decline':
        friend_request.decline()
        return JsonResponse({'success': True, 'message': 'Friend request declined'})

    return JsonResponse({'error': 'Invalid action'}, status=400)


@login_required
@require_POST
def remove_friend(request, user_id):
    """Remove a friend."""
    friend = get_object_or_404(User, id=user_id)

    # Remove bidirectional friendship
    Friendship.objects.filter(
        Q(user=request.user, friend=friend) |
        Q(user=friend, friend=request.user)
    ).delete()

    return JsonResponse({'success': True, 'message': 'Friend removed'})


@login_required
def my_library(request):
    """User's audiobook library/favorites."""
    favorites = request.user.audiobook_favorites.all()

    paginator = Paginator(favorites, 12)
    page = request.GET.get('page', 1)
    favorites_page = paginator.get_page(page)

    context = {
        'favorites': favorites_page,
    }
    return render(request, 'friends/library.html', context)


@login_required
@require_POST
def add_favorite(request):
    """Add an audiobook to favorites."""
    data = request.POST

    # Extract Spotify ID from URL if provided
    spotify_url = data.get('spotify_url', '')
    spotify_id = data.get('spotify_id', '')

    if not spotify_id and spotify_url:
        # Extract ID from URL like https://open.spotify.com/audiobook/ABC123
        parts = spotify_url.rstrip('/').split('/')
        if 'audiobook' in parts:
            idx = parts.index('audiobook')
            if idx + 1 < len(parts):
                spotify_id = parts[idx + 1].split('?')[0]

    if not spotify_id:
        return JsonResponse({'error': 'Invalid audiobook'}, status=400)

    # Check if already favorited
    if AudiobookFavorite.objects.filter(user=request.user, spotify_id=spotify_id).exists():
        return JsonResponse({'error': 'Already in your library'}, status=400)

    # Parse authors and narrators from JSON strings if needed
    import json
    authors = data.get('authors', '[]')
    narrators = data.get('narrators', '[]')

    if isinstance(authors, str):
        try:
            authors = json.loads(authors)
        except json.JSONDecodeError:
            authors = [authors] if authors else []

    if isinstance(narrators, str):
        try:
            narrators = json.loads(narrators)
        except json.JSONDecodeError:
            narrators = [narrators] if narrators else []

    favorite = AudiobookFavorite.objects.create(
        user=request.user,
        spotify_id=spotify_id,
        title=data.get('title', ''),
        authors=authors,
        narrators=narrators,
        image_url=data.get('image_url', ''),
        spotify_url=spotify_url,
        description=data.get('description', ''),
    )

    # Create activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='favorite_added',
        description=f'Added "{favorite.title}" to library',
        metadata={
            'audiobook_title': favorite.title,
            'audiobook_image': favorite.image_url,
        }
    )

    return JsonResponse({
        'success': True,
        'message': 'Added to your library!',
        'favorite_id': favorite.id
    })


@login_required
@require_POST
def remove_favorite(request, favorite_id):
    """Remove an audiobook from favorites."""
    favorite = get_object_or_404(AudiobookFavorite, id=favorite_id, user=request.user)
    favorite.delete()
    return JsonResponse({'success': True, 'message': 'Removed from library'})


@login_required
def user_profile_public(request, username):
    """View another user's public profile."""
    profile_user = get_object_or_404(User, username=username)

    # Check if viewing own profile
    if profile_user == request.user:
        return redirect('profile')

    # Get friendship status
    is_friend = Friendship.objects.filter(user=request.user, friend=profile_user).exists()
    request_sent = FriendRequest.objects.filter(
        from_user=request.user,
        to_user=profile_user,
        status='pending'
    ).exists()
    request_received = FriendRequest.objects.filter(
        from_user=profile_user,
        to_user=request.user,
        status='pending'
    ).first()

    # Get user's public info
    favorites = profile_user.audiobook_favorites.all()[:6]
    recent_posts = profile_user.post_set.all()[:5]
    friends_count = profile_user.friendships.count()

    # Find shared favorites
    user_favorites = set(request.user.audiobook_favorites.values_list('spotify_id', flat=True))
    profile_favorites = set(profile_user.audiobook_favorites.values_list('spotify_id', flat=True))
    shared_count = len(user_favorites & profile_favorites)

    context = {
        'profile_user': profile_user,
        'is_friend': is_friend,
        'request_sent': request_sent,
        'request_received': request_received,
        'favorites': favorites,
        'recent_posts': recent_posts,
        'friends_count': friends_count,
        'shared_favorites_count': shared_count,
    }
    return render(request, 'friends/user_profile.html', context)


@login_required
def ai_recommendation(request):
    """Get a mock AI-powered audiobook recommendation."""
    import time

    # Simulate AI processing time (0.5-1.5 seconds)
    time.sleep(random.uniform(0.5, 1.5))

    # Get user's library for context
    favorites = request.user.audiobook_favorites.all()[:5]
    favorites_list = list(favorites.values_list('title', flat=True))

    # Pick a random recommendation from our mock data
    recommendation = random.choice(MOCK_RECOMMENDATIONS)

    context = {
        'recommendation': recommendation,
        'user_favorites': favorites_list,
    }
    return render(request, 'friends/partials/ai_recommendation.html', context)
