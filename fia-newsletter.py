import os
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------------------------
# Scraping Setup - List of Websites
# -----------------------------------------------
websites = [
    "https://theresanaiforthat.com/s/fashion/",
    "https://bilawal.ai/",
    "https://heatherbcooper.substack.com/",
    "https://www.spatialintelligence.ai/p/2025-the-year-imagination-becomes",  # Blocked
    "https://civitai.com/articles",
    "https://www.thecurrent.com/sections/retail",
    "https://www.businessoffashion.com/topics/technology/",
    "https://fashnerd.com/",
    "https://www.glossy.co/fashion/",
    "https://www.wgsn.com/en/blog",
    "https://blog.wideeyes.ai/category/technology/",
    "https://wwd.com/business-news/technology/",
]

headers = {'User-Agent': 'Mozilla/5.0'}

# Keywords for filtering relevant articles
keywords = [
    'ai', 'artificial intelligence', 'fashion', 'retail', 'creative technology',
    'fashion innovation', 'ml', 'machine learning', 'generative ai', 'gan ai',
    'comfy ui', '2d to 3d', 'text to 3d', 'technology conferences', 'garment',
    'clothing', 'technology and design', 'fashion design', 'creative computing'
]

# -----------------------------------------------
# Scraping Process
# -----------------------------------------------
urls = []

for website in websites:
    try:
        response = requests.get(website, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        for link in soup.find_all('a', href=True):
            href = link['href']

            # Ignore comments links or unrelated pages
            if href.endswith('/comments'):
                continue

            # Check if the URL contains any of the keywords
            if any(re.search(rf'\b{re.escape(keyword)}\b', href, re.IGNORECASE) for keyword in keywords):
                full_url = href if href.startswith('http') else website.rstrip('/') + '/' + href.lstrip('/')
                urls.append(full_url)

    except Exception as e:
        print(f"⚠️ Error scraping {website}: {e}")

# Remove duplicate URLs
urls = list(set(urls))
print(f"✅ Found {len(urls)} articles.")

# -----------------------------------------------
# Article Previews (Text Only)
# -----------------------------------------------
previews = []

for article in tqdm(urls, desc="Scraping articles"):
    try:
        data = requests.get(article, headers=headers, timeout=10)
        soup = BeautifulSoup(data.content, 'html.parser')

        # Extract title
        title_tag = soup.find(['h1', 'h2', 'h3'])
        title = title_tag.text.strip() if title_tag else "No Title"

        # Extract subtitle
        subtitle_tag = soup.find(['h3', 'h4', 'p'])
        subtitle = subtitle_tag.text.strip() if subtitle_tag else "No Subtitle"

        previews.append({
            'title': title,
            'subtitle': subtitle,
            'url': article
        })

    except Exception as e:
        print(f"⚠️ Error processing {article}: {e}")

# -----------------------------------------------
# HTML Generation (Without Images)
# -----------------------------------------------
template_path = "/Users/ayseasliilhan/Desktop/newsletter/email.html"

if os.path.exists(template_path):
    with open(template_path, "r", encoding="utf-8") as template:
        soup = BeautifulSoup(template.read(), "html.parser")
else:
    raise FileNotFoundError(f"Template file '{template_path}' not found.")

article_template = soup.find('div', attrs={'class': 'columns'})
if not article_template:
    raise ValueError("Article template not found in the HTML file.")

html_start = str(soup).split(str(article_template))[0].replace('\n', '')
html_end = str(soup).split(str(article_template))[1].replace('\n', '')

newsletter_content = ""
for article in previews:
    try:
        # Update title
        title = article_template.find('h1')
        if title:
            title.string = article['title'][:300]

        # Update subtitle
        subtitle = article_template.find('p')
        if subtitle:
            subtitle.string = article['subtitle'][:300] + "..."

        # Update link
        link = article_template.find('a')
        if link:
            link['href'] = article['url']
            link.string = "Read more"

        newsletter_content += str(article_template).replace('\n', '')

    except Exception as e:
        print(f"⚠️ Error updating article template: {e}")

email_content = html_start + newsletter_content + html_end
html_output = BeautifulSoup(email_content, "html.parser").prettify()

# Ensure 'src' folder exists
output_folder = "/Users/ayseasliilhan/Desktop/newsletter/fia-newsletter"
os.makedirs(output_folder, exist_ok=True)
output_file = os.path.join(output_folder, "index.html")

with open(output_file, "w", encoding="utf-8") as file:
    file.write(html_output)

print(f"✅ HTML saved successfully: {output_file}")

# -----------------------------------------------
# Email Sending
# -----------------------------------------------
sender_email = "fia.newsletter.2025@gmail.com"
receiver_email = "asli.ilhan@arts.ac.uk"
password = "kuvx ouol tnem relg"

newsletter_link = "https://fia-newsletter.vercel.app"

message = MIMEMultipart("alternative")
message["Subject"] = "🚀 Our Newsletter is Updated!"
message["From"] = sender_email
message["To"] = receiver_email

text = f"""Hey Team,
Our latest newsletter is now available. Click below to read it:

🔗 {newsletter_link} ➡️

Stay inspired!

The FIA's Newsletter RoBot 🤖
"""

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
        <p>Stay inspired!<br>
        <br>The FIA's Newsletter RoBot 🤖</p>
    </body>
</html>
"""

message.attach(MIMEText(html, "html"))

context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())

print("✅ Email sent successfully!")
