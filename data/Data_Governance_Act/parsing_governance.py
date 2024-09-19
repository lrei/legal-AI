import json
from bs4 import BeautifulSoup
import requests
import re

chapter_mapping = {
    range(1, 3): "Chapter I: General provisions",
    range(3, 10): "Chapter II: Re-use of certain categories of protected data held by public sector bodies",
    range(10, 16): "Chapter III: Requirements applicable to data intermediation services",
    range(16, 26): "Chapter IV: Data altruism",
    range(26, 29): "Chapter V: Competent authorities and procedural provisions",
    range(29, 31): "Chapter VI: European Data Innovation Board",
    range(31, 32): "Chapter VII: International access and transfer",
    range(32, 34): "Chapter VIII: Delegation and committee procedure",
    range(34, 39): "Chapter IX: Final and transitional provisions"
}

exclude_sections = [
    "Understanding Cybersecurity in the European Union",
    "The NIS 2 Directive", "The European Cyber Resilience Act",
    "The Digital Operational Resilience Act (DORA)", "The Critical Entities Resilience Directive (CER)",
    "The Digital Services Act (DSA)", "The Digital Markets Act (DMA)",
    "The European Health Data Space (EHDS)", "The European Chips Act",
    "The European Data Act", "European Data Governance Act (DGA)",
    "The Artificial Intelligence Act", "The European ePrivacy Regulation",
    "The European Cyber Defence Policy", "The Strategic Compass of the European Union",
    "The EU Cyber Diplomacy Toolbox"
]

def int_to_roman(n):
    roman_numerals = [
        ('M', 1000), ('CM', 900), ('D', 500), ('CD', 400),
        ('C', 100), ('XC', 90), ('L', 50), ('XL', 40),
        ('X', 10), ('IX', 9), ('V', 5), ('IV', 4), ('I', 1)
    ]
    result = []
    for numeral, value in roman_numerals:
        while n >= value:
            result.append(numeral)
            n -= value
    return ''.join(result)

def get_chapter(art_number):
    for article_range, chapter in chapter_mapping.items():
        if art_number in article_range:
            roman_chapter = chapter.split()[1] 
            return f"{chapter.split(':')[0]}: {chapter.split(':')[1].strip()}"
    return "Unknown Chapter"

def get_chapter_number(art_number):
    for article_range, chapter in chapter_mapping.items():
        if art_number in article_range:
            return chapter.split()[1] 
    return "Unknown Chapter"

def split_paragraph_with_overlap_characters(text, chunk_size=184, overlap=30):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text) and text[end] != ' ':
            while end < len(text) and text[end] != ' ':
                end += 1
        chunk = text[start:end].strip()
        if len(chunk) >= overlap:
            chunks.append(chunk)
        start = end - overlap
        while start < len(text) and text[start] != ' ':
            start += 1
        start += 1
    return chunks

def clean_extra_spaces_in_text(text):
    return re.sub(r'(\d+)\.\s+', r'\1. ', text)

def replace_apostrophes(text):
    text = text.replace("‘", "'").replace("’", "' ")
    return text

def normalize_text(text):
    return re.sub(r'[:,]', ' ', text).lower().strip()

def scrape_article(art_number):
    url = f"https://www.european-data-governance-act.com/Data_Governance_Act_Article_{art_number}.html"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article {art_number}: {e}")
        return []

    chapter_title = get_chapter(art_number)
    chapter_number = get_chapter_number(art_number)

    title_tag = soup.find('b')
    if not title_tag:
        return []

    article_title = title_tag.text.strip().replace(f"Article {art_number}, ", "")
    full_article_title = f"Article {art_number}: {article_title}"

    if article_title in exclude_sections:
        return []

    paragraphs = soup.find_all('p', class_='text-left')
    if not paragraphs:
        print(f"No paragraphs found for article {art_number}")
        return []

    json_objects = []
    paragraph_counter = 1

    for paragraph in paragraphs:
        paragraph_text = paragraph.get_text(strip=True)
        paragraph_text = clean_extra_spaces_in_text(paragraph_text)
        paragraph_text = replace_apostrophes(paragraph_text)  

        if any(exclude in paragraph_text for exclude in exclude_sections):
            print(f"Skipping excluded content: {paragraph_text}")
            continue

        if paragraph_text.lower().startswith("article"):
            continue

        if normalize_text(paragraph_text) == normalize_text(article_title):
            continue

        if not paragraph_text:
            continue

        if len(paragraph_text) > 184:
            paragraph_chunks = split_paragraph_with_overlap_characters(paragraph_text, chunk_size=184, overlap=30)
        else:
            paragraph_chunks = [paragraph_text]

        for chunk_counter, chunk in enumerate(paragraph_chunks, start=1):
            passage_number = f"{chapter_number}.{art_number}.{paragraph_counter}.{chunk_counter}".replace(":", "")


            data = {
                'Regulation': "The European Data Governance Act",
                'Chapter': chapter_title,
                'Article': full_article_title,
                'Passage': passage_number,  
                'Content': chunk
            }
            json_objects.append(data)

        paragraph_counter += 1

    return json_objects

def scrape_dga(output_file='DGA/dga.json'):
    all_json_objects = []

    for art_number in range(1, 39): 
        print(f"Scraping article {art_number}...")
        article_data = scrape_article(art_number)

        if article_data:
            all_json_objects.extend(article_data)

    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(all_json_objects, json_file, indent=4, ensure_ascii=False)

    print(f"All data has been saved to {output_file}.")

if __name__ == "__main__":
    scrape_dga()
