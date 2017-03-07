SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

CREATE DATABASE IF NOT EXISTS `Artemis` COLLATE=utf8mb4_unicode_ci;
USE `Artemis`;

CREATE TABLE IF NOT EXISTS `attachments` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `timestamp` DATETIME NOT NULL,
  `spam_id` CHAR(32),
  `sensor_id` VARCHAR(64) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `sender` VARCHAR(256) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `recipient` VARCHAR(256) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `source_ip` VARCHAR(16) CHARACTER SET utf8 COLLATE utf8_unicode_ci,
  `file_name` VARCHAR(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `file_path` MEDIUMTEXT NOT NULL,
  `file_type` VARCHAR(50) NOT NULL,
  `md5` CHAR(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `sha1` CHAR(40),
  `sha256` CHAR(64),
  `vt_positives` SMALLINT UNSIGNED,
  `vt_total` SMALLINT UNSIGNED,
  `last_vt` DATETIME,
  PRIMARY KEY (`id`),
  KEY `spam_id` (`spam_id`),
  KEY `file_name` (`file_name`),
  KEY `md5` (`md5`)
) ENGINE=InnoDB DEFAULT COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS `thugfiles` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `timestamp` DATETIME NOT NULL,
  `file_name` VARCHAR(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `file_path` MEDIUMTEXT NOT NULL,
  `md5` CHAR(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `sha1` CHAR(40),
  `sha256` CHAR(64),
  `vt_positives` SMALLINT UNSIGNED,
  `vt_total` SMALLINT UNSIGNED,
  `last_vt` DATETIME,
  PRIMARY KEY (`id`),
  KEY `file_name` (`file_name`),
  KEY `md5` (`file_name`)
) ENGINE=InnoDB DEFAULT COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=1;
