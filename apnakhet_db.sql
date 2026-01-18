create database apnakhet_db;

USE apnakhet_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    mobile VARCHAR(15),
    password VARCHAR(255),
    role ENUM('farmer', 'user'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farmer_id INT,
    crop_name VARCHAR(100),
    price_per_kg INT,
    quantity INT,
    image VARCHAR(200),
    video VARCHAR(200)
);

