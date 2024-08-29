from flask import *
from misterscrapper import UpdateMisterData
import pymysql
import os
from dotenv import load_dotenv
from db.mister.misterdb import *

app = Flask(__name__)

load_dotenv()

# Datos de ejemplo
jugadores = [
    {'nombre': 'Jugador 1', 'puntos': {'jornada1': 10, 'jornada2': 8, 'jornada3': 15}},
    {'nombre': 'Jugador 2', 'puntos': {'jornada1': 12, 'jornada2': 11, 'jornada3': 9}},
    {'nombre': 'Jugador 3', 'puntos': {'jornada1': 7, 'jornada2': 14, 'jornada3': 12}},
    {'nombre': 'Jugador 4', 'puntos': {'jornada1': 9, 'jornada2': 10, 'jornada3': 11}},
]

# ==== BASE DE DATOS ====
def get_db_connection():
    """Obtiene una conexión a la base de datos."""
    return pymysql.connect(
        host='localhost',
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        cursorclass=pymysql.cursors.DictCursor
    )

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
    success, standings = UpdateMisterData()
    if not success:
        return {"message": "Error Updating"}, 400
    return jsonify(standings), 200


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