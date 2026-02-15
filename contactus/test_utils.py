from django.test import TestCase
from contactus.utils import (
    validate_email,
    validate_contact_form,
    sanitize_message,
    truncate_subject,
)


class ValidateEmailTest(TestCase):
    def test_valid_email(self):
        self.assertTrue(validate_email('test@example.com'))

    def test_valid_with_dots(self):
        self.assertTrue(validate_email('user.name@domain.co.in'))

    def test_empty(self):
        self.assertFalse(validate_email(''))

    def test_none(self):
        self.assertFalse(validate_email(None))

    def test_no_at(self):
        self.assertFalse(validate_email('testexample.com'))

    def test_no_domain(self):
        self.assertFalse(validate_email('test@'))

    def test_no_tld(self):
        self.assertFalse(validate_email('test@example'))


class ValidateContactFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Hello',
            'message': 'Test message',
        }
        errors = validate_contact_form(data)
        self.assertEqual(errors, {})

    def test_empty_form(self):
        errors = validate_contact_form({})
        self.assertIn('name', errors)
        self.assertIn('email', errors)
        self.assertIn('subject', errors)
        self.assertIn('message', errors)

    def test_short_name(self):
        data = {
            'name': 'J',
            'email': 'j@example.com',
            'subject': 'Hi',
            'message': 'Test',
        }
        errors = validate_contact_form(data)
        self.assertIn('name', errors)
        self.assertIn('at least 2', errors['name'])

    def test_invalid_email(self):
        data = {
            'name': 'John',
            'email': 'not-an-email',
            'subject': 'Hi',
            'message': 'Test',
        }
        errors = validate_contact_form(data)
        self.assertIn('email', errors)

    def test_long_subject(self):
        data = {
            'name': 'John',
            'email': 'john@example.com',
            'subject': 'x' * 201,
            'message': 'Test',
        }
        errors = validate_contact_form(data)
        self.assertIn('subject', errors)

    def test_whitespace_only(self):
        data = {
            'name': '   ',
            'email': '   ',
            'subject': '   ',
            'message': '   ',
        }
        errors = validate_contact_form(data)
        self.assertEqual(len(errors), 4)


class SanitizeMessageTest(TestCase):
    def test_removes_html(self):
        self.assertEqual(sanitize_message('<b>Hello</b>'), 'Hello')

    def test_removes_script(self):
        self.assertEqual(sanitize_message('<script>alert("xss")</script>'), 'alert("xss")')

    def test_plain_text(self):
        self.assertEqual(sanitize_message('Hello world'), 'Hello world')

    def test_empty(self):
        self.assertEqual(sanitize_message(''), '')

    def test_none(self):
        self.assertEqual(sanitize_message(None), '')

    def test_strips_whitespace(self):
        self.assertEqual(sanitize_message('  hello  '), 'hello')


class TruncateSubjectTest(TestCase):
    def test_short_subject(self):
        self.assertEqual(truncate_subject('Hello'), 'Hello')

    def test_exact_length(self):
        text = 'x' * 100
        self.assertEqual(truncate_subject(text), text)

    def test_long_subject(self):
        text = 'x' * 150
        result = truncate_subject(text)
        self.assertEqual(len(result), 100)
        self.assertTrue(result.endswith('...'))

    def test_empty(self):
        self.assertEqual(truncate_subject(''), '')

    def test_none(self):
        self.assertEqual(truncate_subject(None), '')

    def test_custom_max_length(self):
        result = truncate_subject('Hello World', max_length=8)
        self.assertEqual(result, 'Hello...')
