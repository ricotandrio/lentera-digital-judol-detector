from flask import Flask, jsonify, request
from database.db import db
from utils.inference_util import perform_inference
from flask_cors import CORS
import os

def create_app():
  app = Flask(__name__)
  CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

  app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL")

  db.init_app(app)

  @app.route('/')
  def index():
    return "<h1>Welcome to the Lentera Digital Judol Detector API!</h1>"

  @app.route('/inference', methods=['POST'])
  def inference():
    data = request.get_json(silent=True)
    url = data.get("url") if data else None

    if not url:
      return jsonify({
        "status": 400,
        "success": False,
        "message": "URL is required.",
        "error": {"code": "MISSING_URL", "field": "url"}
      }), 400

    try:
      output_class = perform_inference(url)
    
    except ValueError as ve:
      return jsonify({
        "status": 400,
        "success": False,
        "message": str(ve),
        "error": {"code": "INVALID_URL", "detail": str(ve)},
        "url": url
      }), 400
      
    except Exception as e:
      return jsonify({
        "status": 500,
        "success": False,
        "message": "Exception during inference.",
        "error": {"code": "INFERENCE_ERROR", "detail": str(e)},
        "url": url
      }), 500

    return jsonify({
      "status": 200,
      "success": True,
      "message": "Inference completed.",
      "data": {
        "url": url,
        "classification": "judol" if output_class else "not judol"
      }
    }), 200

  with app.app_context():
    db.create_all()

  return app
