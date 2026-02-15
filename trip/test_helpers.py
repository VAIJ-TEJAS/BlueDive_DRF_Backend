from datetime import date, timedelta
from django.test import TestCase
from trip.helpers import (
    format_trip_name,
    get_trip_progress_percentage,
    get_trip_capacity_status,
    get_trip_duration_display,
)


class FormatTripNameTest(TestCase):
    def test_with_package(self):
        from package.models import Package
        from trip.models import Trip
        
        package = Package.objects.create(name='Konkan Trip')
        trip = Trip.objects.create(
            package=package,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3)
        )
        
        result = format_trip_name(trip)
        self.assertIn('Konkan Trip', result)
        self.assertIn(str(date.today()), result)

    def test_none_trip(self):
        self.assertEqual(format_trip_name(None), 'Unknown Trip')

    def test_trip_without_package(self):
        trip = type('Trip', (), {'package': None})()
        self.assertEqual(format_trip_name(trip), 'Unknown Trip')


class GetTripProgressPercentageTest(TestCase):
    def test_future_trip(self):
        future = date.today() + timedelta(days=10)
        end = date.today() + timedelta(days=13)
        self.assertEqual(get_trip_progress_percentage(future, end), 0)

    def test_past_trip(self):
        start = date.today() - timedelta(days=10)
        end = date.today() - timedelta(days=7)
        self.assertEqual(get_trip_progress_percentage(start, end), 100)

    def test_ongoing_trip(self):
        start = date.today() - timedelta(days=2)
        end = date.today() + timedelta(days=2)
        result = get_trip_progress_percentage(start, end)
        self.assertTrue(0 < result < 100)

    def test_none_dates(self):
        self.assertEqual(get_trip_progress_percentage(None, None), 0)


class GetTripCapacityStatusTest(TestCase):
    def test_plenty_seats(self):
        self.assertEqual(get_trip_capacity_status(15), 'plenty')

    def test_limited_seats(self):
        self.assertEqual(get_trip_capacity_status(8), 'limited')

    def test_critical_seats(self):
        self.assertEqual(get_trip_capacity_status(3), 'critical')

    def test_no_seats(self):
        self.assertEqual(get_trip_capacity_status(0), 'critical')

    def test_none_seats(self):
        self.assertEqual(get_trip_capacity_status(None), 'unknown')


class GetTripDurationDisplayTest(TestCase):
    def test_one_day(self):
        start = date.today()
        end = date.today()
        self.assertEqual(get_trip_duration_display(start, end), '1 Day')

    def test_two_days(self):
        start = date.today()
        end = date.today() + timedelta(days=1)
        self.assertEqual(get_trip_duration_display(start, end), '2 Days')

    def test_three_days(self):
        start = date.today()
        end = date.today() + timedelta(days=2)
        self.assertEqual(get_trip_duration_display(start, end), '3 Days')

    def test_many_days(self):
        start = date.today()
        end = date.today() + timedelta(days=10)
        self.assertEqual(get_trip_duration_display(start, end), '10 Days')

    def test_none_dates(self):
        self.assertEqual(get_trip_duration_display(None, None), 'Unknown')
