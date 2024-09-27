from flask import Flask, request, redirect, url_for, render_template, jsonify
from flask_mysqldb import MySQL
from misterscrapper import get_player_list, get_all_jornada_points
from dotenv import load_dotenv
from db.mister.misterdb import upsert_points, upsert_player, get_jornada, get_rounds, get_debts, calcular_y_actualizar_deudas
import os
import logging

app = Flask(__name__)

# Configuración del registro
logging.basicConfig(level=logging.DEBUG)

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DATABASE')

# Inicializar la conexión a MySQL
db = MySQL(app)

# ==== RUTAS ====
# -- PORTFOLIO --
@app.route('/')
def portfolio():
    return render_template('portfolio/portfolio.html')

# -- MISTER --
@app.route('/mister')
def mister():
    if request.cookies.get('authenticated') == 'true':
        return render_template('mister/mister.html')
    else:
        return redirect(url_for('misterlogin'))

@app.route('/mister/login', methods=['GET', 'POST'])
def misterlogin():
    if request.method == 'POST':
        if request.form.get('password') == 'uc':
            response = redirect(url_for('mister'))
            response.set_cookie('authenticated', 'true')
            return response
        else:
            return render_template('mister/misterlogin.html', error="Contraseña incorrecta. Inténtalo de nuevo.")

    return render_template('mister/misterlogin.html')

# ==== API ====
# -- MISTER --
@app.route('/api/misterupdate', methods=['POST'])
def misterupdate():
    success, jornadas = get_all_jornada_points()
    if not success:
        logging.error("Error updating jornada points")
        return {"message": "Error Updating"}, 400

    success = upsert_points(db, jornadas)
    if success:
        return {"message": "OK"}, 200
    else:
        logging.error("Error inserting/updating points")
        return {"message": "Error Updating"}, 400

@app.route('/api/playersupdate', methods=['POST'])
def playersupdate():
    success, players = get_player_list()
    if not success:
        logging.error("Error updating player list")
        return {"message": "Error Updating"}, 400

    success = upsert_player(db, players)
    if success:
        return {"message": "OK"}, 200
    else:
        logging.error("Error inserting/updating players")
        return {"message": "Error Updating"}, 400

@app.route('/api/jornada', methods=['GET'])
def obtener_puntos():
    jornada = request.args.get('jornada')
    try:
        
        jornada_points = get_jornada(db, int(jornada))
        jornada_points = [
            {'username': item[0], 'name': item[1], 'img': item[2], 'points': item[3], 'debt': item[4]} for item in jornada_points
        ]
        if jornada_points:
            return jsonify(jornada_points), 200
        else:
            return {"message": "Jornada not found"}, 404
    except ValueError:
        return {"message": "Invalid jornada number"}, 400
    except Exception as e:
        logging.error(f"Error retrieving jornada points: {e}")
        return {"message": "Error"}, 500

@app.route('/api/numjornadas', methods=['GET'])
def num_jornadas():
    try:
        return jsonify(get_rounds(db)), 200
    except Exception as e:
        logging.error(f"Error retrieving rounds: {e}")
        return {"message": "Error"}, 500

@app.route('/api/deudas', methods=['GET'])
def debts_list():
    try:
        return jsonify(get_debts(db)), 200
    except Exception as e:
        logging.error(f"Error retrieving rounds: {e}")
        return {"message": "Error"}, 500

@app.route('/api/calcdebts', methods=['GET'])
def debts_calc():
    try:
        calcular_y_actualizar_deudas(db)
        return {"message": "OK"}, 200
    except Exception as e:
        logging.error(f"Error retrieving rounds: {e}")
        return {"message": "Error"}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0')