from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Friends
    path('friends/', views.friends_list, name='friends-list'),
    path('discover/', views.discover_users, name='discover-users'),
    path('friend-request/<int:user_id>/', views.send_friend_request, name='send-friend-request'),
    path('friend-request/respond/<int:request_id>/', views.respond_friend_request, name='respond-friend-request'),
    path('friend/remove/<int:user_id>/', views.remove_friend, name='remove-friend'),

    # Library / Favorites
    path('library/', views.my_library, name='my-library'),
    path('favorite/add/', views.add_favorite, name='add-favorite'),
    path('favorite/remove/<int:favorite_id>/', views.remove_favorite, name='remove-favorite'),

    # AI Features
    path('ai/recommend/', views.ai_recommendation, name='ai-recommendation'),

    # User profiles
    path('user/<str:username>/', views.user_profile_public, name='user-profile-public'),
]
