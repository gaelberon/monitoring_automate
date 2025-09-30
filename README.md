# Automated Technology Monitoring &amp; Content Summarization

This project is an automated pipeline designed to monitor various content sources, summarize the findings using a Large Language Model (LLM), and deliver the results in a structured email report. It's built to help users stay informed about the latest developments in technology, AI research, and other areas of interest with minimal manual effort.

## What it does

The core purpose of this project is to automate the process of technology watch and content curation. It connects to different sources, processes the information, and presents it in a digestible format.

### Key Features

-   **Multi-Source Content Aggregation**: Fetches data from various platforms:
    -   YouTube channels (for tech reviews, debates, entertainment, etc.)
    -   AI research paper repositories (e.g., Hugging Face Papers)
    -   Technology news articles (e.g., ActuIA)
-   **AI-Powered Summarization**: Utilizes a powerful LLM (likely Google's Gemini/Vertex AI) to generate concise and accurate summaries of the collected content.
-   **Customizable Prompts**: Employs a sophisticated templating system (`/templates` directory) with tailored prompts for different content types (technical videos, debates, research papers) to ensure high-quality, structured summaries.
-   **Automated Reporting**: Formats the generated summaries into a clean HTML table and prepares it for email delivery.

## How it Works

The pipeline follows a simple, yet powerful, workflow:

1.  **Authentication**: The script first authenticates with Google APIs using OAuth 2.0 (`client_secret_...json`, `token.json`) for accessing YouTube data and a service account (`healthy-fuze-...json`) for Google Cloud AI services.
2.  **Data Collection**: It connects to the specified sources (e.g., a list of YouTube channels, RSS feeds, or preprint servers) to gather new content like videos, articles, and papers.
3.  **Content Processing &amp; Summarization**: For each piece of content, the system prepares a detailed prompt using the templates found in the `/templates` directory. This prompt, along with the content (e.g., video transcript, article text), is sent to the LLM.
4.  **Summary Generation**: The LLM processes the request and returns a structured summary, which may include key topics, methodologies, results, and potential follow-up questions as defined in the prompt templates.
5.  **Report Assembly**: The summaries are collected and formatted into an HTML report using the `templates/email_template_monitoring_content.html` template, ready to be sent via email.

## Setup and Usage

### 1. Prerequisites

-   Python 3.8+ (The `.python-version` file specifies 3.5.10, which is outdated and not recommended. The dependencies will likely require a more modern version).
-   A Google Cloud Project with the **YouTube Data API v3** and **Vertex AI API** enabled.

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

1.  **Google Cloud OAuth 2.0 Credentials (for YouTube):**
    -   Go to the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
    -   Create an "OAuth 2.0 Client ID" for a "Desktop app".
    -   Download the JSON file and place it in the root of the project. Ensure its name matches the one in `.gitignore` (e.g., `client_secret_....json`).
    -   The first time you run the script, you will be prompted to authorize access in your browser. This will generate the `token.json` file.

2.  **Google Cloud Service Account (for AI Platform):**
    -   In the Google Cloud Console, navigate to "IAM & Admin" > "Service Accounts".
    -   Create a new service account with the "Vertex AI User" role.
    -   Create a key for this service account, download the JSON file, and place it in the project root (e.g., `healthy-fuze-...json`).

### 4. Running the Project

Execute the main script to start the monitoring and summarization process.
```bash
python main.py
```
*(Note: The main script file is not provided in the context; `main.py` is a placeholder name.)*

## Project Structure

```
.
├── templates/                  # Prompt and email templates
│   ├── prompt_...md            # Various prompts for the LLM
│   └── email_...html           # HTML template for the email report
├── .gitignore                  # Files and directories to ignore
├── requirements.txt            # Python dependencies (New)
├── README.md                   # Project explanation (This file)
├── token.json                  # Generated OAuth token for YouTube API
├── client_secret_...json       # OAuth client credentials
└── healthy-fuze-...json        # Service account credentials for GCP
```