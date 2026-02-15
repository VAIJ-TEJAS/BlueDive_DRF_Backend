from django.test import TestCase
from user.utils import (
    format_phone_number,
    mask_phone_number,
    validate_phone_number,
    get_display_name,
    validate_otp,
)


class FormatPhoneNumberTest(TestCase):
    def test_ten_digit(self):
        self.assertEqual(format_phone_number('9876543210'), '+919876543210')

    def test_with_country_code(self):
        self.assertEqual(format_phone_number('919876543210'), '+919876543210')

    def test_with_plus(self):
        self.assertEqual(format_phone_number('+919876543210'), '+919876543210')

    def test_empty(self):
        self.assertEqual(format_phone_number(''), '')

    def test_none(self):
        self.assertEqual(format_phone_number(None), '')

    def test_with_dashes(self):
        result = format_phone_number('98-765-43210')
        self.assertEqual(result, '+919876543210')


class MaskPhoneNumberTest(TestCase):
    def test_ten_digit(self):
        self.assertEqual(mask_phone_number('9876543210'), '******3210')

    def test_short_number(self):
        self.assertEqual(mask_phone_number('123'), '123')

    def test_four_digits(self):
        self.assertEqual(mask_phone_number('1234'), '1234')

    def test_empty(self):
        self.assertEqual(mask_phone_number(''), '')

    def test_none(self):
        self.assertEqual(mask_phone_number(None), '')


class ValidatePhoneNumberTest(TestCase):
    def test_valid_number(self):
        self.assertTrue(validate_phone_number('9876543210'))

    def test_valid_with_country_code(self):
        self.assertTrue(validate_phone_number('919876543210'))

    def test_starts_with_6(self):
        self.assertTrue(validate_phone_number('6123456789'))

    def test_starts_with_5(self):
        self.assertFalse(validate_phone_number('5123456789'))

    def test_too_short(self):
        self.assertFalse(validate_phone_number('98765'))

    def test_empty(self):
        self.assertFalse(validate_phone_number(''))

    def test_none(self):
        self.assertFalse(validate_phone_number(None))


class GetDisplayNameTest(TestCase):
    def test_full_name(self):
        user = {'first_name': 'John', 'last_name': 'Doe', 'username': '+919876543210'}
        self.assertEqual(get_display_name(user), 'John Doe')

    def test_first_name_only(self):
        user = {'first_name': 'John', 'last_name': '', 'username': '+919876543210'}
        self.assertEqual(get_display_name(user), 'John')

    def test_no_name_falls_back_to_username(self):
        user = {'first_name': '', 'last_name': '', 'username': '+919876543210'}
        self.assertEqual(get_display_name(user), '+919876543210')

    def test_none_user(self):
        self.assertEqual(get_display_name(None), 'Unknown')

    def test_empty_dict(self):
        self.assertEqual(get_display_name({}), 'Unknown')


class ValidateOtpTest(TestCase):
    def test_valid_otp(self):
        self.assertTrue(validate_otp('123456'))

    def test_too_short(self):
        self.assertFalse(validate_otp('1234'))

    def test_too_long(self):
        self.assertFalse(validate_otp('1234567'))

    def test_non_numeric(self):
        self.assertFalse(validate_otp('abcdef'))

    def test_empty(self):
        self.assertFalse(validate_otp(''))

    def test_none(self):
        self.assertFalse(validate_otp(None))

    def test_with_spaces(self):
        self.assertFalse(validate_otp('12 345'))

    def test_integer_input(self):
        self.assertTrue(validate_otp(123456))
