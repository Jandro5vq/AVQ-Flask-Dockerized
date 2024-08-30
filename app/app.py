from flask import *
from flask_mysqldb import MySQL
from misterscrapper import get_player_list, get_all_jornada_points
from dotenv import load_dotenv
from db.mister.misterdb import *
import os
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# ==== BASE DE DATOS ====
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

db = MySQL(app)

# Datos de ejemplo
jugadores = [
    {'nombre': 'Jugador 1', 'puntos': {'jornada1': 10, 'jornada2': 8, 'jornada3': 15}},
    {'nombre': 'Jugador 2', 'puntos': {'jornada1': 12, 'jornada2': 11, 'jornada3': 9}},
    {'nombre': 'Jugador 3', 'puntos': {'jornada1': 7, 'jornada2': 14, 'jornada3': 12}},
    {'nombre': 'Jugador 4', 'puntos': {'jornada1': 9, 'jornada2': 10, 'jornada3': 11}},
]

# ==== RUTAS ====
# Portfolio
@app.route('/')
def portfolio():
    return render_template('portfolio/portfolio.html')

# UC Mister
MISTER_KEY = 'uc'

@app.route('/mister')
def mister():
    # Verifica si el usuario ya ha ingresado la contraseña
    if 'authenticated' in request.cookies and request.cookies.get('authenticated') == 'true':
        return render_template('mister/mister.html')
    else:
        # Redirige a la página de login si no está autenticado
        return redirect(url_for('misterlogin'))


@app.route('/misterlogin', methods=['GET', 'POST'])
def misterlogin():
    if request.method == 'POST':
        if request.form['password'] == MISTER_KEY:
            response = redirect(url_for('mister'))
            response.set_cookie('authenticated', 'true')
            return response
        else:
            return render_template('mister/misterlogin.html', error="Contraseña incorrecta. Inténtalo de nuevo.")

    return render_template('mister/misterlogin.html')


# ==== API ====
# UC Mister
@app.route('/api/misterupdate', methods=['POST'])
def misterupdate():
    success, jornadas = get_all_jornada_points()
    if not success:
        return {"message": "Error Updating"}, 400
    
    success = upsert_points(db, jornadas)

    if success:
        return {"message": "OK"}, 200

    else:
        return {"message": "Error Updating"}, 400

@app.route('/api/playersupdate', methods=['POST'])
def playersupdate():
    success, players = get_player_list()
    if not success:
        return {"message": "Error Updating"}, 400

    success = upsert_player(db, players)

    if success:
        return {"message": "OK"}, 200
    else:
        return {"message": "Error Updating"}, 400

@app.route('/api/jornada', methods=['GET'])
def obtener_puntos():
    jornada = request.args.get('jornada')
    if jornada not in ['jornada1', 'jornada2', 'jornada3']:
        return jsonify({'error': 'Jornada no válida'}), 400
    
    puntuaciones = [
        {'nombre': jugador['nombre'], 'puntos': jugador['puntos'][jornada]}
        for jugador in jugadores
    ]
    
    # Ordenar los jugadores por puntos de manera descendente
    puntuaciones.sort(key=lambda x: x['puntos'], reverse=True)
    
    return jsonify(puntuaciones)

if __name__ == '__main__':
    app.run(host='0.0.0.0')