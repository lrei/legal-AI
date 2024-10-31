
# AI Legal Assistant

## Introduction

AI Legal Assistant is a tool for processing and analyzing legal documents related to artificial intelligence. It functions as a Retrieval-Augmented Generation (RAG) application.

The project workflow consists of four main stages:

- Data Collection: Scraping data from four AI-related European regulations (European Artificial Intelligence Act, Data Act, Data Governance Act, and the General Data Protection Regulation) and parsing it into overlapping passages.
- Embedding and Storage: Embedding passages, storing the metadata in SQLite databases, and storing the embeddings separately in LanceDB vector database files.
- Article Retrieval: Implementing an article retrieval system that retrieves the most relevant articles above a certain similarity threshold using vector similarity search.
- Web Application Development: Developing a web application that constructs a prompt based on the user's query and the retrieved articles, which is then sent to GPT-3.5 Turbo. Both the articles and the LLM response are displayed on the website.

You are required to have a valid OpenAI API key to use this application and generate responses.

## Project Workflow

### 1. Scraping and parsing data

#### Web Scraping
#### Overview
The initial step involves scraping official websites of the mentioned European regulations to collect their whole content. Each regulation has its own subfolder within the `data` directory. Within each subfolder there exists a scraping script (e.g. [`parsing_ai_act.py`](https://github.com/makov3c/legal-AI/blob/main/data/AI_Act/parsing_ai_act.py)) that extracts the content from the regulation and stores the output in a JSON file within the same folder (e.g. [`ai_act.json`](https://github.com/makov3c/legal-AI/blob/main/data/AI_Act/ai_act.json)). 

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
[`embed_store_data.py`](https://github.com/makov3c/legal-AI/blob/main/embed_store_data.py) is an interactive script that has three main fuctions: 
- merging the four existing JSONs into one -    [`data/Merged/merged.json`](https://github.com/makov3c/legal-AI/blob/main/data/Merged/merged.json),
- embedding each passage,
- storing metadata and embeddings. 

#### Generating Embeddings
Each passage is encoded into a high-dimensional vector (embedding) using a pre-trained language model:

- **Model Used**: [`BAAI/bge-small-en`](https://huggingface.co/BAAI/bge-small-en), which is especially suitable for generating embeddings that capture a semantic meaning.
- **Normalization**: Embeddings are normalized to unit length to enable the computation of cosine similarity of each article.                   

#### Storing Metadata and Embeddings 
To optimize storage and retrieval efficiency, embeddings and metadata are stored separately:

- **Metadata in SQLite Database**:
  - Metadata such as the id, regulation, chapter, article, passage number, and content are stored in their respective subfolders within the `data` directory (e.g. [`data/AI_act/ai_act.db`](https://github.com/makov3c/legal-AI/blob/main/data/AI_Act/ai_act.db)).
  - This separation allows efficient vector searches while keeping detailed metadata accessible.

- **Embeddings in [LanceDB vector database](https://github.com/lancedb/lancedb)**:
  - Corresponding ids and the embedding vectors are stored in a LanceDB vector database (e.g. [`lancedb_files/AI_Act/data`](https://github.com/makov3c/legal-AI/tree/main/lancedb_files/AI_Act/embeddings.lance/data)).


### 3. Article Retrieval
#### Overview
[`retrieving_articles.py`](https://github.com/makov3c/legal-AI/blob/main/app-public/retrieving_articles.py) is a script that retrieves the most relevant articles with respect to the user's query by comparing their cosine similarity.

#### Workflow

#### 1. Query Embedding Generation
The user's query is first normalized using the same pre-trained language model to generate an embedding that is comparable to other embeddings stored in the LanceDB vector database.

#### 2. Similarity Search in LanceDB
- **Similarity Calculation**: The user query embedding is compared against stored passage embeddings using [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity).
- **Retrieving Top Matches**: The LanceDB database is then searched for the most similar embeddings to the query, retrieving an initial set of candidate passages. 

#### 3. Filtering Candidate Passages and Re-ranking model 
- Retrieves metadata for each candidate passage from the SQLite database.
- Creates input pairs of [query_text, passage_text] for each candidate passage which are necessary inptus for the re-ranking model. 
- Using a model from sentence-transformers, [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), to compute a relevance score for each query-passage pair. It provides a more accurate assessment of relevance by considering the context and semantics of both texts together.

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
There are two versions of the web application:

1. Public version [app_public.py](https://github.com/makov3c/legal-AI/blob/main/app-public/app_public.py): Designed for public users, this version uses default parameters and provides a user-friendly interface. Users can input their legal queries and receive responses without needing to configure any settings. An OpenAI API key is required to generate responses. 
At the bottom of the page there are six example queries from real articles that were picked carefully to illustrate how a query should be worded in order to receive an accurate responsef from the LLM. 

2. Testing version [app_testing.py](https://github.com/makov3c/legal-AI/blob/main/app-testing/app_testing.py): Intended for testing and development purposes, this version allows users to configure various parameters such as the OpenAI model to use, maximum tokens, number of responses, temperature, and models for sentence embedding and re-ranking. Users can also choose to store their API key for the session in order to make mass generating an easier task. 

Both applications use FastAPI for handling web requests and Uvicorn as the ASGI server. They share similar workflows for processing user queries and generating responses.

#### Workflow
#### User Input:
Users enter their legal query and OpenAI API key in the provided form. 

#### Article Retrieval:
The application uses the retrieving_articles.py script to fetch relevant legal passages based on the user's query.
A prompt template is used to incorporate both the user's query and the retrieved context.
The prompt is formatted to guide the language model in generating an appropriate response.

#### LLM Response Generation:

The constructed prompt is sent to the OpenAI language model (GPT-3.5 Turbo) to generate a response.
The application uses the OpenAI API, with the user's API key, to obtain the response from the model.

#### Displaying Results:
The user's query, the retrieved articles, the constructed prompt, and the LLM's response are displayed on the web interface.


## Dependencies and Installation

### a. Python Version
- Requires Python 3.9 or higher.

### b. Clone the repository locally
- Clone the repository from GitHub:
```bash
git clone https://github.com/makov3c/legal-AI.git
```

## Usage Instructions
### - Running the app within a virtual environment (Preferred)
1. Navigate to the cloned repository and create a virtual Python environment:

```bash
cd legal-AI
python -m venv myenv
myenv\Scripts\activate
pip install -r package_requirements.txt
```

2. Edit run_app.bat:

- Navigate to the cloned folder and open run_app.bat file with notepad.
- Adjust the third line with the absolute path of the same directory, for example "cd /d C:\Users\User\legal-AI".
- Save the file.

3. Run the file to access the website. 



**OR**

If you have all the required packages already installed on your PC:

Run the Uvicorn application locally
  ```bash
  cd legal-AI
  cd app-public
  python app_public.py
  ```
After running the file you should see this message:

![uvicorn](https://github.com/user-attachments/assets/4253e095-9779-42be-9101-f6aad1c3673b)


Access the Interface:
   - Open your web browser and navigate to [http://localhost:8001/](http://localhost:8001/).
   - Enter your query in the provided form.
   - Enter your OpenAI API key in the provided form.
   - Press submit and view the results.

### - Deploying via Docker
1. Make sure you have the [Docker Destop](https://www.docker.com/products/docker-desktop/) installed on your PC.
2. Navigate to the cloned repository and build the Docker image:

```bash
cd legal-AI
docker build --no-cache -t legal-ai-app .
```
Building the image can take up to 10 minutes. 

3. Create the Docker container: 

```bash
docker run -d -p 8001:8001 --name legal-ai-container legal-ai-app
```

4. Open the Docker Destop app and click on Containers. Click on "legal-ai-container" and start the container. 

![docker](https://github.com/user-attachments/assets/13817248-6948-4389-9d77-c61820c2d7a2)

5. Access the interface on [http://localhost:8001/](http://localhost:8001/).

![ai_interface](https://github.com/user-attachments/assets/8259c907-afb5-4724-a170-3be874d71821)

