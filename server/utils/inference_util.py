from urllib import response
from playwright.sync_api import sync_playwright
from database.model import BlacklistsModel
from transformers import pipeline
import time
import requests
import json
import dotenv

def get_inference_pipeline():
  try:
    return pipeline("text-classification", model="google/gemma-3n-E2B-it")
  except Exception as e:
    print(f"Error loading inference pipeline: {e}")
    raise Exception("Failed to load inference pipeline. Ensure the model is available and the transformers library is correctly installed.")
  
def inference(cleaned_html_content: str) -> str:

  prompt = """
    You are a professional gambling site detector.
    Analyze the given HTML content and decide: is it a gambling site?
    Output exactly one keyword based on your analysis:
    "Judol" if the HTML is from a gambling site,
    "Non-Judol" otherwise.

    Answer with no explanation, no punctuation, only the keyword either "Judol" or "Non-Judol".

    Don't include prompt or any other than "Judol" or "Non-Judol" in your response.

    Here is the content of the site:
    {cleaned_html_content}
  """.format(cleaned_html_content=cleaned_html_content.replace("\n", " ").replace("  ", ""))
  
  try:
    API_KEY = dotenv.get("API_KEY")
    
    if not API_KEY:
      raise Exception("API_KEY not found in environment variables. Please set the API_KEY in your .env file.")
    
    URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    headers = {
      "Content-Type": "application/json",
      "X-goog-api-key": API_KEY
    }

    payload = {
      "contents": [
        {
          "parts": [
              {
                "text": prompt
              }
          ]
        }
      ]
    }
    
    start = time.perf_counter()

    response = requests.post(URL, headers=headers, data=json.dumps(payload))

    end = time.perf_counter()
    
    if response.ok:
      response = response.json()
      
      print("[DEBUG] API request successful, response: ", response)
      
      print("[DEBUG] Inference time: ", end - start)
      
      print("[DEBUG] Inference response: ", response["candidates"][0]["content"]["parts"][0]["text"].strip().replace("\n", ""))
      
      output = response["candidates"][0]["content"]["parts"][0]["text"].strip().replace("\n", "")

      if output == "Judol":
        return "Judol"
      elif output == "Non-Judol":
        return "Non-Judol"
      else:
        raise Exception(f"Unexpected output: {output}")
    else:
      raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
      
  except Exception as e:
    print(f"Error during classification: {e}")
    raise Exception("Inference failed, please check the input data or model configuration.")

def perform_inference(url, cleaned_html_content: str) -> bool:

  if not cleaned_html_content:
    print("No HTML content provided for inference.")
    return False
  
  try:
    output_class = inference(cleaned_html_content)
    
    print("\n[DEBUG] Inference output class:", output_class)
    
    if output_class == "Judol":
      print("Detected Judol content, adding to blacklist.")
      BlacklistsModel.add_to_blacklist(url)
      return True
    else:
      print("Content is not Judol, no action taken.")
      return False
    
  except Exception as e:
    print(f"Error adding to blacklist: {e}")
    return None