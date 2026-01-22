from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, FindAudioBook
from api.spotify import SpotifyClient, SpotifyAuthError


def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created! Log in now!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    """Handle user profile display and updates."""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)


@login_required
def findAudioBook(request):
    """Search for audiobooks using Spotify API."""
    form = FindAudioBook()
    result = None
    error = None

    if request.method == 'POST':
        form = FindAudioBook(request.POST)
        title = request.POST.get('audio_title', '').strip()

        if title:
            try:
                spotify = SpotifyClient()
                results = spotify.search_audiobooks(title, limit=5)

                if results:
                    # Find exact match or use first result
                    exact = next(
                        (r for r in results if r['title'].lower() == title.lower()),
                        None
                    )
                    result = exact or results[0]
                else:
                    error = 'No audiobooks found for that title.'
            except SpotifyAuthError as e:
                error = 'Spotify API not configured. Please add your credentials to .env file.'
            except Exception as e:
                error = f'Error searching for audiobooks: {str(e)}'
        else:
            error = 'Please enter an audiobook title.'

    context = {
        'form': form,
        'information': result,
        'error': error,
    }
    return render(request, 'users/find_friends.html', context)


@login_required
@require_http_methods(['POST'])
def search_audiobooks_htmx(request):
    """HTMX endpoint for live audiobook search."""
    title = request.POST.get('audio_title', '').strip()

    if not title:
        return render(request, 'users/partials/audiobook_results.html', {
            'error': 'Please enter an audiobook title.'
        })

    try:
        spotify = SpotifyClient()
        results = spotify.search_audiobooks(title, limit=5)

        return render(request, 'users/partials/audiobook_results.html', {
            'results': results,
            'query': title,
        })
    except SpotifyAuthError:
        return render(request, 'users/partials/audiobook_results.html', {
            'error': 'Spotify API not configured. Please add your credentials to .env file.'
        })
    except Exception as e:
        return render(request, 'users/partials/audiobook_results.html', {
            'error': f'Error: {str(e)}'
        })
