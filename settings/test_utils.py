from datetime import date, timedelta
from django.test import TestCase
from settings.utils import (
    is_scuba_free_for_trip,
    is_discount_applicable_for_trip,
    can_do_advance_payment,
    get_scuba_cutoff_date,
    get_discount_cutoff_date,
    get_balance_payment_due_date,
    validate_settings_values,
)


class IsScubaFreeForTripTest(TestCase):
    def test_far_future_trip(self):
        future = date.today() + timedelta(days=60)
        self.assertTrue(is_scuba_free_for_trip(future, 30))

    def test_near_trip(self):
        near = date.today() + timedelta(days=5)
        self.assertFalse(is_scuba_free_for_trip(near, 30))

    def test_exact_limit(self):
        exact = date.today() + timedelta(days=30)
        self.assertTrue(is_scuba_free_for_trip(exact, 30))

    def test_none_date(self):
        self.assertFalse(is_scuba_free_for_trip(None, 30))

    def test_none_limit(self):
        future = date.today() + timedelta(days=60)
        self.assertFalse(is_scuba_free_for_trip(future, None))


class IsDiscountApplicableForTripTest(TestCase):
    def test_far_future(self):
        future = date.today() + timedelta(days=45)
        self.assertTrue(is_discount_applicable_for_trip(future, 20))

    def test_near_trip(self):
        near = date.today() + timedelta(days=5)
        self.assertFalse(is_discount_applicable_for_trip(near, 20))

    def test_none_date(self):
        self.assertFalse(is_discount_applicable_for_trip(None, 20))


class CanDoAdvancePaymentTest(TestCase):
    def test_far_trip(self):
        future = date.today() + timedelta(days=30)
        self.assertTrue(can_do_advance_payment(future, 10))

    def test_near_trip(self):
        near = date.today() + timedelta(days=3)
        self.assertFalse(can_do_advance_payment(near, 10))

    def test_exact_limit(self):
        exact = date.today() + timedelta(days=10)
        self.assertFalse(can_do_advance_payment(exact, 10))

    def test_none_date(self):
        self.assertFalse(can_do_advance_payment(None, 10))


class GetScubaCutoffDateTest(TestCase):
    def test_valid(self):
        start = date(2025, 8, 30)
        result = get_scuba_cutoff_date(start, 30)
        self.assertEqual(result, date(2025, 7, 31))

    def test_none_date(self):
        self.assertIsNone(get_scuba_cutoff_date(None, 30))

    def test_none_limit(self):
        self.assertIsNone(get_scuba_cutoff_date(date(2025, 8, 30), None))


class GetDiscountCutoffDateTest(TestCase):
    def test_valid(self):
        start = date(2025, 9, 15)
        result = get_discount_cutoff_date(start, 20)
        self.assertEqual(result, date(2025, 8, 26))

    def test_none(self):
        self.assertIsNone(get_discount_cutoff_date(None, 20))


class GetBalancePaymentDueDateTest(TestCase):
    def test_valid(self):
        start = date(2025, 10, 1)
        result = get_balance_payment_due_date(start, 7)
        self.assertEqual(result, date(2025, 9, 24))

    def test_none(self):
        self.assertIsNone(get_balance_payment_due_date(None, 7))


class ValidateSettingsValuesTest(TestCase):
    def test_valid_values(self):
        errors = validate_settings_values(30, 20, 7)
        self.assertEqual(errors, [])

    def test_negative_scuba(self):
        errors = validate_settings_values(-1, 20, 7)
        self.assertIn('scuba_limit_days cannot be negative', errors)

    def test_negative_discount(self):
        errors = validate_settings_values(30, -5, 7)
        self.assertIn('discount_limit_days cannot be negative', errors)

    def test_negative_balance(self):
        errors = validate_settings_values(30, 20, -3)
        self.assertIn('balance_payment_limit_days cannot be negative', errors)

    def test_scuba_less_than_discount(self):
        errors = validate_settings_values(10, 20, 7)
        self.assertIn('scuba_limit_days should be >= discount_limit_days', errors)

    def test_all_none(self):
        errors = validate_settings_values(None, None, None)
        self.assertEqual(errors, [])
