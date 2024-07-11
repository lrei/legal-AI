import json
from bs4 import BeautifulSoup
import re

# Load the HTML content from the file
with open("data/ai-legalisation.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, "html.parser")

# Initialize the JSON structure
json_data = {
    "Chapter": "",
    "Article": "",
    "Expected date": "January 2025",
    "Summary": "",
    "paragraphs": []
}

# Extract chapter and article titles
chapter_title = soup.find("p", class_="parent-title").get_text(strip=True)
article_title = soup.find("p", id="sopen-art").get_text(strip=True)

json_data["Chapter"] = chapter_title
json_data["Article"] = article_title

# Extract summary (assuming it's available in a known tag/class)
summary = soup.find("div", class_="et_pb_text_inner").find_next("p").get_text(strip=True)
json_data["Summary"] = summary

# Extract paragraphs
content_div = soup.find("div", class_="et_pb_text_inner")
paragraphs = content_div.find_all("p")

for para in paragraphs:
    para_text = para.get_text(strip=True)
    match = re.match(r"^\(?(\d+)\)?", para_text)
    if match:
        para_number = int(match.group(1))
        json_data["paragraphs"].append({
            "paragraph": para_number,
            "content": para_text
        })

# Save the JSON data to a file
with open("article_data.json", "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, indent=4, ensure_ascii=False)

print("Data has been successfully extracted and saved to article_data.json")
