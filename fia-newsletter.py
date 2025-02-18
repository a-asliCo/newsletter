import os
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------------------------
# Scraping Setup - News & Research Papers
# -----------------------------------------------
news_sources = [
    "https://theresanaiforthat.com/s/fashion/",
    "https://bilawal.ai/",
    "https://heatherbcooper.substack.com/",
    "https://civitai.com/articles",
    "https://www.thecurrent.com/sections/retail",
    "https://www.businessoffashion.com/topics/technology/",
    "https://fashnerd.com/",
    "https://www.glossy.co/fashion/",
    "https://www.wgsn.com/en/blog",
    "https://blog.wideeyes.ai/category/technology/",
    "https://wwd.com/business-news/technology/",
]

academic_sources = [
    "https://arxiv.org/list/cs.AI/recent",
    "https://arxiv.org/list/cs.LG/recent",
    "https://arxiv.org/list/cs.CV/recent",
    "https://arxiv.org/list/cs.HC/recent",
    "https://dl.acm.org/action/showMostCitedArticles",
    "https://www.nature.com/subjects/artificial-intelligence",
    "https://journals.sagepub.com/home/dsj",
    "https://ieeexplore.ieee.org/Xplore/home.jsp",
]

headers = {'User-Agent': 'Mozilla/5.0'}

keywords = [
    'ai', 'artificial intelligence', 'fashion', 'retail', 'creative technology',
    'fashion innovation', 'ml', 'machine learning', 'generative ai', 'gan ai',
    'comfy ui', '2d to 3d', 'text to 3d', 'technology conferences', 'garment',
    'clothing', 'technology and design', 'fashion design', 'creative computing'
]

# -----------------------------------------------
# Scraping Function
# -----------------------------------------------
def scrape_articles(sources):
    urls = []
    for website in sources:
        try:
            response = requests.get(website, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            for link in soup.find_all('a', href=True):
                href = link['href']

                if href.endswith('/comments'):
                    continue

                if any(re.search(rf'\b{re.escape(keyword)}\b', href, re.IGNORECASE) for keyword in keywords):
                    full_url = href if href.startswith('http') else website.rstrip('/') + '/' + href.lstrip('/')
                    urls.append(full_url)

        except Exception as e:
            print(f"⚠️ Error scraping {website}: {e}")

    return list(set(urls))  # Remove duplicates

# -----------------------------------------------
# Scraping News & Research Papers
# -----------------------------------------------
news_urls = scrape_articles(news_sources)
academic_urls = scrape_articles(academic_sources)

print(f"✅ Found {len(news_urls)} news articles.")
print(f"✅ Found {len(academic_urls)} research papers.")

# -----------------------------------------------
# Extract Titles, Subtitles & Links
# -----------------------------------------------
def get_previews(urls):
    previews = []
    for article in tqdm(urls, desc="Scraping articles"):
        try:
            data = requests.get(article, headers=headers, timeout=10)
            soup = BeautifulSoup(data.content, 'html.parser')

            title_tag = soup.find(['h1', 'h2', 'h3'])
            title = title_tag.text.strip() if title_tag else "No Title"

            subtitle_tag = soup.find(['h3', 'h4', 'p'])
            subtitle = subtitle_tag.text.strip() if subtitle_tag else "No Subtitle"

            previews.append({'title': title, 'subtitle': subtitle, 'url': article})

        except Exception as e:
            print(f"⚠️ Error processing {article}: {e}")
    
    return previews

news_previews = get_previews(news_urls)
academic_previews = get_previews(academic_urls)

# -----------------------------------------------
# HTML Generation (Preserving Structure)
# -----------------------------------------------
template_path = "/Users/ayseasliilhan/Desktop/newsletter/email.html"

if os.path.exists(template_path):
    with open(template_path, "r", encoding="utf-8") as template:
        soup = BeautifulSoup(template.read(), "html.parser")
else:
    raise FileNotFoundError(f"Template file '{template_path}' not found.")

news_section = soup.find('div', class_='news-feed').find('div', class_='scrollable-content')
long_readings_section = soup.find('div', class_='longer-readings').find('div', class_='scrollable-content')

if not news_section or not long_readings_section:
    raise ValueError("❌ News or Longer Readings section not found in the HTML template.")

# News Section
for article in news_previews:
    article_entry = BeautifulSoup(f"""
    <div class="columns">
        <div class="column">
            <h1 class="title">{article['title']}</h1>
            <p class="subtitle">{article['subtitle']}...</p>
            <a class="link" href="{article['url']}">Read more</a>
        </div>
    </div>
    """, "html.parser")

    news_section.append(article_entry)

# Longer Readings Section (Research Papers)
for article in academic_previews:
    article_entry = BeautifulSoup(f"""
    <div class="columns">
        <div class="column">
            <h1 class="title">{article['title']}</h1>
            <p class="subtitle">{article['subtitle']}...</p>
            <a class="link" href="{article['url']}">Read more</a>
        </div>
    </div>
    """, "html.parser")

    long_readings_section.append(article_entry)

# Save Updated HTML
output_folder = "/Users/ayseasliilhan/Desktop/newsletter/fia-newsletter"
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.join(output_folder, "index.html")

with open(output_file, "w", encoding="utf-8") as file:
    file.write(str(soup))

print(f"✅ HTML saved successfully: {output_file}")

# -----------------------------------------------
# Email Sending (Fixed to Include All Recipients)
# -----------------------------------------------
sender_email = "fia.newsletter.2025@gmail.com"
receiver_email = [
    "asli.ilhan@arts.ac.uk", "l.chatterton@fashion.arts.ac.uk",
    "m.robertsislam@fashion.arts.ac.uk", "c.kazantzis@arts.ac.uk",
    "e.cies@fashion.arts.ac.uk", "t.ellins@arts.ac.uk"
]
password = "kuvx ouol tnem relg"

newsletter_link = "https://fia-newsletter.vercel.app"

message = MIMEMultipart("alternative")
message["Subject"] = "🚀 Our Newsletter is Updated!"
message["From"] = sender_email
message["To"] = ", ".join(receiver_email)  # ✅ FIXED: Ensuring all emails receive the message

html = f"""
<html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Hey Team,</p>
        <p>Our latest newsletter is now available. Click below to read it:</p>
        <p>
            <a href="{newsletter_link}" style="font-size: 16px; text-decoration: none; color: #007BFF; font-weight: bold;">
                🔗 Read the Newsletter ➡️
            </a>
        </p>
        <p>Stay inspired!<br><br>The FIA's Newsletter RoBot 🤖</p>
    </body>
</html>
"""

message.attach(MIMEText(html, "html"))

context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())

print("✅ Email sent successfully to all recipients!")
