-- =============================================================================
-- ASSIGNMENT #3 - SQL QUERIES FOR APACHE SUPERSET
-- =============================================================================

-- TASK 5: GEO VISUALIZATION (8 pts)
-- Map of all F1 circuits worldwide
SELECT 
    c.name AS circuit_name,
    c.location,
    c.country,
    c.lat,
    c.lng,
    COUNT(r.raceid) AS total_races
FROM circuits c
LEFT JOIN races r ON r.circuitid = c.circuitid
WHERE c.lat IS NOT NULL AND c.lng IS NOT NULL
GROUP BY c.circuitid, c.name, c.location, c.country, c.lat, c.lng
ORDER BY total_races DESC;

-- =============================================================================
-- TASK 6: HEATMAP (7 pts)
-- Constructor performance by year (2010+)
SELECT 
    c.name AS constructor,
    ra.year,
    SUM(r.points) AS total_points
FROM results r
JOIN constructors c ON c.constructorid = r.constructorid
JOIN races ra ON ra.raceid = r.raceid
WHERE ra.year >= 2010
GROUP BY c.name, ra.year
HAVING SUM(r.points) > 0
ORDER BY ra.year, total_points DESC;

-- Alternative: Driver × Circuit performance
SELECT 
    d.surname AS driver,
    ci.name AS circuit,
    COUNT(CASE WHEN r.position IN (1,2,3) THEN 1 END) AS podiums,
    AVG(r.position) AS avg_position
FROM results r
JOIN drivers d ON d.driverid = r.driverid
JOIN races ra ON ra.raceid = r.raceid
JOIN circuits ci ON ci.circuitid = ra.circuitid
WHERE r.position IS NOT NULL AND ra.year >= 2010
GROUP BY d.surname, ci.name
HAVING COUNT(*) >= 5
ORDER BY podiums DESC;

-- =============================================================================
-- TASK 7: SUNBURST (7 pts)
-- Hierarchy: Constructor → Driver → Season Points
SELECT 
    c.name AS constructor,
    d.forename || ' ' || d.surname AS driver,
    ra.year AS season,
    SUM(r.points) AS total_points
FROM results r
JOIN drivers d ON d.driverid = r.driverid
JOIN constructors c ON c.constructorid = r.constructorid
JOIN races ra ON ra.raceid = r.raceid
WHERE ra.year >= 2015 AND r.points > 0
GROUP BY c.name, d.driverid, driver, ra.year
ORDER BY ra.year DESC, total_points DESC;

-- =============================================================================
-- TASK 8: TREEMAP (7 pts)
-- Constructor contribution to total F1 points (2010+)
SELECT 
    c.name AS constructor,
    SUM(r.points) AS total_points,
    COUNT(DISTINCT ra.year) AS seasons_active,
    COUNT(DISTINCT r.driverid) AS unique_drivers
FROM results r
JOIN constructors c ON c.constructorid = r.constructorid
JOIN races ra ON ra.raceid = r.raceid
WHERE ra.year >= 2010
GROUP BY c.name
HAVING SUM(r.points) > 100
ORDER BY total_points DESC;

-- Alternative: Driver contribution within each constructor
SELECT 
    c.name AS constructor,
    d.surname AS driver,
    SUM(r.points) AS driver_points
FROM results r
JOIN drivers d ON d.driverid = r.driverid
JOIN constructors c ON c.constructorid = r.constructorid
JOIN races ra ON ra.raceid = r.raceid
WHERE ra.year >= 2015
GROUP BY c.name, d.surname
HAVING SUM(r.points) > 50
ORDER BY constructor, driver_points DESC;

-- =============================================================================
-- TASK 9: WORD CLOUD (7 pts)
-- Most frequent circuits (by number of races)
SELECT 
    c.name AS circuit_name,
    COUNT(r.raceid) AS race_count
FROM circuits c
JOIN races r ON r.circuitid = c.circuitid
GROUP BY c.name
ORDER BY race_count DESC;

-- Alternative: Most frequent Grand Prix names
SELECT 
    ra.name AS grand_prix,
    COUNT(*) AS occurrences
FROM races ra
GROUP BY ra.name
ORDER BY occurrences DESC;

-- Alternative: Constructor participation
SELECT 
    c.name AS constructor,
    COUNT(DISTINCT ra.raceid) AS races_participated
FROM results r
JOIN constructors c ON c.constructorid = r.constructorid
JOIN races ra ON ra.raceid = r.raceid
GROUP BY c.name
ORDER BY races_participated DESC;

-- =============================================================================
-- TASK 10: DATA ENGINEERING (8 pts)
-- Simple time series for results growth
SELECT 
    ra.year,
    ra.round,
    ra.date,
    COUNT(r.resultid) AS total_results
FROM races ra
LEFT JOIN results r ON r.raceid = ra.raceid
WHERE ra.year >= 2020
GROUP BY ra.year, ra.round, ra.date
ORDER BY ra.date;

