from flask import Flask, jsonify, request
from database.db import db
import os

def create_app():
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")
  
  db.init_app(app)

  from utils.inference_util import perform_inference
  
  @app.route('/')
  def index():
    return "<h1>Welcome to the Lentera Digital Judol Detector API!</h1>"

  @app.route('/inference', methods=['POST'])
  def inference():
    data = request.get_json()
    url = data.get("url")

    if not url:
      return jsonify({
        "error": "URL is required."
      }), 400
    
    output_class = perform_inference(url)
    
    if output_class is True:
      return jsonify({
        "message": "The URL is classified as a judol.",
        "url": url
      }), 200
    elif output_class is False:
      return jsonify({
        "message": "The URL is classified as not a judol.",
        "url": url
      }), 200
    else:
      return jsonify({
        "error": "An error occurred during inference.",
        "url": url
      }), 500
  
  with app.app_context():
    db.create_all()

  return app