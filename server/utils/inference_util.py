import pytesseract
from PIL import Image
import os
import tempfile
from playwright.sync_api import sync_playwright
from database.model import BlacklistsModel

def screenshot_and_ocr(url):
  with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
    path = tmp.name

  with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    page.screenshot(path=path)
    html_content = page.content()
    browser.close()

  text = pytesseract.image_to_string(Image.open(path))
  print("saved to", path)
  print("ocr:", text)
  print("html:", html_content)
  os.remove(path)
  return text, html_content

def create_blacklist_entry(db, url, classification):
  
  return 

def perform_inference(url) -> bool:
  
  try:
    BlacklistsModel.add_to_blacklist(url)
  except Exception as e:
    print(f"Error adding to blacklist: {e}")
    return None
  
  return False