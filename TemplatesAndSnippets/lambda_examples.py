# Simple lambda for arithmetic
add = lambda x, y: x + y

# Lambda with map to square numbers
squares = list(map(lambda x: x * x, range(5)))

# Lambda as a key function to sort by second element
data = [(1, 'b'), (2, 'a'), (3, 'c')]
sorted_by_value = sorted(data, key=lambda x: x[1])

# Lambda with filter to keep even numbers
evens = list(filter(lambda x: x % 2 == 0, range(10)))

# Lambda with reduce to calculate product
from functools import reduce
product = reduce(lambda x, y: x * y, [1, 2, 3, 4])

# Lambda to extract domain from email list
emails = ["a@example.com", "b@test.org"]
domains = list(map(lambda e: e.split('@')[1], emails))

# Lambda with conditional expression
sign = lambda x: "positive" if x > 0 else "negative" if x < 0 else "zero"

# Lambda used inside a dictionary
operations = {
    "add": lambda x, y: x + y,
    "sub": lambda x, y: x - y,
    "mul": lambda x, y: x * y
}

# Lambda with sorted and complex tuple structure
records = [("Alice", 30, 50000), ("Bob", 25, 70000), ("Charlie", 30, 45000)]
sorted_by_age_then_salary = sorted(records, key=lambda x: (x[1], -x[2]))

# Nested lambda expression to build curried function
curried_adder = lambda x: lambda y: lambda z: x + y + z
sum_fn = curried_adder(1)(2)(3)  # returns 6