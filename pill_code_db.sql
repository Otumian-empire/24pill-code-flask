-- Database name = pill_code_db

-- SQLITE3 tables
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS `users` (
	`user_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`user_first_name` TEXT NOT NULL,
	`user_last_name` TEXT NOT NULL,
	`user_email` TEXT NOT NULL UNIQUE,
	`user_password` TEXT NOT NULL,
	`user_bio` TEXT NOT NULL,
	`user_register_date` TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS `tokens` (
	`token_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`token_text` TEXT NOT NULL UNIQUE,
	`token_date` TEXT NOT NULL,
	`token_dormancy` TEXT NOT NULL,
	`token_purpose` TEXT NOT NULL,
	`user_email` TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS `comments` (
	`comment_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`post_id` INTEGER NOT NULL,
	`comment_text` TEXT NOT NULL,
	`comment_date` TEXT NOT NULL,
	`user_email` TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS `articles` (
	`post_id` INTEGER NOT NULL,
	`post_title` TEXT NOT NULL UNIQUE,
	`post_content` TEXT NOT NULL,
	`user_email` TEXT NOT NULL,
	`post_date` TEXT NOT NULL,
	PRIMARY KEY(`post_id`)
);

COMMIT;

-- MySQL tables
CREATE TABLE IF NOT EXISTS `users`(
	`user_id` INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`user_first_name` VARCHAR(25) NOT NULL,
	`user_last_name` VARCHAR(25) NOT NULL,
	`user_email` VARCHAR(125) NOT NULL UNIQUE,
	`user_password` VARCHAR(60) NOT NULL,
	`user_bio` VARCHAR(400) NOT NULL,
	`user_register_date` VARCHAR(60) NOT NULL
);

CREATE TABLE IF NOT EXISTS `tokens`(
	`token_id` INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`token_text` VARCHAR(10) NOT NULL UNIQUE,
	`token_date` VARCHAR(60) NOT NULL,
	`token_dormancy` VARCHAR(60) NOT NULL,
	`token_purpose` VARCHAR(60) NOT NULL,
	`user_email` VARCHAR(125) NOT NULL
);

CREATE TABLE IF NOT EXISTS `comments`(
	`comment_id` INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`post_id` INTEGER NOT NULL,
	`comment_text` VARCHAR(400) NOT NULL,
	`comment_date` VARCHAR(60) NOT NULL,
	`user_email` VARCHAR(125) NOT NULL
);

CREATE TABLE IF NOT EXISTS `articles`(
	`post_id` INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`post_title` VARCHAR(120) NOT NULL UNIQUE,
	`post_content` VARCHAR(600) NOT NULL,
	`user_email` VARCHAR(120) NOT NULL,
	`post_date` VARCHAR(60) NOT NULL
);