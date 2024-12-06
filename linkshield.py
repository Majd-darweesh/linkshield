from flask import Flask, render_template_string, request, send_file
import re
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)

# Home page route
@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LinkShield - URL Scanner</title>
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background: #111;
                color: #fff;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                overflow: hidden;
            }

            .container {
                text-align: center;
                background: linear-gradient(135deg, #ff2a68, #00b3e6);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
                animation: pulse 3s infinite alternate;
            }

            h1 {
                font-size: 3em;
                margin-bottom: 30px;
                text-transform: uppercase;
                color: #ffffff;
                letter-spacing: 2px;
                text-shadow: 0 0 10px rgba(0, 255, 255, 0.6);
            }

            input[type="text"] {
                width: 70%;
                padding: 15px;
                font-size: 1.2em;
                border: none;
                border-radius: 10px;
                background-color: #333;
                color: #fff;
                margin-bottom: 20px;
                box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
            }

            button {
                padding: 12px 25px;
                background-color: #00b3e6;
                border: none;
                border-radius: 5px;
                color: #fff;
                font-size: 1.1em;
                cursor: pointer;
                box-shadow: 0 0 10px rgba(255, 255, 255, 0.4);
                transition: all 0.3s ease;
            }

            button:hover {
                background-color: #ff2a68;
                transform: scale(1.1);
            }

            @keyframes pulse {
                0% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.05);
                }
                100% {
                    transform: scale(1);
                }
            }

            .error {
                color: #ff2a68;
                font-size: 1.2em;
                margin-top: 20px;
            }

        </style>
    </head>
    <body>
        <div class="container">
            <h1>LinkShield - Scan Your URL</h1>
            <p>Welcome, Majd Darwish!</p> <!-- Your name added here -->
            <form action="/scan" method="post">
                <input type="text" name="url" placeholder="Enter a URL to scan..." required>
                <br>
                <button type="submit">Start Scan</button>
            </form>
            {% if error %}
            <p class="error">{{ error }}</p>
            {% endif %}
        </div>
    </body>
    </html>
    ''')

# Scan result page route
@app.route('/scan', methods=['POST'])
def scan():
    url = request.form['url']
    
    # Validate URL
    if not is_valid_url(url):
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>LinkShield - Scan Result</title>
            <style>
                body {
                    font-family: 'Roboto', sans-serif;
                    background: #111;
                    color: #fff;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }

                .result-container {
                    background: linear-gradient(135deg, #ff2a68, #00b3e6);
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
                    text-align: center;
                    width: 80%;
                    max-width: 600px;
                    animation: pulse 3s infinite alternate;
                }

                h1 {
                    font-size: 2.5em;
                    margin-bottom: 30px;
                }

                p {
                    font-size: 1.5em;
                    margin-bottom: 20px;
                }

                @keyframes pulse {
                    0% {
                        transform: scale(1);
                    }
                    50% {
                        transform: scale(1.05);
                    }
                    100% {
                        transform: scale(1);
                    }
                }
            </style>
        </head>
        <body>
            <div class="result-container">
                <h1>Scan Result</h1>
                <p>URL: {{ url }}</p>
                <p class="error">{{ error }}</p>
                <br>
                <a href="/" style="color: #fff; text-decoration: none; font-size: 1.2em;">Go Back</a>
            </div>
        </body>
        </html>
        ''', error="Invalid URL!")

    # Perform scan (simple at this stage)
    result = perform_scan(url)
    
    # Generate the PDF report
    pdf = generate_pdf_report(url, result)

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LinkShield - Scan Result</title>
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background: #111;
                color: #fff;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }

            .result-container {
                background: linear-gradient(135deg, #ff2a68, #00b3e6);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
                text-align: center;
                width: 80%;
                max-width: 600px;
                animation: pulse 3s infinite alternate;
            }

            h1 {
                font-size: 2.5em;
                margin-bottom: 30px;
            }

            p {
                font-size: 1.5em;
                margin-bottom: 20px;
            }

            @keyframes pulse {
                0% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.05);
                }
                100% {
                    transform: scale(1);
                }
            }
        </style>
    </head>
    <body>
        <div class="result-container">
            <h1>Scan Result</h1>
            <p>URL: {{ url }}</p>
            <p>{{ result }}</p>
            <br>
            <a href="{{ url_for('download_pdf', url=url) }}" style="color: #fff; text-decoration: none; font-size: 1.2em;">Download PDF Report</a>
            <br><br>
            <a href="/" style="color: #fff; text-decoration: none; font-size: 1.2em;">Go Back</a>
        </div>
    </body>
    </html>
    ''', url=url, result=result)

# URL validation
def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

# Simple scan simulation (replace with real scan logic)
def perform_scan(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return "URL is accessible and safe!"
        else:
            return f"URL returned status code: {response.status_code}"
    except requests.RequestException as e:
        return f"Error occurred: {e}"

# Generate PDF report
def generate_pdf_report(url, result):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica", 12)

    c.drawString(100, 750, f"LinkShield Scan Report for {url}")
    c.drawString(100, 730, f"Result: {result}")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

# Download PDF route
@app.route('/download_pdf')
def download_pdf():
    url = request.args.get('url')
    result = perform_scan(url)
    pdf = generate_pdf_report(url, result)
    return send_file(pdf, as_attachment=True, download_name="scan_report.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True)
