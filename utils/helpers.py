"""
Utility helper functions for formatting, validation, and calculations.

This module provides reusable functions for common operations including:
- Price formatting and currency handling
- Date/time manipulation and formatting
- Data validation
- Mathematical calculations
"""

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
import re
from typing import Union, Optional, List, Tuple


# ============================================================================
# PRICE FORMATTING FUNCTIONS
# ============================================================================

def format_price(amount: Union[float, int, Decimal], currency: str = "USD", 
                 decimal_places: int = 2) -> str:
    """
    Format a price value with currency symbol and proper decimal places.
    
    Args:
        amount: The price amount to format
        currency: Currency code (USD, EUR, GBP, etc.) - default: USD
        decimal_places: Number of decimal places - default: 2
    
    Returns:
        Formatted price string with currency symbol
    
    Example:
        >>> format_price(1234.5)
        '$1,234.50'
        >>> format_price(1234.5, 'EUR', 2)
        '€1,234.50'
    """
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CHF': 'Fr',
        'CAD': 'C$',
        'AUD': 'A$',
        'CNY': '¥',
    }
    
    symbol = currency_symbols.get(currency.upper(), currency)
    
    try:
        amount = Decimal(str(amount))
        formatted = f"{amount:,.{decimal_places}f}"
        return f"{symbol}{formatted}"
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid price amount: {amount}")


def parse_price(price_string: str) -> float:
    """
    Parse a formatted price string and return the numeric value.
    
    Args:
        price_string: String containing price (e.g., '$1,234.50', '€100.00')
    
    Returns:
        Float value of the price
    
    Example:
        >>> parse_price('$1,234.50')
        1234.5
        >>> parse_price('€100.00')
        100.0
    """
    # Remove currency symbols and commas
    cleaned = re.sub(r'[^\d.-]', '', price_string)
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(f"Cannot parse price: {price_string}")


def calculate_discount(original_price: Union[float, int], 
                      discount_percent: Union[float, int]) -> dict:
    """
    Calculate discount amount and final price.
    
    Args:
        original_price: Original price before discount
        discount_percent: Discount percentage (0-100)
    
    Returns:
        Dictionary with original, discount_amount, and final_price
    
    Example:
        >>> calculate_discount(100, 20)
        {'original_price': 100, 'discount_amount': 20.0, 'final_price': 80.0}
    """
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount percent must be between 0 and 100")
    
    discount_amount = Decimal(str(original_price)) * Decimal(str(discount_percent)) / 100
    final_price = Decimal(str(original_price)) - discount_amount
    
    return {
        'original_price': float(original_price),
        'discount_amount': float(discount_amount),
        'discount_percent': discount_percent,
        'final_price': float(final_price)
    }


def calculate_tax(amount: Union[float, int], tax_rate: Union[float, int]) -> dict:
    """
    Calculate tax on an amount.
    
    Args:
        amount: Base amount
        tax_rate: Tax rate as percentage (e.g., 10 for 10%)
    
    Returns:
        Dictionary with amount, tax, and total
    
    Example:
        >>> calculate_tax(100, 10)
        {'base_amount': 100, 'tax_amount': 10.0, 'total': 110.0}
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")
    
    amount_decimal = Decimal(str(amount))
    tax_amount = amount_decimal * Decimal(str(tax_rate)) / 100
    
    return {
        'base_amount': float(amount),
        'tax_amount': float(tax_amount),
        'tax_rate': tax_rate,
        'total': float(amount_decimal + tax_amount)
    }


# ============================================================================
# DATE/TIME FORMATTING FUNCTIONS
# ============================================================================

def format_date(date_obj: Union[datetime, str], 
                date_format: str = "%Y-%m-%d") -> str:
    """
    Format a datetime object or string to a specified format.
    
    Args:
        date_obj: datetime object or string
        date_format: Desired output format - default: YYYY-MM-DD
    
    Returns:
        Formatted date string
    
    Example:
        >>> format_date(datetime(2026, 1, 8), "%B %d, %Y")
        'January 08, 2026'
    """
    if isinstance(date_obj, str):
        # Try to parse common formats
        for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y"]:
            try:
                date_obj = datetime.strptime(date_obj, fmt)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f"Unable to parse date string: {date_obj}")
    
    return date_obj.strftime(date_format)


def format_datetime(dt_obj: Union[datetime, str], 
                   dt_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to include both date and time.
    
    Args:
        dt_obj: datetime object or string
        dt_format: Desired output format - default: YYYY-MM-DD HH:MM:SS
    
    Returns:
        Formatted datetime string
    
    Example:
        >>> format_datetime(datetime(2026, 1, 8, 13, 49, 28))
        '2026-01-08 13:49:28'
    """
    if isinstance(dt_obj, str):
        try:
            dt_obj = datetime.fromisoformat(dt_obj)
        except ValueError:
            try:
                dt_obj = datetime.strptime(dt_obj, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise ValueError(f"Unable to parse datetime string: {dt_obj}")
    
    return dt_obj.strftime(dt_format)


def calculate_time_difference(start_date: Union[datetime, str], 
                             end_date: Union[datetime, str], 
                             unit: str = "days") -> Union[int, float]:
    """
    Calculate time difference between two dates.
    
    Args:
        start_date: Start datetime
        end_date: End datetime
        unit: Unit of difference ('days', 'hours', 'minutes', 'seconds')
    
    Returns:
        Time difference in specified unit
    
    Example:
        >>> start = datetime(2026, 1, 1)
        >>> end = datetime(2026, 1, 8)
        >>> calculate_time_difference(start, end)
        7
    """
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)
    
    diff = end_date - start_date
    
    unit_map = {
        'days': lambda d: d.days,
        'hours': lambda d: d.total_seconds() / 3600,
        'minutes': lambda d: d.total_seconds() / 60,
        'seconds': lambda d: d.total_seconds(),
    }
    
    if unit not in unit_map:
        raise ValueError(f"Invalid unit: {unit}. Must be one of {list(unit_map.keys())}")
    
    return unit_map[unit](diff)


