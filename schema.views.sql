/**
 * Whitelister schema
 */

-- Disable foreign key checks until all schema has been created.
SET FOREIGN_KEY_CHECKS=0;

CREATE VIEW `pokemon_names_chinese` AS
SELECT
    dex,
    chinese AS name
FROM pokemon_names;

CREATE VIEW `pokemon_names_english` AS
SELECT
    dex,
    english AS name
FROM pokemon_names;

CREATE VIEW `pokemon_names_french` AS
SELECT
    dex,
    french AS name
FROM pokemon_names;

CREATE VIEW `pokemon_names_german` AS
SELECT
    dex,
    german AS name
FROM pokemon_names;

CREATE VIEW `pokemon_names_italian` AS
SELECT
    dex,
    italian AS name
FROM pokemon_names;

CREATE VIEW `pokemon_names_japanese` AS
SELECT
    dex,
    japanese AS name
FROM pokemon_names;

CREATE VIEW `pokemon_names_korean` AS
SELECT
    dex,
    korean AS name
FROM pokemon_names;

CREATE VIEW `pokemon_names_portuguese` AS
SELECT
    dex,
    portuguese AS name
FROM pokemon_names;

CREATE VIEW `pokemon_names_spanish` AS
SELECT
    dex,
    spanish AS name
FROM pokemon_names;

CREATE VIEW `pokemon_names_thai` AS
SELECT
    dex,
    thai AS name
FROM pokemon_names;

-- Enable foreign key checks.
SET FOREIGN_KEY_CHECKS=1;
# EOF
