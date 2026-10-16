-- Script de inicialização do banco de dados MariaDB (Ambiente Local e Futura VM)
CREATE DATABASE IF NOT EXISTS pfat_database;
USE pfat_database;

CREATE TABLE IF NOT EXISTS contatos_pfat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    valor_string VARCHAR(255),
    criacao_em DATETIME NOT NULL,
    obtido_em DATETIME,
    grupo VARCHAR(100),
    identificacao_operacional VARCHAR(255),
    UNIQUE KEY uk_email_criacao (email, criacao_em)
);