def add_days(date_obj: Union[datetime, str], days: int) -> datetime:
    """
    Add days to a date.
    
    Args:
        date_obj: datetime object or string
        days: Number of days to add
    
    Returns:
        New datetime object
    
    Example:
        >>> add_days(datetime(2026, 1, 8), 7)
        datetime.datetime(2026, 1, 15, 0, 0)
    """
    if isinstance(date_obj, str):
        date_obj = datetime.fromisoformat(date_obj)
    
    return date_obj + timedelta(days=days)


def get_time_ago(date_obj: Union[datetime, str]) -> str:
    """
    Get a human-readable "time ago" string for a past date.
    
    Args:
        date_obj: Past datetime object or string
    
    Returns:
        Human-readable string (e.g., "2 hours ago", "3 days ago")
    
    Example:
        >>> get_time_ago(datetime.now() - timedelta(hours=2))
        '2 hours ago'
    """
    if isinstance(date_obj, str):
        date_obj = datetime.fromisoformat(date_obj)
    
    diff = datetime.now() - date_obj
    
    if diff.days > 365:
        return f"{diff.days // 365} year{'s' if diff.days // 365 > 1 else ''} ago"
    elif diff.days > 30:
        return f"{diff.days // 30} month{'s' if diff.days // 30 > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def is_valid_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid email format, False otherwise
    
    Example:
        >>> is_valid_email('user@example.com')
        True
        >>> is_valid_email('invalid.email')
        False
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """
    Validate phone number format (supports common international formats).
    
    Args:
        phone: Phone number to validate
    
    Returns:
        True if valid phone format, False otherwise
    
    Example:
        >>> is_valid_phone('+1-555-123-4567')
        True
        >>> is_valid_phone('555-123-4567')
        True
    """
    # Remove common separators and spaces
    cleaned = re.sub(r'[\s\-\(\)\.+]', '', phone)
    # Check if it's mostly digits and has reasonable length
    return bool(re.match(r'^\d{7,15}$', cleaned))


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid URL format, False otherwise
    
    Example:
        >>> is_valid_url('https://www.example.com')
        True
        >>> is_valid_url('not a url')
        False
    """
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))


def is_valid_credit_card(card_number: str) -> bool:
    """
    Validate credit card number using Luhn algorithm.
    
    Args:
        card_number: Credit card number (digits only)
    
    Returns:
        True if valid credit card number, False otherwise
    
    Example:
        >>> is_valid_credit_card('4532015112830366')
        True
    """
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s\-]', '', card_number)
    
    if not cleaned.isdigit() or len(cleaned) < 13 or len(cleaned) > 19:
        return False
    
    # Luhn algorithm
    total = 0
    for i, digit in enumerate(reversed(cleaned)):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    
    return total % 10 == 0


def is_strong_password(password: str) -> bool:
    """
    Validate password strength (min 8 chars, uppercase, lowercase, digit, special char).
    
    Args:
        password: Password to validate
    
    Returns:
        True if password meets strength requirements, False otherwise
    
    Example:
        >>> is_strong_password('WeakPass')
        False
        >>> is_strong_password('StrongPass123!')
        True
    """
    if len(password) < 8:
        return False
    
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password))
    
    return has_upper and has_lower and has_digit and has_special


def validate_input(value: str, field_type: str, 
                  min_length: Optional[int] = None, 
                  max_length: Optional[int] = None) -> Tuple[bool, Optional[str]]:
    """
    Generic input validation function.
    
    Args:
        value: Input value to validate
        field_type: Type of field ('email', 'phone', 'url', 'password', 'numeric')
        min_length: Minimum length constraint
        max_length: Maximum length constraint
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Example:
        >>> validate_input('user@example.com', 'email')
        (True, None)
        >>> validate_input('invalid', 'email')
        (False, 'Invalid email format')
    """
    if not value:
        return False, "Value cannot be empty"
    
    if min_length and len(value) < min_length:
        return False, f"Value must be at least {min_length} characters"
    
    if max_length and len(value) > max_length:
        return False, f"Value must be at most {max_length} characters"
    
    validators = {
        'email': (is_valid_email, "Invalid email format"),
        'phone': (is_valid_phone, "Invalid phone format"),
        'url': (is_valid_url, "Invalid URL format"),
        'password': (is_strong_password, "Password does not meet strength requirements"),
        'numeric': (lambda x: x.replace('.', '', 1).replace('-', '', 1).isdigit(), "Value must be numeric"),
    }
    
    if field_type not in validators:
        return False, f"Unknown field type: {field_type}"
    
    validator_func, error_msg = validators[field_type]
    
    if not validator_func(value):
        return False, error_msg
    
    return True, None


# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def round_decimal(value: Union[float, int, Decimal], 
                 decimal_places: int = 2) -> float:
    """
    Round a number to specified decimal places.
    
    Args:
        value: Number to round
        decimal_places: Number of decimal places
    
    Returns:
        Rounded float value
    
    Example:
        >>> round_decimal(3.14159, 2)
        3.14
    """
    decimal_value = Decimal(str(value))
    return float(round(decimal_value, decimal_places))


def calculate_percentage(part: Union[float, int], 
                        total: Union[float, int]) -> float:
    """
    Calculate percentage of a part relative to total.
    
    Args:
        part: The part value
        total: The total value
    
    Returns:
        Percentage (0-100)
    
    Example:
        >>> calculate_percentage(25, 100)
        25.0
        >>> calculate_percentage(1, 3)
        33.33
    """
    if total == 0:
        raise ValueError("Total cannot be zero")
    
    return float(Decimal(str(part)) / Decimal(str(total)) * 100)


def calculate_average(values: List[Union[float, int]]) -> float:
    """
    Calculate average of a list of numbers.
    
    Args:
        values: List of numeric values
    
    Returns:
        Average value
    
    Example:
        >>> calculate_average([10, 20, 30])
        20.0
    """
    if not values:
        raise ValueError("List cannot be empty")
    
    return float(sum(Decimal(str(v)) for v in values) / len(values))


def calculate_total_with_items(items: List[dict], price_key: str = 'price', 
                              quantity_key: str = 'quantity') -> float:
    """
    Calculate total price from a list of items with quantity.
    
    Args:
        items: List of item dictionaries
        price_key: Key for price in item dict
        quantity_key: Key for quantity in item dict
    
    Returns:
        Total price
    
    Example:
        >>> items = [{'price': 10, 'quantity': 2}, {'price': 20, 'quantity': 1}]
        >>> calculate_total_with_items(items)
        40.0
    """
    total = Decimal('0')
    
    for item in items:
        if price_key not in item or quantity_key not in item:
            raise KeyError(f"Item must contain '{price_key}' and '{quantity_key}' keys")
        
        price = Decimal(str(item[price_key]))
        quantity = Decimal(str(item[quantity_key]))
        total += price * quantity
    
    return float(total)


def clamp(value: Union[float, int], min_val: Union[float, int], 
         max_val: Union[float, int]) -> Union[float, int]:
    """
    Clamp a value between minimum and maximum.
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
    
    Returns:
        Clamped value
    
    Example:
        >>> clamp(15, 0, 10)
        10
        >>> clamp(5, 0, 10)
        5
    """
    return max(min_val, min(value, max_val))
