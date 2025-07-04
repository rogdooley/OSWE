from bs4 import BeautifulSoup

def extract_h2_in_div_title(html: str) -> str | None:
    """Extracts username from: <div class="title"><h2>USERNAME</h2></div>"""
    soup = BeautifulSoup(html, 'html.parser')
    title_div = soup.find('div', class_='title')
    if title_div:
        h2 = title_div.find('h2')
        if h2:
            return h2.text.strip()
    return None

def extract_link_from_anchor(html: str) -> list[str]:
    """Extracts all href values from <a> tags"""
    soup = BeautifulSoup(html, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def extract_table_text(html: str) -> list[list[str]]:
    """Extracts text content from all table rows and cells"""
    soup = BeautifulSoup(html, 'html.parser')
    return [
        [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
        for row in soup.find_all('tr')
    ]