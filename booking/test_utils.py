from decimal import Decimal
from django.test import TestCase
from booking.utils import (
    calculate_total_cost,
    calculate_discounted_cost,
    calculate_advance_cost,
    count_total_customers,
    count_total_rooms,
    get_status_label,
    is_booking_cancellable,
    calculate_balance,
)


class CalculateTotalCostTest(TestCase):
    def test_single_record(self):
        records = [{'customer_details': [{'package_cost': 5000}]}]
        self.assertEqual(calculate_total_cost(records), Decimal('5000'))

    def test_multiple_records(self):
        records = [
            {'customer_details': [
                {'package_cost': 3000},
                {'package_cost': 4000},
            ]},
            {'customer_details': [
                {'package_cost': 3500},
            ]},
        ]
        self.assertEqual(calculate_total_cost(records), Decimal('10500'))

    def test_empty_records(self):
        self.assertEqual(calculate_total_cost([]), Decimal('0.00'))

    def test_missing_cost_field(self):
        records = [{'customer_details': [{'name': 'Test'}]}]
        self.assertEqual(calculate_total_cost(records), Decimal('0'))

    def test_zero_cost(self):
        records = [{'customer_details': [{'package_cost': 0}]}]
        self.assertEqual(calculate_total_cost(records), Decimal('0'))


class CalculateDiscountedCostTest(TestCase):
    def test_single_record(self):
        records = [{'customer_details': [{'discounted_package_cost': 4000}]}]
        self.assertEqual(calculate_discounted_cost(records), Decimal('4000'))

    def test_multiple_records(self):
        records = [
            {'customer_details': [
                {'discounted_package_cost': 2500},
                {'discounted_package_cost': 3500},
            ]},
        ]
        self.assertEqual(calculate_discounted_cost(records), Decimal('6000'))

    def test_empty_records(self):
        self.assertEqual(calculate_discounted_cost([]), Decimal('0.00'))


class CalculateAdvanceCostTest(TestCase):
    def test_default_advance(self):
        records = [{'pax': 2}, {'pax': 3}]
        self.assertEqual(calculate_advance_cost(records), 12500)

    def test_custom_advance(self):
        records = [{'pax': 2}]
        self.assertEqual(calculate_advance_cost(records, advance_per_pax=2000), 4000)

    def test_empty_records(self):
        self.assertEqual(calculate_advance_cost([]), 0)

    def test_single_pax(self):
        records = [{'pax': 1}]
        self.assertEqual(calculate_advance_cost(records), 2500)


class CountTotalCustomersTest(TestCase):
    def test_counts_customers(self):
        records = [
            {'customer_details': [{'name': 'A'}, {'name': 'B'}]},
            {'customer_details': [{'name': 'C'}]},
        ]
        self.assertEqual(count_total_customers(records), 3)

    def test_empty_records(self):
        self.assertEqual(count_total_customers([]), 0)

    def test_no_customer_details(self):
        records = [{'pax': 1}]
        self.assertEqual(count_total_customers(records), 0)


class CountTotalRoomsTest(TestCase):
    def test_counts_rooms(self):
        records = [{'pax': 2}, {'pax': 3}, {'pax': 1}]
        self.assertEqual(count_total_rooms(records), 3)

    def test_empty(self):
        self.assertEqual(count_total_rooms([]), 0)


class GetStatusLabelTest(TestCase):
    def test_confirmed(self):
        self.assertEqual(get_status_label('Confirmed'), 'Booking Confirmed')

    def test_partially_confirmed(self):
        self.assertEqual(get_status_label('Partially Confirmed'), 'Awaiting Full Payment')

    def test_cancelled(self):
        self.assertEqual(get_status_label('Cancelled'), 'Booking Cancelled')

    def test_unknown(self):
        self.assertEqual(get_status_label('SomeOtherStatus'), 'Unknown Status')


class IsBookingCancellableTest(TestCase):
    def test_confirmed_is_cancellable(self):
        self.assertTrue(is_booking_cancellable('Confirmed'))

    def test_partially_confirmed_is_cancellable(self):
        self.assertTrue(is_booking_cancellable('Partially Confirmed'))

    def test_cancelled_is_not_cancellable(self):
        self.assertFalse(is_booking_cancellable('Cancelled'))


class CalculateBalanceTest(TestCase):
    def test_positive_balance(self):
        self.assertEqual(calculate_balance(10000, 5000), Decimal('5000'))

    def test_zero_balance(self):
        self.assertEqual(calculate_balance(5000, 5000), Decimal('0.00'))

    def test_negative_prevented(self):
        self.assertEqual(calculate_balance(3000, 5000), Decimal('0.00'))

    def test_decimal_values(self):
        self.assertEqual(calculate_balance(10000.50, 2500), Decimal('7500.50'))
