"""
websites_specific.py


"""

# Standard library imports
import os
import json
import re
# import time
from datetime import datetime
from typing import List, Dict

# Third party imports
import requests
from bs4 import BeautifulSoup
# import html2text

# Local resources imports
from utils import config
from utils import extract_node_values
# from utils import json_to_html
# from utils import send_email
from utils import download_pdf
# from utils import filter_unknown_items
# from utils import summarize_from_pdf_file
# from utils import summarize_from_text_content
from utils import process_list_of_items

# List of recipients for email sending
# list_email_recipients = [config["recipient.gael.beron.fr"], config["recipient.gael.beron.gmail.com"], config["recipient.gael.beroons.hotmail.com"], ]

# Temporary folder to store downloaded PDFs
# tmp_raw_sources_dir = "tmp_raw_sources_dir"
# Data Dir containing the json file with the list of all downloaded sources for a given day
# data_dir = "data"
# Create 'data' directory if it doesn't exist
os.makedirs(config["json.key.data.dir"], exist_ok=True)

# Create tmp_raw_sources_dir directory if it doesn't exist
os.makedirs(
    config["json.key.tmp.raw.sources.dir"], exist_ok=True
)

def pull_new_hf_papers(data_file_path: str) -> List[Dict]:
    """
    Fetches information about daily papers from Hugging Face's papers page and downloads their PDFs.

    This function retrieves details about new papers on Hugging Face's papers page,
    extracts information like title, authors, link, and arXiv ID. It then attempts to 
    download the corresponding PDF and stores the details along with the PDF path in a dictionary.
    Finally, it returns a list containing dictionaries for each paper found.
    
    **Args:**
    data_file_path (str): The path to the json data file to store the papers from Hugging Face.

    **Returns:**
        A list of dictionaries. Each dictionary is an article that contains the following attributes:
            * `title (str)`: The title of the article,
            * `authors (list)`: The list of authors of the article,
            * `link (str)`: The URL of the article,
            * `pdf_path (str)`: The local path where the PDF is saved (if downloaded).
    """
    
    # Fetch the Hugging Face papers page content
    response = requests.get(config["key.json.hf.url"])
    soup = BeautifulSoup(response.content, "html.parser")

    # Initialize empty list to store paper details and set to track seen arXiv IDs
    hf_papers: List[Dict[str, str, str, str]] = []
    seen_ids = set()  # Set to track seen arXiv IDs
    arxiv_id = None
    
    # Check if an existing JSON file stores previously processed Hugging Face Papers
    # print(f"data_file_path: {data_file_path}") # For Debug Only
    if os.path.isfile(data_file_path) is True:
        # Load list of previously processed articles from the JSON file
        with open(data_file_path) as fp:
            # Extract and store a set of IDs from previously processed papers
            seen_ids = extract_node_values(json.load(fp),
                                           config["key.json.id"]) # Set to track seen HF Papers IDs
        # print(f"Already seen IDs: {', '.join(seen_ids)}") # For Debug Only
    
    # Define directory for storing downloaded PDFs (using configuration key)
    hf_pdfs_dir = config["json.key.tmp.raw.sources.dir"] + "/hf_pdfs"
    
    # Create tmp_raw_sources_dir/hf_pdfs directory if it doesn't exist
    os.makedirs(
        hf_pdfs_dir, exist_ok=True
    )

    # Loop through relevant div elements containing paper information
    # iter = 1 # For Debug Only
    for paper_div in soup.find_all("div", class_="w-full"):
        # Extract paper title
        title_tag = paper_div.find("a", class_="line-clamp-3")
        if title_tag:
            title = title_tag.text.strip()
        else:
            print("Title not found for a paper")
            continue

        # Extract arXiv ID from the paper link
        link = title_tag["href"]
        arxiv_id_match = re.search(r"/papers/(\d+\.\d+)", link)
        if arxiv_id_match:
            arxiv_id = arxiv_id_match.group(1)
        else:
            print(f"Could not extract arXiv ID from link: {link}")
            continue

        # Check for duplicate papers based on arXiv ID
        if arxiv_id in seen_ids:
            # print(f"Duplicate paper detected with ID {arxiv_id}, skipping.") # For Debug Only
            continue
        seen_ids.add(arxiv_id)  # Add ID to set of seen IDs

        # Extract the list of authors
        authors = []
        for li in paper_div.find_all("li"):
            author = li.get("title")
            if author:
                authors.append(author)

        # Construct the full link to the paper on arXiv.org
        full_link = f"https://arxiv.org/abs/{arxiv_id}"

        # Attempt to download the PDF and store details if successful
        pdf_path = os.path.join(hf_pdfs_dir, f"{arxiv_id}.pdf")
        if download_pdf(arxiv_id, pdf_path):
            hf_papers.append(
                {
                    config["key.json.id"]: arxiv_id,
                    config["key.json.title"]: title,
                    config["key.json.authors"]: ", ".join(authors),
                    config["key.json.link"]: full_link,
                    config["key.json.pdf.path"]: pdf_path,
                }
            )
        else:
            print(f"Failed to download PDF for {arxiv_id}")
    
        # if iter == 1:   # For Debug Only
        #     break       # For Debug Only
        # iter = iter + 1 # For Debug Only
    
    # Return the list of dictionaries containing paper details
    return hf_papers

