from datetime import date, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
import hashlib
import os
import time

# Default expiry time in hours (can be overridden in settings)
DEFAULT_TOKEN_EXPIRY_HOURS = 24


def calculate_total_experience(experiences):
    total_days = 0

    for exp in experiences:
        start = exp.start_date
        end = exp.end_date or date.today()
        total_days += (end - start).days

    years = total_days // 365
    remaining_days = total_days % 365
    months = remaining_days // 30
    days = remaining_days % 30

    return {
        "years": years,
        "months": months,
        "days": days,
    }


def generate_email_verification_token(user, expiry_timestamp=None):
    """Generate a unique token for email verification with timestamp."""
    # Get the token expiry hours from settings, default to 24 hours
    expiry_hours = getattr(settings, 'EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS', DEFAULT_TOKEN_EXPIRY_HOURS)
    
    # If no expiry_timestamp provided, generate new one
    if expiry_timestamp is None:
        timestamp = int(time.time())
        expiry_timestamp = timestamp + (expiry_hours * 3600)  # Convert hours to seconds
    
    # Use deterministic salt based on user data (so we can recreate it for verification)
    salt = hashlib.sha256(f"{user.id}{user.email}".encode()).hexdigest()[:32]
    token_data = f"{user.id}{user.email}{user.date_joined.timestamp()}{expiry_timestamp}{salt}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    
    # Return token with expiry timestamp
    return f"{token}:{expiry_timestamp}"


def send_verification_email(request, user):
    """Send email verification link to user."""
    # Generate verification token
    token = generate_email_verification_token(user)
    
    # Get the base URL from the request
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    verification_url = f"{protocol}://{domain}/user/verify-email/{user.id}/{token}/"
    
    # Prepare email context
    context = {
        'user': user,
        'cta_url': verification_url,
    }
    
    # Render email templates
    html_message = render_to_string('emails/verification_email.html', context)
    plain_message = render_to_string('emails/verification_email.txt', context)
    
    # Send email
    subject = 'Verify Your Email Address - Workhub'
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=from_email,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
    return token


def verify_email(user, token):
    """Verify the user's email using the token with expiry check."""
    try:
        # Split token and expiry timestamp
        token_parts = token.rsplit(':', 1)
        if len(token_parts) != 2:
            return False
        
        submitted_token, expiry_timestamp = token_parts
        expiry_timestamp = int(expiry_timestamp)
        
        # Check if token has expired
        current_timestamp = int(time.time())
        if current_timestamp > expiry_timestamp:
            return False
        
        # Generate the expected token with the same expiry timestamp
        expected_token = generate_email_verification_token(user, expiry_timestamp)
        expected_token_parts = expected_token.rsplit(':', 1)
        expected_token_value = expected_token_parts[0]
        
        # Compare tokens (timing-safe comparison)
        if constant_time_compare(submitted_token, expected_token_value):
            return True
    except (ValueError, AttributeError):
        return False
    
    return False


def constant_time_compare(val1, val2):
    """Compare two strings in constant time to prevent timing attacks."""
    if len(val1) != len(val2):
        return False
    result = 0
    for c1, c2 in zip(val1, val2):
        result |= ord(c1) ^ ord(c2)
    return result == 0
