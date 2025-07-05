CREATE DATABASE IF NOT EXISTS url_shortener;

USE url_shortener;

CREATE TABLE urls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_url TEXT NOT NULL,
    short_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL
);