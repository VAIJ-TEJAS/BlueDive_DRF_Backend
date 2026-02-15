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


class GetDaysUntilTripTest(TestCase):
    def test_future_trip(self):
        future = date.today() + timedelta(days=10)
        self.assertEqual(get_days_until_trip(future), 10)

    def test_past_trip(self):
        past = date.today() - timedelta(days=5)
        self.assertEqual(get_days_until_trip(past), -5)

    def test_today(self):
        self.assertEqual(get_days_until_trip(date.today()), 0)

    def test_none(self):
        self.assertEqual(get_days_until_trip(None), 0)


class IsTripUpcomingTest(TestCase):
    def test_future_date(self):
        future = date.today() + timedelta(days=30)
        self.assertTrue(is_trip_upcoming(future))

    def test_past_date(self):
        past = date.today() - timedelta(days=1)
        self.assertFalse(is_trip_upcoming(past))

    def test_today(self):
        self.assertFalse(is_trip_upcoming(date.today()))

    def test_none(self):
        self.assertFalse(is_trip_upcoming(None))


class IsTripBookableTest(TestCase):
    def test_scheduled_with_seats(self):
        self.assertTrue(is_trip_bookable('Scheduled', 10))

    def test_scheduled_no_seats(self):
        self.assertFalse(is_trip_bookable('Scheduled', 0))

    def test_completed_with_seats(self):
        self.assertFalse(is_trip_bookable('Completed', 10))

    def test_cancelled(self):
        self.assertFalse(is_trip_bookable('Cancelled', 5))

    def test_ongoing(self):
        self.assertFalse(is_trip_bookable('Ongoing', 5))


class GetTripStatusLabelTest(TestCase):
    def test_scheduled(self):
        self.assertEqual(get_trip_status_label('Scheduled'), 'Upcoming')

    def test_ongoing(self):
        self.assertEqual(get_trip_status_label('Ongoing'), 'In Progress')

    def test_completed(self):
        self.assertEqual(get_trip_status_label('Completed'), 'Finished')

    def test_cancelled(self):
        self.assertEqual(get_trip_status_label('Cancelled'), 'Cancelled')

    def test_omitted(self):
        self.assertEqual(get_trip_status_label('Omitted'), 'Skipped')

    def test_unknown(self):
        self.assertEqual(get_trip_status_label('Random'), 'Unknown')


class FormatDateRangeTest(TestCase):
    def test_valid_range(self):
        start = date(2024, 8, 1)
        end = date(2024, 8, 5)
        result = format_date_range(start, end)
        self.assertIn('01 Aug', result)
        self.assertIn('05 Aug 2024', result)

    def test_none_start(self):
        self.assertEqual(format_date_range(None, date(2024, 8, 5)), '')

    def test_none_end(self):
        self.assertEqual(format_date_range(date(2024, 8, 1), None), '')

    def test_both_none(self):
        self.assertEqual(format_date_range(None, None), '')


class GetTripDurationDaysTest(TestCase):
    def test_multi_day(self):
        start = date(2024, 8, 1)
        end = date(2024, 8, 4)
        self.assertEqual(get_trip_duration_days(start, end), 3)

    def test_same_day(self):
        d = date(2024, 8, 1)
        self.assertEqual(get_trip_duration_days(d, d), 0)

    def test_none_values(self):
        self.assertEqual(get_trip_duration_days(None, None), 0)

    def test_single_day(self):
        start = date(2024, 8, 1)
        end = date(2024, 8, 2)
        self.assertEqual(get_trip_duration_days(start, end), 1)


class HasEnoughSeatsTest(TestCase):
    def test_enough(self):
        self.assertTrue(has_enough_seats(10, 5))

    def test_exact(self):
        self.assertTrue(has_enough_seats(5, 5))

    def test_not_enough(self):
        self.assertFalse(has_enough_seats(3, 5))

    def test_zero_available(self):
        self.assertFalse(has_enough_seats(0, 1))


class HasEnoughRoomsTest(TestCase):
    def test_enough(self):
        self.assertTrue(has_enough_rooms(6, 3))

    def test_exact(self):
        self.assertTrue(has_enough_rooms(3, 3))

    def test_not_enough(self):
        self.assertFalse(has_enough_rooms(2, 4))
