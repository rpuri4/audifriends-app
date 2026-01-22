# AudiFriends

A terminal-themed social platform for audiobook enthusiasts built with Django, featuring a unique CLI-inspired design, HTMX-powered interactions, and AI-powered recommendations.

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Django](https://img.shields.io/badge/django-5.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

### Core Features
- **Audiobook Search** - Search millions of audiobooks via Spotify API integration
- **Personal Library** - Save favorites and build your audiobook collection
- **Social Connections** - Find friends, send requests, see what others are listening to
- **Community Posts** - Share thoughts and reviews with the community
- **User Profiles** - Customizable profiles with profile pictures

### Terminal-Themed UI
- **CLI-Inspired Design** - Monospace fonts, terminal color palette, command-style navigation
- **Dark/Light Mode** - Toggle between dark terminal and light themes
- **Split-Pane Layout** - Click posts to view in sliding side panel without page reload
- **Keyboard Navigation** - Use `j/k` to navigate, `Enter` to open, `Esc` to close
- **Command Palette** - Press `Ctrl+K` for quick navigation
- **Sound Effects** - Optional keyboard click sounds for immersion

### AI-Powered Recommendations
- **Smart Suggestions** - Get personalized audiobook recommendations based on your library
- **Typewriter Effect** - Terminal-style animated text display
- **Context-Aware** - Recommendations include reasoning based on your taste

### REST API
- **Full-Featured API** - Complete REST API with JWT authentication
- **Swagger Documentation** - Interactive API docs at `/api/v1/docs/`
- **Audiobook Search Endpoint** - Programmatic access to Spotify audiobook search

## Screenshots

```
┌─────────────────────────────────────────────────────────────────┐
│ user@audifriends:~$                    [◐] [♪] [@user] [logout] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  $ ls ./posts --recent                                          │
│  Community Feed                                                 │
│                                                                 │
│  01  [img] username · Jan 22                                    │
│      Post Title Here                                            │
│      Post content preview...                                    │
│      > click to expand                                          │
│                                                                 │
│  02  [img] another_user · Jan 21                                │
│      Another Post                                               │
│      More content here...                                       │
│      > click to expand                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Category | Technology |
|----------|------------|
| Backend | Django 5.0, Django REST Framework |
| Database | SQLite (dev), PostgreSQL (prod) |
| Frontend | HTMX, Custom Terminal CSS, JetBrains Mono |
| API Auth | JWT (SimpleJWT) |
| External API | Spotify Web API |
| Testing | Pytest, Factory Boy |
| CI/CD | GitHub Actions |
| Deployment | Docker, Gunicorn, Nginx |

## Quick Start

### Prerequisites

- Python 3.10+
- Spotify Developer Account (for audiobook search)

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/AudiFriends.git
cd AudiFriends

# Create and activate virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
cd django_project
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your settings (see Configuration section)

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit http://localhost:8000 to see the app.

### Docker Deployment

```bash
cd django_project

# Build and run with Docker Compose
docker-compose up --build

# Run in detached mode
docker-compose up -d
```

Visit http://localhost to see the app (Nginx serves on port 80).

## Configuration

Create a `.env` file in the `django_project` directory:

```env
# Django Settings
SECRET_KEY=your-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (for password reset)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Spotify API (https://developer.spotify.com/dashboard)
SPOTIFY_CLIENT_ID=your-client-id
SPOTIFY_CLIENT_SECRET=your-client-secret
```

### Getting Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy the Client ID and Client Secret to your `.env` file

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Open command palette |
| `j` | Navigate down in lists |
| `k` | Navigate up in lists |
| `Enter` | Open selected item |
| `Esc` | Close panel/palette |

## API Documentation

The REST API is available at `/api/v1/` with interactive documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs/
- **ReDoc**: http://localhost:8000/api/v1/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/v1/schema/

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/posts/` | GET | List all posts |
| `/api/v1/posts/` | POST | Create a post (auth required) |
| `/api/v1/posts/{id}/` | GET | Get a specific post |
| `/api/v1/users/` | GET | List users |
| `/api/v1/users/me/` | GET | Get current user (auth required) |
| `/api/v1/audiobooks/search/` | GET/POST | Search audiobooks (auth required) |
| `/api/v1/auth/token/` | POST | Get JWT token |
| `/api/v1/auth/token/refresh/` | POST | Refresh JWT token |

### Authentication

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'

# Use token in requests
curl http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer <your-access-token>"
```

## Testing

```bash
cd django_project

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py
```

## Project Structure

```
AudiFriends/
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI/CD pipeline
├── django_project/
│   ├── api/                       # REST API app
│   │   ├── serializers.py         # DRF serializers
│   │   ├── views.py               # API viewsets
│   │   ├── spotify.py             # Spotify client
│   │   └── urls.py                # API routes
│   ├── blog/                      # Blog/Posts app
│   │   ├── models.py              # Post model
│   │   ├── views.py               # Blog views
│   │   ├── static/blog/main.css   # Terminal theme CSS
│   │   └── templates/
│   │       ├── blog/base.html     # Base template with nav
│   │       ├── blog/landing.html  # Landing page
│   │       └── blog/partials/     # HTMX partials
│   ├── friends/                   # Social features app
│   │   ├── models.py              # Friendship, Favorites models
│   │   ├── views.py               # Friends, Library, AI views
│   │   └── templates/             # Friends templates
│   ├── users/                     # User management app
│   │   ├── models.py              # Profile model
│   │   └── templates/             # User templates
│   ├── tests/                     # Test suite
│   ├── django_project/            # Project config
│   │   └── settings.py            # Django settings
│   ├── Dockerfile                 # Docker image
│   ├── docker-compose.yml         # Multi-container setup
│   └── requirements.txt           # Python dependencies
└── README.md
```

## Design System

### Color Palette (Dark Mode)
```css
--term-bg: #0a0a0a;        /* Background */
--term-green: #00ff9f;     /* Primary/Success */
--term-cyan: #00d4ff;      /* Secondary/Info */
--term-amber: #ffb000;     /* Warning/Accent */
--term-red: #ff4444;       /* Danger/Error */
--term-white: #e0e0e0;     /* Text */
--term-gray: #666666;      /* Muted text */
```

### Typography
- **Font**: JetBrains Mono (monospace)
- **Base Size**: 16px
- **Line Height**: 1.6

## Development

### Code Quality

```bash
# Format code with Black
black .

# Sort imports
isort .

# Lint with Ruff
ruff check .
```

### Adding New Features

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Write tests first (TDD recommended)
3. Implement the feature
4. Run tests: `pytest`
5. Create a pull request

## Deployment Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Generate a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Configure email backend
- [ ] Set up SSL/HTTPS
- [ ] Configure static file serving (WhiteNoise/CDN)
- [ ] Set up monitoring and logging

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Django](https://www.djangoproject.com/) - Web framework
- [Django REST Framework](https://www.django-rest-framework.org/) - API toolkit
- [HTMX](https://htmx.org/) - Frontend interactivity
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) - Audiobook data
- [JetBrains Mono](https://www.jetbrains.com/lp/mono/) - Monospace font
