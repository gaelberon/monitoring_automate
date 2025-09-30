"""
summarize_source.py

This script summarizes the daily papers pulled from Hugging Face's papers page,
updates the README with the summaries, and cleans up temporary files.
"""

# Standard library imports
import json
import os
import time
from datetime import datetime
from typing import List, Dict

# Local resources imports
from utils import config
from utils import summarize_from_pdf_file

# Data Dir containing the json file with the list of all downloaded sources for a given day
data_dir = "data"
# Suffix to use for the PDF files from the Hugging Face Papers
hf_paper_file_suffix = "_hf_papers"

def update_readme(summaries: List[Dict[str, str]]) -> None:
    """
    Updates the README file with the summaries of the papers.

    Args:
    - summaries (List[Dict[str, str]]): A list of dictionaries containing paper information and summaries.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_content = f"\n\n## Papers for {date_str}\n\n"
    new_content += "| Title | Authors | Summary |\n"
    new_content += "|-------|---------|---------|\n"
    for summary in summaries:
        # Replace line breaks with spaces
        summary[config["key.json.summary"]] = summary[config["key.json.summary"]].replace("\n", " ")
        hf_link = summary[config["key.json.link"]].replace("https://arxiv.org/abs/", "https://huggingface.co/papers/")
        new_content += f"| {summary[config["key.json.title"]]} (Read more on [arXiv]({summary[config["key.json.link"]]}) or [HuggingFace]({hf_link}))| {summary[config["key.json.authors"]]} | {summary[config["key.json.summary"]]} |\n"

    day = date_str.split("-")[2]

    # Write the new content to the archive
    # Create the archive directory if it doesn't exist
    year = date_str.split("-")[0]
    month = date_str.split("-")[1]
    os.makedirs(f"archive/{year}/{month}", exist_ok=True)
    with open(f"archive/{year}/{month}/{day}.md", "w") as f:
        f.write(new_content)

    # Update the README with the new content
    # Load the existing README
    with open("README.md", "r") as f:
        existing_content = f.read()

    # Load the intro template
    with open("templates/README_intro.md", "r") as f:
        intro_content = f.read()

    # Add the date to the intro
    date_str_readme = date_str.replace("-", "--")
    intro_content = intro_content.replace("{DATE}", f"{date_str_readme} \n \n")

    # Remove the existing header
    front_content = existing_content.split("## Papers for")[0]
    existing_content = existing_content.replace(front_content, "")

    # Combine the intro, new content, and existing content
    updated_content = intro_content + new_content + "\n\n" +  existing_content

    # Write the updated content to the README
    with open("README.md", "w") as f:
        f.write(updated_content)

def main() -> None:
    """
    Main function to summarize papers, update the README, and clean up temporary files.
    """
    date = datetime.now().strftime("%Y-%m-%d")
    print(f"Try opening file: {data_dir}/{date}{hf_paper_file_suffix}.json")
    with open(f"{data_dir}/{date}{hf_paper_file_suffix}.json", "r") as f:
        papers = json.load(f)

    summaries = []
    for paper in papers:
        try:
            summary = summarize_from_pdf_file(
                title      = paper[config["key.json.title"]],
                authors    = paper[config["key.json.authors"]],
                pdf_path   = paper[config["key.json.pdf.path"]],
                # model_name = config["gemini.api.service.version.1.5.pro.002"]
                model_name=config["gemini.api.service.version.1.5.flash.002"]
            )
            summaries.append({**paper, config["key.json.summary"]: summary})
            # time.sleep(60) # Sleep for 1 minute to avoid rate limiting
            time.sleep(10) # Sleep for 10 seconds to avoid rate limiting
        except Exception:
            try:
                print(f"Failed to summarize paper {paper[config["key.json.title"]]}. Trying with a different model.")
                summary = summarize_from_pdf_file(
                    title    = paper[config["key.json.title"]],
                    authors  = paper[config["key.json.authors"]],
                    pdf_path = paper[config["key.json.pdf.path"]],
                    # model_name=config["gemini.api.service.version.1.5.flash.002"]
                    model_name=config["gemini.api.service.version.1.5.flash"]
                )
                summaries.append({**paper, config["key.json.summary"]: summary})
            except Exception as e:
                print(f"Failed to summarize paper {paper[config["key.json.title"]]} with both models. Due to {e}")
                continue

    # update_readme(summaries)
    iter = 1
    for summary in summaries:
        # Replace line breaks with spaces
        summary[config["key.json.summary"]] = summary[config["key.json.summary"]].replace("\n", " ")
        hf_link = summary[config["key.json.link"]].replace("https://arxiv.org/abs/", "https://huggingface.co/papers/")
        print(f"Paper {iter} hf_link: {hf_link}")
        print(f"Paper {iter} summary: {summary}")
        iter = iter+1

    # Clean up temporary PDF files
    for paper in papers:
        if os.path.exists(paper[config["key.json.pdf.path"]]):
            os.remove(paper[config["key.json.pdf.path"]])


if __name__ == "__main__":
    main()
