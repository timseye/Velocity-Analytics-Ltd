# Superset Chart Instructions (Detailed)

Here are the detailed queries and settings for the charts you need to create in Apache Superset.

**General Workflow:**
1.  In Superset, go to **SQL Lab**.
2.  Paste the SQL query for the chart you want to create.
3.  Run the query to see the results.
4.  Click the **EXPLORE** button above the results.
5.  Follow the specific instructions below for each chart.

---

## 1. Pie Chart: Most Podiums by Driver

**Chart Type:** Pie Chart

**SQL Query:**
```sql
-- Q9: Most podiums by driver
SELECT d.forename || ' ' || d.surname AS driver, COUNT(*) AS podiums
FROM public.results r
JOIN public.drivers d ON d.driverid = r.driverid
WHERE r.position IN (1,2,3)
GROUP BY d.driverid, driver
ORDER BY podiums DESC
LIMIT 20;
```

**Configuration Steps:**
1.  In the chart builder, set the **Visualization Type** to **Pie Chart**.
2.  In the **DATA** tab:
    - **GROUP BY**: Select `driver`.
    - **METRICS**: Select `podiums` with a `SUM` aggregator.
3.  In the **CUSTOMIZE** tab, give the chart a title (e.g., "Top 20 Drivers by Podiums").

---

## 2. Bar Chart: Top 10 Drivers by Career Points

**Chart Type:** Bar Chart

**SQL Query:**
```sql
-- Q1: Top 10 drivers by career points
SELECT d.driverid, d.forename || ' ' || d.surname AS driver, SUM(r.points) AS total_points
FROM public.results r
JOIN public.drivers d ON d.driverid = r.driverid
GROUP BY d.driverid, driver
ORDER BY total_points DESC
LIMIT 10;
```

**Configuration Steps:**
1.  In the chart builder, set the **Visualization Type** to **Bar Chart**.
2.  In the **DATA** tab:
    - **GROUP BY**: Select `driver`.
    - **METRICS**: Select `total_points` with a `SUM` aggregator.
3.  In the **CUSTOMIZE** tab, give the chart a title and label the axes.

---

## 3. Horizontal Bar Chart: Average Finishing Position by Constructor

**Chart Type:** Bar Chart

**SQL Query:**
```sql
-- Q2: Average finishing position by constructor since 2010
SELECT c.name AS constructor, ROUND(AVG(r.position)::numeric, 2) AS avg_finish
FROM public.results r
JOIN public.races ra ON ra.raceid = r.raceid
JOIN public.constructors c ON c.constructorid = r.constructorid
WHERE ra.year >= 2010 AND r.position IS NOT NULL
GROUP BY c.constructorid, c.name
ORDER BY avg_finish ASC;
```

**Configuration Steps:**
1.  In the chart builder, set the **Visualization Type** to **Bar Chart**.
2.  In the **DATA** tab:
    - **GROUP BY**: Select `constructor`.
    - **METRICS**: Select `avg_finish` with a `SUM` aggregator.
3.  In the **CUSTOMIZE** tab:
    - Under **Bar Chart**, set **Orientation** to **Horizontal**.
    - Give the chart a title.

---

## 4. Line Chart: DNFs per Season

**Chart Type:** Line Chart

**SQL Query:**
```sql
-- Q5: DNFs per season
SELECT ra.year, COUNT(*) AS dnfs
FROM public.results r
JOIN public.races ra ON ra.raceid = r.raceid
JOIN public.status s ON s.statusid = r.statusid
WHERE s.status <> 'Finished'
GROUP BY ra.year
ORDER BY ra.year;
```

**Configuration Steps:**
1.  In the chart builder, set the **Visualization Type** to **Line Chart**.
2.  In the **DATA** tab:
    - **X-AXIS**: Select `year`.
    - **METRICS**: Select `dnfs` with a `SUM` aggregator.
3.  In the **CUSTOMIZE** tab, give the chart a title.

---

## 5. Histogram: Pit Stop Time Distribution

**Chart Type:** Histogram

**SQL Query:**
```sql
-- Pit stop distribution (under 60 seconds)
SELECT milliseconds
FROM public.pit_stops
WHERE milliseconds < 60000;
```

