# Python Snippet Library

This repository contains structured, reusable Python code templates for common development and scripting tasks. These snippets are intended as references, not standalone programs.

---

## Directory Overview

### `boilerplate.py`
Command-line interface setup using `argparse`. Includes:
- Argument definitions
- Help strings
- Positional and optional flags

### `dataclass_templates.py`
Examples of Python `@dataclass` usage:
- Simple structured records
- Multiple fields with type annotations
- Suggestions for `frozen=True`, default values, or ordering

### `file_utils.py`
File and path utility functions:
- Check for file or directory existence
- Read/write text or lines
- Create temporary files
- List files by extension
- Validate relative paths
- File copying

### `request_examples.py`
HTTP request patterns using the `requests` library:
- Basic GET and POST requests
- Posting JSON payloads
- Using custom headers
- Creating and reusing sessions

### `threading_examples.py`
Threaded execution patterns:
- Using `ThreadPoolExecutor` with closures
- Batch processing with `executor.map`
- Handling futures with `as_completed`
- Parameter binding using closures or `functools.partial`

### `print_helpers.py`
Utilities for clean command-line output:
- In-place status updates using carriage return
- Line clearing
- Section banners

### `beautiful_soup.py`
Common HTML parsing techniques using `BeautifulSoup`:
- Extracting tags and nested content
- Parsing attribute values
- Handling lists and tables

### `password.py`
Basic password validation:
- Enforces minimum length and character set requirements
- Can be extended to support entropy estimation or blacklist checks

### `lambda_examples.py`
Progressive examples of `lambda` usage:
- Arithmetic and filtering
- Sorting with key functions
- Conditional logic
- Function currying
- Use inside higher-order constructs

### `list_comprehensions.py`
Comprehension patterns:
- List, set, and dict comprehensions
- Conditional filtering
- Nested and flattened structures
- Dictionary inversion
- Practical transformations on structured data


