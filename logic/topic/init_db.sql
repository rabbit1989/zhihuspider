CREATE DATABASE if not exists `ZHIHUHOT_DATA` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;
USE `ZHIHUHOT_DATA`

CREATE TABLE if not exists `TOPIC` (
  `LINK_ID` int(32) unsigned NOT NULL,
  `NAME` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `FOCUS` int(32) unsigned NOT NULL,
  `LAST_VISIT` datetime DEFAULT NULL,
  `ADD_TIME` datetime DEFAULT NULL,
  PRIMARY KEY (`LINK_ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;