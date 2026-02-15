from django.test import TestCase
from booking.fields import (
    BookingStatusField,
    PaxCountField,
    CurrencyField,
    PhoneNumberField,
)


class BookingStatusFieldTest(TestCase):
    def test_partially_confirmed(self):
        field = BookingStatusField()
        self.assertEqual(field.to_representation('Partially Confirmed'), 'Pending')

    def test_confirmed(self):
        field = BookingStatusField()
        self.assertEqual(field.to_representation('Confirmed'), 'Confirmed')

    def test_cancelled(self):
        field = BookingStatusField()
        self.assertEqual(field.to_representation('Cancelled'), 'Cancelled')

    def test_unknown_status(self):
        field = BookingStatusField()
        self.assertEqual(field.to_representation('Random'), 'Random')


class PaxCountFieldTest(TestCase):
    def test_one_person(self):
        field = PaxCountField()
        self.assertEqual(field.to_representation(1), '1 Person')

    def test_multiple_persons(self):
        field = PaxCountField()
        self.assertEqual(field.to_representation(3), '3 Persons')

    def test_zero_persons(self):
        field = PaxCountField()
        self.assertEqual(field.to_representation(0), '0 Persons')


class CurrencyFieldTest(TestCase):
    def test_positive_amount(self):
        from decimal import Decimal
        field = CurrencyField()
        self.assertEqual(field.to_representation(Decimal('5000.50')), '₹5,000.50')

    def test_zero_amount(self):
        from decimal import Decimal
        field = CurrencyField()
        self.assertEqual(field.to_representation(Decimal('0')), '₹0.00')

    def test_none_amount(self):
        field = CurrencyField()
        self.assertEqual(field.to_representation(None), '₹0.00')

    def test_large_amount(self):
        from decimal import Decimal
        field = CurrencyField()
        self.assertEqual(field.to_representation(Decimal('100000')), '₹100,000.00')


class PhoneNumberFieldTest(TestCase):
    def test_10_digit_number(self):
        field = PhoneNumberField()
        self.assertEqual(field.to_representation('9876543210'), '+91 98765 32110')

    def test_with_country_code(self):
        field = PhoneNumberField()
        self.assertEqual(field.to_representation('+919876543210'), '+91 98765 43210')

    def test_short_number(self):
        field = PhoneNumberField()
        self.assertEqual(field.to_representation('12345'), '12345')

    def test_empty_number(self):
        field = PhoneNumberField()
        self.assertEqual(field.to_representation(''), '')

    def test_none_number(self):
        field = PhoneNumberField()
        self.assertEqual(field.to_representation(None), None)
