"""Utility functions - random helpers I use throughout the project"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

# Some constants I find useful
TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def format_time(time_str: str) -> str:
    """Format time string nicely - handles both HH:MM and HH:MM:SS"""
    try:
        if len(time_str.split(':')) == 3:
            # Has seconds, strip them
            return ':'.join(time_str.split(':')[:2])
        return time_str
    except:
        return time_str  # return as-is if something goes wrong


def add_minutes(time_str: str, minutes: int) -> str:
    """Add minutes to a time string (HH:MM format)"""
    try:
        # Parse the time
        time_obj = datetime.strptime(time_str, TIME_FORMAT)
        # Add minutes
        new_time = time_obj + timedelta(minutes=minutes)
        # Return formatted
        return new_time.strftime(TIME_FORMAT)
    except Exception as e:
        print(f"Error adding minutes: {e}")
        return time_str


def generate_random_phone():
    """Generate a random 10-digit phone number for testing"""
    # Format: +91-XXXXXXXXXX (Indian format)
    return f"+91-{random.randint(7000000000, 9999999999)}"


def calculate_queue_wait(position: int, avg_time: int = 10) -> int:
    """
    Calculate approximate wait time based on queue position
    
    Args:
        position: Position in queue (1-based)
        avg_time: Average consultation time in minutes
    
    Returns:
        Estimated wait time in minutes
    """
    # Simple calculation: (position - 1) * avg_time
    # The -1 is because position 1 is being served now
    return max(0, (position - 1) * avg_time)


def is_slot_time_valid(start_time: str, end_time: str) -> bool:
    """Check if slot times are valid (start < end)"""
    try:
        start = datetime.strptime(start_time, TIME_FORMAT)
        end = datetime.strptime(end_time, TIME_FORMAT)
        return start < end
    except:
        return False


# Some sample data generators for testing
def generate_patient_names() -> List[str]:
    """Returns a list of sample patient names for testing"""
    return [
        "Rajesh Kumar", "Priya Sharma", "Amit Patel", 
        "Sunita Reddy", "Vikram Singh", "Anjali Gupta",
        "Manoj Verma", "Kavita Joshi", "Ravi Mehta",
        "Sneha Desai", "Arjun Rao", "Pooja Nair"
    ]


def generate_patient_data():
    """Generate random patient data for testing"""
    names = generate_patient_names()
    return {
        "name": random.choice(names),
        "phone": generate_random_phone(),
        "age": random.randint(18, 80)
    }


# Debugging helpers
def print_divider(char="=", length=70):
    """Print a divider line - useful for console output"""
    print(char * length)


def print_header(text: str, char="="):
    """Print a centered header with dividers"""
    print_divider(char)
    print(text.center(70))
    print_divider(char)


# TODO: Add more utility functions as needed
# - Date validation
# - Time slot conflict detection
# - Patient data sanitization
# - Report generation helpers
