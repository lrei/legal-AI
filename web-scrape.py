import json
from bs4 import BeautifulSoup
import re

# HTML file is just the whole <body> <\body> pasted into .html file. We should fix this, so that it goes through links by itself. 
with open('data/ai-legalisation.html', 'r', encoding='utf-8') as file:
    content = file.read()

soup = BeautifulSoup(content, 'html.parser')

# Chapter and article
def extract_chapter_article(soup):
    chapter = soup.find('div', class_='accordion-header active').find('p', class_='parent-title').text.strip()
    article = soup.find('div', class_='accordion-content').find('p', class_='child-article').text.strip()
    return chapter, article

# Date of entry into force:
def extract_expected_date(soup):
    label_tag = soup.find('p', class_='aia-eif-label', text='Date of entry into force:')

    date_entry_into_force = None

    if label_tag:
        value_tag = label_tag.find_next_sibling('p', class_='aia-eif-value')
        
        if value_tag:
            date_entry_into_force = value_tag.get_text(strip=True)
    return date_entry_into_force

# Article summary
def extract_summary(soup):
    summary_tag = soup.find('p', class_='aia-clairk-summary-content')
    if summary_tag:
        summary = summary_tag.find_next('p').text.strip()
        return summary
    return ""


chapter, article = extract_chapter_article(soup)
expected_date = extract_expected_date(soup)
summary = extract_summary(soup)

# Paragraphs
div_tag = soup.find('div', class_='et_pb_module et_pb_post_content et_pb_post_content_0_tb_body')

json_objects = []

numbered_pattern = re.compile(r'^\d+\.')

if div_tag:
    paragraphs = div_tag.find_all('p')
    
    for paragraph in paragraphs:
        if numbered_pattern.match(paragraph.text.strip()):
            match = numbered_pattern.match(paragraph.text.strip())
            paragraph_number = match.group(0)[:-1]
            paragraph_text = paragraph.text.strip()[len(paragraph_number) + 1:].strip()
            
            data = {
                'Chapter': chapter,
                'Article': article,
                'Expected date': expected_date,
                'Summary': summary,
                'Paragraph': paragraph_number,
                'Text': paragraph_text
            }
            
            json_objects.append(data)



# -----------------
output_file = 'data/ai_article_data.json'
with open(output_file, 'w', encoding='utf-8') as json_file:
    json_file.write("[\n")  

    for i, obj in enumerate(json_objects):
        json.dump(obj, json_file, indent=4, ensure_ascii=False)
        if i < len(json_objects) - 1:
            json_file.write(",\n")  

    json_file.write("\n]")  

print(f'Data has been saved to {output_file}')
