CREATE DATABASE if not exists `ZHIHUHOT_DATA` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;
USE `ZHIHUHOT_DATA`

CREATE TABLE if not exists `topic` (
  `link_id` int(32) unsigned NOT NULL,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `focus` int(32) unsigned NOT NULL,
  `last_visit` datetime DEFAULT NULL,
  `add_time` datetime DEFAULT NULL,
  PRIMARY KEY (`link_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE if not exists `question`(
	`question_id` int(32) unsigned NOT NULL,
	`name` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
	`focus` int (32) unsigned NOT NULL,
	`view` int (32) unsigned NOT NULL,
	`answer_number` int(32) unsigned NOT NULL,
	`last_visit` datetime DEFAULT NULL,
	`last_visit_sec` int(64) unsigned NOT NULL DEFAULT '0',
	`create_time` datetime DEFAULT NULL,
	`visit_interval` int(32) unsigned NOT NULL DEFAULT '0',
	`focus_inc` int(32) unsigned NOT NULL DEFAULT '0',
	`view_inc` int(32) unsigned NOT NULL DEFAULT '0',
	`answer_num_inc` int(32) unsigned NOT NULL DEFAULT '0',
	PRIMARY kEY (`question_id`)
)ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;