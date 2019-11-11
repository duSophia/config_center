CREATE DATABASE `conf` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */

CREATE TABLE `conf_env` (
  `name` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(24) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `create_at` datetime DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `conf_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `value` text COLLATE utf8mb4_unicode_ci,
  `env` varchar(12) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `create_at` datetime DEFAULT NULL,
  `update_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `env` (`env`),
  CONSTRAINT `conf_record_ibfk_1` FOREIGN KEY (`env`) REFERENCES `conf_env` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

insert conf_env(name, display_name, create_at) values('JTPay', 'JTPay', '2016-01-01');