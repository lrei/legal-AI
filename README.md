
# AI Legal Assistant

## Introduction

AI Legal Assistant is a tool used for processing and analyzing legal texts related to AI with the help of a RAG application that we have developed. The project workflow consists of 4 main stages:
- scraping data from 4 AI related European regulations (European Artifical Intelligence Act, Data Act, Data Governance act and the GDPR) and parsing it into overlapping passages,
- embedding passages, storing the metadata in SQL databases and storing the embeddings separately in LanceDB files,
- creating a script that retrieves top k most relevant articles above a certain threshold using a similarity search 
- running the website on local host which constructs a prompt based on the user query and the retrieved articles which is then sent to GPT 3.5. 

## Project Workflow

### 1. Scraping and parsing data

#### Web Scraping
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

### 2. Embedding and database creation
[`embed_store_data.py`](https://github.com/makov3c/legal-AI/blob/main/embed_store_data.py) is an interactive file that has 3 main fuctions: 
- merging the 4 existing JSONs into one big one [`data/Merged/merged.json](https://github.com/makov3c/legal-AI/blob/main/data/Merged/merged.json),
- embedding each passage,
- storing metadata and embeddings. 

#### Generating Embeddings
Each passage is encoded into a high-dimensional vector (embedding) using a pre-trained language model:

- **Model Used**: [`BAAI/bge-small-en`](https://huggingface.co/BAAI/bge-small-en), which is especially suitable for generating embeddings that capture a semantic meaning.
- **Normalization**: Embeddings are normalized to unit length so we can later on compute the cosine similarity of each article. 

#### b. Storing Metadata and Embeddings 
To optimize storage and retrieval efficiency, embeddings and metadata are stored separately:

- **Metadata in SQLite Database**:
  - Metadata such as the id, regulation, chapter, article, passage number, and content are stored in their respective subfolders within the `data` directory (e.g. [`data/AI_act/ai_act.db`](https://github.com/makov3c/legal-AI/blob/main/data/AI_Act/ai_act.db)).
  - This separation allows efficient vector searches while keeping detailed metadata accessible.
- **Embeddings in LanceDB**:
  - Corresponing ids and the embedding vectors are stored in LanceDB vector databases (e.g. [`lancedb_files/AI_Act/data`](https://github.com/makov3c/legal-AI/tree/main/lancedb_files/AI_Act/embeddings.lance/data)).


### 3. Article Retrieval

When a user submits a query through the web interface, the system retrieves the most relevant articles through the following steps:

#### a. Query Embedding Generation
- The user's query is processed using the same pre-trained language model to generate an embedding.
- This embedding represents the semantic content of the query.

#### b. Similarity Search in LanceDB
- **Similarity Calculation**: The query embedding is compared against stored passage embeddings using cosine similarity.
- **Retrieving Top Matches**: The system retrieves the top 5 embeddings most similar to the query.

#### d. Article Reconstruction
- **Combining Passages**:
  - Passages belonging to the same article are combined to reconstruct the full article text.
  - Overlaps are handled to avoid duplication while preserving context.


#### e. Presenting the Results
- **Ranking**:
  - Results are ranked based on similarity scores.
- **Displaying Information**:
  - For each relevant article, the system displays:
    - Regulation Name
    - Chapter
    - Article Number and Title
    - Full Content
- **User Interface**:
  - Results are presented in a user-friendly format on the web interface.

### 4. Web Application

The Flask web application (`app.py`) provides the user interface and handles user interactions.

#### a. User Interaction
- **Query Input**: Users input their queries through a web form.
- **Results Display**: The app displays top relevant articles along with detailed information.

#### b. Application Workflow
1. **Receive Query**: The app receives the user's query from the web form.
2. **Process Query**: It calls the retrieval script to process the query and retrieve relevant articles.
3. **Render Results**: The app renders results on the web page, including constructed prompts, relevant information, and relevant chunks.

## Dependencies and Installation

### a. Python Version
- Requires Python 3.7 or higher.

### b. Required Packages
- **Flask**: Web application framework.

Install required package using pip:

```bash
pip install flask 
```
### c. Clone the repository locally
- Clone the repository from GitHub:
```bash
git clone https://github.com/makov3c/legal-AI.git
```
  - Navigate to the cloned repository:
  ```bash
  cd legal-AI
  ```

## Usage Instructions

1. **Run the Flask App locally**:

```bash
python app.py
```

2. **Access the Interface**:
   - Open your web browser and go to `http://127.0.0.1:5000/`.
   - Enter your query in the provided form.

3. **Output**:
   - After submitting your query, view the constructed prompt and the response provided by GPT 3.5.

   ![slika]()
