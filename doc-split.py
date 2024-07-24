# Deprecated
# Use web-scrape.py instead
"""
import requests
import re
import fitz  # PyMuPDF
import json

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

def split(text):

    matches = re.finditer(r'\nArticle (1[0-1][0-3]|[1-9][0-9]?|1[0-9]{2})\n.+\n', text)
    positions = [match.start() for match in matches]

    print("POSITIONS: ", positions)

    sections = []
    start = 0

    for pos in positions:
        section = text[start:pos]
        sections.append(section)
        start = pos

    sections.append(text[start:])


    # splittajmo še introduction torej [0:249423]
    matches2 = re.finditer(r'\(\b(1[0-8][0-9]|[1-9]?[0-9])\b\)\n', text[:249422])

    positions2 = [match.start() for match in matches2]
    start = 0

    for pos in positions2:
        section = text[start:pos]
        sections.append(section)
        start = pos

    # itak moramo vse nespremenjeno appendat. Zdaj lahko samo overwritamo vse, zato [start:]
    sections.append(text[start:249422]) 
    separator = "\n---\n".join(sections)
    
    print("LENGTH: ", len(sections))
    print(sections[34])

    return sections

def generate_json(sections):
    print("Pritning from generate_json function")
    print(sections[34])
    objects = []
    for pos, section in enumerate(sections):
        object = {
            "text": section,
            "position": pos
        }
        objects.append(object)

    with open('data/output.json', 'w') as json_file:
        json.dump(objects, json_file, indent=4)




if __name__ == "__main__":
    text = extract_text_from_pdf(pdf_path)
    generate_json(split(text))
"""
