
# AI Legal Assistant

## Introduction

AI Legal Assistant is a tool used for processing and analyzing legal texts related to AI with the help of a RAG application that we have developed. The project workflow consists of 4 main stages:
- scraping data from 4 AI related European regulations (European Artifical Intelligence Act, Data Act, Data Governance act and the GDPR) and parsing it into overlapping passages,
- embedding passages, storing the metadata in SQL databases and storing the embeddings separately in LanceDB files,
- creating a script that retrieves top k most relevant articles above a certain threshold using a similarity search 
- running the website on localhost which constructs a prompt based on the user query and the retrieved articles which is then sent to GPT-3.5 Turbo. 

## Project Workflow

### 1. Scraping and parsing data

#### Web Scraping
#### Overview
The initial step involves scraping official websites of the mentioned European regulations to collect their whole content. Each regulation has its own subfolder within the `data` directory. Within each subfolder there exists a scraping script (e.g. [`data/AI_Act/parsing_ai_act.py`](https://github.com/makov3c/legal-AI/blob/main/data/AI_Act/parsing_ai_act.py)) that extracts the content from the regulation and stores the output in a JSON file within the same folder (e.g. [`data/AI_Act/ai_act.json`](https://github.com/makov3c/legal-AI/blob/main/data/AI_Act/ai_act.json)). 

#### Workflow
1. **Requesting Pages**: Sends HTTP GET requests for each article.
2. **Parsing HTML**: Uses BeautifulSoup to extract relevant data.
3. **Extracting Data**: Extracting chapter name, article name and article content by manipulating tags within the HTML structure of websites and using regular expressions to filter out unwanted content. 

#### Parsing Passages
After scraping the content, the legal texts are parsed into smaller, manageable passages:

- **Passage Structure**: Passages are created with a defined length and overlap to ensure context is preserved across passages belonging to the same article.
- **Metadata**: Each passage includes metadata such as regulation name, chapter, article, passage number, and content.
- **Saving passages**: All passages are stored along with their metadata in a JSON file. 

![json](https://github.com/user-attachments/assets/ff5a7d79-cf7b-4861-86ee-62267168edc5)

### 2. Embedding and database creation
#### Overview
[`embed_store_data.py`](https://github.com/makov3c/legal-AI/blob/main/embed_store_data.py) is an interactive file that has 3 main fuctions: 
- merging the 4 existing JSONs into one -    [`data/Merged/merged.json](https://github.com/makov3c/legal-AI/blob/main/data/Merged/merged.json),
- embedding each passage,
- storing metadata and embeddings. 

#### Generating Embeddings
Each passage is encoded into a high-dimensional vector (embedding) using a pre-trained language model:

- **Model Used**: [`BAAI/bge-small-en`](https://huggingface.co/BAAI/bge-small-en), which is especially suitable for generating embeddings that capture a semantic meaning.
- **Normalization**: Embeddings are normalized to unit length so we can later on compute the cosine similarity of each article. 

#### Storing Metadata and Embeddings 
To optimize storage and retrieval efficiency, embeddings and metadata are stored separately:

- **Metadata in SQLite Database**:
  - Metadata such as the id, regulation, chapter, article, passage number, and content are stored in their respective subfolders within the `data` directory (e.g. [`data/AI_act/ai_act.db`](https://github.com/makov3c/legal-AI/blob/main/data/AI_Act/ai_act.db)).
  - This separation allows efficient vector searches while keeping detailed metadata accessible.

- **Embeddings in [LanceDB vector database](https://github.com/lancedb/lancedb)**:
  - Corresponding ids and the embedding vectors are stored in a LanceDB vector database (e.g. [`lancedb_files/AI_Act/data`](https://github.com/makov3c/legal-AI/tree/main/lancedb_files/AI_Act/embeddings.lance/data)).


### 3. Article Retrieval
#### Overview
[`retrieving_articles.py`](https://github.com/makov3c/legal-AI/blob/main/retrieving_articles.py) is a script that retrieves the most relevant articles in regards to the provided user query which are then displayed on the website.

#### Workflow

#### 1. Query Embedding Generation
The user's query is first normalized using the same pre-trained language model, BGE small, to generate an embedding that is comparable to other embeddings stored in the LanceDB vector database.

#### 2. Similarity Search in LanceDB
- **Similarity Calculation**: The user query embedding is compared against stored passage embeddings using [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity).
- **Retrieving Top Matches**: The LanceDB database is then searched for the most similar embeddings to the query, retrieving an initial set of candidate passages. 

#### 3. Filtering Candidate Passages and Re-ranking model 
- Retrieves metadata for each candidate passage from the SQLite database.
- Creates input pairs of [query_text, passage_text] for each candidate passage which are necessary inptus for the re-ranking model. 
- [The Cross-Encoder model MS Marco](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2) computes a relevance score for each query-passage pair. It provides a more accurate assessment of relevance by considering the context and semantics of both texts together.

#### 4. Presenting the Top Results
- Selects the top k passages based on the re-ranked scores.
- Passages belonging to the same article are combined to reconstruct the full article text. 
- **Displaying Information**:
  For each relevant article, the system displays:
    - Regulation name,
    - Chapter number and title,
    - Article number and title,
    - Full content.

### 4. Web Application and LLM Integration
#### Overview
By running [`app.py`](https://github.com/makov3c/legal-AI/blob/main/app.py) you are able to run the website on localhost. It provides a Flask wesbsite with a minimalistic user interface that accepts a user query.
The script captures the input and runs the external script [`retrieving_articles.py`](https://github.com/makov3c/legal-AI/blob/main/retrieving_articles.py) to fetch relevant text chunks and assemble a detailed prompt incorporating the user's query and the retrieved context. This prompt is then sent to the ChatGPT model to generate a response. The script concludes by displaying the constructed prompt and the generated response, providing both for review.

## Dependencies and Installation

### a. Python Version
- Requires Python 3.7 or higher.

### b. Required Packages
- **Uvicorn**: Web server implementation for Python.

Install required package using pip:

```bash
pip install uvicorn 
```
### c. Clone the repository locally
- Clone the repository from GitHub:
```bash
git clone https://github.com/makov3c/legal-AI.git
```
## Usage Instructions
1. **Navigate to the cloned repository and run the Uvicorn application locally**:
  ```bash
  cd legal-AI
  cd app-public
  python app_public.py
  ```
After running the file you should see this message

![uvicorn](https://github.com/user-attachments/assets/8fd1eb7b-e8a2-4979-b893-d15c8f06d9de)

2. **Access the Interface**:
   - Open your web browser and go to `http://127.0.0.1:8001/`.
   - Enter your query in the provided form.
   - Enter your OpenAI API key in the provided form.
   - Press submit.

3. **Output**:
   - After submitting your query, view the constructed prompt that contains all relevant retrieved articles along with the response provided by GPT-3.5 Turbo.
   
   ![query](https://github.com/user-attachments/assets/c6610178-3ba2-4056-863b-1c9e94f17802)

