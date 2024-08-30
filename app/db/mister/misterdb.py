import re
import logging
from collections import defaultdict

# Configura el logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def point_db(db, cur):
    sql_init = '''USE avqdb'''
    cur.execute(sql_init)
    db.connection.commit()

def get_player_id(db, username):
    try:
        cur = db.connection.cursor()
        point_db(db, cur)
        query = 'SELECT id FROM players WHERE username = %s'
        cur.execute(query, (username,))
        result = cur.fetchone()
        cur.close()
        
        if result:
            return result[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error al obtener el ID del jugador: {e}")
        return None


# PLAYERS
def upsert_player(db, players):
    sql_insert = '''
    INSERT INTO players (username, name, image)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE username = VALUES(username);
    '''

    try:
        with db.connection.cursor() as cur:
            logging.debug("Iniciando el proceso de upsert en la base de datos.")
            point_db(db, cur)

            for player in players:
                cur.execute(sql_insert, (player['username'], player['name'], player['profile_image']))

            db.connection.commit()
            return True

    except Exception as e:
        db.connection.rollback()
        logging.error(f"Error durante el upsert: {e}", exc_info=True)
        return False


def upsert_points(db, jornadas):

    sql_insert_round = '''
    INSERT INTO rounds (num, name)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE name = VALUES(name);
    '''

    sql_insert_player_points = '''
    INSERT INTO player_points (player_id, round_id, points)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE points = VALUES(points);
    '''

    sql_insert_player_debts = '''
    INSERT INTO player_debts (player_id, amount)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE amount = VALUES(amount);
    '''

    try:
        with db.connection.cursor() as cur:
            logging.debug("Iniciando el proceso de upsert en la base de datos.")
            point_db(db, cur)
            
            for x, jornada in enumerate(jornadas):
                num = x + 1
                cur.execute(sql_insert_round, (num, f"Jornada {num}"))
                
                if cur.lastrowid:
                    round_id = cur.lastrowid
                else:
                    cur.execute("SELECT id FROM rounds WHERE num = %s", (num,))
                    round_id = cur.fetchone()[0]

                for user in jornada:
                    player_id = get_player_id(db, user['username'])

                    points_str = user['points']
                    points_cleaned = re.sub(r'\D', '', points_str)
                    points = int(points_cleaned) if points_cleaned else 0

                    cur.execute(sql_insert_player_points, (player_id, round_id, points))

            db.connection.commit()
            calcular_y_actualizar_deudas(db)
            return True

    except Exception as e:
        db.connection.rollback()
        logging.error(f"Error durante el upsert: {e}", exc_info=True)
        return 


def calcular_y_actualizar_deudas(mysql):
    try:
        cur = mysql.connection.cursor()

        # Paso 1: Obtener todas las rondas y los puntos de los jugadores para cada ronda
        cur.execute("""
            SELECT round_id, player_id, points
            FROM player_points
            ORDER BY round_id, points DESC
        """)
        results = cur.fetchall()

        if not results:
            return "No hay datos para calcular las deudas", 404

        # Paso 2: Crear un diccionario para almacenar las deudas acumuladas
        debts = {}
        
        # Paso 3: Calcular deudas acumuladas
        current_round = None
        for round_id, player_id, points in results:
            if round_id != current_round:
                # Al cambiar de ronda, identificar los tres últimos jugadores de la ronda anterior
                if current_round is not None:
                    # Determinar los últimos tres jugadores
                    sorted_players = sorted(round_points.items(), key=lambda x: x[1])
                    last_three = sorted_players[-3:]
                    min_points = last_three[0][1]
                    involved_in_tie = [player_id for player_id, points in last_three if points == min_points]

                    for pid, points in last_three:
                        if pid in involved_in_tie:
                            debts[pid] = debts.get(pid, 0) + 1
                        else:
                            debts[pid] = debts.get(pid, 0) + 2
                
                # Reiniciar para la nueva ronda
                round_points = {}
                current_round = round_id

            # Agregar puntos de jugadores para la ronda actual
            round_points[player_id] = points

        # Procesar la última ronda
        sorted_players = sorted(round_points.items(), key=lambda x: x[1])
        last_three = sorted_players[-3:]
        min_points = last_three[0][1]
        involved_in_tie = [player_id for player_id, points in last_three if points == min_points]

        for pid, points in last_three:
            if pid in involved_in_tie:
                debts[pid] = debts.get(pid, 0) + 1
            else:
                debts[pid] = debts.get(pid, 0) + 2

        # Paso 4: Actualizar la tabla player_debts con la deuda total
        cur.execute("TRUNCATE TABLE player_debts")  # Limpiar tabla antes de actualizar

        for player_id, total_debt in debts.items():
            cur.execute("""
                INSERT INTO player_debts (player_id, amount)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE amount = %s
            """, (player_id, total_debt, total_debt))

        mysql.connection.commit()

        return "Deudas calculadas y actualizadas correctamente."

    except Exception as e:
        mysql.connection.rollback()
        return f"Error al calcular o actualizar deudas: {str(e)}"

    finally:
        cur.close()