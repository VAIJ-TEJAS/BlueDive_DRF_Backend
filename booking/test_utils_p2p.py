from decimal import Decimal
from django.test import TestCase
from booking.utils import (
    calculate_total_cost,
    calculate_discounted_cost,
    calculate_advance_cost,
    count_total_customers,
    get_status_label,
    is_booking_cancellable,
    calculate_balance,
)


class CalculateTotalCostExtraTest(TestCase):
    def test_large_number_of_records(self):
        records = [{'customer_details': [{'package_cost': 1000}]} for _ in range(10)]
        self.assertEqual(calculate_total_cost(records), Decimal('10000'))

    def test_mixed_costs(self):
        records = [{'customer_details': [
            {'package_cost': 3500},
            {'package_cost': 4500},
        ]}]
        self.assertEqual(calculate_total_cost(records), Decimal('8000'))


class CalculateDiscountedCostExtraTest(TestCase):
    def test_large_discount(self):
        records = [{'customer_details': [
            {'discounted_package_cost': 100},
            {'discounted_package_cost': 200},
        ]}]
        self.assertEqual(calculate_discounted_cost(records), Decimal('300'))


class CalculateAdvanceCostExtraTest(TestCase):
    def test_many_rooms(self):
        records = [{'pax': 4}, {'pax': 4}, {'pax': 4}]
        self.assertEqual(calculate_advance_cost(records), 30000)

    def test_zero_pax(self):
        records = [{'pax': 0}]
        self.assertEqual(calculate_advance_cost(records), 0)


class CountTotalCustomersExtraTest(TestCase):
    def test_multiple_rooms_multiple_customers(self):
        records = [
            {'customer_details': [{'name': 'A'}, {'name': 'B'}, {'name': 'C'}]},
            {'customer_details': [{'name': 'D'}, {'name': 'E'}]},
        ]
        self.assertEqual(count_total_customers(records), 5)


class GetStatusLabelExtraTest(TestCase):
    def test_empty_string(self):
        self.assertEqual(get_status_label(''), 'Unknown Status')


class IsBookingCancellableExtraTest(TestCase):
    def test_empty_status(self):
        self.assertTrue(is_booking_cancellable(''))


class CalculateBalanceExtraTest(TestCase):
    def test_large_amounts(self):
        self.assertEqual(calculate_balance(100000, 25000), Decimal('75000'))

    def test_float_inputs(self):
        result = calculate_balance(7500.75, 2500.25)
        self.assertEqual(result, Decimal('5000.50'))
