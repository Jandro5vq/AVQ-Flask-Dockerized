CREATE TABLE players (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
);

CREATE TABLE rounds (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
);

CREATE TABLE player_points (
    id INT PRIMARY KEY AUTO_INCREMENT,
    player_id INT NOT NULL,
    round_id INT NOT NULL,
    points INT NOT NULL,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (round_id) REFERENCES rounds(id)
);

CREATE TABLE player_debts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    player_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (player_id) REFERENCES players(id)
);
