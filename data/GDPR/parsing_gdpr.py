import json
from bs4 import BeautifulSoup
import requests
import re

# Easier to set the chapter and article titles manually
chapter_mapping_manual = {
    range(1, 5): "Chapter I: General provisions",
    range(5, 12): "Chapter II: Principles",
    range(12, 24): "Chapter III: Rights of the data subject",
    range(24, 44): "Chapter IV: Controller and processor",
    range(44, 51): "Chapter V: Transfers of personal data to third countries or international organisations",
    range(51, 60): "Chapter VI: Independent supervisory authorities",
    range(60, 77): "Chapter VII: Cooperation and consistency",
    range(77, 85): "Chapter VIII: Remedies, liability and penalties",
    range(85, 92): "Chapter IX: Provisions relating to specific processing situations",
    range(92, 94): "Chapter X: Delegated acts and implementing acts",
    range(94, 100): "Chapter XI: Final provisions"
}

article_titles_manual = {
    1: "Subject-matter and objectives",
    2: "Material scope",
    3: "Territorial scope",
    4: "Definitions",
    5: "Principles relating to processing of personal data",
    6: "Lawfulness of processing",
    7: "Conditions for consent",
    8: "Conditions applicable to child's consent in relation to information society services",
    9: "Processing of special categories of personal data",
    10: "Processing of personal data relating to criminal convictions and offences",
    11: "Processing which does not require identification",
    12: "Transparent information, communication and modalities for the exercise of the rights of the data subject",
    13: "Information to be provided where personal data are collected from the data subject",
    14: "Information to be provided where personal data have not been obtained from the data subject",
    15: "Right of access by the data subject",
    16: "Right to rectification",
    17: "Right to erasure (‘right to be forgotten’)",
    18: "Right to restriction of processing",
    19: "Notification obligation regarding rectification or erasure of personal data or restriction of processing",
    20: "Right to data portability",
    21: "Right to object",
    22: "Automated individual decision-making, including profiling",
    23: "Restrictions",
    24: "Responsibility of the controller",
    25: "Data protection by design and by default",
    26: "Joint controllers",
    27: "Representatives of controllers or processors not established in the Union",
    28: "Processor",
    29: "Processing under the authority of the controller or processor",
    30: "Records of processing activities",
    31: "Cooperation with the supervisory authority",
    32: "Security of processing",
    33: "Notification of a personal data breach to the supervisory authority",
    34: "Communication of a personal data breach to the data subject",
    35: "Data protection impact assessment",
    36: "Prior consultation",
    37: "Designation of the data protection officer",
    38: "Position of the data protection officer",
    39: "Tasks of the data protection officer",
    40: "Codes of conduct",
    41: "Monitoring of approved codes of conduct",
    42: "Certification",
    43: "Certification bodies",
    44: "General principle for transfers",
    45: "Transfers on the basis of an adequacy decision",
    46: "Transfers subject to appropriate safeguards",
    47: "Binding corporate rules",
    48: "Transfers or disclosures not authorised by Union law",
    49: "Derogations for specific situations",
    50: "International cooperation for the protection of personal data",
    51: "Supervisory authority",
    52: "Independence",
    53: "General conditions for the members of the supervisory authority",
    54: "Rules on the establishment of the supervisory authority",
    55: "Competence",
    56: "Competence of the lead supervisory authority",
    57: "Tasks",
    58: "Powers",
    59: "Activity reports",
    60: "Cooperation between the lead supervisory authority and the other supervisory authorities concerned",
    61: "Mutual assistance",
    62: "Joint operations of supervisory authorities",
    63: "Consistency mechanism",
    64: "Opinion of the Board",
    65: "Dispute resolution by the Board",
    66: "Urgency procedure",
    67: "Exchange of information",
    68: "European Data Protection Board",
    69: "Independence",
    70: "Tasks of the Board",
    71: "Reports",
    72: "Procedure",
    73: "Chair",
    74: "Tasks of the Chair",
    75: "Secretariat",
    76: "Confidentiality",
    77: "Right to lodge a complaint with a supervisory authority",
    78: "Right to an effective judicial remedy against a supervisory authority",
    79: "Right to an effective judicial remedy against a controller or processor",
    80: "Representation of data subjects",
    81: "Suspension of proceedings",
    82: "Right to compensation and liability",
    83: "General conditions for imposing administrative fines",
    84: "Penalties",
    85: "Processing and freedom of expression and information",
    86: "Processing and public access to official documents",
    87: "Processing of the national identification number",
    88: "Processing in the context of employment",
    89: "Safeguards and derogations relating to processing for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes",
    90: "Obligations of secrecy",
    91: "Existing data protection rules of churches and religious associations",
    92: "Exercise of the delegation",
    93: "Committee procedure",
    94: "Repeal of Directive 95/46/EC",
    95: "Relationship with Directive 2002/58/EC",
    96: "Relationship with previously concluded Agreements",
    97: "Commission reports",
    98: "Review of other Union legal acts on data protection",
    99: "Entry into force and application"
}