def process_hf_daily() -> None:
    """
    This function aims to process daily Hugging Face papers by performing the following tasks:

    1. Retrieves a list of daily papers from Hugging Face using `pull_new_hf_papers`.
    2. Attempts to summarize each paper using a large language model (summarize_from_pdf_file).
    3. Handles potential summarization failures by trying a different model.
    4. Cleans up temporary PDF files and replaces line breaks in summaries.
    5. Exports the processed papers with summaries to a JSON file.
    6. Sends an email notification to the provided recipients with details and summaries.
    """
    
    # Retrieve the path of the json data file with all preprocessed Hugging Face Papers
    hf_data_file_path = os.path.join(config["json.key.data.dir"],
                                     f"EVER{config['key.json.hf.file.suffix']}.json")
    # Retrieve the new papers from Hugging Face, download PDF file locally and load the json list
    # papers with details in a list 'hf_papers'
    hf_papers = pull_new_hf_papers(data_file_path = hf_data_file_path) # Get list of paper details
    
    # Retrieve current date
    date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"""
    {date} - {len(hf_papers)} new Hugging Face Papers:""") # For Debug Only
    # print(f"""{''.join(f"""
    #     => ID: {curr_paper[config['key.json.id']]}
    #        Title: {curr_paper[config['key.json.title']]}""" for curr_paper in hf_papers)}""") # For Debug Only
    
    # Initialize email_details with the list of recipients and the subject
    email_details = {config["key.json.email.detail.recipients"]: config["key.json.hf.papers.recipients"],
                     config["key.json.email.detail.subject"]: f"{config['key.json.monitoring.category.techno']} - {date} - {config['key.json.hf.source.name']} Papers"
    }
    
    # Process the list of articles
    process_list_of_items(
        source_name = config["key.json.hf.source.name"],
        source_format = config["key.json.source.format.pdf"],
        data_file_path = hf_data_file_path,
        known_items_json_key = config["key.json.link"],
        new_items = hf_papers,
        smtp_server_details = config["smtp.server.details.gmail"],
        email_details = email_details,
        keys_to_ignore = [config["key.json.id"], config["key.json.pdf.path"],], # Ignore key 'pdf_path' from the HTML to generate
        summarize_it = True
    )

