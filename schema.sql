/**
 * Whitelister schema
 */

-- Disable foreign key checks until all schema has been created.
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `preferences` (
  `guild` bigint(20) NOT NULL COMMENT 'Discord Guild ID',
  `command_prefix` char(1) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'The character that is the prefix of commands',
  PRIMARY KEY (`guild`),
  UNIQUE KEY `guild` (`guild`),
  KEY `index_guild` (`guild`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Specific Guild Preferences';

CREATE TABLE `shiny_list` (
  `dex` int(10) unsigned NOT NULL COMMENT 'The Pokemons ID in the national dex',
  `name_de` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'German name of the Pokemon',
  `name_en` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'English name of the Pokemon',
  `name_fr` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'French name of the Pokemon',
  `name_ja` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Japanese name of the Pokemon',
  `name_kr` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Korean name of the Pokemon',
  `name_zh` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Chinese name of the Pokemon',
  `type` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Type to signify a family difference',
  `shiny_released` int(1) unsigned NOT NULL COMMENT 'Boolean whether it is released or not',
  `released_date` date DEFAULT NULL COMMENT 'Date that the shiny was released',
  `fn` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'Preset image ID',
  `isotope` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Isolated type number',
  `family` varchar(24) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Pokemons evolution family',
  PRIMARY KEY (`dex`,`type`,`isotope`,`family`),
  UNIQUE KEY `dex_type_isotope_family` (`dex`,`type`,`isotope`,`family`),
  KEY `dex` (`dex`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='List of shiny Pokemon from Github';

-- Enable foreign key checks.
SET FOREIGN_KEY_CHECKS=1;
# EOF
