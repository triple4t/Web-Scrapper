import requests
import gradio as gr
from bs4 import BeautifulSoup

def scrape_website(url):
    """Scrapes a website and extracts plain text content."""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text_content = soup.get_text(separator="\n", strip=True)
            file_path = "scraped_text.txt"
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_content)
            return text_content, file_path
        else:
            return f"❌ Error: Unable to fetch the website (Status Code: {response.status_code})", None
    except Exception as e:
        return f"❌ Exception occurred: {str(e)}", None

iface = gr.Interface(
    fn=scrape_website,
    inputs=gr.Textbox(label="Enter Website URL"),
    outputs=[gr.Textbox(label="Scraped Content", lines=10), gr.File(label="Download Scraped Text")],
    title="Website Scraper",
    description="Enter a URL to scrape the text content from the website. Download the scraped text as a file.",
    allow_flagging="never"
)

if __name__ == "__main__":
    iface.launch()
