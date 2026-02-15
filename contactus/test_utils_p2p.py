from django.test import TestCase
from contactus.utils import (
    validate_email,
    validate_contact_form,
    sanitize_message,
    truncate_subject,
)


class ValidateEmailExtraTest(TestCase):
    def test_with_plus(self):
        self.assertTrue(validate_email('user+tag@example.com'))

    def test_with_subdomain(self):
        self.assertTrue(validate_email('user@mail.example.co.uk'))

    def test_double_at(self):
        self.assertFalse(validate_email('user@@example.com'))


class ValidateContactFormExtraTest(TestCase):
    def test_valid_long_message(self):
        data = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'subject': 'Inquiry about Konkan trip',
            'message': 'I would like to know more about the upcoming trips. ' * 10,
        }
        errors = validate_contact_form(data)
        self.assertEqual(errors, {})

    def test_exactly_200_char_subject(self):
        data = {
            'name': 'Test',
            'email': 'test@example.com',
            'subject': 'x' * 200,
            'message': 'Hello',
        }
        errors = validate_contact_form(data)
        self.assertNotIn('subject', errors)


class SanitizeMessageExtraTest(TestCase):
    def test_nested_tags(self):
        self.assertEqual(sanitize_message('<div><p>Hello</p></div>'), 'Hello')

    def test_mixed_content(self):
        result = sanitize_message('Hello <b>world</b> test')
        self.assertEqual(result, 'Hello world test')


class TruncateSubjectExtraTest(TestCase):
    def test_unicode_subject(self):
        result = truncate_subject('Hello World')
        self.assertEqual(result, 'Hello World')

    def test_exactly_at_limit(self):
        text = 'a' * 100
        self.assertEqual(len(truncate_subject(text, 100)), 100)
