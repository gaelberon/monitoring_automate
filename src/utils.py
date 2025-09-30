"""
utils.py

"""

# Standard library imports
import os
from dotenv import load_dotenv
import json
import html
import time
# import textwrap

# Third party imports
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
# import yagmail
from typing import List, Dict
import PyPDF2
# to speech conversion
# import speakify
from gtts import gTTS

# Third party imports
import google.generativeai as genai
# from google import generativeai as genai

## CONFIGURATION
# --- Configuration initiale ---
load_dotenv()
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

## Local Variables
# Technology Monitoring Category settings
monitoring_category_techno = "[Techno Monitoring]"
monitoring_category_business = "[Business Monitoring]"
prompt_template_file_techno_youtube_channel = "templates/prompt_summarize_techno_youtube_chanel.md"
prompt_template_file_debate_youtube_channel = "templates/prompt_summarize_debate_youtube_chanel.md"
prompt_template_file_entertainment_youtube_channel = "templates/prompt_summarize_entertainment_youtube_chanel.md"
# Entertainment Monitoring Category settings
monitoring_category_entertainment = "[Entertainment Monitoring]"
gmail_smtp_server = "smtp.gmail.com"
gmail_smtp_port = "465"
gmail_sender_email = "gael.beron@gmail.com"
# gmail_sender_email = "gael@beron.fr"
gmail_sender_app_password = "ohab oibk fzuo wkmf"
humbrela_smtp_server = "mail.humbrela.com"
humbrela_smtp_port = "587"
humbrela_sender_email = "noreply@humbrela.com"
humbrela_sender_password = "Admin@Humbrela2025"
recipient_gael_beron_fr = "gael@beron.fr"
recipient_helene_duval = "helene.e.duval@gmail.com"
recipient_gberon_humbrela_com = "gberon@humbrela.com"
recipient_gael_beron_gmail_com = "gael.beron@gmail.com"
recipient_gael_beroons_hotmail_com = "gael_beroons@hotmail.com"
# recipient_gspay_humbrela_com = "gspay@humbrela.com"
# recipient_szaidi_humbrela_com = "szaidi@humbrela.com"
# recipient_jlemery_humbrela_com = "joffrey.lemery.jl@gmail.com"
hf_papers_recipients = [recipient_gael_beron_fr]
smtp_server_details_humbrela = {
    "sender": humbrela_sender_email,
    "sender.password": humbrela_sender_password,
    "smtp.server": humbrela_smtp_server,
    "smtp.port": humbrela_smtp_port
}
smtp_server_details_gmail = {
    "sender": gmail_sender_email,
    "sender.password": gmail_sender_app_password,
    "smtp.server": gmail_smtp_server,
    "smtp.port": gmail_smtp_port
}

# ActuIA domains definition
# actuia_domain_insurance = {
#     "name": "assurance",
#     "recipients": [recipient_gberon_humbrela_com, recipient_szaidi_humbrela_com, recipient_gspay_humbrela_com],
#     "smtp.server.details": smtp_server_details_humbrela
# }
actuia_domain_insurance = {
    "name": "assurance",
    "recipients": [recipient_gberon_humbrela_com],
    "smtp.server.details": smtp_server_details_humbrela
}
actuia_domain_recherche_fondamentale = {
    "name": "recherche-fondamentale",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail
}
actuia_domain_education = {
    "name": "education",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail
}
actuia_domain_emploi = {
    "name": "emploi",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail
}
actuia_domain_energie = {
    "name": "energie",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail
}
actuia_domain_environnement = {
    "name": "environnement",
    "recipients": [recipient_gael_beron_fr, recipient_gael_beroons_hotmail_com],
    "smtp.server.details": smtp_server_details_gmail
}
actuia_domain_finances = {
    "name": "finances",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail
}
actuia_domain_sante_medecine = {
    "name": "sante-medecine",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail
}
actuia_domain_vie_courante = {
    "name": "vie-courante",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail
}

# List of domains to analyse from ActuIA website
list_actuia_domains = [actuia_domain_insurance,
                       actuia_domain_recherche_fondamentale,
                       actuia_domain_education,
                       actuia_domain_emploi,
                       actuia_domain_energie,
                       actuia_domain_environnement,
                       actuia_domain_finances,
                       actuia_domain_sante_medecine,
                       actuia_domain_vie_courante]

