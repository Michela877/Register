from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import re
import bcrypt
import os
import datetime

app = Flask(__name__)
app.secret_key = 'il_tuo_segreto'



# Configurazione del database MySQL
db_config = {
    'host': os.getenv('MYSQL_HOST', '192.168.178.162'),
    'port': os.getenv('MYSQL_PORT', '3308'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'my-secret-pw'),
    'database': os.getenv('MYSQL_DATABASE', 'asset_management')
}

def get_db_connection():
    return mysql.connector.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )

@app.route('/info')
def info():
    if 'loggedin' in session:
        app.logger.debug('User is logged in, redirecting to home page.')
        return redirect('http://192.168.178.162:18000/info?email=' + session['email'])
    app.logger.debug('User not logged in, rendering login page.')
    return redirect('http://192.168.178.162:13000/')

@app.route('/')
def index():
    if 'loggedin' in session:
        app.logger.debug('User is logged in, redirecting to home page.')
        return redirect('http://192.168.178.162:14000/home?email=' + session['email'])
    app.logger.debug('User not logged in, rendering login page.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('email', None)
    return redirect('http://192.168.178.162:13000/')  # Reindirizza alla pagina di login dell'app di login

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' not in session:
        flash('Devi essere autenticato per accedere a questa pagina.', 'error')
        return redirect('http://192.168.178.162:13000/')

    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        nome = request.form['nome']
        cognome = request.form['cognome']
        sesso = request.form['sesso']
        codicefiscale = request.form['cod_fisc']
        data_nascita = request.form['data_nascita']
        citta = request.form['citta']
        provincia = request.form['provincia']
        via = request.form['via']
        telefono = request.form['telefono']
        tipologia_contratto = request.form['tipologia_contratto']
        data_assunzione = request.form['data_assunzione']
        ruolo = request.form['ruolo']
        sede_azienda = request.form['sede_azienda']
        stipendio = request.form['stipendio']
        reparto = request.form['reparto']
        password = request.form['password'].encode('utf-8')
        
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT * FROM dipendenti WHERE email = %s FOR UPDATE', (email,))
                    email_exists = cursor.fetchone()
                    
                    if email_exists:
                        msg = "L'email esiste già."
                    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                        msg = 'Indirizzo email non valido.'
                    elif not re.match(r'[A-Za-z0-9]+', password.decode('utf-8')):
                        msg = 'La password deve contenere solo caratteri e numeri.'
                    elif not email or not nome or not cognome or not data_nascita or not citta or not provincia or not via or not telefono or not tipologia_contratto or not data_assunzione or not ruolo or not sede_azienda or not password or not codicefiscale or not stipendio or not reparto:
                        msg = 'Compila tutti i campi.'
                    else:
                        cursor.execute('INSERT INTO dipendenti (nome, cognome, sesso, cod_fisc, email, data_nascita, citta, provincia, via, telefono1, tipologia_contratto, data_assunzione, ruolo, sede_azienda, stipendio, reparto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                                       (nome, cognome, sesso, codicefiscale, email, data_nascita, citta, provincia, via, telefono, tipologia_contratto, data_assunzione, ruolo, sede_azienda, stipendio, reparto))
                        cursor.execute('INSERT INTO login (email, credenziali_accesso) VALUES (%s, %s)', 
                                       (email, hashed_password.decode('utf-8')))
                        conn.commit()
                        msg = 'Registrazione avvenuta con successo!'
                        return redirect(url_for('index'))
        except mysql.connector.Error as err:
            app.logger.error(f"Errore durante la registrazione: {err}")
            msg = "Errore durante la registrazione, riprova più tardi."

    email = session.get('email')
    return render_template('register.html', msg=msg, email=email)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=11000)

