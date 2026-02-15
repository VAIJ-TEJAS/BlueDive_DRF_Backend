from django.test import TestCase
from package.utils import (
    calculate_meal_cost,
    get_package_display_price,
    format_duration,
    get_pax_discount,
)


class CalculateMealCostTest(TestCase):
    def test_discounted_price(self):
        self.assertEqual(calculate_meal_cost(5000, 4000, True), 4000)

    def test_regular_price(self):
        self.assertEqual(calculate_meal_cost(5000, 4000, False), 5000)

    def test_no_discounted_price(self):
        self.assertEqual(calculate_meal_cost(5000, None, True), 5000)

    def test_no_price(self):
        self.assertEqual(calculate_meal_cost(None, None, False), 0)


class GetPackageDisplayPriceTest(TestCase):
    def test_with_discount(self):
        self.assertEqual(get_package_display_price(10000, 20), 8000)

    def test_no_discount(self):
        self.assertEqual(get_package_display_price(10000, 0), 10000)

    def test_no_price(self):
        self.assertEqual(get_package_display_price(None, 20), 0)

    def test_none_discount(self):
        self.assertEqual(get_package_display_price(5000, None), 5000)

    def test_negative_discount(self):
        self.assertEqual(get_package_display_price(5000, -10), 5000)


class FormatDurationTest(TestCase):
    def test_days_and_nights(self):
        result = format_duration('3 Days / 2 Nights')
        self.assertEqual(result['days'], 3)
        self.assertEqual(result['nights'], 2)
        self.assertEqual(result['display'], '3 Days / 2 Nights')

    def test_days_only(self):
        result = format_duration('2 Days')
        self.assertEqual(result['days'], 2)
        self.assertEqual(result['nights'], 0)
        self.assertEqual(result['display'], '2 Days')

    def test_single_day(self):
        result = format_duration('1 Day')
        self.assertEqual(result['days'], 1)
        self.assertEqual(result['display'], '1 Day')

    def test_empty_string(self):
        result = format_duration('')
        self.assertEqual(result['days'], 0)
        self.assertEqual(result['nights'], 0)
        self.assertEqual(result['display'], '')

    def test_none(self):
        result = format_duration(None)
        self.assertEqual(result['display'], '')

    def test_single_night(self):
        result = format_duration('1 Night')
        self.assertEqual(result['nights'], 1)
        self.assertEqual(result['display'], '1 Night')


class GetPaxDiscountTest(TestCase):
    def test_matching_pax(self):
        options = [{'pax': 2, 'discount': 10}, {'pax': 3, 'discount': 15}]
        self.assertEqual(get_pax_discount(options, 3), 15)

    def test_no_match(self):
        options = [{'pax': 2, 'discount': 10}]
        self.assertEqual(get_pax_discount(options, 5), 0)

    def test_empty_options(self):
        self.assertEqual(get_pax_discount([], 2), 0)

    def test_none_options(self):
        self.assertEqual(get_pax_discount(None, 2), 0)

    def test_none_discount_value(self):
        options = [{'pax': 2, 'discount': None}]
        self.assertEqual(get_pax_discount(options, 2), 0)
