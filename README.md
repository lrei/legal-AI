# AI Legal Assistant

This document outlines the workflow for processing and analyzing AI-related legal texts, consisting of three main stages: web scraping, database creation, and vector encoding with semantic search. Special attention is given to the vector encoding process, which enhances search capabilities.

## 1. Web Scraping 

### Overview
The ([`web-scrape.py`](https://github.com/makov3c/ijs/blob/main/web-scrape.py)) script extracts AI-related legal texts from a website. It gathers articles, chapters, enforcement dates, summaries, and paragraph texts.

### Workflow
1. **Requesting Pages**: Sends HTTP GET requests for each article.
2. **Parsing HTML**: Uses BeautifulSoup to extract relevant data.
3. **Extracting Data**:
   - **Chapter and Article**: From `<h1>` and specific paragraphs.
   - **Expected Date and Summary**: From designated paragraph classes.
   - **Paragraph Texts**: Using regex for numbered paragraphs.
4. **Storing Data**: Saves extracted data in [`data/ai_article_data.json`](https://github.com/makov3c/ijs/blob/main/data/ai_article_data.json).

### TODO
- **Optimization**: Direct parsing from the response object could be more efficient.
- **Single Paragraph Handling**: Requires special processing (e.g. Article 16)
- Chapter titles are not fetched properly

## 2. Storing into a database

### Overview
The [`create-db.py`](https://github.com/makov3c/ijs/blob/main/create-db.py) script creates and populates a SQLite database ([`data/blocks.db`](https://github.com/makov3c/ijs/blob/main/data/blocks.db) with the scraped data. This will later be useful for converting into vector form.

Imports data from the JSON file and creates a SQLite database with a `blocks` table for storing data. Then it inserts chapter, article title, expected date of going into force, article summary and the number of the paragraph along with the relevant text.

The article title, along with summary and the expected date of the enforcement is duplicated with each paragraph, that belongs to the same article.

## 3. Vector Encoding and Semantic Search

### Overview
The [`vec-encoding.py`](https://github.com/makov3c/ijs/blob/main/vec-encoding.py) script performs vector encoding and semantic search, converting text into high-dimensional vectors for advanced search functionalities.

First, the script connects to an SQLite database and extracts legal text documents, which are then indexed in Elasticsearch. This involves setting up an Elasticsearch index named documents, where each document from the database is formatted and uploaded in bulk.

The core of the script is the use of the BAAI/bge-base-en-v1.5 model from SentenceTransformers. This model is utilized to convert the documents into high-dimensional vectors, capturing their semantic content. The script then normalizes these embeddings to ensure consistency in the vector space.

#### Setting up Elasticsearch locally
Download Ellasticsearch and run this command in cmd:
```
bin\elasticsearch.bat
```
You can check if Elasticsearch cluster is running by visiting `http://localhost:9200` where you should see a JSON response.

#### How it works
When a search query is issued, the script starts by encoding the query into a vector. It performs an initial search using Elasticsearch, which retrieves documents based on keyword matches. The script then refines these results by comparing the query vector to the vectors of the top retrieved documents. This process involves re-ranking the documents using semantic similarity, rather than just keyword frequency.

Finally, the script retrieves and displays the re-ranked documents, providing results that are more contextually relevant and semantically aligned with the query. This approach ensures that the search results reflect the true meaning behind the query, offering more accurate and meaningful information.

### Usage
If you only want to get the relevant acts, witout the use of LLMs, provide a query text as a command-line argument:
```python
python vec-encoding.py "AI Legalisation and Documentation keeping"
```

## 4. LLM Integration

This script integrates OpenAI's ChatGPT to generate responses that are both relevant and contextually accurate, based on user queries and additional information retrieved through a vector encoding process. It automates the interaction with the ChatGPT API, extracts relevant textual data through a subprocess, and combines these elements to produce a well-formed response.

 It handles the sequence of processing user queries by first capturing the input, running an external script [`vec-encoding.py`](https://github.com/makov3c/ijs/blob/main/vec-encoding.py) to fetch relevant text chunks, and assembling a detailed prompt incorporating the user's query and the retrieved context. This prompt is then sent to the ChatGPT model to generate a response. The script concludes by displaying the constructed prompt and the generated response, providing both for review.

## Running application locally
First, install Flask (if its not already installed) using pip
```python
pip install flask
```

Then run the application with command
```python
python app.py
```

Open your web browser and navigate to `http://127.0.0.1:5000/`. Write your query in the query interface and click enter. The answers will be displayed shortly. 

![slika](https://github.com/user-attachments/assets/17fcf71e-a561-4202-889b-ec0baa1e947f)

