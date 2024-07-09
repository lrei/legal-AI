import requests
import re
import re
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

output_path = "data/extracted_text.txt"

with open(output_path, 'w', encoding='utf-8') as file: # encoding mora biti na windowsu
    file.write(extracted_text)

    with open(output_path, 'r', encoding='utf-8') as file:
        text = file.read()

    matches = re.finditer(r'\nArticle (1[0-1][0-3]|[1-9][0-9]?|1[0-9]{2})\n.+\n', text)
    positions = [match.start() for match in matches]

    print(positions)

    sections = []
    start = 0

    for pos in positions:
        section = extracted_text[start:pos]
        sections.append(section)
        start = pos

    # Add the last section from the last position to the end of the text
    sections.append(extracted_text[start:])

    sections_text = "\n---\n".join(sections)

    sections_path = "data/sections.txt"

    with open(sections_path, 'w', encoding='utf-8') as file:
        file.write(sections_text)

    