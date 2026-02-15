from datetime import datetime, timedelta
from django.test import TestCase
from booking.helpers import (
    format_booking_id,
    get_booking_status_color,
    get_booking_status_icon,
    is_recent_booking,
)


class FormatBookingIdTest(TestCase):
    def test_valid_id(self):
        self.assertEqual(format_booking_id(123), '#123')

    def test_zero_id(self):
        self.assertEqual(format_booking_id(0), '#0')

    def test_none_id(self):
        self.assertEqual(format_booking_id(None), 'N/A')

    def test_empty_id(self):
        self.assertEqual(format_booking_id(''), 'N/A')


class GetBookingStatusColorTest(TestCase):
    def test_partially_confirmed(self):
        self.assertEqual(get_booking_status_color('Partially Confirmed'), 'warning')

    def test_confirmed(self):
        self.assertEqual(get_booking_status_color('Confirmed'), 'success')

    def test_cancelled(self):
        self.assertEqual(get_booking_status_color('Cancelled'), 'danger')

    def test_unknown_status(self):
        self.assertEqual(get_booking_status_color('Random'), 'secondary')


class GetBookingStatusIconTest(TestCase):
    def test_partially_confirmed(self):
        self.assertEqual(get_booking_status_icon('Partially Confirmed'), 'clock')

    def test_confirmed(self):
        self.assertEqual(get_booking_status_icon('Confirmed'), 'check-circle')

    def test_cancelled(self):
        self.assertEqual(get_booking_status_icon('Cancelled'), 'x-circle')

    def test_unknown_status(self):
        self.assertEqual(get_booking_status_icon('Random'), 'question-circle')


class IsRecentBookingTest(TestCase):
    def test_today(self):
        self.assertTrue(is_recent_booking(datetime.now()))

    def test_yesterday(self):
        self.assertTrue(is_recent_booking(datetime.now() - timedelta(days=1)))

    def test_week_ago(self):
        self.assertTrue(is_recent_booking(datetime.now() - timedelta(days=7)))

    def test_week_and_one_day(self):
        self.assertFalse(is_recent_booking(datetime.now() - timedelta(days=8)))

    def test_none_date(self):
        self.assertFalse(is_recent_booking(None))

    def test_custom_days(self):
        self.assertTrue(is_recent_booking(datetime.now() - timedelta(days=2), days=3))
        self.assertFalse(is_recent_booking(datetime.now() - timedelta(days=4), days=3))
