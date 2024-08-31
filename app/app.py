from flask import Flask, request, redirect, url_for, render_template, jsonify
from flask_mysqldb import MySQL
from misterscrapper import get_player_list, get_all_jornada_points
from dotenv import load_dotenv
from db.mister.misterdb import upsert_points, upsert_player, get_jornada, get_rounds
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

# Datos de ejemplo (para pruebas o desarrollo)
jugadores = [
    {'nombre': 'Jugador 1', 'puntos': {'jornada1': 10, 'jornada2': 8, 'jornada3': 15}},
    {'nombre': 'Jugador 2', 'puntos': {'jornada1': 12, 'jornada2': 11, 'jornada3': 9}},
    {'nombre': 'Jugador 3', 'puntos': {'jornada1': 7, 'jornada2': 14, 'jornada3': 12}},
    {'nombre': 'Jugador 4', 'puntos': {'jornada1': 9, 'jornada2': 10, 'jornada3': 11}},
]

# ==== RUTAS ====

@app.route('/')
def portfolio():
    """
    Ruta para la página principal del portfolio.
    :return: Renderiza la plantilla 'portfolio/portfolio.html'
    """
    return render_template('portfolio/portfolio.html')

@app.route('/mister')
def mister():
    """
    Ruta para la página principal de UC Mister. Solo accesible si el usuario está autenticado.
    :return: Renderiza la plantilla 'mister/mister.html' si autenticado, de lo contrario redirige a /misterlogin
    """
    if request.cookies.get('authenticated') == 'true':
        return render_template('mister/mister.html')
    else:
        return redirect(url_for('misterlogin'))

@app.route('/misterlogin', methods=['GET', 'POST'])
def misterlogin():
    """
    Ruta para la página de login de UC Mister. Permite al usuario ingresar la contraseña para autenticarse.
    :return: Renderiza la plantilla 'mister/misterlogin.html' con un mensaje de error si la contraseña es incorrecta,
             o redirige a /mister si la contraseña es correcta.
    """
    if request.method == 'POST':
        if request.form.get('password') == 'uc':  # Considera usar un método más seguro para manejar contraseñas
            response = redirect(url_for('mister'))
            response.set_cookie('authenticated', 'true')
            return response
        else:
            return render_template('mister/misterlogin.html', error="Contraseña incorrecta. Inténtalo de nuevo.")

    return render_template('mister/misterlogin.html')

# ==== API ====

@app.route('/api/misterupdate', methods=['POST'])
def misterupdate():
    """
    Ruta para actualizar los puntos de las jornadas. Llama a la función get_all_jornada_points para obtener los datos
    y luego a upsert_points para insertar o actualizar los datos en la base de datos.
    :return: JSON con mensaje de éxito o error
    """
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
    """
    Ruta para actualizar la lista de jugadores. Llama a la función get_player_list para obtener los datos
    y luego a upsert_player para insertar o actualizar los datos en la base de datos.
    :return: JSON con mensaje de éxito o error
    """
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
    """
    Ruta para obtener los puntos de los jugadores para una jornada específica.
    :return: JSON con los puntos de los jugadores para la jornada especificada, o un mensaje de error
    """
    jornada = request.args.get('jornada')
    try:
        
        jornada_points = get_jornada(db, int(jornada))
        jornada_points = [
            {'username': item[0], 'name': item[1], 'img': item[2], 'points': item[3]} for item in jornada_points
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
    """
    Ruta para obtener el número de jornadas disponibles.
    :return: JSON con el número de jornadas disponibles, o un mensaje de error
    """
    try:
        return jsonify(get_rounds(db)), 200
    except Exception as e:
        logging.error(f"Error retrieving rounds: {e}")
        return {"message": "Error"}, 500

if __name__ == '__main__':
    # Ejecutar la aplicación Flask
    app.run(host='0.0.0.0', debug=True)  # Habilitar debug=True para desarrollo; considera deshabilitar en producción
