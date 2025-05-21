import os
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI
from dotenv import load_dotenv, find_dotenv
from crawl4ai import AsyncWebCrawler

# Load .env into os.environ
load_dotenv(find_dotenv())

# Configure logging so you see tracebacks in your console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key      =os.getenv("AZURE_OPENAI_API_KEY"),
    api_version  =os.getenv("AZURE_OPENAI_API_VERSION"),
)

class TextInput(BaseModel):
    text: str

@app.post("/summarize-text/")
async def summarize_text(input_data: TextInput):
    try:
        chat_prompt = [
            {"role": "system", "content": [
                {"type": "text", "text": "You are an AI assistant that summarizes text."}
            ]},
            {"role": "user", "content": [
                {"type": "text", "text": input_data.text}
            ]}
        ]
        completion = client.chat.completions.create(
            model              = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages           = chat_prompt,
            max_tokens         = 800,
            temperature        = 0.7,
            top_p              = 0.95,
            frequency_penalty  = 0,
            presence_penalty   = 0,
            stream             = False,
        )
        data = json.loads(completion.to_json())
        return {"summary": data["choices"][0]["message"]["content"]}

    except Exception as e:
        logger.exception("summarize-text failed")
        raise HTTPException(500, detail=str(e))


class URLItem(BaseModel):
    url: str

@app.post("/scrape/")
async def scrape_url(url_item: URLItem):
    try:
        # Use AsyncWebCrawler.arun() (not .crawl())
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url_item.url)

        # Prefer markdown, fallback to plain text
        text_content = getattr(result, "markdown", None) or getattr(result, "text", None)
        if not text_content:
            raise ValueError("No content extracted (markdown/text is empty)")

        # Persist to file
        file_path = "scraped_text.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text_content)

        return {"content": text_content, "file": file_path}

    except Exception as e:
        logger.exception("Error in /scrape/")
        raise HTTPException(500, detail=f"Scraping failed: {e}")
