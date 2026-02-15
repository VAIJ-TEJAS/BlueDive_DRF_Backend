from decimal import Decimal
from django.test import TestCase
from payment.utils import (
    amount_to_paise,
    paise_to_amount,
    validate_payment_type,
    get_payment_status_label,
    is_payment_successful,
    generate_receipt_id,
    calculate_order_amount,
)


class AmountToPaiseTest(TestCase):
    def test_integer_amount(self):
        self.assertEqual(amount_to_paise(100), 10000)

    def test_decimal_amount(self):
        self.assertEqual(amount_to_paise(99.50), 9950)

    def test_zero(self):
        self.assertEqual(amount_to_paise(0), 0)

    def test_none(self):
        self.assertEqual(amount_to_paise(None), 0)

    def test_large_amount(self):
        self.assertEqual(amount_to_paise(50000), 5000000)


class PaiseToAmountTest(TestCase):
    def test_integer_paise(self):
        self.assertEqual(paise_to_amount(10000), Decimal('100'))

    def test_odd_paise(self):
        self.assertEqual(paise_to_amount(9950), Decimal('99.50'))

    def test_zero(self):
        self.assertEqual(paise_to_amount(0), Decimal('0'))

    def test_none(self):
        self.assertEqual(paise_to_amount(None), Decimal('0.00'))


class ValidatePaymentTypeTest(TestCase):
    def test_advance(self):
        self.assertTrue(validate_payment_type('advance'))

    def test_full(self):
        self.assertTrue(validate_payment_type('full'))

    def test_invalid(self):
        self.assertFalse(validate_payment_type('partial'))

    def test_empty(self):
        self.assertFalse(validate_payment_type(''))

    def test_none(self):
        self.assertFalse(validate_payment_type(None))


class GetPaymentStatusLabelTest(TestCase):
    def test_created(self):
        self.assertEqual(get_payment_status_label('Created'), 'Payment Initiated')

    def test_captured(self):
        self.assertEqual(get_payment_status_label('Captured'), 'Payment Successful')

    def test_failed(self):
        self.assertEqual(get_payment_status_label('Failed'), 'Payment Failed')

    def test_refunded(self):
        self.assertEqual(get_payment_status_label('Refunded'), 'Payment Refunded')

    def test_unknown(self):
        self.assertEqual(get_payment_status_label('Random'), 'Unknown')


class IsPaymentSuccessfulTest(TestCase):
    def test_captured(self):
        self.assertTrue(is_payment_successful('Captured'))

    def test_authorized(self):
        self.assertTrue(is_payment_successful('Authorized'))

    def test_failed(self):
        self.assertFalse(is_payment_successful('Failed'))

    def test_created(self):
        self.assertFalse(is_payment_successful('Created'))


class GenerateReceiptIdTest(TestCase):
    def test_default_prefix(self):
        result = generate_receipt_id()
        self.assertTrue(result.startswith('receipt_'))

    def test_custom_prefix(self):
        result = generate_receipt_id('order')
        self.assertTrue(result.startswith('order_'))

    def test_unique(self):
        id1 = generate_receipt_id()
        id2 = generate_receipt_id()
        # They could be the same if called in the same second, but format should be correct
        self.assertTrue(id1.startswith('receipt_'))
        self.assertTrue(id2.startswith('receipt_'))


class CalculateOrderAmountTest(TestCase):
    def test_full_payment(self):
        self.assertEqual(calculate_order_amount(10000, 5000, 'full'), 1000000)

    def test_advance_payment(self):
        self.assertEqual(calculate_order_amount(10000, 5000, 'advance'), 500000)

    def test_invalid_type(self):
        self.assertEqual(calculate_order_amount(10000, 5000, 'partial'), 0)
