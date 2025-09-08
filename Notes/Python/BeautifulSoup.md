BeautifulSoup Object Type Cheat Sheet

BeautifulSoup parses HTML/XML documents and represents the structure as a tree of objects. Each object belongs to a specific type, and understanding these is essential for effective traversal, querying, and manipulation.

1. bs4.BeautifulSoup

Description:
	•	The root object representing the entire parsed document.
	•	Acts like a Tag, but specifically for the document root.

Example:

soup = BeautifulSoup("<html><body><p>Hello</p></body></html>", "html.parser")

Common Usage:

soup.find("p")
soup.title


⸻

2. bs4.Tag

Description:
	•	Represents an individual HTML/XML tag.
	•	Behaves like a dictionary for attributes and can contain other Tag and NavigableString objects.

Example:

tag = soup.find("p")

Common Properties and Methods:

tag.name                # e.g. 'p'
tag.attrs               # e.g. {'class': 'intro'}
tag["class"]            # e.g. 'intro'
tag.get("href")         # safer attribute access
tag.text or tag.string  # text inside tag


⸻

3. bs4.NavigableString

Description:
	•	Represents text within a tag.
	•	Subclass of Python’s str, but cannot have attributes or children.

Example:

text = soup.find("p").string

Notes:
	•	Use str(text) or text.strip() as needed.
	•	Cannot be indexed like a Tag.

⸻

4. bs4.Comment

Description:
	•	Subclass of NavigableString that specifically represents an HTML comment.

Example:

comment = soup.find(string=lambda text: isinstance(text, Comment))

Notes:
	•	You can manipulate or remove comments using this object.

⸻

5. bs4.Doctype

Description:
	•	Represents the DOCTYPE declaration in HTML.
	•	Rarely used in most scraping tasks, but available.

Example:

doctype = next((el for el in soup.contents if isinstance(el, Doctype)), None)


⸻

6. bs4.ResultSet

Description:
	•	A subclass of Python list, returned by .find_all() and similar methods.
	•	Contains multiple Tag objects.

Example:

links = soup.find_all("a")  # ResultSet of Tag elements


⸻

Type Hierarchy (Simplified)

object
├── bs4.element.PageElement
│   ├── Tag
│   ├── NavigableString
│   │   └── Comment
│   └── BeautifulSoup (also a Tag)


⸻


