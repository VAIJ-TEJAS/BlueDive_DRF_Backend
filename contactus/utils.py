import re


def validate_email(email):
    """Basic email format validation."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_contact_form(data):
    """Validate contact form fields and return a dict of errors."""
    errors = {}

    name = data.get('name', '').strip()
    if not name:
        errors['name'] = 'Name is required'
    elif len(name) < 2:
        errors['name'] = 'Name must be at least 2 characters'

    email = data.get('email', '').strip()
    if not email:
        errors['email'] = 'Email is required'
    elif not validate_email(email):
        errors['email'] = 'Enter a valid email address'

    subject = data.get('subject', '').strip()
    if not subject:
        errors['subject'] = 'Subject is required'
    elif len(subject) > 200:
        errors['subject'] = 'Subject must be 200 characters or less'

    message = data.get('message', '').strip()
    if not message:
        errors['message'] = 'Message is required'

    return errors


def sanitize_message(text):
    """Remove potentially harmful HTML tags from message text."""
    if not text:
        return ''
    cleaned = re.sub(r'<[^>]+>', '', text)
    return cleaned.strip()


def truncate_subject(subject, max_length=100):
    """Truncate a subject line to a maximum length."""
    if not subject:
        return ''
    if len(subject) <= max_length:
        return subject
    return subject[:max_length - 3] + '...'
