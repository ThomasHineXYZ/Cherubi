/**
 * Whitelister schema
 */

-- Disable foreign key checks until all schema has been created.
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `checks` (
  `name` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` text COLLATE utf8mb4_unicode_ci NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='A table to store checks persistently';

CREATE TABLE `friend_codes` (
  `user_id` bigint(20) unsigned NOT NULL COMMENT 'The users Discord ID',
  `identifier` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The trainer name or other identifying text',
  `code` bigint(12) unsigned NOT NULL COMMENT 'The friend code itself',
  `main` int(1) unsigned NOT NULL DEFAULT 0 COMMENT 'If this is the users main account or not',
  `updated` datetime NOT NULL COMMENT 'The datetime for when it was added or updated',
  PRIMARY KEY (`user_id`,`identifier`),
  UNIQUE KEY `user_id_identifier` (`user_id`,`identifier`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='The storage for friend codes';

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

CREATE TABLE `pokemon_categories` (
  `dex` int(4) unsigned NOT NULL COMMENT 'The Pokemons ID in the national dex',
  `chinese` varchar(32) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons category in Chinese',
  `english` varchar(32) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons category in English',
  `french` varchar(32) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons category in French',
  `german` varchar(32) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons category in German',
  `italian` varchar(32) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons category in Italian',
  `japanese` varchar(32) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons category in Japanese',
  `korean` varchar(32) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons category in Korean',
  `portuguese` varchar(32) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons category in Portuguese',
  `russian` varchar(32) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons category in Russian',
  `spanish` varchar(32) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons category in Spanish',
  `thai` varchar(32) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons category in Thai',
  PRIMARY KEY (`dex`),
  UNIQUE KEY `dex` (`dex`),
  KEY `dex_index` (`dex`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='List of the categories for the different Pokemon';

CREATE TABLE `pokemon_descriptions` (
  `dex` int(4) unsigned NOT NULL COMMENT 'The Pokemons ID in the national dex',
  `chinese` varchar(512) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons description in Chinese',
  `english` varchar(512) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons description in English',
  `french` varchar(512) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons description in French',
  `german` varchar(512) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons description in German',
  `italian` varchar(512) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons description in Italian',
  `japanese` varchar(512) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons description in Japanese',
  `korean` varchar(512) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons description in Korean',
  `portuguese` varchar(512) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons description in Portuguese',
  `russian` varchar(512) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons description in Russian',
  `spanish` varchar(512) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons description in Spanish',
  `thai` varchar(512) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons description in Thai',
  PRIMARY KEY (`dex`),
  UNIQUE KEY `dex` (`dex`),
  KEY `dex_index` (`dex`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='List of the descriptions for the different Pokemon';

CREATE TABLE `pokemon_names` (
  `dex` int(4) unsigned NOT NULL COMMENT 'The Pokemons ID in the national dex',
  `chinese` varchar(16) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons name in Chinese',
  `english` varchar(16) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons name in English',
  `french` varchar(16) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons name in French',
  `german` varchar(16) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons name in German',
  `italian` varchar(16) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons name in Italian',
  `japanese` varchar(16) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons name in Japanese',
  `korean` varchar(16) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons name in Korean',
  `portuguese` varchar(16) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons name in Portuguese',
  `russian` varchar(16) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons name in Russian',
  `spanish` varchar(16) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons name in Spanish',
  `thai` varchar(16) COLLATE utf8mb4_unicode_ci NULL COMMENT 'The Pokemons name in Thai',
  PRIMARY KEY (`dex`),
  UNIQUE KEY `dex` (`dex`),
  KEY `dex_index` (`dex`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='List of the names for the different Pokemon';

CREATE TABLE `user_preferences` (
  `user_id` bigint(20) unsigned NOT NULL COMMENT 'The users Discord ID',
  `home_guild` bigint(20) unsigned NULL COMMENT 'The users home guild / sever ID',
  `fc_visibility` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'private',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `user_id_index` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Storage for user specific settings';

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
