-- Some parts and solutions of this code was found through help from Claude (Anthropic).
-- Views over the gold layer. Task 5 asks for at least two per marathon type.
-- The last two are extra ones used by the dashboard.


-- Top 10 fastest finishers per distance event
CREATE OR REPLACE VIEW marathos.gold.vw_distance_top10_fastest_per_event AS
WITH ranked AS (
    SELECT
        e.event_name,
        e.event_distance_value,
        e.event_distance_unit,
        a.athlete_id,
        a.athlete_gender,
        c.country_name,
        f.performance_seconds,
        f.age_at_event,
        ROW_NUMBER() OVER (PARTITION BY f.event_id ORDER BY f.performance_seconds ASC) AS rank_in_event
    FROM marathos.gold.fct_results f
    JOIN marathos.gold.dim_event e ON f.event_id = e.event_id
    JOIN marathos.gold.dim_athlete a ON f.athlete_id = a.athlete_id
    JOIN marathos.gold.dim_country c ON f.country_code = c.country_code
    WHERE f.event_type = 'distance' AND f.performance_seconds IS NOT NULL
)
SELECT *
FROM ranked
WHERE rank_in_event <= 10;


-- Average finish time per age group for distance events
CREATE OR REPLACE VIEW marathos.gold.vw_distance_avg_time_by_age_group AS
SELECT
    CASE
        WHEN age_at_event < 20 THEN 'Under 20'
        WHEN age_at_event BETWEEN 20 AND 29 THEN '20-29'
        WHEN age_at_event BETWEEN 30 AND 39 THEN '30-39'
        WHEN age_at_event BETWEEN 40 AND 49 THEN '40-49'
        WHEN age_at_event BETWEEN 50 AND 59 THEN '50-59'
        WHEN age_at_event BETWEEN 60 AND 69 THEN '60-69'
        ELSE '70+'
    END AS age_group,
    COUNT(*) AS num_results,
    ROUND(AVG(performance_seconds), 0) AS avg_seconds,
    ROUND(AVG(performance_seconds) / 3600.0, 2) AS avg_hours
FROM marathos.gold.fct_results
WHERE event_type = 'distance' AND performance_seconds IS NOT NULL
GROUP BY age_group
ORDER BY age_group;


-- Top 10 longest distances per time event (24h, 12h, 6h etc)
CREATE OR REPLACE VIEW marathos.gold.vw_time_top10_longest_per_event AS
WITH ranked AS (
    SELECT
        e.event_name,
        e.event_distance_value AS event_hours,
        a.athlete_id,
        a.athlete_gender,
        c.country_name,
        f.performance_distance,
        f.performance_unit,
        f.age_at_event,
        ROW_NUMBER() OVER (PARTITION BY f.event_id ORDER BY f.performance_distance DESC) AS rank_in_event
    FROM marathos.gold.fct_results f
    JOIN marathos.gold.dim_event e ON f.event_id = e.event_id
    JOIN marathos.gold.dim_athlete a ON f.athlete_id = a.athlete_id
    JOIN marathos.gold.dim_country c ON f.country_code = c.country_code
    WHERE f.event_type = 'time' AND f.performance_distance IS NOT NULL
)
SELECT *
FROM ranked
WHERE rank_in_event <= 10;


-- Average distance covered per age group for time events
CREATE OR REPLACE VIEW marathos.gold.vw_time_avg_distance_by_age_group AS
SELECT
    CASE
        WHEN age_at_event < 20 THEN 'Under 20'
        WHEN age_at_event BETWEEN 20 AND 29 THEN '20-29'
        WHEN age_at_event BETWEEN 30 AND 39 THEN '30-39'
        WHEN age_at_event BETWEEN 40 AND 49 THEN '40-49'
        WHEN age_at_event BETWEEN 50 AND 59 THEN '50-59'
        WHEN age_at_event BETWEEN 60 AND 69 THEN '60-69'
        ELSE '70+'
    END AS age_group,
    COUNT(*) AS num_results,
    ROUND(AVG(performance_distance), 2) AS avg_distance
FROM marathos.gold.fct_results
WHERE event_type = 'time' AND performance_distance IS NOT NULL
GROUP BY age_group
ORDER BY age_group;


-- Top 10 longest distances in multi-day events
CREATE OR REPLACE VIEW marathos.gold.vw_multiday_top10_longest AS
SELECT
    e.event_name,
    e.event_distance_value AS event_days,
    a.athlete_id,
    a.athlete_gender,
    c.country_name,
    f.performance_distance,
    f.age_at_event
FROM marathos.gold.fct_results f
JOIN marathos.gold.dim_event e ON f.event_id = e.event_id
JOIN marathos.gold.dim_athlete a ON f.athlete_id = a.athlete_id
JOIN marathos.gold.dim_country c ON f.country_code = c.country_code
WHERE f.event_type = 'multi_day' AND f.performance_distance IS NOT NULL
ORDER BY f.performance_distance DESC
LIMIT 10;


-- Multi-day results aggregated by country
CREATE OR REPLACE VIEW marathos.gold.vw_multiday_results_by_country AS
SELECT
    c.country_name,
    c.continent,
    COUNT(*) AS num_results,
    ROUND(AVG(f.performance_distance), 2) AS avg_distance,
    ROUND(MAX(f.performance_distance), 2) AS max_distance
FROM marathos.gold.fct_results f
JOIN marathos.gold.dim_country c ON f.country_code = c.country_code
WHERE f.event_type = 'multi_day' AND f.performance_distance IS NOT NULL
GROUP BY c.country_name, c.continent
ORDER BY num_results DESC;


-- Results per year across all event types (used by dashboard)
CREATE OR REPLACE VIEW marathos.gold.vw_results_per_year AS
SELECT
    d.year,
    f.event_type,
    COUNT(*) AS num_results
FROM marathos.gold.fct_results f
JOIN marathos.gold.dim_date d ON f.start_date_id = d.date_id
GROUP BY d.year, f.event_type
ORDER BY d.year, f.event_type;


-- Results and unique athletes per country (used by dashboard)
CREATE OR REPLACE VIEW marathos.gold.vw_results_by_country AS
SELECT
    c.country_name,
    c.continent,
    COUNT(*) AS num_results,
    COUNT(DISTINCT f.athlete_id) AS unique_athletes
FROM marathos.gold.fct_results f
JOIN marathos.gold.dim_country c ON f.country_code = c.country_code
GROUP BY c.country_name, c.continent
ORDER BY num_results DESC;