import sys

def status_line(message: str):
    """Prints a message that stays on the same line"""
    print(f"\r{message}", end='', flush=True)

def clear_and_print(message: str):
    """Clears the current line and prints a new message"""
    print('\r' + ' ' * 80, end='\r')  # Clear line
    print(message)

def print_banner(title: str):
    """Prints a section banner"""
    print(f"\n{'=' * 10} {title} {'=' * 10}")