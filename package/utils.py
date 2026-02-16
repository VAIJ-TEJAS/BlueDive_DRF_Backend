from decimal import Decimal


def calculate_meal_cost(price, discounted_price, is_discount_applicable):
    """Return the appropriate meal cost based on discount applicability."""
    if is_discount_applicable and discounted_price is not None:
        return discounted_price
    return price or 0


def get_package_display_price(display_price, display_discount_percentage):
    """Calculate the effective display price after discount."""
    if not display_price:
        return 0
    if not display_discount_percentage or display_discount_percentage <= 0:
        return display_price
    # Ensure discount percentage is reasonable (not over 100%)
    if display_discount_percentage > 100:
        return 0
    discount = Decimal(str(display_price)) * Decimal(str(display_discount_percentage)) / 100
    return int(Decimal(str(display_price)) - discount)


def format_duration(duration_str):
    """Parse and normalize a duration string like '3 Days / 2 Nights'."""
    if not duration_str:
        return {'days': 0, 'nights': 0, 'display': ''}
    import re
    day_match = re.search(r'(\d+)\s*(?:day|days)', duration_str, re.IGNORECASE)
    night_match = re.search(r'(\d+)\s*(?:night|nights)', duration_str, re.IGNORECASE)
    days = int(day_match.group(1)) if day_match else 0
    nights = int(night_match.group(1)) if night_match else 0

    parts = []
    if days:
        parts.append(f"{days} Day{'s' if days != 1 else ''}")
    if nights:
        parts.append(f"{nights} Night{'s' if nights != 1 else ''}")

    return {
        'days': days,
        'nights': nights,
        'display': ' / '.join(parts),
    }


def get_pax_discount(pax_options, pax_count):
    """Find the discount percentage for a given pax count from pax options list."""
    if not pax_options:
        return 0
    for option in pax_options:
        if option.get('pax') == pax_count:
            return option.get('discount', 0) or 0
    return 0
