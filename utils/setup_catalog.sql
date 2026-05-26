-- Setup script for Marathos Unity Catalog structure

CREATE CATALOG IF NOT EXISTS marathos;

CREATE SCHEMA IF NOT EXISTS marathos.bronze;
CREATE SCHEMA IF NOT EXISTS marathos.silver;
CREATE SCHEMA IF NOT EXISTS marathos.gold;

CREATE VOLUME IF NOT EXISTS marathos.default.raw;