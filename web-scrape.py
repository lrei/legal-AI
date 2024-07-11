import json
from bs4 import BeautifulSoup
import re

# Read the HTML file
with open('data/ai-legalisation.html', 'r', encoding='utf-8') as file:
    content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(content, 'html.parser')

# Function to extract chapter and article
def extract_chapter_article(soup):
    chapter = soup.find('div', class_='accordion-header active').find('p', class_='parent-title').text.strip()
    article = soup.find('div', class_='accordion-content').find('p', class_='child-article').text.strip()
    return chapter, article

# Function to extract expected date
def extract_expected_date(soup):
    label_tag = soup.find('p', class_='aia-eif-label', text='Date of entry into force:')

    # Initialize date_entry_into_force
    date_entry_into_force = None

    # Check if label_tag is found
    if label_tag:
        # Get the next sibling, which should be <p class="aia-eif-value">
        value_tag = label_tag.find_next_sibling('p', class_='aia-eif-value')
        
        # Extract the text from value_tag if it exists
        if value_tag:
            date_entry_into_force = value_tag.get_text(strip=True)
    return date_entry_into_force

# Function to extract summary
def extract_summary(soup):
    summary_tag = soup.find('p', class_='aia-clairk-summary-content')
    if summary_tag:
        summary = summary_tag.find_next('p').text.strip()
        return summary
    return ""


# Extract data from the HTML
chapter, article = extract_chapter_article(soup)
expected_date = extract_expected_date(soup)
summary = extract_summary(soup)


# ------------- Paragraphs
# Find the div with class 'et_pb_module et_pb_post_content et_pb_post_content_0_tb_body'
div_tag = soup.find('div', class_='et_pb_module et_pb_post_content et_pb_post_content_0_tb_body')

# Initialize a list to store JSON objects
json_objects = []

# Regular expression to match a number followed by a period
numbered_pattern = re.compile(r'^\d+\.')

# Find all <p> tags within the div
if div_tag:
    paragraphs = div_tag.find_all('p')
    
    for paragraph in paragraphs:
        # Check if the paragraph starts with a number followed by a period
        if numbered_pattern.match(paragraph.text.strip()):
            # Extract paragraph number
            match = numbered_pattern.match(paragraph.text.strip())
            paragraph_number = match.group(0)[:-1]  # Remove the period
            
            # Extract paragraph text
            paragraph_text = paragraph.text.strip()[len(paragraph_number) + 1:].strip()
            
            # Create JSON object
            # Structure the data
            data = {
                'Chapter': chapter,
                'Article': article,
                'Expected date': expected_date,
                'Summary': summary,
                'Paragraph': paragraph_number,
                'Text': paragraph_text
            }
            
            # Append JSON object to list
            json_objects.append(data)



# -----------------
# Save the data to a JSON file
output_file = 'data/ai_article_data.json'
with open(output_file, 'w', encoding='utf-8') as json_file:
    for obj in json_objects:
        json.dump(obj, json_file, indent=4, ensure_ascii=False)

print(f'Data has been saved to {output_file}')

