import os
import json
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AzureOpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="YOUR_API_VERISON",
)

class TextInput(BaseModel):
    text: str

@app.post("/summarize-text/")
async def summarize_text(input_data: TextInput):
    try:
        text = input_data.text  
        
        chat_prompt = [
            {"role": "system", "content": [{"type": "text", "text": "You are an AI assistant that helps people summarize text."}]},
            {"role": "user", "content": [{"type": "text", "text": text}]}
        ]
        
        completion = client.chat.completions.create(
            model=deployment,
            messages=chat_prompt,
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )

        response_json = completion.to_json()
        response_dict = json.loads(response_json)
        summary = response_dict["choices"][0]["message"]["content"]
        
        return {"summary": summary}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing the content: {str(e)}")

class URLItem(BaseModel):
    url: str

@app.post("/scrape/")
async def scrape_url(url_item: URLItem):
    try:
        response = requests.get(url_item.url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text_content = soup.get_text(separator="\n", strip=True)
            
            file_path = "scraped_text.txt"
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text_content)
            
            return {"content": text_content, "file": file_path}
        else:
            raise HTTPException(status_code=response.status_code, detail="Unable to fetch the website")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping the website: {str(e)}")