def pull_new_actuia_articles(domain_name: str,
                             data_file_path: str) -> None:
    """
    Fetches new articles from ActuIA for a specific domain and sends notifications.

    This function performs the following tasks:

    1. Scrapes ActuIA's website for articles related to the provided domain.
    2. Extracts information from each article, including title, author, thumbnail URL,
       date, content, and summary (using a large language model).
    3. Saves the extracted information for new articles to a JSON file.
    4. Sends an email notification to recipients if new articles are found.

    **Args:**
        domain_name (str): The name of the domain to be considered when scraping ActuIA articles.
        data_file_path (str): The path to the json data file to store the articles from ActuIA for a given domain.
        
    **Returns:**
        A list of dictionaries. Each dictionary is an article that contains the following attributes:
            * `title (str)`: The title of the article,
            * `author (list)`: The author of the article,
            * `thumbnailUrl (str)`: The URL of the thumbnail image to illustrate the article,
            * `date (str)`: The date of the article,
            * `link (str)`: The URL of the article,
            * `content (str)`: The content of the article.
    """
    # Print information about processing ActuIA articles
    print(f"Retrieving new articles from ActuIA website for the domain: '{domain_name}'")
    # Fetch the ActuIA website content for the specified domain
    response = requests.get(config["key.json.actuia.url"]+domain_name+"/")
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Initialise the list of articles to store with their paramaters:
    # - title
    # - author
    # - image_url
    # - date
    # - link
    # - content
    # - summary (filled in later)
    
    ## Local variables
    # Initialize empty list to store article details and sets to track seen articles
    actuia_articles: List[Dict[str, str, str, str, str, str]] = []
    seen_urls = set() # Set to track already seen ActuIA article URLs
    # Check if an existing JSON file stores previously processed ActuIA articles
    # print(f"data_file_path: {data_file_path}") # For Debug Only
    if os.path.isfile(data_file_path) is True:
        # Load list of previously processed articles from the JSON file
        with open(data_file_path) as fp:
            # Extract and store a set of URLs from previously processed articles
            seen_urls = extract_node_values(json.load(fp),
                                            config["key.json.link"]) # Set to track seen ActuIA articles URLs
        # print(f"Already seen URLs: {', '.join(seen_urls)}") # For Debug Only
    
    # Loop through ActuIA articles in reverse order (latest first)
    # Locate the relevant div elements
    # <div class="td_module_16 td_module_wrap td-animation-stack">
    # iter = 1 # For Debug Only
    # for actuia_article_div in soup.find_all("div", class_="td_module_16 td_module_wrap td-animation-stack"):
    # Start from the end of the list of articles
    my_resultset = soup.find_all("div", class_="td_module_16 td_module_wrap td-animation-stack")
    # for current_div_index in range(len(my_resultset))[::-1]:
    #     actuia_article_div = my_resultset[current_div_index]
    for current_div_index in range(len(my_resultset)): # Reverse loop for latest first
        # print(f"Length of the list of articles: {len(my_resultset)}") # For Debug Only
        # print(f"Current index: {len(my_resultset)-1-current_div_index}") # For Debug Only
        # print(f"Dealing with ActuIA article of index #{len(my_resultset)-1-current_div_index}") # For Debug Only
        actuia_article_div = my_resultset[len(my_resultset)-1-current_div_index]
        
        # Extract title, URL, and check for duplicates
        # <a href="https://www.actuia.com/actualite/my-article-URL/" rel="bookmark" title="my_article_title">
        title_tag = actuia_article_div.find("a", class_="")
        post_title = ""
        if title_tag:
            post_title = title_tag.text.strip()
        else:
            print("Title not found for an article in ActuIA")
            continue
        # print(f"=> ActuIA article title: {post_title}") # For Debug Only
        
        # Extract the paper ID from the link
        article_url_match = re.search(r"^(https:\/\/www\.actuia\.com\/.*\/)$", title_tag["href"])
        if article_url_match:
            article_url = article_url_match.group(1)
        else:
            print(f"Could not recognize ActuIA URL from link: {title_tag['href']}")
            continue
        # print(f"=> ActuIA article URL: {article_url}") # For Debug Only
        
        # Check for duplicates using ActuIA article URL
        if article_url in seen_urls:
            # print(f"Duplicate article detected with URL {article_url}, skipping.") # For Debug Only
            continue
        seen_urls.add(article_url) # Add unique URL to seen URLs
        
        # Extract additional information (image URL, author, date)
        # <img width="150" height="85" class="entry-thumb webpexpress-processed" src="https://my-thumbnailUrl" alt="" title="my_article_title">
        # <img width="150" height="85" class="entry-thumb" src="https://my-thumbnailUrl" alt="" title="my_article_title"/>
        image_url = actuia_article_div.find("img", class_="entry-thumb webpexpress-processed")
        if image_url:
            image_url = image_url['src']
        else:
            image_url = actuia_article_div.find("img", class_="entry-thumb")
            if image_url:
                image_url = image_url['src']
            else:
                print(f"Could not recognize image URL: {image_url}")
        # print(f"ActuIA article image URL: {image_url}") # For Debug Only
        post_author = actuia_article_div.find("span", class_="td-post-author-name")
        if post_author:
            post_author = post_author.text.replace("-","").strip()
        else:
            print(f"Could not recognize post author: {post_author}")
        # print(f"ActuIA article author: {post_author}") # For Debug Only
        post_date = actuia_article_div.find("span", class_="td-post-date")
        if post_date:
            post_date = post_date.text.strip()
        else:
            print(f"Could not recognize post date: {post_date}")
        # print(f"ActuIA article date: {post_date}") # For Debug Only
        
        # Extract article content
        response_article = requests.get(article_url)
        soup_article = BeautifulSoup(response_article.content, "html.parser")
        # print(f"ActuIA article content: {soup_article}")
        # Locate the relevant div element
        # <div class="entry-content">
        post_content = soup_article.find("div", class_="entry-content")
        # post_content = html2text.html2text(soup_article.find("div", class_="entry-content"))
        if not post_content:
            post_content = soup_article.find("div", class_="tdb-block-inner td-fix-index")
        if post_content:
            post_content = post_content.text.strip()
        else:
            print(f"Could not recognize post content: {article_url}")
        
        # if post_content:
        #     post_content = post_content.text.strip()
        # else:
        #     # <div class="tdb-block-inner td-fix-index">
        #     post_content = soup_article.find("div", class_="tdb-block-inner td-fix-index")
        #     if post_content:
        #         post_content = post_content.text.strip()
        #     else:
        #         print(f"Could not recognize post content: {post_content}")
        # print(f"ActuIA article content: {post_content}")
        
        # Add article details to the list 'actuia_articles'
        actuia_articles.insert(0, {
            config["key.json.title"]: post_title,
            config["key.json.author"]: post_author,
            config["key.json.thumbnail.url"]: image_url,
            config["key.json.date"]: post_date,
            config["key.json.link"]: article_url,
            config["key.json.content"]: post_content
            })
        
    # Return the list of articles from ActuIA website with extracted details
    return actuia_articles

