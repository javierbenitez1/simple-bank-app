-- Simple Bank Application: database schema
-- Run with: mysql -u bank_user -p simple_bank < sql/schema.sql


-- Drop in reverse order so foreign keys don't block it
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id     INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) NOT NULL UNIQUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    account_id    INT PRIMARY KEY AUTO_INCREMENT,
    user_id       INT NOT NULL,
    balance       DECIMAL(10,2) NOT NULL DEFAULT 0,
    account_type  VARCHAR(50) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    CHECK (balance >= 0)
);

CREATE TABLE transactions (
    txn_id      INT PRIMARY KEY AUTO_INCREMENT,
    account_id  INT NOT NULL,
    txn_type    VARCHAR(20) NOT NULL,
    amount      DECIMAL(10,2) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    CHECK (amount > 0)
);