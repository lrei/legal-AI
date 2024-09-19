
# AI Legal Assistant

This project focuses on processing and analyzing legal texts related to AI regulations such as the GDPR, the European Data Act, the European Artificial Intelligence Act, and the European Data Governance Act.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Project Workflow](#project-workflow)
   - [1. Data Collection](#1-data-collection)
   - [2. Embedding Generation and Data Storage](#2-embedding-generation-and-data-storage)
   - [3. Article Retrieval Process](#3-article-retrieval-process)
   - [4. Web Application](#4-web-application)
3. [Scripts and Utilities](#scripts-and-utilities)
4. [Dependencies and Installation](#dependencies-and-installation)
5. [Usage Instructions](#usage-instructions)

## Project Overview
The AI Legal Assistant aims to facilitate easy access to complex legal documents related to AI regulations. By leveraging natural language processing and vector embeddings, users can query the system in plain language and retrieve the most relevant legal articles.

## Project Workflow

### 1. Data Collection

#### a. Web Scraping
The initial step involves scraping official websites or repositories to collect the full text of each of the four regulations. Each regulation has its own subfolder within the `data` directory (e.g., `data/AI_Act`, `data/GDPR`). Within each subfolder:

- **Scraping Scripts**: Scripts like `scrape_ai_act.py` are used to download and extract the text of the regulations.
- **Output Data**: The scraped data is saved as JSON files, maintaining the hierarchical structure of the regulations.

#### b. Parsing and Structuring the Data
After scraping, the legal texts are parsed into smaller, manageable passages:

- **Passage Length and Overlap**: Passages are created with a defined length and overlap to ensure context is preserved across passages.
- **Structured Data**: Each passage includes metadata such as regulation name, chapter, article, passage number, and content.
- **Data Storage**: The structured passages are saved as JSON files for each regulation.

### 2. Embedding Generation and Data Storage

#### a. Generating Embeddings
Each passage is encoded into a high-dimensional vector (embedding) using a pre-trained language model:

- **Model Used**: `BAAI/bge-small-en`, suitable for generating embeddings that capture semantic meaning.
- **Process**:
  - **Tokenization**: Passages are tokenized using the model's tokenizer.
  - **Embedding**: Tokens are passed through the model to obtain embeddings.
- **Normalization**: Embeddings are normalized to unit length to facilitate accurate similarity calculations.

#### b. Storing Embeddings and Metadata
To optimize storage and retrieval efficiency, embeddings and metadata are stored separately:

- **Embeddings in LanceDB**:
  - Only the `id` (unique identifier) and the embedding vector are stored.
  - LanceDB is a vector database optimized for efficient similarity searches.
- **Metadata in SQLite Database**:
  - Metadata such as regulation, chapter, article, passage, and content are stored.
  - This separation allows efficient vector searches while keeping detailed metadata accessible.

**Process Flow**:

1. **Insert Metadata**: Passages are inserted into the SQLite database, which assigns an `id` to each entry.
2. **Store Embeddings**: Corresponding embeddings, along with their `id`s, are stored in LanceDB.

### 3. Article Retrieval Process

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

## Scripts and Utilities

- **Data Scraping and Parsing Scripts**:
  - Located in each regulation's subfolder within the `data` directory.
  - Responsible for downloading and extracting legal texts.
  - Used to parse scraped data into structured passages.

- **Embedding and Storage Script**: `create_sql_and_store_embeddings.py` is an interactive file that:
  - Merges JSON files.
  - Generates embeddings for passages.
  - Stores embeddings in LanceDB and metadata in SQLite databases.
  - Deletes old LanceDB files before creating new ones to optimize storage.

- **Article Retrieval Script**: `retrieving_articles.py`
  - Processes user queries.
  - Performs similarity searches in LanceDB.
  - Retrieves and reconstructs relevant articles using the SQLite database.

- **Web Application Script**: `app.py`
  - Implements the Flask web application.
  - Handles routes, user input, and rendering templates.

## Dependencies and Installation

### a. Python Version
- Requires Python 3.7 or higher.

### b. Required Packages
- **Flask**: Web application framework.

Install required package using pip:

```bash
pip install flask 
```

## Usage Instructions

1. **Start the Flask App**:

```bash
python app.py
```

2. **Access the Interface**:
   - Open your web browser and go to `http://127.0.0.1:5000/`.
   - Enter your query in the provided form.

3. **View Results**:
   - After submitting your query, view the constructed prompt, relevant information, and relevant chunks on the results page.
