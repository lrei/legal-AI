import re
import json
from bs4 import BeautifulSoup
import requests

# Function to split paragraphs into overlapping chunks
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

def clean_paragraph_text(paragraph):
    for span in paragraph.find_all('span', class_='aia-recital-ref'):
        span.decompose() 
    return paragraph.get_text().strip()

# Using roman numerals for chapter numbers
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

def get_chapter_number(chapter):
    match = re.search(r'Chapter (\w+)', chapter)
    chapter_number = match.group(1) if match else '1'

    if chapter_number.isdigit():
        return int_to_roman(int(chapter_number))
    else:
        return chapter_number

def get_article_number(article):
    match = re.search(r'Article (\d+)', article)
    return match.group(1) if match else '1'

def extract_chapter_article(soup):
    h1_tag = soup.find('h1', class_='entry-title')
    article = h1_tag.text.strip() if h1_tag else "Article not found"

    chapter = "Chapter not found"
    p_tags = soup.find_all('p')
    for p_tag in p_tags:
        if 'Part of' in p_tag.get_text():
            a_tag = p_tag.find('a')
            if a_tag:
                chapter = a_tag.get_text(strip=True).replace('\n', ' ')
                break
    return chapter, article

def scrape_article(art_number):
    url = f"https://artificialintelligenceact.eu/article/{art_number}/"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article {art_number}: {e}")
        return []

    chapter, article = extract_chapter_article(soup)
    div_tag = soup.find('div', class_='et_pb_module et_pb_post_content et_pb_post_content_0_tb_body')
    
    json_objects = []
    passage_counter = 0  

    if div_tag:
        paragraphs = div_tag.find_all('p')
        for i, paragraph in enumerate(paragraphs):
            paragraph_text = clean_paragraph_text(paragraph) 

            if paragraph_text:
                paragraph_chunks = split_paragraph_with_overlap_characters(paragraph_text)

                chapter_number = get_chapter_number(chapter)
                article_number = get_article_number(article)

                passage_counter += 1  

                for j, chunk in enumerate(paragraph_chunks):
                    data = {
                        'Regulation': "European Artificial Intelligence Act",
                        'Chapter': chapter,
                        'Article': article,
                        'Passage': f'{chapter_number}.{article_number}.{passage_counter}.{j + 1}',  # Correct passage and chunk numbering
                        'Content': chunk
                    }
                    json_objects.append(data)

    return json_objects

# Scrape all articles and save to JSON
def scrape_all_articles(start=1, end=114, output_file='EAA/eaa.json'):
    all_json_objects = []

    for art in range(start, end + 1):
        print(f"Scraping article {art}...")
        article_data = scrape_article(art)

        if article_data:
            all_json_objects.extend(article_data)

    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(all_json_objects, json_file, indent=4, ensure_ascii=False)

    print(f"All data has been saved to {output_file}.")

if __name__ == "__main__":
    scrape_all_articles()
