from flask import *
import pymysql

app = Flask(__name__)

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
    return render_template('portfolio.html')

# UC Mister
@app.route('/mister')
def mister():
    return render_template('mister.html')


# ==== API ====
# UC Mister
@app.route('/api/misterupdate', methods=['POST'])
def misterupdate():
    return {"message": "Updated"}, 202

@app.route('/api/puntos', methods=['GET'])
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