# Youtube channels definition
youtube_channel_france_inter = {
    "name": "France Inter",
    "monitoring.category": monitoring_category_entertainment,
    "prompt.template": prompt_template_file_entertainment_youtube_channel,
    "id": "UCJldRgT_D7Am-ErRHQZ90uw",
    "recipients": [recipient_gael_beron_fr, recipient_gael_beroons_hotmail_com],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": False
}
youtube_channel_quotidien = {
    "name": "Quotidien",
    "monitoring.category": monitoring_category_entertainment,
    "prompt.template": prompt_template_file_entertainment_youtube_channel,
    "id": "UCpi-4daExRSchtsJzO06rwA",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": False
}
youtube_channel_radionova = {
    "name": "Radio Nova",
    "monitoring.category": monitoring_category_entertainment,
    "prompt.template": prompt_template_file_entertainment_youtube_channel,
    "id": "UCGvjUWz3mGV9cssraATuEsw",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": False
}
youtube_channel_imda = {
    "name": "IMDA Singapore",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCeW5IMmy5uUzEv3f4ijV2cg",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_deeplearningai = {
    "name": "DeepLearningAI",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCcIXc5mJsHVYTZR1maL5l9w",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_tensorflow = {
    "name": "TensorFlow",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UC0rqucBdTuFTjJiefW5t-IQ",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_ai_all_in_one = {
    "name": "Artificial Intelligence - All in One",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UC5zx8Owijmv-bbhAK6Z9apg",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_ludovic_salenne= {
    "name": "Ludo Salenne",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCnnYqSNKKygemgmxC9PyLTw",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_krish_naik = {
    "name": "Krish Naik",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCNU_lfiiWBdtULKOw6X0Dig",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_data_science_brain = {
    "name": "Data Science Brain",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCtuTob3IALE72NuriTIEQHw",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_sam_witteveen = {
    "name": "Sam Witteveen",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UC55ODQSvARtgSyc8ThfiepQ",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_two_minutes_papers = {
    "name": "Two Minute Papers",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCbfYPyITQ-7l4upoX8nvctg",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_codebasics = {
    "name": "codebasics",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCh9nVJoWXmFb7sLApWGcLPQ",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_thibault_neveu = {
    "name": "Thibault Neveu",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCVso5UVvQeGAuwbksmA95iA",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_eo = {
    "name": "EO",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UClWTCPVi-AU9TeCN6FkGARg",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_yannic_kilcher = {
    "name": "Yannic Kilcher",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCZHmQk67mSJgfCCTn7xBfew",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_aleksa_gordic_the_ai_epiphany = {
    "name": "Aleksa Gordic - The AI Epiphany",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCj8shE7aIn4Yawwbo2FceCQ",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_3blue1brown = {
    "name": "3Blue1Brown",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCYO_jab_esuFRV4b17AJtAw",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_lex_fridman = {
    "name": "Lex Fridman",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCSHZKyawb77ixDdsGog4iWA",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_ken_jee = {
    "name": "Ken Jee",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCiT9RITQ9PW6BhXK0y2jaeg",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_jean_marc_jancovici = {
    "name": "Jean-Marc Jancovici",
    "monitoring.category": monitoring_category_entertainment,
    "prompt.template": prompt_template_file_debate_youtube_channel,
    "id": "UCNovJemYKcdKt7PDdptJZfQ",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_mystery_science = {
    "name": "Mystery Science",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCPRCRM3JKm3sw55lB_427qg",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_il_etait_une_fois_vevo = {
    "name": "iletaitunefoisVEVO",
    "monitoring.category": monitoring_category_entertainment,
    "prompt.template": prompt_template_file_entertainment_youtube_channel,
    "id": "UCiPNU0VO-m9OC_0q2MAAnXw",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": False
}
# youtube_channel_sports = {
#     "name": "Sports",
#     "monitoring.category": monitoring_category_entertainment,
#     "prompt.template": prompt_template_file_entertainment_youtube_channel,
#     "id": "UCEgdi0XIXXZ-qJOFPf4JSKw",
#     "recipients": [recipient_gael_beron_fr],
#     "smtp.server.details": smtp_server_details_gmail,
#     "summarize.it": False
# }
youtube_channel_le_monde_en_cartes = {
    "name": "Le monde en cartes",
    "monitoring.category": monitoring_category_entertainment,
    "prompt.template": prompt_template_file_debate_youtube_channel,
    "id": "UCYA_ElxMgkJlvcKa4SM0dOg",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": False
}
youtube_channel_lcp_assemblee_nationale = {
    "name": "LCP - Assemblée nationale",
    "monitoring.category": monitoring_category_entertainment,
    "prompt.template": prompt_template_file_debate_youtube_channel,
    "id": "UCHGFbA0KWBgf6gMbyUCZeCQ",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": False
}
youtube_channel_brick_machines = {
    "name": "Brick Machines",
    "monitoring.category": monitoring_category_entertainment,
    "prompt.template": prompt_template_file_entertainment_youtube_channel,
    "id": "UCly-ZW4hcXU5MPLGpuQBFdA",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": False
}
youtube_channel_c_est_pas_sorcier = {
    "name": "C'est pas sorcier",
    "monitoring.category": monitoring_category_entertainment,
    "prompt.template": prompt_template_file_entertainment_youtube_channel,
    "id": "UCENv8pH4LkzvuSV_qHIcslg",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": False
}
youtube_channel_nate_hagens = {
    "name": "Nate Hagens",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UCWJOjGOpN8oSVr_OoJLzk9g",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": True
}
youtube_channel_mistralai = {
    "name": "MistralAI",
    "monitoring.category": monitoring_category_techno,
    "prompt.template": prompt_template_file_techno_youtube_channel,
    "id": "UC5-pBdfdA3KUo-vq72l-umA",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": False
}
youtube_channel_siphano = {
    "name": "Siphano",
    "monitoring.category": monitoring_category_entertainment,
    "prompt.template": prompt_template_file_entertainment_youtube_channel,
    "id": "UCwa-qCAFghXwkcQvLadzRxQ",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": False
}
youtube_channel_c_a_vous_france_televisions = {
    "name": "C à vous - France Télévisions",
    "monitoring.category": monitoring_category_entertainment,
    "prompt.template": prompt_template_file_entertainment_youtube_channel,
    "id": "UCejTWYquMXD_MFHRZiqo_Aw",
    "recipients": [recipient_gael_beron_fr],
    "smtp.server.details": smtp_server_details_gmail,
    "summarize.it": False
}

# List of channels to analyse from Youtube
list_youtube_channels = [youtube_channel_quotidien,
                         youtube_channel_radionova,
                         youtube_channel_france_inter,
                         # youtube_channel_sports,
                         youtube_channel_il_etait_une_fois_vevo,
                         youtube_channel_brick_machines,
                         youtube_channel_c_est_pas_sorcier,
                         youtube_channel_siphano,
                         youtube_channel_c_a_vous_france_televisions,
                         youtube_channel_jean_marc_jancovici,
                         youtube_channel_le_monde_en_cartes,
                         youtube_channel_lcp_assemblee_nationale,
                         youtube_channel_imda,
                         youtube_channel_mistralai,
                         youtube_channel_deeplearningai,
                         youtube_channel_tensorflow,
                         youtube_channel_ai_all_in_one,
                         youtube_channel_ludovic_salenne,
                         youtube_channel_krish_naik,
                         youtube_channel_data_science_brain,
                         youtube_channel_sam_witteveen,
                         youtube_channel_two_minutes_papers,
                         youtube_channel_codebasics,
                         youtube_channel_thibault_neveu,
                         youtube_channel_eo,
                         youtube_channel_yannic_kilcher,
                         youtube_channel_aleksa_gordic_the_ai_epiphany,
                         youtube_channel_3blue1brown,
                         youtube_channel_lex_fridman,
                         youtube_channel_ken_jee,
                         youtube_channel_mystery_science,
                         youtube_channel_nate_hagens]

# Insurance Times UK domains definition
# insurance_times_uk_domain_home = {
#     "name": "home",
#     "link": "https://www.insurancetimes.co.uk",
#     "recipients": [recipient_gberon_humbrela_com, recipient_szaidi_humbrela_com, recipient_gspay_humbrela_com, recipient_jlemery_humbrela_com],
#     "smtp.server.details": smtp_server_details_humbrela
# }
insurance_times_uk_domain_home = {
    "name": "home",
    "link": "https://www.insurancetimes.co.uk",
    "recipients": [recipient_gberon_humbrela_com],
    "smtp.server.details": smtp_server_details_humbrela
}
insurance_times_uk_domain_news = {
    "name": "news",
    "link": "https://www.insurancetimes.co.uk/news",
    "recipients": [recipient_gberon_humbrela_com],
    "smtp.server.details": smtp_server_details_humbrela
}
insurance_times_uk_domain_techtalk = {
    "name": "techtalk",
    "link": "https://www.insurancetimes.co.uk/analysis/techtalk",
    "recipients": [recipient_gberon_humbrela_com],
    "smtp.server.details": smtp_server_details_humbrela
}
insurance_times_uk_domain_cyber = {
    "name": "cyber",
    "link": "https://www.insurancetimes.co.uk/topics/cyber",
    "recipients": [recipient_gberon_humbrela_com],
    "smtp.server.details": smtp_server_details_humbrela
}
# List of domains to analyse from Insurance Times UK website
list_insurance_times_uk_domains = [
    insurance_times_uk_domain_home,
    insurance_times_uk_domain_news,
    insurance_times_uk_domain_techtalk,
    insurance_times_uk_domain_cyber]

# Config Dictionaries
config = {
    "json.key.data.dir": "data",
    "json.key.tmp.raw.sources.dir": "tmp_raw_sources_dir",
    "key.json.source.format.pdf": "sourceFormatAsPDF",
    "key.json.source.format.text.content": "sourceFormatAsPDFTextContent",
    "key.json.source.format.youtube.video": "sourceFormatAsYoutubeVideo",
    "google.cloud.project.id": "healthy-fuze-437202-j9",
    "google.service.account.key.json.file": "healthy-fuze-437202-j9-e32d9ee30852.json",
    "gemini.api.service.version.1.5.flash.002": "gemini-1.5-flash-002",
    "gemini.api.service.version.1.5.flash": "gemini-1.5-flash",
    "gemini.api.service.version.2.5.flash": "gemini-2.5-flash",
    "gemini.api.service.version.1.5.pro.002": "gemini-1.5-pro-002",
    "gemini.api.service.version.2.5.pro": "gemini-2.5-pro",
    "youtube.api.service.name": "youtube",
    "youtube.api.service.version": "v3",
    # "youtube.api.service.scopes": ["https://www.googleapis.com/auth/youtube"],
    "youtube.api.service.scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
    "youtube.api.service.token.file": "token.json",
    "youtube.api.service.credentials.file": "client_secret_413915175774-jdf1o37s414ifkr4dulc8erhnjlinn89.apps.googleusercontent.com.json",
    "genai.api.key": GENAI_API_KEY,
    "youtube.api.key": YOUTUBE_API_KEY,
    "google.genai.sleep.time": 3,
    "smtp.server.details.gmail": smtp_server_details_gmail,
    # "gmail.smtp.server": gmail_smtp_server,
    # "gmail.smtp.port": gmail_smtp_port,
    # "gmail.username": gmail_sender_email,
    # "gmail.password": gmail_sender_app_password,
    "smtp.server.details.humbrela": smtp_server_details_humbrela,
    # "humbrela.smtp.server": humbrela_smtp_server,
    # "humbrela.smtp.port": humbrela_smtp_port,
    # "humbrela.username": humbrela_sender_email,
    # "humbrela.password": humbrela_sender_password,
    "recipient.gael.beron.fr": recipient_gael_beron_fr,
    "recipient.gael.beron.gmail.com": recipient_gael_beron_gmail_com,
    "recipient.gael.beroons.hotmail.com": recipient_gael_beroons_hotmail_com,
    "actuia.list.domains": list_actuia_domains,
    "youtube.api.list.channels": list_youtube_channels,
    "insurance.times.uk.list.domains": list_insurance_times_uk_domains,
    "key.json.email.detail.recipients": "emailDetailRecipients",
    "key.json.email.detail.subject": "emailDetailSubject",
    "key.json.email.detail.body": "emailDetailBody",
    "key.json.hf.source.name": "Hugging Face",
    "key.json.hf.url": "https://huggingface.co/papers",
    "key.json.hf.file.suffix": "_hf_papers",
    "key.json.hf.papers.recipients": hf_papers_recipients,
    "key.json.actuia.source.name": "ActuIA",
    "key.json.youtube.source.name": "Youtube",
    "key.json.insurance.times.uk.source.name": "Insurance Times UK",
    # "key.json.actuia.url": "https://www.actuia.com/domaine/assurance/",
    "key.json.actuia.url": "https://www.actuia.com/domaine/",
    "key.json.actuia.file.suffix": "_actuia_articles",
    "key.json.insurance.times.uk.file.suffix": "_insurance_times_uk_articles",
    "key.json.monitoring.category.techno": monitoring_category_techno,
    "key.json.monitoring.category.business": monitoring_category_business,
    "key.json.pdf.path": "pdf_path",
    "key.json.authors": "authors",
    "key.json.id": "id",
    "key.json.title": "title",
    "key.json.author": "author",
    "key.json.thumbnail.url": "thumbnailUrl",
    "key.json.date": "date",
    "key.json.link": "link",
    "key.json.content": "content",
    "key.json.summary": "summary",
    "key.json.channel.name": "channelName",
    # "key.json.video.id": "videoId",
    "key.json.description": "description",
    "key.json.transcript": "transcript",
    "template.file.prompt.summarize.actuia.articles": "templates/prompt_summarize_ActuIA_articles_template.md",
    "template.file.prompt.summarize.HF.paper": "templates/prompt_summarize_HF_paper_template.md"
}

# Configure the Gemini API
genai.configure(api_key=config["genai.api.key"])
# genai.configure(api_key=os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
# genai.init()

def download_pdf(arxiv_id: str, save_path: str) -> bool:
    """
    Downloads the PDF of a paper from arXiv given its ID.

    Args:
        arxiv_id (str): The arXiv ID of the paper.
        save_path (str): The path where the PDF will be saved.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        return True
    return False

def extract_node_values(json_data: dict, json_key: str) -> set:
    """Extracts values stored in a given node name from JSON data.

    Args:
        json_data (dict): A Json data dictionary.
        json_key (str): The name of the node to extract values from.

    Returns:
        A set of values stored in the specified node.
    """
    
    values = set()
    def traverse(json_data, json_key):
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if key == json_key:
                    values.add(value)
                else:
                    traverse(value, json_key)
        elif isinstance(json_data, list):
            for item in json_data:
                traverse(item, json_key)

    traverse(json_data, json_key)
    return values

def get_value2_on_key2_from_value1_on_key1_in_channels_list(key1: str,
                                                            value1: str,
                                                            key2: str,
                                                            channels: list[dict]) -> str:
  """
  Retrieves the monitoring category for a given channel name within a list of dictionaries.

  Args:
      channel_name (str): The name of the YouTube channel for which to find the monitoring category.
      channels (list): A list of dictionaries representing YouTube channel configurations.

  Returns:
      The monitoring category associated with the channel name,
      or None if not found.
  """
  for channel in channels:
    if channel[key1] == value1:
      return channel.get(key2)
  return None
import requests
from bs4 import BeautifulSoup

# Function to generate tag attributes (assumed to be defined elsewhere)
def generate_tag_attributes(key: str, value: any, link_text: str) -> str:
    """Generates HTML attributes based on the given key and value.

    Args:
        key: The JSON key to generate attributes for.
        value: The JSON value associated with the key.

    Returns:
        A string containing the HTML attributes.
    """

    attributes = ""
    if key == config["key.json.thumbnail.url"]:
        # Set the width attribute for image URLs to 15vw and include the image tag
        attributes += f" text-align: center; width: 15vw'><a href='{link_text}'><img style='max-width: 100%; height: auto;' src='{value}'></a>"
    elif key == config["key.json.summary"]:
        # Set the width attribute for summary content to 55vw
        attributes += f" text-align: left; width: 55vw'>{value}"
    elif key == config["key.json.author"]:
        # Set the width attribute for summary author to 5vw
        attributes += f" text-align: left; width: 5vw'>{value}"
    elif key == config["key.json.date"]:
        # Set the width attribute for summary date to 5vw
        attributes += f" text-align: left; width: 5vw'>{value}"
    elif key == config["key.json.description"]:
        # Set the width attribute for summary description to 30vw
        attributes += f" text-align: left; width: 30vw'>{value}"
    else:
        # Set the width attribute for any other content to 10vw
        attributes += f" text-align: left; width: 10vw'>{value}"
    
    # Return a string containing the HTML attributes.
    return attributes

# Function to generate header tag attributes (assumed to be defined elsewhere)
def generate_header_tag_attributes(key: str, value: str) -> str:
    """Generates HTML attributes based on the given key and value.

    Args:
        key: The JSON key to generate attributes for.
        value: The JSON value associated with the key.

    Returns:
        A string containing the HTML attributes.
    """

    attributes = ""
    if key == config["key.json.thumbnail.url"]:
        # Set the width attribute for image URLs to 15vw and include the image tag
        attributes += f""" width: 15vw'>{value}"""
    elif key == config["key.json.summary"]:
        # Set the width attribute for summary content to 55vw
        attributes += f""" width: 55vw'>{value}"""
    elif key == config["key.json.author"]:
        # Set the width attribute for summary author to 5vw
        attributes += f""" width: 5vw'>{value}"""
    elif key == config["key.json.date"]:
        # Set the width attribute for summary date to 5vw
        attributes += f""" width: 5vw'>{value}"""
    elif key == config["key.json.description"]:
        # Set the width attribute for summary description to 30vw
        attributes += f""" width: 30vw'>{value}"""
    else:
        # Set the width attribute for any other content to 10vw
        attributes += f""" width: 10vw'>{value}"""
    
    # Return a string containing the HTML attributes.
    return attributes

def json_to_html(json_data: dict, keys_to_ignore: list[str]) -> str:
    """Converts a JSON object into an HTML table.

    Args:
        json_data (dict): The JSON object (dictionary) to convert.
        keys_to_ignore (list(str)): A list of keys to exclude from the generated HTML table.

    Returns:
        The HTML table representation of the JSON data as a string.
    """
    
    # html_content = f"<!DOCTYPE html><html><head><title>{email_title}</title></head><body>"
    # html_content += '<table style="border-collapse: collapse; width: 100%;">'
    # html_content += '<thead style="background-color: #f2f2f2;"><tr>'
    # for key in json_data[0].keys():
    #     if key != "content":
    #         html_content += "<th style='border: 1px solid #ccc; padding: 8px; text-align: left;'>" + html.escape(key) + "</th>"
    # html_content += "</tr></thead>"
    # html_content += '<tbody>'
    # 
    # for item in json_data:
    #     html_content += "<tr>"
    #     for key, value in item.items():
    #         if key != "content":
    #             if key == config["key.json.thumbnail.url"]:
    #                 html_content += f"<td style='border: 1px solid #ccc; padding: 8px;'><img src='{value}' width='200'></td>"
    #             elif key == config["key.json.summary"]:
    #                 html_content += "<td style='border: 1px solid #ccc; padding: 8px;' width='400'>" + html.escape(value) + "</td>"
    #             else:
    #                 html_content += "<td style='border: 1px solid #ccc; padding: 8px;'>" + html.escape(value) + "</td>"
    #     html_content += "</tr>"
    # 
    # html_content += "</tbody></table></body></html>"
    
# {generate_tag_attributes(key, value, item[config["key.json.link"]][1])}</td>""" for key, value in item.items() if key not in keys_to_ignore)}

#     html_content = f"""<!DOCTYPE html>
# <html>
#     <body style='margin: 0; padding: 0; font-family: Arial, sans-serif;'>
#         <table style='border-collapse: collapse; width: 100%;'>
#             <thead> 
#                 <tr>{''.join(f"""
#                     <th style='padding: 0; text-align: center; border: 1px solid #ccc; background-color: #f2f2f2;\
# {generate_header_tag_attributes(key, html.escape(key))}</th>""" for key in json_data[0].keys() if key not in keys_to_ignore)}
#                 </tr>
#             </thead>
#             <tbody>{''.join(f"""
#                 <tr>{''.join(f"""
#                     <td style='padding: 8px; border: 1px solid #ccc;\
# {generate_tag_attributes(key, value, item.get(config.get('key.json.link'), [1]))}</td>""" for key, value in item.items() if key not in keys_to_ignore)}
#                 </tr>""" for item in json_data)}
#             </tbody>
#         </table>
#     </body>
# </html>"""
    
    # Build HTML table header
    html_table_header = ''.join(f"""
                    <th style='padding: 0; text-align: center; border: 1px solid #ccc; background-color: #f2f2f2;\
{generate_header_tag_attributes(key, html.escape(key))}</th>""" for key in json_data[0].keys() if key not in keys_to_ignore)
    # print(f"html_table_header: {html_table_header}") # For Debug Only

    # Build HTML table body
    # print(f"==============> Items in json_data list: {''.join(f'{', '.join(f'{key + ', ' + value}' for key, value in item.items())}' for item in json_data)}") # For Debug Only
    html_table_body = ""
    for item in json_data:
        # print(f"==============> Key, value in current item: {', '.join(f'{key + ', ' + value}' for key, value in item.items())}") # For Debug Only
        html_table_body += """
                <tr>"""
        html_table_body += ''.join(f"""
                    <td style='padding: 8px; border: 1px solid #ccc;\
{generate_tag_attributes(key, value, item.get(config.get('key.json.link'), [1]))}</td>""" for key, value in item.items() if key not in keys_to_ignore)
        html_table_body += """
                </tr>"""
    # print(f"html_table_body: {html_table_body}") # For Debug Only
    
    # Initiate template_html_file variable
    template_html_file_path = "./templates/email_template_monitoring_content.html"
    # Load the prompt template for summarizing videos from the specific channel
    with open(template_html_file_path, "r") as f:
        template_html_file = f.read()

    # Format the prompt by replacing placeholders with actual video information
    html_content = template_html_file.\
        replace("{htmlTableHeader}", html_table_header if html_table_header else ""). \
            replace("{htmlTableBody}", html_table_body if html_table_body else "")
    
    # Encode html content to utf-8
    # html_content = html_content.encode('utf-8') # Raises an error
    # print(html_content)
    
    # Return the HTML table representation of the JSON data as a string.
    return html_content

def send_email_via_smtplib_gmail(email_details: Dict,
                                 smtp_server_details: Dict) -> None:
    """
    Sends an email to a list of recipients using Gmail's SMTP server.

    Args:
        email_details (Dict): A dictionary that contains details for the email notification to be sent (i.e.: list of recipient, subject, body)
        smtp_server_details (Dict): A dictionary that contains SMTP server details in order to send email notification.

    Raises:
        Exception: If an error occurs during email sending.
    """
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = email_details[config["key.json.email.detail.subject"]]
    msg['From'] = smtp_server_details["sender"]
    
    # Connect to Gmail's SMTP server using SSL
    with smtplib.SMTP_SSL(smtp_server_details["smtp.server"],
                          smtp_server_details["smtp.port"]) as mail_server:
        try:
            mail_server.ehlo() # Can be omitted
            # Login to the SMTP server using the sender's credentials.
            mail_server.login(smtp_server_details["sender"],
                              smtp_server_details["sender.password"])
            
            # Send the email. The sendmail function requires the sender's email, the list of recipients, and the email message as a string.
            html_content = email_details[config["key.json.email.detail.body"]]
            text_content = "This is an example of a plain text email."
            
            # Attach parts into message container.
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send the email
            for recipient in email_details[config["key.json.email.detail.recipients"]]:
                # Add recipients to the message
                # msg['To'] = recipient
                # mail_server.sendmail(msg['From'], msg['To'], msg.as_string())
                mail_server.sendmail(msg['From'], recipient, msg.as_string())
                # mail_server.sendmail(msg['From'], msg['To'], msg.as_string())
                print(f"Email sent successfully to: '{recipient}'")
        except Exception as e:
            # Print any error messages to stdout
            print("Error sending email:", e)
            raise e
        finally:
            # Ensure the SMTP server connection is closed, even if an exception occurs
            mail_server.quit()

def send_email_via_smtplib_humbrela(email_details: Dict,
                                    smtp_server_details: Dict) -> None:
    """
    Sends an email to a list of recipients using Humbrela's SMTP server.

    Args:
        email_details (Dict): A dictionary that contains details for the email notification to be sent (i.e.: list of recipient, subject, body)
        smtp_server_details (Dict): A dictionary that contains SMTP server details in order to send email notification.

    Raises:
        Exception: If an error occurs during email sending.
    """
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = email_details[config["key.json.email.detail.subject"]]
    msg['From'] = humbrela_sender_email

    # Create a secure SSL context with certificate verification disabled (adjust as needed)
    context = ssl.create_default_context()
    ## NOT SECURED ENOUGH: to accept self-signed certificates
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # **Do not verify certificate (less secure)**
    # context.set_ciphers('DEFAULT@SECP384R1,HIGH:!DH:!ECDSA:!AES128-CCM')
    # context.set_ciphers('ECDHE-RSA-AES256-GCM-SHA384')
    # context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    
    # Connect to the SMTP server
    with smtplib.SMTP(smtp_server_details["smtp.server"],
                      smtp_server_details["smtp.port"]) as mail_server:
        try:
            mail_server.ehlo() # Can be omitted
            mail_server.starttls(context=context) # Start TLS encryption if required by your provider
            # server.ehlo() # Can be omitted
            # Login to the SMTP server using the sender's credentials.
            mail_server.login(smtp_server_details["sender"],
                              smtp_server_details["sender.password"])
            # Send the email. The sendmail function requires the sender's email, the list of recipients, and the email message as a string.
            html_content = email_details[config["key.json.email.detail.body"]]
            text_content = "This is an example of a plain text email."
            # Attach parts into message container.
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            # Send the email
            for recipient in email_details[config["key.json.email.detail.recipients"]]:
                # Add recipients to the message
                # msg['To'] = recipient
                # mail_server.sendmail(msg['From'], msg['To'], msg.as_string())
                mail_server.sendmail(msg['From'], recipient, msg.as_string())
                # mail_server.sendmail(msg['From'], msg['To'], msg.as_string())
                print(f"Email sent successfully to: '{recipient}'")
        except Exception as e:
            # Print any error messages to stdout
            print("Error sending email:", e)
            raise e
        finally:
            # Ensure the SMTP server connection is closed, even if an exception occurs
            mail_server.quit()

def send_email_via_yagmail_for_gmail(recipients: list, subject: str, body: str) -> None:
    """
    Sends an email to a list of recipients using Gmail and Yagmail.

    Args:
        recipients (list): A list of recipient email addresses.
        subject (str): The subject of the email.
        body (str): The body of the email (HTML format).
    """
    
    # Initializing the server connection
    yag = yagmail.SMTP(gmail_sender_email, gmail_sender_app_password)
    
    # Send the email to each recipient
    for recipient in recipients:
        # message = {
        #     'to': recipient,
        #     'subject': subject,
        #     'body': body
        #     # 'attachments': ['path/to/your_attachment.pdf']
        #     }
        # yag.send(**message)
        # yag.send(recipient, subject=subject, body=body, attachments=attachments)
        try:
            # Sending the email
            yag.send(to=recipient, subject=subject, contents=body)
            print(f"Email sent successfully to: '{recipient}'")
        except Exception as err:
            print("Error sending email:", err)
            print(Exception, err)
            # raise  # Re-raise the exception for further handling

def send_email(email_details: Dict,
               # recipients: list, subject: str, body: str,
               smtp_server_details: Dict) -> None:
    """
    Sends an email using the appropriate SMTP server based on the sender's email address.

    This function determines whether the sender's email address is associated with Gmail or Humbrela, and then calls the corresponding function to send the email using SMTP.

    Args:
        email_details (Dict): A dictionary that contains details for the email notification to be sent (i.e.: list of recipient, subject, body)
        smtp_server_details (Dict): A dictionary that contains SMTP server details in order to send email notification.
    """

    if "gmail" in smtp_server_details["sender"]:
        # If the sender's email is a Gmail address, use the Gmail SMTP server
        send_email_via_smtplib_gmail(email_details = email_details,
                                     smtp_server_details = smtp_server_details)
    elif "humbrela" in smtp_server_details["sender"]:
        # If the sender's email is a Humbrela address, use the Humbrela SMTP server
        send_email_via_smtplib_humbrela(email_details = email_details,
                                        smtp_server_details = smtp_server_details)
    else:
        # If the sender's email is not associated with Gmail or Humbrela, raise an error
        raise ValueError("Sender's email address must be a Gmail or Humbrela address.")
    # send_email_via_yagmail_for_gmail(recipients, subject, body)
    # print("Do nothing")

def filter_unknown_items(items: list, known_items_keys: list, key: str) -> list:
    """Filters a list of items (articles, videos, etc.) to exclude known items.
    
    Args:
        items (list): A list of items in the format described in the prompt.
        known_items_keys (list): A list of known item URLs.
        key (str): The Json key to compare in the list of items with known_items.
    
    Returns:
        A list of items that are not in the known items list.
    """
  
    unknown_items = []
    for item in items:
        # print(f"item URL: {item[config["key.json.link"]]}") # For Debug Only
        # print(f"Known items list type: {known_items_keys.type}") # For Debug Only
        # print(f"List of known items: {"".join(known_items_keys)}") # For Debug Only
        # print(f"Is item URL in list of known items: {item[config["key.json.link"]] in known_items_keys}") # For Debug Only
        if item[key] not in known_items_keys:
            unknown_items.append(item)
    return unknown_items

def pdf_to_audio_using_speakify(pdf_file: str, language:str='en'):
  """Converts a PDF file to audio.

  Args:
    pdf_file (str): The path to the PDF file.
    language (str): The language to use for text-to-speech (default: 'en').
  """

  with open(pdf_file, 'rb') as pdf_reader:
    reader = PyPDF2.PdfReader(pdf_reader)
    text = ""
    for page in reader.pages:
      text += page.extract_text()

  # speakify.speak(text, language=language)

def pdf_to_audio(pdf_file: str, language: str = 'en',
                tmp_raw_sources_dir: str = config["json.key.tmp.raw.sources.dir"]) -> None:
    """
    Converts a PDF file to an audio file (MP3) using gTTS.

    This function reads the text content from a PDF and converts it to an audio file using the Google Text-to-Speech (gTTS) library.

    Args:
        pdf_file (str): Path to the PDF file.
        language (str, optional): The language code for the generated audio. Defaults to 'en' (English).
        tmp_raw_sources_dir (str, optional): Directory to store temporary raw source files.
            Defaults to the value of the configuration key "json.key.tmp.raw.sources.dir".

    Raises:
        Exception: If an error occurs while reading the PDF or saving the audio file.
    """

    try:
        # Extract text from the PDF
        with open(pdf_file, 'rb') as pdf_reader:
            reader = PyPDF2.PdfReader(pdf_reader)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

        # Create and save the audio file
        myobj = gTTS(text=text, lang=language, slow=False)
        filename = os.path.join(tmp_raw_sources_dir, "welcome.mp3")  # Use a descriptive filename
        myobj.save(filename)
        print(f"Converted PDF to audio: {filename}")

    except Exception as e:
        print(f"Error converting PDF to audio: {e}")
        raise  # Re-raise the exception for further handling

def convert_to_voice_recorder(tmp_raw_sources_dir: str = config["json.key.tmp.raw.sources.dir"]) -> None:
    """
    Converts a specific Hugging Face PDF to audio (for future implementation).

    This function is currently a placeholder for future functionality of converting Hugging Face PDFs to audio.

    Args:
        tmp_raw_sources_dir (str, optional): Directory to store temporary raw source files.
            Defaults to the value of the configuration key "json.key.tmp.raw.sources.dir".
    """

    print("Converting Hugging Face PDFs to audio is not yet implemented.")
    # Uncomment the following line when functionality is implemented
    pdf_file = f"{tmp_raw_sources_dir}/BACKUP-2024.09.30-hf_pdfs/2409.17280.pdf"
    pdf_to_audio(pdf_file, language='en')

def summarize_video_from_transcript(channel_name: str, title: str,
                                    description: str, date: str,
                                    transcript: str, url: str,
                                    model_name: str) -> str:
    """
    Summarizes a Youtube video using the Gemini API based on its transcript.

    This function takes information about a Youtube video (channel name, title, description, date, transcript, URL), and the model name to use, and returns a summary of the video content.

    Args:
        channel_name (str): The name of the Youtube channel that uploaded the video.
        title (str): The title of the Youtube video.
        description (str): The description of the Youtube video.
        date (str): The date the Youtube video was published.
        transcript (str): The text transcript of the Youtube video.
        url (str): The URL of the Youtube video.
        model_name (str): The name of the Gemini model to be used for summarization.

    Returns:
        str: The generated summary of the video content, or None if an error occurs.
    """

    # Initialize a GenerativeModel object using the provided model name
    model = genai.GenerativeModel(model_name = model_name)

    # Find the appropriate prompt template based on the channel name
    template_file = get_value2_on_key2_from_value1_on_key1_in_channels_list(
        key1 = "name",
        value1 = channel_name,
        key2 = "prompt.template",
        channels = config["youtube.api.list.channels"])

    # Load the prompt template for summarizing videos from the specific channel
    with open(template_file, "r") as f:
        prompt_template = f.read()

    # Format the prompt by replacing placeholders with actual video information
    prompt = prompt_template.replace("{channelName}", channel_name if channel_name else "") \
        .replace("{title}", title if title else "") \
        .replace("{description}", description if description else "") \
        .replace("{date}", date if date else "") \
        .replace("{transcript}", transcript if transcript else "") \
        .replace("{url}", url if url else "")
        
    # print(f"prompt: {[prompt]}") # For Debug Only

    try:
        # Generate content using the formatted prompt
        response = model.generate_content([prompt])
    except Exception as e:
        print(f"Failed to summarize video '{title}' due to {e}")
        return None

    # Extract the text from the response object (assuming successful generation)
    try:
        return response.text
    except Exception as e:
        print(f"Failed to access the generated text: {e}")  # Improved error message
        # Log additional information for debugging (optional)
        print(f"First candidate and its finish_reason: {response.candidates[0].finish_reason}")
        return None

def summarize_from_text_content(title: str, author: str, date: str,
                                content: str, model_name: str) -> str:
    """
    Summarizes the content of an article using the Gemini API.

    This function takes information about an article (title, author, date, and content) and the model name to use, and returns a summary of the content.

    Args:
        title (str): The title of the article.
        author (str): The author of the article.
        date (str): The date of the article.
        content (str): The text content of the article.
        model_name (str): The name of the Gemini model to be used for summarization.

    Returns:
        str: The generated summary of the article content.
    """

    # Initialize a GenerativeModel object using the provided model name
    model = genai.GenerativeModel(model_name=model_name)

    # Load the prompt template for summarizing ActuIA articles
    with open(config["template.file.prompt.summarize.actuia.articles"], "r") as f:
        prompt_template = f.read()

    # Format the prompt by replacing placeholders with actual article information
    prompt = prompt_template.replace("{title}", title).replace("{author}", author).replace("{date}", date).replace("{content}", content)

    # Generate content using the formatted prompt
    response = model.generate_content([prompt])

    # Extract the text from the response object and return it as the summary
    return response.text

def summarize_from_pdf_file(title: str, authors: str, pdf_path: str,
                            model_name: str) -> str:
    """
    Summarizes a research paper using the Gemini API.

    This function takes the title, authors, PDF path, and model name as input and returns a summary of the paper.

    Args:
        title (str): The title of the paper.
        authors (str): The authors of the paper (comma-separated list or single author).
        pdf_path (str): The path to the PDF file containing the research paper.
        model_name (str): The name of the Gemini model to be used for summarization.

    Returns:
        str: The generated summary of the research paper.
    """

    # Initialize a GenerativeModel object using the provided model name
    model = genai.GenerativeModel(model_name=model_name)

    # Upload the PDF file to Gemini with a descriptive display name
    pdf_file = genai.upload_file(path=pdf_path, display_name=f"paper_{title}")

    # Load the prompt template for summarizing Hugging Face papers
    with open(config["template.file.prompt.summarize.HF.paper"], "r") as f:
        prompt_template = f.read()

    # Replace placeholders in the prompt template with actual title and authors
    prompt = prompt_template.replace("{title}", title).replace("{authors}", authors)

    # Generate content using the uploaded PDF and the formatted prompt
    response = model.generate_content([pdf_file, prompt])

    # Extract the text from the response object and return it as the summary
    return response.text

def call_LLM_to_get_summary(item: Dict, source_format: str, model_name: str) -> str:
    """
    In order to create a content's summary, the function calls the right LLM accordingly to the source format and model name passed as parameters.
    Finally, it returns an updated dictionary.
    
    **Args:**
        item (Dict): A dictionary containing the needed attributes to create a summary from.
        source_format (str): The format of the content to be summarized. It could be a PDF file, a regular text content, or a Youtube video.
        model_name (str): The LLM to be used to create the summary from the item's content.
    
    **Returns:**
        The summary created from the given content.
    """
    # Initialize output summary
    summary = None
    # Depending on the source format, call the right function to summarize the item using the model name passed as parameter
    if (source_format == config["key.json.source.format.pdf"]):
        # print("Source format: PDF file.") # For Debug Only
        summary = summarize_from_pdf_file(
            title      = item[config["key.json.title"]],
            authors    = item[config["key.json.authors"]],
            pdf_path   = item[config["key.json.pdf.path"]],
            model_name = model_name
        )
    elif (source_format == config["key.json.source.format.text.content"]):
        # print("Source format: Regular text content.") # For Debug Only
        summary = summarize_from_text_content(
            title      = item[config["key.json.title"]],
            author     = item[config["key.json.author"]],
            date       = item[config["key.json.date"]],
            content    = item[config["key.json.content"]],
            model_name = model_name
        )
    elif (source_format == config["key.json.source.format.youtube.video"]):
        # print("Source format: Youtube channel's video.") # For Debug Only
        # Try to get the summary of the video
        # # print(f"Channel Name: {item[config["key.json.channel.name"]]}")
        # print(f"Title: {item[config["key.json.title"]]}")
        # print(f"Description: {item[config["key.json.description"]]}")
        # print(f"Date: {item[config["key.json.date"]]}")
        # print(f"Transcript: {item[config["key.json.transcript"]],}")
        # print(f"URL: {item[config["key.json.link"]]}")
        summary = summarize_video_from_transcript(
            channel_name = item[config["key.json.channel.name"]],
            title        = item[config["key.json.title"]],
            description  = item[config["key.json.description"]],
            date         = item[config["key.json.date"]],
            transcript   = item[config["key.json.transcript"]],
            url          = item[config["key.json.link"]],
            model_name   = model_name
        )
    else:
        print("Unrecognized source format.") # For Debug Only
        # If the source's format is not recognized, i.e. not a PDF, a regular text content or a Youtube video, raise an ValueError
        raise ValueError("Source's format is not recognized, i.e. not a PDF, a regular text content or a Youtube video.")
    
    # Return the computed summary
    return summary

def process_list_of_items(source_name: str,
                          source_format: str,
                          data_file_path: str,
                          known_items_json_key: str,
                          new_items: List[Dict],
                          smtp_server_details: Dict,
                          email_details: Dict,
                          keys_to_ignore: list,
                          summarize_it: bool = True) -> None:
                          # keys_to_ignore: list) -> List[Dict]:
    """
    This function aims to process daily a list of items (papers, articles, videos or else) by performing the following tasks:
    
    1. Retrieves a list of items from a given website (papers, articles in PDF, HTML format, etc.) or Youtube channels (videos)
    2. In the event of new items compared to a list of items stored in a json data file, do the following tasks:
        a. Iterates on the new items and compute a summary of each item's content using LLM API.
        b. If successfully computed, the summary is then added to the list of item's attributes.
        c. Updates the json data file with new items (and their summaries).
        d. Sends an email notification to a list of recipients.
    
    **Args:**
        source_name (str): The name of the source of the content to be summarized.
        source_format (str): The format of the content to be summarized. It could be a PDF file, a regular text content, or a Youtube video.
        data_file_path (str): Json file to store processed items.
        known_items_json_key (str): Key for known items in Json data file.
        new_items (List[Dict]): A list of dictionaries. Each dictionary contains the following attributes:
        (Note: the items contain at least those attributes as they might be mandatory for the computation of the summary)
            * `title (str)`: The title of the article,
            * `authors (list) or author (str)`: The list of author(s) of the article,
            * `link (str)`: The URL of the article,
            * `pdf_path (str)`: The local path where the PDF is saved (if downloaded).
            * `thumbnailUrl (str)`: The URL of the thumbnail image to illustrate the article,
            * `date (str)`: The date of the article,
            * `link (str)`: The URL of the article,
            * `content (str)`: The content of the article.
            * `recipients (list)`: A list of email addresses to send notifications to.
            * `sender (str)`: Email address of the sender.
            * `sender_password (str)`: Password of the email address of the sender.
            * `smtp_server (str)`: SMTP server to be used to send the email.
            * `smtp_port (str)`: SMTP server port to be used to send the email.
        smtp_server_details (Dict): Details of the SMTP server in order to send email notification.
        email_details (Dict): Details of the email notification to be sent.
        keys_to_ignore (list): A list of keys to exclude from the json data to generate the HTML table.
        summarize_it (bool): Whether the summarizing function leveragin GenAI must be called or not.
    
    **Returns:**
        An updated list of dictionaries. Each dictionary contains the same attributes as the input ones, plus the summary:
            * `title (str)`: The title of the article,
            * `authors (list) or author (str)`: The list of author(s) of the article,
            * `link (str)`: The URL of the article,
            * `pdf_path (str)`: The local path where the PDF is saved (if downloaded).
            * `thumbnailUrl (str)`: The URL of the thumbnail image to illustrate the article,
            * `date (str)`: The date of the article,
            * `link (str)`: The URL of the article,
            * `content (str)`: The content of the article.
            * `recipients (list)`: A list of email addresses to send notifications to.
            * `sender (str)`: Email address of the sender.
            * `sender_password (str)`: Password of the email address of the sender.
            * `smtp_server (str)`: SMTP server to be used to send the email.
            * `smtp_port (str)`: SMTP server port to be used to send the email.
            * `summary (str)`: The summary that was created by external LLM and added to each item's list of attributes.
    """
    # print(f"====> Start with printing the list of treated items for '{source_name}': {', '.join(extract_node_values(
    #         json_data = items,
    #         json_key = known_items_json_key))}") # For Debug Only
    
    ## Local variables
    all_items: List[Dict] = []
    known_items_keys = list() # Set to track initially known items based on their unique key
    # print(f"=> data_file_path: {data_file_path}") # For Debug Only
    if os.path.isfile(data_file_path) is True:
        # Load list of previously processed articles from the JSON file
        # Extract and store a set of URLs from previously processed articles
        with open(data_file_path) as fp:
            all_items = json.load(fp)
        known_items_keys = extract_node_values(
            json_data = all_items,
            json_key = known_items_json_key) # Set to track seen ActuIA articles URLs
        # print(f"List of known items from '{data_file_path}': {', '.join(known_items_keys)}") # For Debug Only
    
    # print(f"List of treated items for '{source_name}': {', '.join(extract_node_values(
    #         json_data = new_items,
    #         json_key = known_items_json_key))}") # For Debug Only
    # If there are new articles, compute summary, update list of items and send email notification to a list of recipients
    # NOTE: THIS IS REDUNDANT BECAUSE THE LIST 'new_items' ALREADY CONTAINS NEW ITEMS ONLY
    new_items = filter_unknown_items(
        items = new_items,
        known_items_keys = known_items_keys,
        key = known_items_json_key)
    print(f"=> Number of new items: {len(new_items)}") # For Debug Only
    
    # If there isn't any new items, exit the function
    if len(new_items) <= 0:
        print(f"=> Number of items treated for: '{source_name}': {len(new_items)}") # For Debug Only
        print(f"=> Number of items already known for: '{source_name}': {len(known_items_keys)}") # For Debug Only
        print(f"=> No new item to extract for: '{source_name}'")
        return
    
    # Initialize the ouput list of dictionaries
    new_items_with_summary = new_items.copy()
    
    # If there are new items, attempt to get a summary leveraging LLM,
    # then export the updated list of items to json file
    # 2. Define primary and secondary models
    # primary_model = config["gemini.api.service.version.1.5.flash.002"]
    primary_model = config["gemini.api.service.version.2.5.pro"]
    # primary_model = config["gemini.api.service.version.1.5.pro.002"]
    # secondary_model = config["gemini.api.service.version.1.5.flash"]
    secondary_model = config["gemini.api.service.version.2.5.flash"]
    # secondary_model = config["gemini.api.service.version.1.5.flash.002"]
    
    # 3. Iterate on each item (dictionary) to be summarized in the list
    # iter_item = 1 # For Debug Only
    for item in new_items:
        # break
        # for key, value in item.items():
        #     print(f"Current item key: {key}, Value: {value}") # For Debug Only
        summary = None
        if not summarize_it:
            # Update the relevant dictionary with summary = None and loop to next item
            matching_dictionary = next(filter(lambda d: d[config["key.json.link"]] == item[config["key.json.link"]], new_items_with_summary))
            matching_dictionary["summary"] = summary
            continue
        
        try:
            # 4a. Try using primary model to summarize the item's content
            summary = call_LLM_to_get_summary(item = item,
                                              source_format = source_format,
                                              model_name = primary_model)
        except Exception:
            try:
                # 4b. Fallback to secondary model on summarization failure
                print(f"Failed to summarize item {item[config['key.json.title']]}. Trying with a different model.")
                summary = call_LLM_to_get_summary(item = item,
                                                  source_format = source_format,
                                                  model_name = secondary_model)
            except Exception as e:
                print(f"Failed to summarize content for the item '{item[config['key.json.title']]}' with both models.")
                print(f"Due to {e}")
        finally:
            if summary != None:
                summary.replace("\n", " ")
                # If Hugging Face Papers, update link and delete temporary PDF files
                if config["key.json.hf.source.name"] in source_name:
                    item[config["key.json.link"]].replace("https://arxiv.org/abs/", "https://huggingface.co/papers/")
                    # hf_link = item[config["key.json.link"]].replace("https://arxiv.org/abs/", "https://huggingface.co/papers/")
                    # print(f"=> Hugging Face Paper hf_link: {hf_link}") # For Debug Only
                    if os.path.exists(item[config["key.json.pdf.path"]]):
                        os.remove(item[config["key.json.pdf.path"]])
            
            # print(f"=> summary: {summary}")
            # Update the relevant dictionary item with the computed summary and store
            # new_items_with_summary.append({**item, config["key.json.summary"]: summary})
            # Use filter to find the dictionary with the matching title and update the summary
            matching_dictionary = next(filter(lambda d: d[config["key.json.link"]] == item[config["key.json.link"]], new_items_with_summary))
            matching_dictionary["summary"] = summary
            
            # Introduce a delay to avoid rate limiting
            time.sleep(config["google.genai.sleep.time"])
        # if iter_item > 2: # For Debug Only
        #     break # For Debug Only
        # iter_item += 1 # For Debug Only
    
    # Add new items with summary to the list of already known items and export it to the json data file
    # print(f"Updating data to Json file {data_file_path}") # For Debug Only
    # all_items.insert(0,
    #                  new_items_with_summary)
    # all_items.extend(new_items_with_summary) # Concatenates at the end instead of beginning
    all_items = new_items_with_summary + all_items
    with open(data_file_path, "w") as f:
        json.dump(all_items, f, indent=2)
    print(f"=> Saved {len(all_items)} items' information for '{source_name}'")
    
    # Send an email notification if new articles were found
    # Before sending email, test if there are any non-ASCII character in the Json data
    # for key, value in actuia_articles[0].items():
    #     for char in value:
    #         if ord(char) > 127:
    #             print(f"Non-ASCII character: {char} (ordinal: {ord(char)})")
    
    # Create email subject
    # email_subject = f"{config["key.json.monitoring.category.techno"]} {source_name}"
    # Ignore key 'content' from the HTML to generate
    # keys_to_ignore = [config["key.json.content"],
    #               config["key.json.link"]]
    # Add body to email details by converting Json data to HTML
    email_details[config["key.json.email.detail.body"]] = \
        json_to_html(new_items_with_summary,
                     keys_to_ignore)
    # Send email
    send_email(email_details = email_details,
               # recipients = recipients,
               # subject = email_subject,
               # body = email_body,
               smtp_server_details = smtp_server_details)
    
    # Returns list of items (dictionaries) including attribute 'summary'
    # return new_items_with_summary
