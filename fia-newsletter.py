import os
import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------------------------
# Scraping Setup
# -----------------------------------------------
keywords = [
    'ai', 'artificial intelligence', 'fashion', 'retail', 'creative technology',
    'fashion innovation', 'ml', 'machine learning', 'generative ai', 'gan ai',
    'comfy ui', '2d to 3d', 'text to 3d', 'technology conferences', 'garment',
    'clothing', 'technology and design', 'fashion design', 'creative computing'
]

base_url = "https://heatherbcooper.substack.com/"
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(base_url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

urls = []
for link in soup.find_all('a', href=True):
    href = link['href']
    if href.endswith('/comments'):
        continue

    if any(re.search(rf'\b{re.escape(keyword)}\b', href, re.IGNORECASE) for keyword in keywords):
        full_url = href if href.startswith('http') else base_url.rstrip('/') + '/' + href.lstrip('/')
        urls.append(full_url)

urls = list(set(urls))  # Remove duplicates

# -----------------------------------------------
# Article Previews
# -----------------------------------------------
previews = []

for article in tqdm(urls, desc="Scraping articles"):
    try:
        data = requests.get(article, headers=headers)
        soup = BeautifulSoup(data.content, 'html.parser')

        # Extract title
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else "No Title"

        # Extract subtitle
        subtitle_tag = soup.find('h3')
        subtitle = subtitle_tag.text.strip() if subtitle_tag else "No Subtitle"

        # Locate article content area to extract relevant images
        content_divs = soup.find_all(['div', 'article'], class_=re.compile(r'(content|article|post|entry)', re.IGNORECASE))

        image = None
        for div in content_divs:
            img_tags = div.find_all('img', src=True)
            for img in img_tags:
                image = img.get('srcset', '').split(" ")[0] or img.get('data-src') or img.get('src')
                if image:
                    break
            if image:
                break

        previews.append({
            'title': title,
            'subtitle': subtitle,
            'image': image if image else "No Relevant Image Found"
        })

    except Exception as e:
        print(f"Error processing {article}: {e}")

# -----------------------------------------------
# HTML Generation
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
for i, article in enumerate(previews):
    try:
        # Update image
        img = article_template.find('img')
        if img:
            img['src'] = article['image']

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
            link['href'] = urls[i]
            link.string = "Read more"

        newsletter_content += str(article_template).replace('\n', '')

    except Exception as e:
        print(f"Error updating article template: {e}")

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
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
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