**Configuration Steps:**
1.  In the chart builder, set the **Visualization Type** to **Histogram**.
2.  In the **DATA** tab:
    - **X-AXIS**: Select `milliseconds`.
    - You do not need a metric for a histogram.
3.  In the **CUSTOMIZE** tab:
    - Under **Histogram**, you can set the **Number of Bins** (e.g., 30) to control the granularity.
    - Give the chart a title.

---

## 6. Scatter Plot: Qualifying vs. Race Position

**Chart Type:** Scatter Plot

**SQL Query:**
```sql
-- Qualifying vs. Race Position
SELECT q.position AS qualifying_position, r.position AS race_position
FROM public.qualifying q
JOIN public.results r ON r.raceid = q.raceid AND r.driverid = q.driverid
WHERE q.position IS NOT NULL AND r.position IS NOT NULL;
```

**Configuration Steps:**
1.  In the chart builder, set the **Visualization Type** to **Scatter Plot**.
2.  In the **DATA** tab:
    - **X-AXIS**: Select `qualifying_position`.
    - **Y-AXIS**: Select `race_position`.
    - **SERIES**: You can leave this empty for a simple scatter plot.
3.  In the **CUSTOMIZE** tab, give the chart a title.

---
---
# Advanced Visualizations

---

## 7. Geo Map: F1 Circuits Worldwide

**Chart Type:** Map

**SQL Query:**
```sql
-- Map of all F1 circuits worldwide
SELECT
  c.name AS circuit_name,
  c.location,
  c.country,
  c.lat,
  c.lng,
  COUNT(r.raceid) AS total_races
FROM public.circuits c
LEFT JOIN public.races r
  ON r.circuitid = c.circuitid
WHERE c.lat IS NOT NULL AND c.lng IS NOT NULL
GROUP BY c.circuitid, c.name, c.location, c.country, c.lat, c.lng
ORDER BY total_races DESC;
```

**Configuration Steps:**
1.  In the chart builder, set the **Visualization Type** to **Map**.
2.  In the **DATA** tab:
    - **Longitude**: Select `lng`.
    - **Latitude**: Select `lat`.
    - **GROUP BY**: Select `circuit_name`.
    - **METRICS**: Select `total_races` with a `SUM` aggregator. This will control the point size.
3.  In the **CUSTOMIZE** tab, give the chart a title.

---

## 8. Heatmap: Constructor Performance by Year

**Chart Type:** Heatmap

**SQL Query:**
```sql
-- Constructor performance by year (2010+)
SELECT
    c.name AS constructor,
    ra.year,
    SUM(r.points) AS total_points
FROM public.results r
JOIN public.constructors c ON c.constructorid = r.constructorid
JOIN public.races ra ON ra.raceid = r.raceid
WHERE ra.year >= 2010
GROUP BY c.name, ra.year
HAVING SUM(r.points) > 0
ORDER BY ra.year, total_points DESC;
```

**Configuration Steps:**
1.  In the chart builder, set the **Visualization Type** to **Heatmap**.
2.  In the **DATA** tab:
    - **X-AXIS**: Select `year`.
    - **Y-AXIS**: Select `constructor`.
    - **METRIC**: Select `total_points` with a `SUM` aggregator.
3.  In the **CUSTOMIZE** tab, choose a color scheme and give the chart a title.

---

## 9. Sunburst Chart: Constructor & Driver Hierarchy

**Chart Type:** Sunburst Chart

**SQL Query:**
```sql
-- Hierarchy: Constructor -> Driver -> Season Points
SELECT
    c.name AS constructor,
    d.forename || ' ' || d.surname AS driver,
    ra.year AS season,
    SUM(r.points) AS total_points
FROM public.results r
JOIN public.drivers d ON d.driverid = r.driverid
JOIN public.constructors c ON c.constructorid = r.constructorid
JOIN public.races ra ON ra.raceid = r.raceid
WHERE ra.year >= 2015 AND r.points > 0
GROUP BY c.name, d.driverid, driver, ra.year
ORDER BY ra.year DESC, total_points DESC;
```

**Configuration Steps:**
1.  In the chart builder, set the **Visualization Type** to **Sunburst Chart**.
2.  In the **DATA** tab:
    - **HIERARCHY**: Select the columns in order of the hierarchy. Start with `constructor`, then add `driver`, then `season`.
    - **METRICS**: Select `total_points` with a `SUM` aggregator.
