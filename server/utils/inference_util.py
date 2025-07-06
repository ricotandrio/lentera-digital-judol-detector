import pytesseract
from PIL import Image
import os
import tempfile
from playwright.sync_api import sync_playwright
from database.model import BlacklistsModel
from transformers import pipeline
from bs4 import BeautifulSoup
import re

def get_inference_pipeline():
  try:
    return pipeline("text-generation", model="google/gemma-3n-E2B-it")
  except Exception as e:
    print(f"Error loading inference pipeline: {e}")
    raise Exception("Failed to load inference pipeline. Ensure the model is available and the transformers library is correctly installed.")
  
def inference(text_ocr: str, cleaned_html_content: str) -> str:
  inference_pipeline = get_inference_pipeline()
  
  prompt = """
    You are a helpful AI assistant that classifies website into one of the following categories:
    - "Judol" for content related to gambling, betting, or any form of illegal online gambling.
    - "Non-Judol" for content that does not relate to gambling or illegal activities
    
    Your task is to analyze the provided website content and return the most appropriate classification.
    Please classify the following content that is extracted from all image and HTML content of a website:
    - Here is the text of image that fetched via OCR:
    {text_ocr}
    
    - Here is the cleaned HTML content:
    {cleaned_html_content}
    
    Based on the above content, classify it as either "Judol" or "Non-Judol".
    Provide only the classification label as your response.
  """.format(text_ocr=text_ocr, cleaned_html_content=cleaned_html_content)
  
  try:
    result = inference_pipeline(prompt, max_new_tokens=5)
    output = result[0]["generated_text"].strip().split()[-1]
    
    # print(f"[OUTPUT] {output}")

    if output == "Judol":
      return "Judol"
    elif output == "Non-Judol":
      return "Non-Judol"
    else:
      raise Exception(f"Unexpected output: {output}")
      
  except Exception as e:
    print(f"Error during classification: {e}")
    raise Exception("Inference failed, please check the input data or model configuration.")

def get_screenshot_and_ocr(url: str):
  with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
    path = tmp.name

  with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    page.screenshot(path=path)
    html_content = page.content()
    browser.close()

  text_ocr = pytesseract.image_to_string(Image.open(path))
  
  # print("\n[DEBUG] Screenshot saved to:", path)
  # print("[OCR TEXT START]")
  # print(text_ocr.strip())
  # print("[OCR TEXT END]")

  # print("\n[HTML CONTENT START]")
  # print(html_content.strip()[:100]) 
  # print("[HTML CONTENT END]\n")

  os.remove(path)
  
  return text_ocr, html_content

def perform_inference(url: str) -> bool:
  if not url:
    print("URL is empty, cannot perform inference.")
    raise ValueError("URL cannot be empty.")
  
  def clean_html_content(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for tag in soup(["script", "style", "iframe", "video", "audio", "img", "svg", "form", "input", "button"]):
      tag.decompose()
      
    raw_text = soup.get_text(separator="\n")
    
    collapsed = re.sub(r'\n+', '\n', raw_text)
    
    return collapsed.strip()
  
  try:
    text_ocr, html_content = get_screenshot_and_ocr(url)
    if not text_ocr or not html_content:
      print("No OCR or HTML content found.")
      return False
    
    cleaned_html_content = clean_html_content(html_content)
    
    print("\n[DEBUG] Cleaned HTML content:")
    print("[CLEANED HTML CONTENT START]")
    print(cleaned_html_content[:100])  
    print("[CLEANED HTML CONTENT END]\n")
    
    if not cleaned_html_content:
      raise Exception("Cleaned HTML content is empty.")
    
    output_class = inference(text_ocr, cleaned_html_content)
    
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