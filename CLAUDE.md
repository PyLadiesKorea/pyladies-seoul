This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PyLadies Seoul Official Homepage - A **Wagtail-based** multilingual CMS website for PyLadies Seoul, promoting women Python developers in Korea.  
Built with **Wagtail 6+**, **Django 5.2+**, **SCSS (Sass)**, **Logfire APM/monitoring**, and Python 3.11+.  
Runs inside **Docker** containers, orchestrated by **Docker Compose**.  
Uses **uv** for Python package management and **ruff** for code linting & formatting.

## Key Architecture

### Tech Stack
- **Backend**: Django 5.2+, Wagtail 6.x, Python 3.11+
- **Frontend**: SCSS (Sass), vanilla JS (optionally HTMX)
- **Database**: SQLite (development), PostgreSQL (recommended for production)
- **Observability**: Logfire (APM, logging, tracing)
- **Package Management**: uv (Python), npm (for SCSS)
- **Code Quality**: ruff (PEP8 formatting, linting, import sorting, type hints)
- **Deployment**: Docker, Docker Compose, Kubernetes/Helm ready

## Security Guidelines

### Environment Variables & Secrets Management
- **NEVER hardcode secrets** in source code (SECRET_KEY, API keys, database passwords, etc.)
- Use `.env` files for local development environment variables
- Load environment variables using `python-dotenv` package
- Add `.env` to `.gitignore` to prevent committing secrets
- Use environment-specific settings files (settings/dev.py, settings/prod.py)
- For production, use proper secrets management (Docker secrets, Kubernetes secrets, cloud key vaults)

### Required Environment Variables
- `SECRET_KEY`: Django secret key (generate with `django.core.management.utils.get_random_secret_key()`)
- `DEBUG`: Boolean for debug mode (False in production)
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string for caching
- `LOGFIRE_TOKEN`: Logfire APM token (if using Logfire)
- `EMAIL_HOST_PASSWORD`: Email service password
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

### Example .env structure:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/pyladies_seoul
REDIS_URL=redis://localhost:6379/0
LOGFIRE_TOKEN=your-logfire-token
EMAIL_HOST_PASSWORD=your-email-password
ALLOWED_HOSTS=localhost,127.0.0.1,pyladiesseoul.org
```

## Testing & Quality Assurance

### Test-Driven Development (TDD) Requirements
- **MANDATORY**: Write tests FIRST before implementing any feature
- Follow the Red-Green-Refactor cycle:
  1. **Red**: Write a failing test that describes the desired functionality
  2. **Green**: Write the minimal code to make the test pass
  3. **Refactor**: Improve code quality while keeping tests green
- **All tests must pass** before considering a feature complete
- If tests fail, **fix the code immediately** - never ignore failing tests

### Test Coverage Requirements
- **Minimum 80% test coverage** for all Python code
- **100% coverage** for critical business logic (models, views, forms)
- Use `coverage.py` to measure and report test coverage
- Run tests with: `python manage.py test` or `pytest`
- Generate coverage report: `coverage run --source='.' manage.py test && coverage report`

### Required Test Types
- **Unit Tests**: Test individual functions, methods, and classes
- **Model Tests**: Test Django/Wagtail models, validation, and methods
- **View Tests**: Test HTTP responses, authentication, permissions
- **Form Tests**: Test form validation and data processing
- **Integration Tests**: Test component interactions
- **Functional Tests**: Test complete user workflows using Selenium/Playwright

### Test Structure
```python
# Example model test
class EventPageTestCase(TestCase):
    def setUp(self):
        self.home_page = HomePage.objects.get(slug='home')
        self.event_page = EventPage(
            title="Test Event",
            date=timezone.now() + timedelta(days=7),
            location="Seoul, Korea"
        )
        self.home_page.add_child(instance=self.event_page)
    
    def test_event_page_creation(self):
        """Test that event page can be created with required fields"""
        self.assertTrue(self.event_page.live)
        self.assertEqual(self.event_page.title, "Test Event")
    
    def test_event_page_url(self):
        """Test event page URL generation"""
        response = self.client.get(self.event_page.url)
        self.assertEqual(response.status_code, 200)
```

### Continuous Testing Workflow
1. **Before implementing any feature**: Write comprehensive tests
2. **During development**: Run tests frequently (`python manage.py test`)
3. **Before committing**: Ensure ALL tests pass and coverage meets requirements
4. **If tests fail**: Stop development and fix the failing tests immediately
5. **No exceptions**: Failing tests must be resolved before proceeding

### Test Automation
- Use GitHub Actions or similar CI/CD to run tests automatically
- Set up pre-commit hooks to run tests before commits
- Configure test database settings for faster test execution
- Use factory_boy or similar libraries for test data generation

## Git Commit Guidelines

### Commit Strategy
- **Commit frequently** after each significant milestone or feature completion
- **Never commit** failing tests or broken code
- Commit **after each phase** completion to track progress
- Use **meaningful, concise** commit messages in present tense

### Commit Message Format
- **One line only** - keep it under 50 characters when possible
- Use **present tense** ("Add user model" not "Added user model")
- Start with **action verb** (Add, Fix, Update, Remove, Refactor, etc.)
- Be **specific** about what was changed

### Example Commit Messages
```
Add Django project structure with Wagtail setup
Create EventPage and InterviewPage models
Implement multilingual support for content
Add scroll-triggered animations with Intersection Observer
Configure Docker development environment
Add comprehensive test suite with 85% coverage
Optimize images with WebP conversion
Fix responsive design issues on mobile
Add FAQ accordion with smooth transitions
Configure production deployment with nginx
```

### When to Commit
- ✅ **After each phase completion** (setup, models, admin, etc.)
- ✅ **After test suite passes** with required coverage
- ✅ **After successful feature implementation** and testing
- ✅ **Before starting next major feature**
- ❌ **Never commit** failing tests
- ❌ **Never commit** broken or incomplete features
- ❌ **Never commit** hardcoded secrets or sensitive data
- ❌ **Never commit** temporary files, build guides, or development notes (*.md guides, run_all_agents.py, etc.)

### Automated Commit Integration
Agents should automatically commit after:
1. Successfully completing each implementation phase
2. All tests pass with minimum coverage requirements
3. Code passes ruff linting and formatting
4. Docker build succeeds (if applicable)

