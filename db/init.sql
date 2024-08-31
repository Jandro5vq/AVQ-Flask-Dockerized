-- Seleccionar la base de datos
USE avqdb;

-- Crear tablas
CREATE TABLE players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(300) NOT NULL
);

CREATE TABLE rounds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    num INT NOT NULL,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE player_points (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    round_id INT NOT NULL,
    points INT NOT NULL,
    UNIQUE KEY unique_player_round (player_id, round_id),
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (round_id) REFERENCES rounds(id),
    CHECK (points >= 0)
);

CREATE TABLE player_debts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (player_id) REFERENCES players(id),
    CHECK (amount >= 0)
);

CREATE TABLE player_debts_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    round_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    UNIQUE KEY unique_player_round (player_id, round_id),
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (round_id) REFERENCES rounds(id),
    CHECK (amount >= 0)
);