def process_actuia_daily() -> None:
    """
    This function aims to process daily Hugging Face papers by performing the following tasks:
    
    1. Retrieves a list of daily articles from ActuIA using `pull_new_hf_papers(`.
    2. Attempts to summarize each paper using a large language model (summarize_from_pdf_file).
    3. Handles potential summarization failures by trying a different model.
    4. Cleans up temporary PDF files and replaces line breaks in summaries.
    5. Exports the processed papers with summaries to a JSON file.
    6. Sends an email notification to the provided recipients with details and summaries.
    """
    
    ## Extract ActuIA list of domains from settings
    list_domains = config["actuia.list.domains"]
    
    ## Iterate on domain in list of ActuIA domains to extract articles
    for domain in list_domains:
        # Skip this domain for debugging (uncomment for testing specific domain)
        # if domain["name"] != "your_domain_name":
        #     continue
        # break # For Debug Only
        
        # Retrieve the path of the json data file for the given domain
        actuia_data_file_path = os.path.join(config[
            "json.key.data.dir"],
            f"EVER{config['key.json.actuia.file.suffix']}-{domain['name']}.json")
        
        # For each domain, retrieve the list of articles from ActuIA website
        articles = pull_new_actuia_articles(
            domain_name = domain["name"],
            data_file_path = actuia_data_file_path)  # Get list of articles details
        
        # print(f"""
        # {datetime.now().strftime('%Y-%m-%d')} - {len(articles)} new ActuIA articles for domain '{domain['name']}':""") # For Debug Only
        # print(f"""{''.join(f"""
        # => Title: {curr_article[config['key.json.title']]}""" for curr_article in articles)}""") # For Debug Only
    
        # Initialize email_details with the list of recipients and the subject
        email_details = {config["key.json.email.detail.recipients"]: domain["recipients"],
                         config["key.json.email.detail.subject"]: f"{config['key.json.monitoring.category.techno']} {config['key.json.actuia.source.name']} - {domain['name']}"}
        
        # Step 3. process the list of articles
        process_list_of_items(
            source_name = f'{config["key.json.actuia.source.name"]} - {domain["name"]}',
            source_format = config["key.json.source.format.text.content"],
            data_file_path = actuia_data_file_path,
            known_items_json_key = config["key.json.link"],
            new_items = articles,
            smtp_server_details = domain["smtp.server.details"],
            email_details = email_details,
            keys_to_ignore = [config["key.json.content"], config["key.json.link"]])