-- =============================================================================
-- TASK 12: METRICS (7 pts)
-- Driver statistics with AVG, MEDIAN, and growth rate

-- For creating metrics in Superset interface:
-- Metric 1: AVG(points) - Average Points
-- Metric 2: PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY points) - Median Points
-- Metric 3: Growth Rate calculation (requires window functions)

-- Base query for metrics:
SELECT 
    d.forename || ' ' || d.surname AS driver,
    COUNT(r.resultid) AS total_races,
    SUM(r.points) AS total_points,
    AVG(r.points) AS avg_points,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY r.points) AS median_points,
    MAX(r.points) AS max_points_single_race,
    MIN(CASE WHEN r.position IS NOT NULL THEN r.position END) AS best_position
FROM results r
JOIN drivers d ON d.driverid = r.driverid
GROUP BY d.driverid, driver
HAVING COUNT(r.resultid) >= 50
ORDER BY total_points DESC
LIMIT 20;

-- Year over year growth:
WITH yearly_points AS (
    SELECT 
        ra.year,
        SUM(r.points) AS season_points
    FROM results r
    JOIN races ra ON ra.raceid = r.raceid
    WHERE ra.year >= 2010
    GROUP BY ra.year
)
SELECT 
    year,
    season_points,
    LAG(season_points) OVER (ORDER BY year) AS previous_year,
    season_points - LAG(season_points) OVER (ORDER BY year) AS points_change,
    ROUND(
        ((season_points - LAG(season_points) OVER (ORDER BY year)) * 100.0 / 
        NULLIF(LAG(season_points) OVER (ORDER BY year), 0)),
        2
    ) AS growth_rate_pct
FROM yearly_points
ORDER BY year;

-- =============================================================================
-- TASK 13: CALCULATED COLUMNS (7 pts)
-- Normalization formula: (x - min) / (max - min)
-- This will be done in Superset UI under "Calculated Columns"
-- Formula example for normalizing points:
-- (points - MIN(points)) / (MAX(points) - MIN(points))

-- Base data for normalized visualization:
SELECT 
    d.surname AS driver,
    SUM(r.points) AS total_points
FROM results r
JOIN drivers d ON d.driverid = r.driverid
JOIN races ra ON ra.raceid = r.raceid
WHERE ra.year >= 2015
GROUP BY d.surname
HAVING SUM(r.points) > 100
ORDER BY total_points DESC;

-- =============================================================================
-- TASK 14: CATEGORIZATION (8 pts)
-- Points categories: Low / Medium / High / Elite
-- This will be done in Superset UI using CASE WHEN

-- Base query:
SELECT 
    d.forename || ' ' || d.surname AS driver,
    SUM(r.points) AS career_points,
    CASE 
        WHEN SUM(r.points) >= 400 THEN 'Elite'
        WHEN SUM(r.points) >= 201 THEN 'High'
        WHEN SUM(r.points) >= 51 THEN 'Medium'
        ELSE 'Low'
    END AS points_category
FROM results r
JOIN drivers d ON d.driverid = r.driverid
GROUP BY d.driverid, driver
ORDER BY career_points DESC;

-- =============================================================================
-- ADDITIONAL USEFUL QUERIES
-- =============================================================================

-- Constructor standings by year (for animations)
SELECT 
    ra.year,
    c.name AS constructor,
    SUM(r.points) AS season_points,
    COUNT(CASE WHEN r.position = 1 THEN 1 END) AS wins,
    COUNT(CASE WHEN r.position IN (1,2,3) THEN 1 END) AS podiums
FROM results r
JOIN constructors c ON c.constructorid = r.constructorid
JOIN races ra ON ra.raceid = r.raceid
WHERE ra.year >= 2010
GROUP BY ra.year, c.name
ORDER BY ra.year, season_points DESC;

-- Driver age analysis
SELECT 
    d.forename || ' ' || d.surname AS driver,
    d.dob,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, d.dob)) AS current_age,
    COUNT(r.resultid) AS total_races,
    SUM(r.points) AS total_points
FROM drivers d
LEFT JOIN results r ON r.driverid = d.driverid
WHERE d.dob IS NOT NULL
GROUP BY d.driverid, driver, d.dob
HAVING COUNT(r.resultid) > 0
ORDER BY total_points DESC
LIMIT 50;

-- Reliability analysis (finish rate by constructor)
SELECT 
    c.name AS constructor,
    COUNT(r.resultid) AS total_results,
    COUNT(CASE WHEN s.status = 'Finished' THEN 1 END) AS finished,
    ROUND(
        COUNT(CASE WHEN s.status = 'Finished' THEN 1 END) * 100.0 / 
        COUNT(r.resultid),
        2
    ) AS finish_rate_pct
FROM results r
JOIN constructors c ON c.constructorid = r.constructorid
JOIN status s ON s.statusid = r.statusid
JOIN races ra ON ra.raceid = r.raceid
WHERE ra.year >= 2010
GROUP BY c.name
HAVING COUNT(r.resultid) >= 100
ORDER BY finish_rate_pct DESC;
