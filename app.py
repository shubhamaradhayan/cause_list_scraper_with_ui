# import flast module
from telnetlib import EC
from urllib import response
from flask import Flask, render_template, request, redirect, url_for,jsonify, send_from_directory
from models import db, Record
from werkzeug.utils import secure_filename
import requests
from bs4 import BeautifulSoup

import os
from sources.captcha_module import CaptchaSolver
import json
import re
import html 

from sources.scraper import WebScraper

url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list"

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize the database
db.init_app(app)


@app.route("/")
def index():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    states = []
    state_options = soup.find('select', id='sess_state_code').find_all('option')
    for option in state_options:
        states.append({
            'value': option['value'],
            'key': option.text.strip()
        })
    return render_template("index.html", data=jsonify(states))

@app.route("/fetchStates")
def fetch_states():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    states = []
    state_options = soup.find('select', id='sess_state_code').find_all('option')
    for option in state_options:
        states.append({
            'value': option['value'],
            'key': option.text.strip()
        })
    return jsonify(states)

@app.route("/fetchDistricts/<state_code>")
def fetch_districts(state_code):
    print(f"Fetching districts for state_code: {state_code}")
    dist_url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/fillDistrict"
    data = {
        "state_code": state_code
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0"  # Helps avoid being blocked as a bot
    }
    
    try:
        response = requests.post(dist_url, data=data, headers=headers)
        response.raise_for_status()
        # print("Response:", response.text)
        soup = BeautifulSoup(response.text, "html.parser")
    
        # Extract the entire content inside <body> as HTML string
        body_html = str(soup.body)
        
        # print(body_html)  # Prints the full <body> ... </body> including tags
    
        # 1. Extract dist_list value manually
        match = re.search(r'"dist_list":"(.*?)"}', body_html, re.DOTALL)
    
        if match:
            # Get raw HTML from the "dist_list"
            dist_list_raw = match.group(1)
    
            # 2. Unescape HTML entities and fix slashes
            dist_list_html = html.unescape(dist_list_raw.replace('\\"', '"').replace('\\/', '/'))
    
            # 3. Extract district values using regex
            options = re.findall(r'<option value="(\d*)">(.*?)</option>', dist_list_html)
    
            # 4. Convert to structured list
            district_data = [{"id": int(val), "name": name} for val, name in options if val]
    
            # # 5. Print result
            # for d in district_data:
            #     print(d)
        else:
            print("[!] dist_list not found")
    
    
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
    

    return jsonify(district_data)

@app.route("/fetchComplexes/<state_code>/<dist_code>")
def fetch_complexes(state_code, dist_code):
    complex_url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/fillcomplex"
    data = {
        "state_code": state_code,
        "dist_code": dist_code
    }

    headers = {
        "User-Agent": "Mozilla/5.0"  # Helps avoid being blocked as a bot
    }

    try:
        response = requests.post(complex_url, data=data, headers=headers)
        response.raise_for_status()
        # print("Response:", response.text)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the entire content inside <body> as HTML string
        body_html = str(soup.body)

        # print(body_html)  # Prints the full <body> ... </body> including tags

        # 1. Extract complex_list value manually
        match = re.search(r'"complex_list":"(.*?)"}', body_html, re.DOTALL)

        if match:
            # Get raw HTML from the "complex_list"
            complex_list_raw = match.group(1)

            # 2. Unescape HTML entities and fix slashes
            complex_list_html = html.unescape(complex_list_raw.replace('\\"', '"').replace('\\/', '/'))
            print(complex_list_html)
            # 3. Extract complex values using regex
            options = re.findall(r'<option value="([^"]*)">(.*?)</option>', complex_list_html)

            # options = re.findall(r'<option value="(\d*)">(.*?)</option>', complex_list_html)
            print(options)
            # 4. Convert to structured list
            complex_data = [{"id": val, "name": name} for val, name in options if val]
            print(complex_data)
            # 5. Print result
            for d in complex_data:
                print(d)
        else:
            print("[!] complex_list not found")


    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

    return jsonify(complex_data)


@app.route("/fetchCourtNames/<state_code>/<dist_code>/<court_complex>")
def fetch_court_names(state_code, dist_code, court_complex):
    print(f"\n\n\n\nFetching court names for state_code: {state_code}, dist_code: {dist_code}, court_complex: {court_complex}")
    court_name_url = "https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/fillCauseList"

    # Sample input
    state_code = state_code
    dist_code = dist_code
    # complex_code_raw = "1080060@1,2,3,4@Y"  # comes from complex_list
    complex_code_raw = court_complex# comes from complex_list

    # Split complex code like JavaScript
    parts = complex_code_raw.split('@')
    court_complex_code = parts[0]
    est_code = "1" if parts[2] == "Y" else parts[1]  # use selected establishment or pre-set

    data = {
        "state_code": state_code,
        "dist_code": dist_code,
        "court_complex_code": court_complex_code,
        "est_code": est_code,
        "search_act": ""
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.post(court_name_url, data=data, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        body_html = str(soup.body)
        # print(body_html)  # Prints the full <body> ... </body> including tags
        # Extract cause_list HTML from response
        match = re.search(r'"cause_list":"(.*?)"', body_html, re.DOTALL)
        # 1. Unescape HTML


        if match:
            # cause_list_raw = match.group(1)
            unescaped_html = html.unescape(body_html.replace('\\/', '/'))

            # 2. Extract only valid <option> entries (skip value="D" and empty)
            options = re.findall(r'<option\s+(?!disabled).*?value="([^"]+)">(.*?)</option>', unescaped_html)

            # 3. Structure the result
            court_list = [{"id": value, "name": name.strip()} for value, name in options if value and value != "D"]

            # 4. Print results
            for court in court_list:
                print(court)

            # cause_list_raw = match.group(1)
            # cause_list_html = html.unescape(cause_list_raw.replace('\\"', '"').replace('\\/', '/'))

            # # Extract court numbers/names from <option> tags
            # options = re.findall(r'<option value="([^"]*)">(.*?)</option>', cause_list_html)
            # court_list = [{"id": val, "name": name} for val, name in options if val]

            # for court in court_list:
            #     print(court)
        else:
            print("[!] 'cause_list' not found in response.")

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

    return jsonify(court_list)




@app.route("/start-scraping", methods=["POST"])
def start_scraping():
    data = request.json
    print("Received data:", data)
    scraper = WebScraper(data)
    filename = scraper.start_scraping()
    # Here you would start the scraping process
    return jsonify({"status": "success", "filename": filename})



@app.route("/download/<filename>")
def download_file(filename):
    try:
        # Ensure the filename is safe
        filename = secure_filename(filename)

        # Send the file from the download directory
        file_dir = os.path.join(os.getcwd(), "output")
        new_download_name = "cause_list.zip"
        # Send the file with a different download name
        response = send_from_directory(
            directory=file_dir,
            path=filename,
            as_attachment=True,
            mimetype='application/zip',
            download_name=new_download_name  # New filename for download
        )
        print("File sent:", response)
    except Exception as e:
        print("Error sending file:", e)
        return jsonify({"status": "error", "message": "File not found"}), 404   
    # os.remove(os.path.join(file_dir, filename))  # Delete after sending
    return response


@app.route("/result")
def result():
    records = Record.query.all()
    return render_template("result.html", records=records)



# if __name__ == '__main__':
#     # Run the app with the asynchronous server (eventlet or gevent)
#     socketio.run(app, debug=True)
#     # socketio.run(app, debug=True, use_reloader=False)


if __name__ == '__main__':
    app.run(debug=True)