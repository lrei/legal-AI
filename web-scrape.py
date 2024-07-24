import json
from bs4 import BeautifulSoup
import re
import requests

def extract_chapter_article(soup, number):
    h1_tag = soup.find('h1', class_='entry-title')
    if h1_tag:
        article = h1_tag.text.strip()
    else:
        article = "Article not found"
    
    p_tag = soup.find('p', string=lambda text: text and 'Part of' in text)
    if p_tag and p_tag.find('a'):
        chapter = p_tag.find('a').text.strip()
    else:
        chapter = "Chapter not found"
    
    return chapter, article

def extract_expected_date(soup):
    label_tag = soup.find('p', class_='aia-eif-label', text='Date of entry into force:')

    date_entry_into_force = None

    if label_tag:
        value_tag = label_tag.find_next_sibling('p', class_='aia-eif-value')
        
        if value_tag:
            date_entry_into_force = value_tag.get_text(strip=True)
    return date_entry_into_force

def extract_summary(soup):
    summary_tag = soup.find('p', class_='aia-clairk-summary-content')
    if summary_tag:
        summary = summary_tag.find_next('p').text.strip()
        return summary
    return ""
# ----------------- Begin iteration for every Article #n -----------------
# TODO: maybe put this into function, and then just loop in __main__? 
# Also fix so that it doesn't save the html file locally, and works with online resource instead
output_file = 'data/ai_article_data.json'

for art in range(5, 8):

    url = "https://artificialintelligenceact.eu/article/" + str(art) + "/"

    response = requests.get(url)

    if response.status_code == 200: # is online
        soup = BeautifulSoup(response.text, 'html.parser')
        
        body_content = soup.find('body', class_=True)
        body_html = str(body_content)
        
        with open('data/ai-legalisation.html', 'w', encoding='utf-8') as file:
            file.write(body_html)
        print("File saved successfully.")
    else:
        print("Failed to retrieve the webpage")

    with open('data/ai-legalisation.html', 'r', encoding='utf-8') as file:
        content = file.read()

    soup = BeautifulSoup(content, 'html.parser')

    chapter, article = extract_chapter_article(soup, art)
    expected_date = extract_expected_date(soup)
    summary = extract_summary(soup)

    div_tag = soup.find('div', class_='et_pb_module et_pb_post_content et_pb_post_content_0_tb_body')

    json_objects = []

    numbered_pattern = re.compile(r'^\d+\.')

    if div_tag:
        paragraphs = div_tag.find_all('p')
        match_indexes = [i for i, p in enumerate(paragraphs) if numbered_pattern.match(p.text.strip())]
        
        for i, paragraph in enumerate(paragraphs):
            if i in match_indexes:
                start_index = i
                next_index = next((x for x in match_indexes if x > i), None)
                
                if next_index:
                    paragraph_texts = [p.text.strip() for p in paragraphs[start_index:next_index]]
                else:
                    paragraph_texts = [p.text.strip() for p in paragraphs[start_index:]]
                
                paragraph_text = " ".join(paragraph_texts)
                
                match = numbered_pattern.match(paragraph.text.strip())
                paragraph_number = match.group(0)[:-1]
                
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

    with open(output_file, 'w', encoding='utf-8') as json_file:
        json_file.write("[\n")  

        for i, obj in enumerate(json_objects):
            json.dump(obj, json_file, indent=4, ensure_ascii=False)
            if i < len(json_objects) - 1:
                json_file.write(",\n")  

        json_file.write("\n]")  

    print(f'Data from article {art} has been saved to {output_file}')