3.  In the **CUSTOMIZE** tab, give the chart a title.

---

## 10. Treemap: Constructor Point Contribution

**Chart Type:** Treemap

**SQL Query:**
```sql
-- Constructor contribution to total F1 points (2010+)
SELECT
    c.name AS constructor,
    SUM(r.points) AS total_points
FROM public.results r
JOIN public.constructors c ON c.constructorid = r.constructorid
JOIN public.races ra ON ra.raceid = r.raceid
WHERE ra.year >= 2010
GROUP BY c.name
HAVING SUM(r.points) > 100
ORDER BY total_points DESC;
```

**Configuration Steps:**
1.  In the chart builder, set the **Visualization Type** to **Treemap**.
2.  In the **DATA** tab:
    - **HIERARCHY**: Select `constructor`.
    - **METRIC**: Select `total_points` with a `SUM` aggregator.
3.  In the **CUSTOMIZE** tab, give the chart a title.

---

## 11. Word Cloud: Most Frequent Circuits

**Chart Type:** Word Cloud

**SQL Query:**
```sql
-- Most frequent circuits (by number of races)
SELECT
    c.name AS circuit_name,
    COUNT(r.raceid) AS race_count
FROM public.circuits c
JOIN public.races r ON r.circuitid = c.circuitid
GROUP BY c.name
ORDER BY race_count DESC;
```

**Configuration Steps:**
1.  In the chart builder, set the **Visualization Type** to **Word Cloud**.
2.  In the **DATA** tab:
    - **SERIES**: Select `circuit_name`.
    - **METRIC**: Select `race_count` with a `SUM` aggregator.
3.  In the **CUSTOMIZE** tab, give the chart a title.

---

## 12. Data Engineering: DB vs. CSV Comparison

**Chart Type:** Mixed Chart (Line Chart)

**SQL Query for CSV Export:**
```sql
SELECT
    ra.year,
    ra.round,
    ra.date,
    COUNT(r.resultid) AS total_results
FROM public.races ra
LEFT JOIN public.results r ON r.raceid = ra.raceid
WHERE ra.year >= 2020
GROUP BY ra.year, ra.round, ra.date
ORDER BY ra.date;
```

**Configuration Steps:**

1.  **Export CSV from Superset SQL Lab:**
    *   Go to **SQL Lab**.
    *   Paste and run the "SQL Query for CSV Export" above.
    *   Click **"Download as CSV"** and save the file as `results_growth.csv` in your project's `exports` directory (e.g., `C:\Users\tima\Velocity-Analytics-Ltd\exports\results_growth.csv`).
2.  **Load CSV into Database using Python Script:**
    *   Open your terminal in the project directory
    *   Run the Python script I created for you: `py load_csv_to_db.py`
    *   This will create a new table named `results_growth_csv` in your PostgreSQL database.
3.  **Add New Table as Dataset in Superset:**
    *   Go to **Data > Datasets**.
    *   Click the blue **"+ Dataset"** button.
    *   Select your **DATABASE** and **SCHEMA (`public`)**.
    *   For **TABLE**, select the newly created **`results_growth_csv`** table from the dropdown.
    *   Click **"Add"**.
4.  **Create Mixed Chart:**
    *   Go to **Charts > + Chart**.
    *   For **Dataset**, select your original **`results`** (physical) dataset.
    *   For **Visualization Type**, choose **"Mixed Chart"**.
    *   **Configure First Line (from DB - `results` dataset):**
        *   **Query Mode**: `Aggregate`
        *   **Time Column**: `date`
        *   **Metric**: `COUNT(resultid)` (or `total_results` if available)
        *   **Chart Type**: `Line`
    *   **Configure Second Line (from CSV - `results_growth_csv` dataset):**
        *   Look for an option to **"+ Add Metric"** or **"+ Add Layer"** within the Mixed Chart configuration.
        *   For this new metric/layer, select the **`results_growth_csv`** dataset.
        *   **Time Column**: `date`
        *   **Metric**: `COUNT(resultid)` (or `total_results` from the CSV dataset)
        *   **Chart Type**: `Line`
    *   Give the chart a clear title (e.g., "Results Growth: DB vs. CSV Comparison").
    *   Save the chart and add it to a dashboard.

---