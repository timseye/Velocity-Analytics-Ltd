# Assignment #3 - Action Plan (2 Days)

## ✅ Already Done
- [x] Apache Superset installed (Docker)
- [x] PostgreSQL F1 database connected
- [x] 6 visualizations from Assignment #2 (can reuse in Superset)
- [x] Dashboard screenshot exists

## 🎯 Day 1 (Today) - Priority Tasks

### Morning (3-4 hours)
- [ ] **Task 2: Auto-refresh script (10 pts)** - CRITICAL
  - [x] Created `auto_insert.py` script
  - [ ] Test: `python auto_insert.py`
  - [ ] Verify data is inserting into DB
  - [ ] In Superset: set Auto Refresh to 10 seconds on dashboard

- [ ] **Task 4: Recreate 6 charts (10 pts)** - HIGH PRIORITY
  - [ ] Pie chart: Constructor podiums (last 10 years)
  - [ ] Bar chart: Constructor points (last 5 years)
  - [ ] Horizontal bar: Constructor podiums
  - [ ] Line chart: DNF trends by year
  - [ ] Histogram: Pit stop durations
  - [ ] Scatter: Qualifying vs Race position
  - SQL queries already exist in `queries.sql`!

### Afternoon (3-4 hours)
- [ ] **Task 3: Dashboard Design (3 pts)**
  - [ ] Create Dashboard #1: "Drivers Performance"
  - [ ] Create Dashboard #2: "Constructors Analysis"
  - [ ] Apply consistent styling, colors, titles

- [ ] **Task 11: Filters (7 pts)**
  - [ ] Add global filters: Year, Constructor, Driver
  - [ ] Enable cross-filtering between charts
  - [ ] Test drill-down on one chart

### Evening (2 hours)
- [ ] **Task 7: Sunburst (7 pts)**
  - [ ] Hierarchy: Constructor → Driver → Season Points
  - [ ] SQL: `SELECT c.name, d.surname, ra.year, SUM(r.points)`

- [ ] **Task 8: Treemap (7 pts)**  
  - [ ] Categories: Constructor contribution to total points
  - [ ] SQL: Similar to Sunburst

---

## 🎯 Day 2 (Tomorrow) - Complete Remaining

### Morning (3-4 hours)
- [ ] **Task 5: Geo Visualization (8 pts)**
  - [ ] Check if `circuits` table has lat/lng
  - [ ] Build map: Circuit locations worldwide
  - [ ] Or: Heatmap of races per region

- [ ] **Task 6: Heatmap (7 pts)**
  - [ ] SQL: Constructor × Year performance
  - [ ] Or: Driver × Circuit performance

- [ ] **Task 9: Word Cloud (7 pts)**
  - [ ] Most frequent: Circuit names
  - [ ] Or: Constructor names by race count

### Afternoon (3-4 hours)
- [ ] **Task 12: Metrics (7 pts)**
  - [ ] Dataset → Metrics → Add:
    - AVG points per driver
    - MEDIAN points
    - Growth rate (year over year)
  - [ ] Show in table: median vs average

- [ ] **Task 13: Calculated Columns (7 pts)**
  - [ ] Normalize points to [0,1] range
  - [ ] Formula: `(x - min) / (max - min)`

- [ ] **Task 14: Categorization (8 pts)**
  - [ ] Create categories for points:
    - "Low" (0-50), "Medium" (51-200), "High" (201-400), "Elite" (400+)
  - [ ] Use CASE WHEN in Calculated Column

### Evening (1-2 hours)
- [ ] **Task 10: Data Engineering (8 pts)**
  - [ ] Export one table to CSV (e.g., `results.csv`)
  - [ ] Import CSV into Superset
  - [ ] Create chart with 2 lines: DB vs CSV
  - [ ] Run `auto_insert.py` to show divergence

- [ ] **Task 15: Export Dashboard (4 pts)**
  - [ ] Export both dashboards as JSON
  - [ ] Save to repository
  - [ ] Update README.md

---

## 🚀 Quick Start Commands

### 1. Check database structure:
```powershell
python check_db.py
```

### 2. Start auto-insert script:
```powershell
python auto_insert.py
```

### 3. Start Superset:
```powershell
docker compose -f "C:\Users\tima\superset\docker-compose-image-tag.yml" up -d
```

### 4. Access Superset:
- URL: http://localhost:8088
- Connect to PostgreSQL using SQLAlchemy URI from .env

---

## 💡 SQL Queries Ready to Use

All queries from `queries.sql` can be reused:
- Q1: Top drivers by points ✅
- Q2: Constructor avg finish ✅  
- Q5: DNFs per season ✅
- Q6: Pit stop durations ✅
- Q9: Most podiums ✅

Just paste into Superset SQL Lab!

---

## ⏰ Time Estimate
- **Day 1**: 8-9 hours → Complete ~50 points
- **Day 2**: 8-9 hours → Complete remaining ~50 points
- **Total**: 100 points achievable in 2 days!

---

## 📝 Notes
- Focus on high-point tasks first (10, 8, 7 pts)
- Screenshots: Take during defense, not for GitHub
- Defense: Show `auto_insert.py` running + dashboard updating live
- Remember: No penalty for late submission until Week 6!
