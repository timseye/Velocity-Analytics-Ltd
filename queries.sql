-- Q1: Top 10 drivers by career points
SELECT d.driverid, d.forename || ' ' || d.surname AS driver, SUM(r.points) AS total_points
FROM results r
JOIN drivers d ON d.driverid = r.driverid
GROUP BY d.driverid, driver
ORDER BY total_points DESC
LIMIT 10;

-- Q2: Average finishing position by constructor since 2010 (exclude DNFs/NULL positions)
SELECT c.constructorid, c.name AS constructor, ROUND(AVG(r.position)::numeric, 2) AS avg_finish
FROM results r
JOIN races ra ON ra.raceid = r.raceid
JOIN constructors c ON c.constructorid = r.constructorid
WHERE ra.year >= 2010 AND r.position IS NOT NULL
GROUP BY c.constructorid, constructor
ORDER BY avg_finish ASC;

-- Q3: Number of races per circuit
SELECT ci.circuitid, ci.name AS circuit, COUNT(*) AS race_count
FROM races ra
JOIN circuits ci ON ci.circuitid = ra.circuitid
GROUP BY ci.circuitid, circuit
ORDER BY race_count DESC;

-- Q4: Avg (qualifying - race) position delta per driver (positive = loses places)
SELECT d.driverid, d.forename || ' ' || d.surname AS driver,
       ROUND(AVG(q.position - r.position)::numeric, 2) AS avg_delta
FROM qualifying q
JOIN results r ON r.raceid = q.raceid AND r.driverid = q.driverid
JOIN drivers d ON d.driverid = q.driverid
WHERE q.position IS NOT NULL AND r.position IS NOT NULL
GROUP BY d.driverid, driver
ORDER BY avg_delta DESC
LIMIT 20;

-- Q5: DNFs per season
SELECT ra.year, COUNT(*) AS dnfs
FROM results r
JOIN races ra ON ra.raceid = r.raceid
JOIN status s ON s.statusid = r.statusid
WHERE s.status <> 'Finished'
GROUP BY ra.year
ORDER BY ra.year;

-- Q6: Avg pit stop duration (ms) by season
SELECT ra.year, ROUND(AVG(ps.milliseconds)::numeric, 2) AS avg_pit_ms
FROM pitstops ps
JOIN races ra ON ra.raceid = ps.raceid
GROUP BY ra.year
ORDER BY ra.year;

-- Q7: Home race podiums (driver nationality matches circuit country)
SELECT d.driverid, d.forename || ' ' || d.surname AS driver, COUNT(*) AS home_podiums
FROM results r
JOIN races ra ON ra.raceid = r.raceid
JOIN circuits ci ON ci.circuitid = ra.circuitid
JOIN drivers d ON d.driverid = r.driverid
WHERE r.position IN (1,2,3)
  AND LOWER(d.nationality) = LOWER(ci.country)
GROUP BY d.driverid, driver
ORDER BY home_podiums DESC;

-- Q8: Avg fastest lap speed by driver (where available)
SELECT d.driverid, d.forename || ' ' || d.surname AS driver,
       ROUND(AVG(r.fastestlapspeed)::numeric, 3) AS avg_fastest_lap_speed
FROM results r
JOIN drivers d ON d.driverid = r.driverid
WHERE r.fastestlapspeed IS NOT NULL
GROUP BY d.driverid, driver
ORDER BY avg_fastest_lap_speed DESC
LIMIT 20;

-- Q9: Most podiums by driver
SELECT d.driverid, d.forename || ' ' || d.surname AS driver, COUNT(*) AS podiums
FROM results r
JOIN drivers d ON d.driverid = r.driverid
WHERE r.position IN (1,2,3)
GROUP BY d.driverid, driver
ORDER BY podiums DESC
LIMIT 20;

-- Q10: Avg grid position by constructor (last 10 seasons)
SELECT c.constructorid, c.name AS constructor,
       ROUND(AVG(r.grid)::numeric, 2) AS avg_grid
FROM results r
JOIN races ra ON ra.raceid = r.raceid
JOIN constructors c ON c.constructorid = r.constructorid
WHERE ra.year >= EXTRACT(YEAR FROM CURRENT_DATE) - 10
  AND r.grid IS NOT NULL
GROUP BY c.constructorid, constructor
ORDER BY avg_grid ASC;
