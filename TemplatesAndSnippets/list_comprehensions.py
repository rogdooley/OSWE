# Basic list comprehension
nums = [x for x in range(5)]

# Comprehension with condition
squares_of_even = [x * x for x in range(10) if x % 2 == 0]

# Nested comprehension (2D grid)
grid = [[(x, y) for y in range(3)] for x in range(3)]

# Flatten a 2D list
nested = [[1, 2], [3, 4], [5]]
flat = [item for sublist in nested for item in sublist]

# Filter and transform strings
words = ["apple", "banana", "cherry", "date"]
short_upper = [w.upper() for w in words if len(w) <= 5]

# Set comprehension for unique first letters
first_letters = {w[0] for w in words}

# Dictionary comprehension to map word to length
word_lengths = {w: len(w) for w in words}

# Build a reverse lookup dict from list of tuples
pairs = [("a", 1), ("b", 2), ("c", 3)]
reverse_lookup = {v: k for k, v in pairs}

# List comprehension with inline function call
import math
roots = [math.sqrt(x) for x in range(1, 11) if x % 2 == 0]

# Complex comprehension with multiple filters and transformation
users = [{"id": i, "name": f"user{i}", "active": i % 3 != 0} for i in range(1, 11)]
active_names = [u["name"].upper() for u in users if u["active"] and u["id"] > 3]