from ...app import get_db_connection

nombres = {
    'Endika Arocena Cartagena': 'Endika'
}

PLAYER_IDS = []

# PLAYERS
def upsert_player(username, image):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO players (username, name, image) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE name=VALUES(name), username=VALUES(username)",
            (username, nombres[username], image)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()