/**
 * Whitelister schema
 */

-- Disable foreign key checks until all schema has been created.
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `checks` (
  `name` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` text COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='A table to store checks persistently';

CREATE TABLE `guild_preferences` (
  `guild` bigint(20) NOT NULL COMMENT 'Discord Guild ID',
  `command_prefix` char(1) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The character that is the prefix of commands',
  PRIMARY KEY (`guild`),
  UNIQUE KEY `guild` (`guild`),
  KEY `index_guild` (`guild`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Specific Guild Preferences';

CREATE TABLE `pokemon` (
  `dex` int(4) unsigned NOT NULL COMMENT 'Dex ID of the Pokemon',
  `type` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Type to signify a family difference',
  `isotope` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The isotype ID of the Pokemon',
  `filename` varchar(46) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Full file name if needed',
  `shiny` int(1) unsigned DEFAULT NULL COMMENT 'Boolean for if the shiny is programmed in to the game',
  PRIMARY KEY (`dex`,`type`,`isotope`),
  UNIQUE KEY `dex_type_isotope` (`dex`,`type`,`isotope`),
  KEY `dex` (`dex`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='List of the Pokemon currently programmed in to the game';

CREATE TABLE `pokemon_names` (
  `dex` int(4) unsigned NOT NULL COMMENT 'The Pokemons ID in the national dex',
  `chinese` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The Pokemon''s name in Chinese',
  `english` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The Pokemon''s name in English',
  `french` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The Pokemon''s name in French',
  `german` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The Pokemon''s name in German',
  `italian` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The Pokemon''s name in Italian',
  `japanese` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The Pokemon''s name in Japanese',
  `korean` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The Pokemon''s name in Korean',
  `portuguese` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The Pokemon''s name in Portuguese',
  `spanish` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The Pokemon''s name in Spanish',
  `thai` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The Pokemon''s name in Thai',
  PRIMARY KEY (`dex`),
  UNIQUE KEY `dex` (`dex`),
  KEY `dex_index` (`dex`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `user_shinies` (
  `user_id` bigint(20) unsigned NOT NULL COMMENT 'The users Discord ID',
  `dex` int(4) unsigned NOT NULL COMMENT 'Dex ID of the Pokemon',
  `type` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Type to signify a family difference',
  `isotope` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The isotype ID of the Pokemon',
  `count` int(4) unsigned NOT NULL COMMENT 'The count of how many the user has',
  PRIMARY KEY (`user_id`,`dex`,`type`,`isotope`),
  UNIQUE KEY `user_id_dex_type_isotope` (`user_id`,`dex`,`type`,`isotope`),
  KEY `dex` (`dex`,`type`,`isotope`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_shinies_ibfk_3` FOREIGN KEY (`dex`, `type`, `isotope`) REFERENCES `pokemon` (`dex`, `type`, `isotope`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Enable foreign key checks.
SET FOREIGN_KEY_CHECKS=1;
# EOF
