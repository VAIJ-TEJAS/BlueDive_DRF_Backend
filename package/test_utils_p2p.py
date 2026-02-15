from django.test import TestCase
from package.utils import (
    calculate_meal_cost,
    get_package_display_price,
    format_duration,
    get_pax_discount,
)


class CalculateMealCostExtraTest(TestCase):
    def test_zero_price(self):
        self.assertEqual(calculate_meal_cost(0, 0, True), 0)

    def test_large_price(self):
        self.assertEqual(calculate_meal_cost(50000, 40000, True), 40000)

    def test_discount_not_applicable_with_discounted(self):
        self.assertEqual(calculate_meal_cost(5000, 3000, False), 5000)


class GetPackageDisplayPriceExtraTest(TestCase):
    def test_fifty_percent(self):
        self.assertEqual(get_package_display_price(10000, 50), 5000)

    def test_hundred_percent(self):
        self.assertEqual(get_package_display_price(10000, 100), 0)

    def test_small_discount(self):
        self.assertEqual(get_package_display_price(10000, 5), 9500)


class FormatDurationExtraTest(TestCase):
    def test_lowercase_input(self):
        result = format_duration('3 days / 2 nights')
        self.assertEqual(result['days'], 3)
        self.assertEqual(result['nights'], 2)

    def test_no_spaces(self):
        result = format_duration('2days')
        self.assertEqual(result['days'], 2)

    def test_large_numbers(self):
        result = format_duration('14 Days / 13 Nights')
        self.assertEqual(result['days'], 14)
        self.assertEqual(result['nights'], 13)
        self.assertEqual(result['display'], '14 Days / 13 Nights')


class GetPaxDiscountExtraTest(TestCase):
    def test_first_option(self):
        options = [{'pax': 1, 'discount': 0}, {'pax': 2, 'discount': 10}]
        self.assertEqual(get_pax_discount(options, 1), 0)

    def test_large_discount(self):
        options = [{'pax': 4, 'discount': 25}]
        self.assertEqual(get_pax_discount(options, 4), 25)
