# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # for flash messages

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Storage Tracker").sheet1

STORAGE_OPTIONS = ["H1", "S1", "S2", "A1", "C1", "D1", "ADI", "Doma"]

@app.route('/')
def index():
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('form.html', storage_options=STORAGE_OPTIONS, today=today)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        form = request.form
        date = form['date'] or datetime.today().strftime('%d-%m-%Y')
        pp = int(form['pp'])
        rst = int(form['rst'])
        name = form['name'].strip()
        village = form['village'].strip()
        phone = form['phone'].strip()
        bags = int(form['bags'])
        quantity = float(form['quantity'])
        rate = int(form['rate'])
        cc = int(form['cc'])
        hamali = int(form['hamali'])
        kanta = int(form['kanta'])
        storage = form['storage']

        if not re.fullmatch(r"\d{10}", phone):
            flash("Phone number must be exactly 10 digits.", "error")
            return redirect(url_for('index'))

        if quantity <= 0:
            flash("Quantity must be greater than 0.", "error")
            return redirect(url_for('index'))

        quantity = round(quantity, 2)
        total = round((quantity * rate) - (hamali + kanta + cc), 2)
        avg = round(total / quantity, 2)

        existing_rows = sheet.get_all_values()
        sno = len(existing_rows)
        if sno > 0:
            sno = sno  # header exists, so 2nd row onwards
        else:
            sno = 1

        storage_data = [0] * len(STORAGE_OPTIONS)
        if storage in STORAGE_OPTIONS:
            storage_index = STORAGE_OPTIONS.index(storage)
            storage_data[storage_index] = quantity

        row = [sno, date, pp, rst, name, village, phone, bags, quantity, rate, cc, hamali, kanta, storage] + storage_data + [total, avg]
        sheet.append_row(row)
        flash("Data submitted successfully!", "success")
    except Exception as e:
        flash(str(e), "error")

    return redirect(url_for('index'))

@app.route('/summary')
def summary():
    data = sheet.get_all_values()[1:]  # skip headers
    totals = {key: 0 for key in STORAGE_OPTIONS}
    for row in data:
        for i, key in enumerate(STORAGE_OPTIONS):
            try:
                totals[key] += float(row[14 + i])
            except:
                continue
    return render_template('summary.html', totals=totals)

@app.route('/view')
def view_all():
    all_data = sheet.get_all_values()
    headers = all_data[0]
    rows = all_data[1:]
    return render_template('view_all.html', headers=headers, rows=rows)

if __name__ == '__main__':
    app.run(debug=True)
