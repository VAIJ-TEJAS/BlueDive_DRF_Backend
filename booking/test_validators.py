from decimal import Decimal
from django.test import TestCase
from booking.validators import (
    validate_pax_records,
    validate_payment_data,
    validate_booking_status_transition,
)


class ValidatePaxRecordsTest(TestCase):
    def test_valid_records(self):
        records = [
            {
                'pax': 2,
                'customer_details': [
                    {'name': 'John', 'contact_number': '9876543210'},
                    {'name': 'Jane', 'contact_number': '9876543211'},
                ],
            }
        ]
        errors = validate_pax_records(records)
        self.assertEqual(errors, [])

    def test_empty_records(self):
        errors = validate_pax_records([])
        self.assertIn('At least one pax record is required', errors)

    def test_none_records(self):
        errors = validate_pax_records(None)
        self.assertIn('At least one pax record is required', errors)

    def test_missing_pax(self):
        records = [{'customer_details': [{'name': 'John', 'contact_number': '123'}]}]
        errors = validate_pax_records(records)
        self.assertTrue(any('Pax count is required' in e for e in errors))

    def test_zero_pax(self):
        records = [{'pax': 0, 'customer_details': [{'name': 'John', 'contact_number': '123'}]}]
        errors = validate_pax_records(records)
        self.assertTrue(any('positive integer' in e for e in errors))

    def test_negative_pax(self):
        records = [{'pax': -1, 'customer_details': [{'name': 'John', 'contact_number': '123'}]}]
        errors = validate_pax_records(records)
        self.assertTrue(any('positive integer' in e for e in errors))

    def test_missing_customer_details(self):
        records = [{'pax': 2}]
        errors = validate_pax_records(records)
        self.assertTrue(any('Customer details are required' in e for e in errors))

    def test_missing_name(self):
        records = [{'pax': 1, 'customer_details': [{'name': '', 'contact_number': '123'}]}]
        errors = validate_pax_records(records)
        self.assertTrue(any('Name is required' in e for e in errors))

    def test_missing_contact(self):
        records = [{'pax': 1, 'customer_details': [{'name': 'John', 'contact_number': ''}]}]
        errors = validate_pax_records(records)
        self.assertTrue(any('Contact number is required' in e for e in errors))

    def test_multiple_rooms(self):
        records = [
            {'pax': 2, 'customer_details': [
                {'name': 'A', 'contact_number': '111'},
                {'name': 'B', 'contact_number': '222'},
            ]},
            {'pax': 1, 'customer_details': [
                {'name': 'C', 'contact_number': '333'},
            ]},
        ]
        errors = validate_pax_records(records)
        self.assertEqual(errors, [])


class ValidatePaymentDataTest(TestCase):
    def test_valid_data(self):
        data = {
            'payment_id': 'pay_123',
            'order_id': 'order_456',
            'signature': 'sig_789',
            'amount': 5000,
        }
        errors = validate_payment_data(data)
        self.assertEqual(errors, [])

    def test_empty_data(self):
        errors = validate_payment_data({})
        self.assertTrue(len(errors) > 0)

    def test_none_data(self):
        errors = validate_payment_data(None)
        self.assertIn('Payment data is required', errors)

    def test_missing_payment_id(self):
        data = {'order_id': 'o', 'signature': 's', 'amount': 100}
        errors = validate_payment_data(data)
        self.assertIn('Payment ID is required', errors)

    def test_missing_order_id(self):
        data = {'payment_id': 'p', 'signature': 's', 'amount': 100}
        errors = validate_payment_data(data)
        self.assertIn('Order ID is required', errors)

    def test_missing_signature(self):
        data = {'payment_id': 'p', 'order_id': 'o', 'amount': 100}
        errors = validate_payment_data(data)
        self.assertIn('Payment signature is required', errors)

    def test_zero_amount(self):
        data = {'payment_id': 'p', 'order_id': 'o', 'signature': 's', 'amount': 0}
        errors = validate_payment_data(data)
        self.assertIn('Payment amount must be positive', errors)

    def test_negative_amount(self):
        data = {'payment_id': 'p', 'order_id': 'o', 'signature': 's', 'amount': -100}
        errors = validate_payment_data(data)
        self.assertIn('Payment amount must be positive', errors)

    def test_decimal_amount(self):
        data = {'payment_id': 'p', 'order_id': 'o', 'signature': 's', 'amount': Decimal('500.50')}
        errors = validate_payment_data(data)
        self.assertEqual(errors, [])


class ValidateBookingStatusTransitionTest(TestCase):
    def test_partial_to_confirmed(self):
        valid, msg = validate_booking_status_transition('Partially Confirmed', 'Confirmed')
        self.assertTrue(valid)

    def test_partial_to_cancelled(self):
        valid, msg = validate_booking_status_transition('Partially Confirmed', 'Cancelled')
        self.assertTrue(valid)

    def test_confirmed_to_cancelled(self):
        valid, msg = validate_booking_status_transition('Confirmed', 'Cancelled')
        self.assertTrue(valid)

    def test_cancelled_to_confirmed(self):
        valid, msg = validate_booking_status_transition('Cancelled', 'Confirmed')
        self.assertFalse(valid)
        self.assertIn('Cannot transition', msg)

    def test_confirmed_to_partial(self):
        valid, msg = validate_booking_status_transition('Confirmed', 'Partially Confirmed')
        self.assertFalse(valid)

    def test_cancelled_to_cancelled(self):
        valid, msg = validate_booking_status_transition('Cancelled', 'Cancelled')
        self.assertFalse(valid)
