# Lentera Digital Judol Detector Server

This is the server component of the Lentera Digital Judol Detector project. It is built using Flask and provides an API for the frontend to interact with.

## Installation

1. Make virtual environment
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
3. Install the required packages
   ```bash
   pip install -r requirements.txt
   ```  
4. Copy the `.env.example` file to `.env` and fill in the required environment variables.
   ```bash
   cp .env.example .env
   ```
5. Run the server
   ```bash
   python run.py
   ```  

## Usage
You can access the API at `http://localhost:5000/`.

- `/`: Returns a simple message indicating that the server is running.
- `/inference`: Endpoint for url-based inference. It accepts a POST request with a JSON body containing the `url` of the web page to be processed.