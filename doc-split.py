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

    # print(positions)

    sections = []
    start = 0

    for pos in positions:
        section = extracted_text[start:pos]
        sections.append(section)
        start = pos

    # Add the last section from the last position to the end of the text
    sections.append(extracted_text[start:])

    separator = "\n---\n".join(sections)

    sections_path = "data/sections.txt"

    with open(sections_path, 'w', encoding='utf-8') as file:
        file.write(separator)
    
    with open(sections_path, 'r', encoding='utf-8') as file:
        text2 = file.read()
        # splittajmo še introduction torej [0:249423]
        matches2 = re.finditer(r'\(\b(1[0-8][0-9]|[1-9]?[0-9])\b\)\n', text2[:249422])

        positions2 = [match.start() for match in matches2]
        print(len(positions2), "\n")
        #splittamo po pos2

        sections = []
        start = 0

        for pos in positions2:
            section = text2[start:pos]
            sections.append(section)
            start = pos

        # itak moramo vse nespremenjeno appendat. Zdaj lahko samo overwritamo vse, zato [start:]
        sections.append(text2[start:]) 
        separator = "\n---\n".join(sections)
    
    with open(sections_path, 'w', encoding='utf-8') as file:
        file.write(separator)