#!/usr/bin/env python3
"""F1 Analytics: Visualizations and Export to Excel."""

import pandas as pd
import plotly.express as px
from connection import F1DatabaseConnector
import os

# Directories
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "charts")
EXPORTS_DIR = os.path.join(os.path.dirname(__file__), "exports")

def get_top_drivers_by_season(connector):
    """Get top 10 drivers by points per season, excluding those with 0 points."""
    query = """
    SELECT ra.year, d.forename || ' ' || d.surname AS driver, SUM(r.points) AS total_points
    FROM results r
    JOIN drivers d ON d.driverid = r.driverid
    JOIN races ra ON ra.raceid = r.raceid
    WHERE r.points > 0
    GROUP BY ra.year, d.driverid, driver
    ORDER BY ra.year, total_points DESC;
    """
    df = pd.read_sql_query(query, connector.connection)
    # For each year, keep only top 10
    df_top = df.groupby('year').head(10).reset_index(drop=True)
    return df_top

def create_plotly_animation(df):
    """Create interactive Plotly chart with time slider for top drivers by season."""
    fig = px.bar(df, x='driver', y='total_points', animation_frame='year',
                 title='Top 10 F1 Drivers by Points per Season',
                 labels={'total_points': 'Total Points', 'driver': 'Driver'},
                 color='driver')
    fig.update_layout(xaxis_tickangle=-45)
    # Save to HTML for viewing
    os.makedirs(CHARTS_DIR, exist_ok=True)
    fig.write_html(os.path.join(CHARTS_DIR, 'top_drivers_by_season.html'))
    print("Interactive chart saved to charts/top_drivers_by_season.html")
    fig.show()

def main():
    print("F1 Analytics: Visualizations")
    connector = F1DatabaseConnector()
    if not connector.connect():
        print("Failed to connect to database.")
        return
    try:
        df = get_top_drivers_by_season(connector)
        print(f"Loaded {len(df)} rows of data.")
        print("Created interactive bar chart: Top 10 F1 Drivers by Points per Season (with time slider)")
        print("The chart shows the evolution of top drivers' points across seasons, excluding drivers with 0 points.")
        create_plotly_animation(df)
    finally:
        connector.disconnect()

if __name__ == "__main__":
    main()