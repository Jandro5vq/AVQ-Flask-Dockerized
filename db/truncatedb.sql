-- Seleccionar la base de datos
USE avqdb;

-- Desactivar la verificación de las claves foráneas temporalmente
SET FOREIGN_KEY_CHECKS = 0;

-- Vaciar y resetear las tablas

-- Tabla player_debts
TRUNCATE TABLE player_debts;

-- Tabla player_debts_history
TRUNCATE TABLE player_debts_history;

-- Tabla player_pointsplayers
TRUNCATE TABLE player_points;

-- Tabla players
TRUNCATE TABLE players;

-- Tabla rounds
TRUNCATE TABLE rounds;


-- Reactivar la verificación de las claves foráneas
SET FOREIGN_KEY_CHECKS = 1;