def pull_new_insurance_times_uk_articles(domain_name: str,
                                         domain_link: str,
                                         data_file_path: str) -> None:
    """
    Fetches new articles from Insurance Times UK for a specific domain and sends notifications.

    This function performs the following tasks:

    1. Scrapes Insurance Times UK's website for articles related to the provided domain.
    2. Extracts information from each article, including title, author, thumbnail URL,
       date, content, and summary (using a large language model).
    3. Saves the extracted information for new articles to a JSON file.
    4. Sends an email notification to recipients if new articles are found.

    **Args:**
        domain_name (str): The name of the domain to be considered when scraping Insurance Times UK articles.
        domain_link (str): The URL of the page related to the domain on the Insurance Times UK website.
        data_file_path (str): The path to the json data file to store the articles from Insurance Times UK for a given domain.
        
    **Returns:**
        A list of dictionaries. Each dictionary is an article that contains the following attributes:
            * `title (str)`: The title of the article,
            * `author (list)`: The author of the article,
            * `thumbnailUrl (str)`: The URL of the thumbnail image to illustrate the article,
            * `date (str)`: The date of the article,
            * `link (str)`: The URL of the article,
            * `content (str)`: The content of the article.
    """
    # Print information about processing Insurance Times UK articles
    print(f"Retrieving new articles from Insurance Times UK website for the domain: '{domain_name}'")
    # Fetch the Insurance Times UK website content for the specified domain
    # Use headers so that the request is not seen as a robot
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    response = requests.get(domain_link+"/", headers = headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        response = None
    
    soup = BeautifulSoup(response.content, "html.parser")
    # print(f"HTML page of Insurance Times UK website, domain {domain_name}: {soup.text}")
    
    # Initialise the list of articles to store with their paramaters:
    # - title
    # - author
    # - image_url
    # - date
    # - link
    # - content
    # - summary (filled in later)
    
    ## Local variables
    # Initialize empty list to store article details and sets to track seen articles
    insurance_times_uk_articles: List[Dict[str, str, str, str, str, str]] = []
    seen_urls = set() # Set to track already seen Insurance Times UK article URLs
    # Check if an existing JSON file stores previously processed Insurance Times UK articles
    # print(f"data_file_path: {data_file_path}") # For Debug Only
    if os.path.isfile(data_file_path) is True:
        # Load list of previously processed articles from the JSON file
        with open(data_file_path) as fp:
            # Extract and store a set of URLs from previously processed articles
            seen_urls = extract_node_values(json.load(fp),
                                            config["key.json.link"]) # Set to track seen Insurance Times UK articles URLs
        # print(f"Already seen URLs: {', '.join(seen_urls)}") # For Debug Only
    
    # Loop through Insurance Times UK articles in reverse order (latest first)
    # Locate the relevant div elements
    # Start from the end of the list of articles
    # Find all div elements with the first class
    resultset1 = soup.find_all("div", class_="spinLayout thumb onecol left item-first hasPicture")
    # Find all div elements with the second class
    resultset2 = soup.find_all("div", class_="spinLayout thumb onecol left item-first item-penultimate hasPicture")
    # Find all div elements with the third class
    resultset3 = soup.find_all("div", class_="spinLayout thumb onecol left item-first item-last hasPicture")
    # Find all div elements with the fourth class
    resultset4 = soup.find_all("div", class_="spinLayout thumb onecol right item-second item-last hasPicture")
    # Find all div elements with the fifth class
    resultset5 = soup.find_all("div", class_="spinLayout thumb onecol right item-second hasPicture")
    # Find all div elements with the sixth class
    resultset6 = soup.find_all("div", class_="spinLayout thumb onecol right item-second item-penultimate hasPicture")
    # Merge the results into a single list
    my_resultset = resultset1 + resultset2 + resultset3 + resultset4 + resultset5 + resultset6
    
    print(f"=> Retrieved {len(my_resultset)} articles in the HTML code for domain {domain_name}")
    # for current_div_index in range(len(my_resultset))[::-1]:
    #     insurance_times_uk_article_div = my_resultset[current_div_index]
    for current_div_index in range(len(my_resultset)): # Reverse loop for latest first
        # print(f"Length of the list of articles: {len(my_resultset)}") # For Debug Only
        # print(f"Current index: {len(my_resultset)-1-current_div_index}") # For Debug Only
        # print(f"Dealing with Insurance Times UK article of index #{len(my_resultset)-1-current_div_index}") # For Debug Only
        insurance_times_uk_article_div = my_resultset[len(my_resultset)-1-current_div_index]
        
        # Extract title, URL, and check for duplicates
        # <a href="https://www.insurancetimes.co.uk/news/intersys-opens-new-london-office/1453257.article">Intersys opens new London office</a>
        title_tag = insurance_times_uk_article_div.find("a", class_ = "")
        post_title = ""
        if title_tag:
            post_title = title_tag.text.strip()
        else:
            print("Title not found for an article in Insurance Times UK")
            continue
        # print(f"=> Insurance Times UK article title: {post_title}") # For Debug Only
        
        # Extract the paper ID from the link
        article_url_match = re.search(r"^(https:\/\/www\.insurancetimes\.co\.uk\/.*)$", title_tag["href"])
        if article_url_match:
            article_url = article_url_match.group(1)
        else:
            print(f"Could not recognize Insurance Times UK URL from link: {title_tag['href']}")
            continue
        # print(f"=> Insurance Times UK article URL: {article_url}") # For Debug Only
        
        # Check for duplicates using Insurance Times UK article URL
        if article_url in seen_urls:
            # print(f"Duplicate article detected with URL {article_url}, skipping.") # For Debug Only
            continue
        seen_urls.add(article_url) # Add unique URL to seen URLs
        
        # Extract additional information (image URL, author, date)
        # <img alt="Leadenhall market" class="lazyloaded" loading="lazy" sizes="(max-width: 1179px) 100px, 220px"
        # src="https://d17mj6xr9uykrr.cloudfront.net/Pictures/100x67/6/9/7/111697_leadenhallmarket_502804.jpg"
        # srcset="https://d17mj6xr9uykrr.cloudfront.net/Pictures/100x67/6/9/7/111697_leadenhallmarket_502804.jpg 100w,
        # https://d17mj6xr9uykrr.cloudfront.net/Pictures/220x147/6/9/7/111697_leadenhallmarket_502804.jpg 220w" width="100" height="67" />
        image_url = insurance_times_uk_article_div.find("img", class_="lazyloaded")
        if image_url:
            image_url = image_url['src']
        else:
            print(f"Could not recognize image URL: {image_url}")
            # image_url = insurance_times_uk_article_div.find("img", class_="entry-thumb")
            # if image_url:
            #     image_url = image_url['src']
            # else:
            #     print(f"Could not recognize image URL: {image_url}")
        # print(f"=> Insurance Times UK article image URL: {image_url}") # For Debug Only
        # post_author = insurance_times_uk_article_div.find("a", rel_="author")
        # if post_author:
        #     post_author = post_author.text.replace("-","").strip()
        # else:
        #     print(f"Could not recognize post author.")
        post_author = None
        # Find the span element with class "author"
        # <span class="author">By <a rel="author" href="https://www.insurancetimes.co.uk/clare-ruel/2216.bio">Clare Ruel</a></span>
        author_span = insurance_times_uk_article_div.find("span", class_="author")
        # Extract the text content from the anchor tag within the span
        if author_span:  # Check if author_span is not None (element found)
            post_author = author_span.find("a", class_ = "")
            if post_author:
                post_author = post_author.text.strip()
            else:
                # <span class="author">By <span class="noLink">Harry Weeks</span></span>
                author_span = insurance_times_uk_article_div.find("span", class_="noLink")
                post_author = author_span.text.strip()
        else:
            print("Could not recognize post author.")
        # print(f"=> Insurance Times UK article author: {post_author}") # For Debug Only
        
        # Find the span element with class "author"
        # <span class="date" data-date-timezone="{&quot;publishdate&quot;: &quot;2024-10-07T07:00:00&quot;}">2024-10-07T07:00:00+01:00</span>
        post_date = insurance_times_uk_article_div.find("span", class_="date")
        if post_date:
            post_date = post_date.text.strip()
        else:
            print("Could not recognize post date.")
        # print(f"=> Insurance Times UK article date: {post_date}") # For Debug Only
        
        # Extract article content
        response_article = requests.get(article_url, headers = headers)
        if response_article.status_code != 200:
            print(f"Error: {response_article.status_code}")
            response = None
        soup_article = BeautifulSoup(response_article.content, "html.parser")
        # print(f"Insurance Times UK article content: {soup_article}")
        if not post_author:
            author_span = soup_article.find("span", class_="author")
            # Extract the text content from the anchor tag within the span
            if author_span:  # Check if author_span is not None (element found)
                post_author = author_span.find("a", class_ = "")
                if post_author:
                    post_author = post_author.text.strip()
                else:
                    # <span class="author">By <span class="noLink">Harry Weeks</span></span>
                    author_span = soup_article.find("span", class_="noLink")
                    post_author = author_span.text.strip()
            else:
                print("Could not recognize post author.")
            # print(f"=> Insurance Times UK article author: {post_author}") # For Debug Only
        if not post_date:
            post_date = soup_article.find("span", class_="date")
            if post_date:
                post_date = post_date.text.strip()
            else:
                print("Could not recognize post date.")
            # print(f"=> Insurance Times UK article date: {post_date}") # For Debug Only
        # Locate the relevant div element
        # <div class="articleContent">
        post_content_div = soup_article.find("div", class_="articleContent")
        post_content = None
        if not post_content_div:
            print(f"Could not recognize post content for article at URL: {article_url}")
        else:
            # Find all paragraphs
            paragraphs = post_content_div.find_all("p")
            # for p in paragraphs:
            #     print(f"{type(p)} 'p' content: {p}")
            # Extract the text content from the paragraphs
            post_content = "".join([p.text.strip() for p in paragraphs if p and not p.text.startswith("<p><strong>Read:") and not p.text.startswith("<p><strong>Explore")])
            # print(f"'p' content: {paragraphs[0]}")
            # Remove unexpected content
            # Find all paragraphs that don't start with "<p><strong>Read:&nbsp;<a href="
            # paragraphs = post_content_div.find_all(
            #     "p",
            #     # lambda p: ((p and not isinstance(p, str)) or (p and not p.startswith("<p><strong>Read:") and not p.startswith("<p><strong>Explore")))
            #     lambda p: p and isinstance(p, str)
            #     )
            # Extract the text content from the paragraphs
            # post_content = "".join([p.text.strip() for p in paragraphs])
        # print(f"=> Insurance Times UK article content: {post_content}")
        
        # Add article details to the list 'insurance_times_uk_articles'
        insurance_times_uk_articles.insert(0, {
            config["key.json.title"]: post_title,
            config["key.json.author"]: post_author,
            config["key.json.thumbnail.url"]: image_url,
            config["key.json.date"]: post_date,
            config["key.json.link"]: article_url,
            config["key.json.content"]: post_content
            })
        
    # Return the list of articles from Insurance Times UK website with extracted details
    return insurance_times_uk_articles

def process_insurance_times_uk_daily() -> None:
    
    ## Extract Insurance Times UK list of domains from settings
    list_domains = config["insurance.times.uk.list.domains"]
    
    ## Iterate on domain in list of Insurance Times UK domains to extract articles
    for domain in list_domains:
        print(f"Processing Insurance Times UK for domain {domain['name']}")
        
        # Skip this domain for debugging (uncomment for testing specific domain)
        # if domain["name"] != "home":
        #     print("Skipping it...")
        #     continue # For Debug Only
        # break # For Debug Only
        
        # Retrieve the path of the json data file for the given domain
        insurance_times_uk_data_file_path = os.path.join(config[
            "json.key.data.dir"],
            f"EVER{config['key.json.insurance.times.uk.file.suffix']}-{domain['name']}.json")
        
        # For each domain, retrieve the list of articles from Insurance Times UK website
        articles = pull_new_insurance_times_uk_articles(
            domain_name = domain["name"],
            domain_link = domain["link"],
            data_file_path = insurance_times_uk_data_file_path)  # Get list of articles details
        
        # print(f"""
        # {datetime.now().strftime("%Y-%m-%d")} - {len(articles)} new Insurance Times UK articles for domain '{domain['name']}':""") # For Debug Only
        # print(f"""{''.join(f"""
        # => Title: {curr_article[config['key.json.title']]}""" for curr_article in articles)}""") # For Debug Only
    
        # Initialize email_details with the list of recipients and the subject
        email_details = {config["key.json.email.detail.recipients"]: domain["recipients"],
                         config["key.json.email.detail.subject"]: f"{config['key.json.monitoring.category.business']} {config['key.json.insurance.times.uk.source.name']} - {domain['name']}"}
        
        # Step 3. process the list of articles
        process_list_of_items(
            source_name = f'{config["key.json.insurance.times.uk.source.name"]} - {domain["name"]}',
            source_format = config["key.json.source.format.text.content"],
            data_file_path = insurance_times_uk_data_file_path,
            known_items_json_key = config["key.json.link"],
            new_items = articles,
            smtp_server_details = domain["smtp.server.details"],
            email_details = email_details,
            keys_to_ignore = [config["key.json.content"], config["key.json.link"]])
    
def extract_article_details_from_websites() -> None:
    """
    Fetches daily content from various websites and sends notifications.
    
    This function performs the following tasks:
    
    1. Extracts Hugging Face papers and sends notifications if any are found.
    2. Extracts ActuIA articles for each domain in a configured list and sends notifications.
    3. Extracts Insurance Times UK articles for each domain in a configured list and sends notifications.
    """
    ## Step 1: Extract Hugging Face papers
    process_hf_daily()
    # convert_to_voice_recorder()
    
    ## Step 2: Extract ActuIA articles
    process_actuia_daily()
    
    ## Step 3: Extract Insurance Times UK articles
    process_insurance_times_uk_daily()
