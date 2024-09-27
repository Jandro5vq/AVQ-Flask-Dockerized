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
    ON DUPLICATE KEY UPDATE name = VALUES(name), image = VALUES(image);
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

    try:
        with db.connection.cursor() as cur:
            logging.debug("Iniciando el proceso de upsert en la base de datos.")
            point_db(db, cur)  # Ensure this function is defined

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
        return False  # Explicitly return False in case of an error

def get_rounds(db):
    try:
        cur = db.connection.cursor()
        point_db(db, cur)
        query = 'SELECT num, name FROM rounds'
        cur.execute(query)
        result = cur.fetchall()
        cur.close()
        
        return dict(result)
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_debts(db):
    try:
        cur = db.connection.cursor()
        point_db(db, cur)
        
        # Obtener todas las jornadas disponibles
        cur.execute('SELECT DISTINCT num FROM rounds ORDER BY num')
        jornadas = [row[0] for row in cur.fetchall()]
        
        # Construir la consulta SQL dinámicamente
        select_clause = ', '.join(
            [f"COALESCE(SUM(CASE WHEN r.num = {jornada} THEN pdh.amount ELSE 0 END), 0) AS Deuda_Jornada{jornada}" for jornada in jornadas]
        )
        
        query = f'''
        SELECT 
            p.name AS Nombre_Usuario,
            {select_clause},
            COALESCE(SUM(pdh.amount), 0) AS Deuda_Total
        FROM players p
        LEFT JOIN player_debts_history pdh ON p.id = pdh.player_id
        LEFT JOIN rounds r ON pdh.round_id = r.id
        GROUP BY p.name
        ORDER BY Deuda_Total DESC;'''

        cur.execute(query)
        result = cur.fetchall()
        cur.close()
        
        print(result)
        return result
            
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_jornada(db, num):
    try:
        cur = db.connection.cursor()
        point_db(db, cur)
        query = '''
        SELECT p.username, 
            p.name, 
            p.image, 
            pp.points, 
            COALESCE(dh.amount, 0) AS amount
        FROM players p
        JOIN player_points pp ON p.id = pp.player_id
        JOIN rounds r ON pp.round_id = r.id
        LEFT JOIN player_debts_history dh ON p.id = dh.player_id AND r.id = dh.round_id
        WHERE r.num = %s
        ORDER BY pp.points DESC;
        '''
        cur.execute(query % num)
        result = cur.fetchall()
        cur.close()
        
        return result
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def calcular_y_actualizar_deudas(db):
    logging.info("CALC DEUDAS")
    cur = db.connection.cursor()
    try:
        # Vaciar la tabla de historial de deudas
        cur.execute("DELETE FROM player_debts_history")

        # Obtener todas las rondas disponibles
        cur.execute("SELECT num FROM rounds")
        rounds = cur.fetchall()
        rounds = [x[0] for x in rounds]

        logging.info(rounds)
        
        all_rounds_scores = {}
        
        for num in rounds:
            logging.info(num)
            cur.execute("""
                    SELECT player_id, points
                    FROM player_points
                    WHERE round_id = %s
                    ORDER BY points DESC
                """, (num,))
            
            player_points = cur.fetchall()
            all_rounds_scores[num] = player_points
        
        menores = {}
        for jornada, datos in all_rounds_scores.items():
            # Ordenar por puntuación
            datos_ordenados = sorted(datos, key=lambda x: x[1])
            
            # Agrupar usuarios por puntuación
            grupos = {}
            for usuario, puntos in datos_ordenados:
                if puntos not in grupos:
                    grupos[puntos] = []
                grupos[puntos].append(usuario)
            
            # Tomar las tres primeras puntuaciones con usuarios
            menores[jornada] = {}
            for i, (puntos, usuarios) in enumerate(grupos.items()):
                if i < 3:
                    menores[jornada][puntos] = usuarios
                else:
                    break
        
        cur.execute("SELECT COUNT(*) FROM players")
        player_num = cur.fetchone()[0]
        
        debts = {}
        
        sql_insert_debts_history = '''
        INSERT INTO player_debts_history (player_id, round_id, amount)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE amount = VALUES(amount);
        '''
        
        for id in range(1, player_num + 1):
            debts[id] = 0
            for jornum, jor in menores.items():
                for debs, users in jor.items():
                    if [id] == users:
                        debts[id] += 2
                        cur.execute(sql_insert_debts_history, (id, jornum, 2))
                    elif id in users and len(users) > 1:
                        debts[id] += 1
                        cur.execute(sql_insert_debts_history, (id, jornum, 1))
                    else:
                        debts[id] += 0
        
        sql_insert_debts = '''
        INSERT INTO player_debts (player_id, amount)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE amount = VALUES(amount);
        '''
        for deb in debts:
            cur.execute(sql_insert_debts, (deb, debts[deb]))

        db.connection.commit()

        return "Deudas calculadas y actualizadas correctamente."

    except Exception as e:
        db.connection.rollback()
        return f"Error al calcular o actualizar deudas: {str(e)}"

    finally:
        cur.close()
