CREATE TABLE players (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(300) NOT NULL
);

CREATE TABLE rounds (
    id INT PRIMARY KEY AUTO_INCREMENT,
    num INT NOT NULL,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE player_points (
    id INT PRIMARY KEY AUTO_INCREMENT,
    player_id INT NOT NULL,
    round_id INT NOT NULL,
    points INT NOT NULL CHECK (points >= 0),
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (round_id) REFERENCES rounds(id)
);

CREATE TABLE player_debts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    player_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL CHECK (amount >= 0),
    FOREIGN KEY (player_id) REFERENCES players(id)
);