/**
 * Whitelister schema
 */

-- Disable foreign key checks until all schema has been created.
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `pogo_pokemon` (
  `dex` int(4) unsigned NOT NULL COMMENT 'Dex ID of the Pokemon',
  `type` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Type to signify a family difference',
  `isotope` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The isotype ID of the Pokemon',
  `filename` varchar(46) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Full file name if needed',
  `shiny` int(1) unsigned DEFAULT NULL COMMENT 'Boolean for if the shiny is programmed in to the game',
  PRIMARY KEY (`dex`,`type`,`isotope`),
  UNIQUE KEY `dex_type_isotope` (`dex`,`type`,`isotope`),
  KEY `dex` (`dex`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='List of the Pokemon currently programmed in to the game';

CREATE TABLE `preferences` (
  `guild` bigint(20) NOT NULL COMMENT 'Discord Guild ID',
  `command_prefix` char(1) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The character that is the prefix of commands',
  PRIMARY KEY (`guild`),
  UNIQUE KEY `guild` (`guild`),
  KEY `index_guild` (`guild`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Specific Guild Preferences';

-- Enable foreign key checks.
SET FOREIGN_KEY_CHECKS=1;
# EOF
