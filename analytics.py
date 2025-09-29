#!/usr/bin/env python3
"""F1 Data Analytics - Assignment 2"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import plotly.express as px
from connection import F1DatabaseConnector

# Настройки
plt.style.use('default')
sns.set_palette("husl")
os.makedirs('charts', exist_ok=True)
os.makedirs('exports', exist_ok=True)

class F1Analytics:
    def __init__(self):
        self.connector = F1DatabaseConnector()
        self.connector.connect()

    def query(self, sql):
        cursor = self.connector.connection.cursor()
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(data, columns=columns)

    def create_visualizations(self):
        # 1. Pie chart - Top 10 drivers by podiums
        df = self.query("""
            SELECT d.forename || ' ' || d.surname AS driver, COUNT(*) AS podiums
            FROM results r JOIN drivers d ON d.driverid = r.driverid
            WHERE r.position IN (1,2,3) GROUP BY driver ORDER BY podiums DESC LIMIT 10
        """)
        plt.figure(figsize=(10, 8))
        plt.pie(df['podiums'], labels=df['driver'], autopct='%1.1f%%', startangle=90)
        plt.title('Top 10 Drivers by Podium Finishes')
        plt.axis('equal')
        plt.savefig('charts/01_podiums_pie_chart.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 2. Bar chart - Top 10 drivers by career points
        df = self.query("""
            SELECT d.forename || ' ' || d.surname AS driver, SUM(r.points) AS total_points
            FROM results r JOIN drivers d ON d.driverid = r.driverid
            GROUP BY driver ORDER BY total_points DESC LIMIT 10
        """)
        plt.figure(figsize=(12, 6))
        plt.bar(range(len(df)), df['total_points'], color=plt.cm.viridis(np.linspace(0, 1, len(df))))
        plt.title('Top 10 Drivers by Career Points')
        plt.xlabel('Driver')
        plt.ylabel('Total Points')
        plt.xticks(range(len(df)), df['driver'], rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('charts/02_points_bar_chart.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 3. Horizontal bar chart - Constructor performance
        df = self.query("""
            SELECT c.name AS constructor, ROUND(AVG(r.position)::numeric, 2) AS avg_finish
            FROM results r JOIN races ra ON ra.raceid = r.raceid
            JOIN constructors c ON c.constructorid = r.constructorid
            WHERE ra.year >= 2010 AND r.position IS NOT NULL
            GROUP BY constructor ORDER BY avg_finish ASC LIMIT 15
        """)
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(df)), df['avg_finish'], color=plt.cm.RdYlGn_r(np.linspace(0, 1, len(df))))
        plt.title('Average Finishing Position by Constructor (2010+)')
        plt.xlabel('Average Position')
        plt.ylabel('Constructor')
        plt.yticks(range(len(df)), df['constructor'])
        plt.tight_layout()
        plt.savefig('charts/03_constructors_horizontal_bar.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 4. Line chart - DNFs by year
        df = self.query("""
            SELECT ra.year, COUNT(*) AS dnfs FROM results r
            JOIN races ra ON ra.raceid = r.raceid JOIN status s ON s.statusid = r.statusid
            WHERE s.status <> 'Finished' GROUP BY ra.year ORDER BY ra.year
        """)
        plt.figure(figsize=(12, 6))
        plt.plot(df['year'], df['dnfs'], marker='o', linewidth=2)
        plt.title('DNFs Trend Over Years')
        plt.xlabel('Year')
        plt.ylabel('Number of DNFs')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('charts/04_dnfs_line_chart.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 5. Histogram - Pit stop times
        df = self.query("""
            SELECT ps.milliseconds FROM pit_stops ps JOIN races ra ON ra.raceid = ps.raceid
            WHERE ra.year >= 2010 AND ps.milliseconds < 10000 AND ps.milliseconds > 1000
        """)
        plt.figure(figsize=(10, 6))
        plt.hist(df['milliseconds'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Distribution of Pit Stop Times (2010+)')
        plt.xlabel('Pit Stop Duration (ms)')
        plt.ylabel('Frequency')
        plt.axvline(df['milliseconds'].mean(), color='red', linestyle='--', label=f'Avg: {df["milliseconds"].mean():.0f}ms')
        plt.legend()
        plt.tight_layout()
        plt.savefig('charts/05_pitstops_histogram.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 6. Scatter plot - Qualifying vs Race
        df = self.query("""
            SELECT q.position as quali_pos, r.position as race_pos
            FROM qualifying q JOIN results r ON r.raceid = q.raceid AND r.driverid = q.driverid
            JOIN races ra ON ra.raceid = q.raceid
            WHERE q.position IS NOT NULL AND r.position IS NOT NULL AND ra.year >= 2020
            LIMIT 500
        """)
        plt.figure(figsize=(10, 8))
        plt.scatter(df['quali_pos'], df['race_pos'], alpha=0.6, s=50)
        plt.title('Qualifying vs Race Position (2020+)')
        plt.xlabel('Qualifying Position')
        plt.ylabel('Race Position')
        plt.plot([1, 20], [1, 20], 'k--', alpha=0.5, label='Perfect correlation')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('charts/06_qualifying_race_scatter.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_plotly_slider(self):
        """Plotly с временным ползунком - Top drivers points evolution"""
        df = self.query("""
            SELECT ra.year, d.forename || ' ' || d.surname AS driver, SUM(r.points) AS season_points
            FROM results r JOIN races ra ON ra.raceid = r.raceid
            JOIN drivers d ON d.driverid = r.driverid
            GROUP BY ra.year, driver ORDER BY ra.year, season_points DESC
        """)

        # Для каждого года берем топ-8 пилотов по очкам в том сезоне
        df_top = df.groupby('year').head(8)
        
        fig = px.bar(df_top, x='driver', y='season_points', color='driver',
                    animation_frame='year', animation_group='driver',
                    title='Top F1 Drivers Points by Season',
                    labels={'season_points': 'Points', 'driver': 'Driver'},
                    range_y=[0, df_top['season_points'].max() + 10])

        fig.update_layout(showlegend=False, height=600, width=1000, xaxis_tickangle=-45)
        fig.show()

    def close(self):
        if self.connector:
            self.connector.disconnect()

def main():
    analytics = F1Analytics()

    # Create all visualizations
    analytics.create_visualizations()

    # Create Plotly interactive chart
    analytics.create_plotly_slider()

    analytics.close()

if __name__ == "__main__":
    main()