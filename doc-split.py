import requests
import fitz  # PyMuPDF

url = "https://www.europarl.europa.eu/doceo/document/TA-9-2024-0138-FNL-COR01_EN.pdf"
response = requests.get(url)
pdf_path = "data/document.pdf"

with open(pdf_path, 'wb') as file:
    file.write(response.content)

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()

    return text

extracted_text = extract_text_from_pdf(pdf_path)

print(extracted_text)
output_file = "data/extracted_text.txt"
with open(output_file, 'w') as file:
    file.write(extracted_text)


# Splitting into sections with regex

import re

# Define the regex pattern
pattern = re.compile(r"Article (1[0-1][0-3]|[1-9][0-9]?|1[0-9]{2})\n.+\n", re.MULTILINE)

# Read the content of the original document
with open('input.txt', 'r') as file:
    content = file.read()

# Find all matches
matches = pattern.findall(content)
matches_with_text = pattern.findall(content)

# Create the output files
with open('matches.txt', 'w') as match_file, open('separators.txt', 'w') as separator_file:
    for match in matches_with_text:
        match_file.write(match + "\n")
        separator_file.write("--------------------\n")

# Remove matches from the original document content
updated_content = pattern.sub("", content)

# Write the updated content back to the original document
with open('input.txt', 'w') as file:
    file.write(updated_content)

