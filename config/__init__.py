"""
Django configuration package initialization.
Initialize Logfire APM when Django starts up.
"""

# Initialize Logfire APM
try:
    from .logfire_config import configure_logfire
    configure_logfire()
except ImportError:
    print("⚠️  Logfire not available, skipping APM configuration")
except Exception as e:
    print(f"⚠️  Error configuring Logfire: {e}")