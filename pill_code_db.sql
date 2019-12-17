BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `users` (
	`user_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`user_first_name`	TEXT NOT NULL,
	`user_last_name`	TEXT NOT NULL,
	`user_email`	TEXT NOT NULL UNIQUE,
	`user_password`	TEXT NOT NULL,
	`user_bio`	TEXT NOT NULL,
	`user_register_date`	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS `tokens` (
	`token_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`token_text`	TEXT NOT NULL UNIQUE,
	`token_date`	TEXT NOT NULL,
	`token_dormancy`	TEXT NOT NULL,
	`token_purpose`	TEXT NOT NULL,
	`user_email`	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS `comments` (
	`comment_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`post_id`	INTEGER NOT NULL,
	`comment_text`	TEXT NOT NULL,
	`comment_date`	TEXT NOT NULL,
	`user_email`	TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS `articles` (
	`post_id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`post_title`	TEXT NOT NULL,
	`post_content`	TEXT NOT NULL,
	`user_email`	TEXT NOT NULL,
	`post_date`	TEXT NOT NULL
);
COMMIT;
