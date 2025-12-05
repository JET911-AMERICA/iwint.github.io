import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime
import locale # Importiere das locale-Modul

# Setze die Sprache für Datumsformate auf Deutsch
# Dies erfordert möglicherweise, dass das deutsche Sprachpaket auf dem System installiert ist.
# Wenn es nicht funktioniert, verwenden wir einen manuellen Ansatz.
try:
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
except locale.Error:
    print("Warnung: Deutsches locale 'de_DE.UTF-8' nicht gefunden. Datumsformat könnte auf Englisch bleiben.")


app = Flask(__name__)
app.secret_key = 'dein-super-geheimer-schluessel' 
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

TRANSACTIONS_DB = []

@app.route('/')
def index():
    latest_transaction = None
    if TRANSACTIONS_DB:
        latest_transaction = TRANSACTIONS_DB[-1]
    return render_template('index.html', latest_transaction=latest_transaction)

@app.route('/pay', methods=['GET', 'POST'])
def pay():
    if request.method == 'POST':
        amount = request.form['amount']
        name = request.form['recipient_name']
        image_file = request.files.get('recipient_image')

        filename = None
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        now = datetime.now()
        # === HIER IST DIE ÄNDERUNG ===
        # Nutzt das deutsche Format, das wir oben eingestellt haben
        formatted_date = now.strftime("%d. %B %Y") 

        new_transaction = {
            'name': name,
            'amount': f"CHF {amount}",
            'image': filename,
            'date': formatted_date
        }

        TRANSACTIONS_DB.append(new_transaction)
        
        return redirect(url_for('success'))

    recipient_name = request.args.get('recipient', None)
    return render_template('pay.html', recipient=recipient_name)

@app.route('/transactions')
def show_all_transactions():
    return render_template('transactions.html', transactions=reversed(TRANSACTIONS_DB))

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/success')
def success():
    transaction = {}
    if TRANSACTIONS_DB:
        transaction = TRANSACTIONS_DB[-1]

    return render_template('succes.html',
                           amount=transaction.get('amount', '0.00').replace('CHF ', ''),
                           name=transaction.get('name', 'Unbekannt'),
                           image=transaction.get('image', None))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)