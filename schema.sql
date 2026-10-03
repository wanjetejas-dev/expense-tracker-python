-- Run once:  mysql -u root -p < schema.sql
CREATE DATABASE IF NOT EXISTS expense_tracker;
USE expense_tracker;

CREATE TABLE IF NOT EXISTS expenses (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    date        DATE           NOT NULL,
    category    VARCHAR(50)    NOT NULL,
    description VARCHAR(255),
    amount      DECIMAL(10, 2) NOT NULL,
    INDEX idx_expenses_date (date)
);

-- Recommended: a dedicated user instead of connecting as root.
-- Change the password before running these two lines.
-- CREATE USER IF NOT EXISTS 'expense_user'@'localhost' IDENTIFIED BY 'change_me';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON expense_tracker.* TO 'expense_user'@'localhost';