# Splitting paragraphs into overlapping chunks
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
        while start < len(text) and start < len(text) and text[start] != ' ':
            start += 1
        start += 1
    return chunks

# Using roman numerals for chapter numbering
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

# Handling special cases where a space is missing between two words due to a hyperlink
def fix_missing_spaces(text):
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
    text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)\s*(to|and|or)\s*(\d)', r'\1 \2 \3', text)
    return text

# Filtering functions
def format_article_mentions(text):
    text = fix_missing_spaces(text)
    text = re.sub(r'\b(Articles?)\s*(\d+)\b', r'\1 \2', text)
    return text

def process_br_tags(paragraph):
    soup = BeautifulSoup(str(paragraph), 'html.parser')
    text_parts = []
    for element in soup.descendants:
        if isinstance(element, str):
            text_parts.append(element.strip())
        elif element.name == 'br':
            text_parts.append('\n')  

    combined_text = ''.join(text_parts)
    formatted_text = format_article_mentions(combined_text)
    return [part.strip() for part in formatted_text.split('\n') if part.strip()]

# Scraping relevant data 
def get_chapter(art_number):
    for article_range, chapter in chapter_mapping_manual.items():
        if art_number in article_range:
            return chapter
    return "Unknown Chapter"

def get_article_title(art_number):
    return article_titles_manual.get(art_number, "Unknown Title")

def scrape_article(art_number):
    if art_number == 41:
        url = "https://www.dpocentre.com/resources/gdpr/article-10/article-41/"
    else:
        url = f"https://www.dpocentre.com/resources/gdpr/article-{art_number}/"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article {art_number}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    content_div = soup.find('div', class_='wpb_wrapper')
    if not content_div:
        print(f"No content found for article {art_number}")
        return []

    article_title = get_article_title(art_number)

    paragraphs = content_div.find_all('p')

    json_objects = []
    paragraph_counter = 1 

    for paragraph in paragraphs:
        if not paragraph.text.strip():
            continue

        # Handling some exceptions
        if 'Recital relating to this Article' in paragraph.text:
            continue
        
        paragraph_texts = process_br_tags(paragraph)
        paragraph_added = False 

        for paragraph_text in paragraph_texts:
            if not paragraph_text.strip():
                continue

            if 'Recitals relating to this Article' in paragraph_text:
                continue

            paragraph_chunks = split_paragraph_with_overlap_characters(paragraph_text)
            chunk_counter = 1
            for chunk in paragraph_chunks:
                passage_number = f"{int_to_roman(art_number // 10 + 1)}.{art_number}.{paragraph_counter}.{chunk_counter}"
                data = {
                    'Regulation': 'General Data Protection Regulation',
                    'Chapter': get_chapter(art_number),
                    'Article': f"Article {art_number}: {article_title}",
                    'Passage': passage_number,
                    'Content': chunk
                }
                json_objects.append(data)
                chunk_counter += 1  
                paragraph_added = True 

        if paragraph_added:
            paragraph_counter += 1

    return json_objects

# Scrape all articles and save everything to gdpr.json in the same directory
def scrape_gdpr(output_file='data/GDPR/gdpr.json'):
    all_json_objects = []
    for art_number in range(1, 100): 
        article_data = scrape_article(art_number)
        if article_data:
            all_json_objects.extend(article_data)
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(all_json_objects, json_file, indent=4, ensure_ascii=False)
    print(f"All data has been saved to {output_file}.")

if __name__ == "__main__":
    scrape_gdpr()
