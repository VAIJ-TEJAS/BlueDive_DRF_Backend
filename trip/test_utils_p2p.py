from datetime import date, timedelta
from django.test import TestCase
from trip.utils import (
    get_days_until_trip,
    is_trip_upcoming,
    is_trip_bookable,
    get_trip_status_label,
    format_date_range,
    get_trip_duration_days,
    has_enough_seats,
    has_enough_rooms,
)


class GetDaysUntilTripExtraTest(TestCase):
    def test_far_future(self):
        future = date.today() + timedelta(days=365)
        self.assertEqual(get_days_until_trip(future), 365)

    def test_yesterday(self):
        yesterday = date.today() - timedelta(days=1)
        self.assertEqual(get_days_until_trip(yesterday), -1)


class IsTripUpcomingExtraTest(TestCase):
    def test_far_future(self):
        future = date.today() + timedelta(days=180)
        self.assertTrue(is_trip_upcoming(future))

    def test_tomorrow(self):
        tomorrow = date.today() + timedelta(days=1)
        self.assertTrue(is_trip_upcoming(tomorrow))


class IsTripBookableExtraTest(TestCase):
    def test_omitted_with_seats(self):
        self.assertFalse(is_trip_bookable('Omitted', 10))

    def test_scheduled_with_one_seat(self):
        self.assertTrue(is_trip_bookable('Scheduled', 1))


class GetTripStatusLabelExtraTest(TestCase):
    def test_all_known_statuses(self):
        expected = {
            'Scheduled': 'Upcoming',
            'Ongoing': 'In Progress',
            'Completed': 'Finished',
            'Cancelled': 'Cancelled',
            'Omitted': 'Skipped',
        }
        for status_val, label in expected.items():
            self.assertEqual(get_trip_status_label(status_val), label)


class FormatDateRangeExtraTest(TestCase):
    def test_same_month(self):
        start = date(2025, 6, 10)
        end = date(2025, 6, 15)
        result = format_date_range(start, end)
        self.assertIn('Jun', result)

    def test_cross_month(self):
        start = date(2025, 6, 28)
        end = date(2025, 7, 2)
        result = format_date_range(start, end)
        self.assertIn('Jun', result)
        self.assertIn('Jul', result)


class GetTripDurationDaysExtraTest(TestCase):
    def test_week_trip(self):
        start = date(2025, 1, 1)
        end = date(2025, 1, 8)
        self.assertEqual(get_trip_duration_days(start, end), 7)

    def test_end_before_start(self):
        start = date(2025, 1, 10)
        end = date(2025, 1, 5)
        self.assertEqual(get_trip_duration_days(start, end), 0)


class HasEnoughSeatsExtraTest(TestCase):
    def test_large_group(self):
        self.assertTrue(has_enough_seats(100, 50))

    def test_zero_requested(self):
        self.assertTrue(has_enough_seats(10, 0))


class HasEnoughRoomsExtraTest(TestCase):
    def test_single_room(self):
        self.assertTrue(has_enough_rooms(1, 1))

    def test_zero_requested(self):
        self.assertTrue(has_enough_rooms(5, 0))
