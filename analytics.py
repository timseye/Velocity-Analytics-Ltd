#!/usr/bin/env python3
"""F1 Data Analytics - Assignment 2: Visualizations, Plotly, Excel Export"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import warnings
from connection import F1DatabaseConnector
warnings.filterwarnings('ignore')

# Настройки для matplotlib
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300

# Создание необходимых папок
os.makedirs('charts', exist_ok=True)
os.makedirs('exports', exist_ok=True)

class F1Analytics:
    def __init__(self):
        """Инициализация подключения к БД"""
        self.connector = F1DatabaseConnector()
        if not self.connector.connect():
            raise RuntimeError("Failed to connect to database")
        print("✅ Подключение к базе данных F1 установлено")
    
    def execute_query(self, query, query_name="Query"):
        """Выполнение SQL запроса и возврат DataFrame"""
        try:
            cursor = self.connector.connection.cursor()
            cursor.execute(query)
            
            # Получаем названия колонок
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Получаем данные
            data = cursor.fetchall()
            cursor.close()
            
            # Создаем DataFrame
            df = pd.DataFrame(data, columns=columns)
            print(f"📊 {query_name}: получено {len(df)} строк")
            return df
        except Exception as e:
            print(f"❌ Ошибка в {query_name}: {e}")
            return pd.DataFrame()
    
    def create_pie_chart(self):
        """1. Pie chart - Топ-10 пилотов по подиумам (Q9 модифицированный)"""
        query = """
        SELECT d.forename || ' ' || d.surname AS driver, COUNT(*) AS podiums
        FROM results r
        JOIN drivers d ON d.driverid = r.driverid
        WHERE r.position IN (1,2,3)
        GROUP BY d.driverid, driver
        ORDER BY podiums DESC
        LIMIT 10;
        """
        
        df = self.execute_query(query, "Pie Chart - Top 10 Podiums")
        if df.empty:
            return
        
        plt.figure(figsize=(12, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(df)))
        
        wedges, texts, autotexts = plt.pie(df['podiums'], labels=df['driver'], 
                                          autopct='%1.1f%%', colors=colors, 
                                          startangle=90, textprops={'fontsize': 10})
        
        # Улучшаем читаемость
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.title('Distribution of Podium Finishes - Top 10 F1 Drivers', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.axis('equal')
        
        plt.tight_layout()
        plt.savefig('charts/01_podiums_pie_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        total_podiums = df['podiums'].sum()
        print(f"📈 Создан pie chart: распределение подиумов среди топ-10 пилотов ({len(df)} пилотов)")
        print(f"   Показывает: {total_podiums} подиумов распределены между лучшими пилотами")
    
    def create_bar_chart(self):
        """2. Bar chart - Топ-10 пилотов по очкам (Q1)"""
        query = """
        SELECT d.driverid, d.forename || ' ' || d.surname AS driver, SUM(r.points) AS total_points
        FROM results r
        JOIN drivers d ON d.driverid = r.driverid
        GROUP BY d.driverid, driver
        ORDER BY total_points DESC
        LIMIT 10;
        """
        
        df = self.execute_query(query, "Bar Chart - Top 10 Points")
        if df.empty:
            return
        
        plt.figure(figsize=(14, 8))
        bars = plt.bar(range(len(df)), df['total_points'], 
                      color=plt.cm.viridis(np.linspace(0, 1, len(df))))
        
        plt.title('Career Points - Top 10 F1 Drivers', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Driver', fontsize=12)
        plt.ylabel('Total Career Points', fontsize=12)
        plt.xticks(range(len(df)), df['driver'], rotation=45, ha='right')
        
        # Добавляем значения на столбцы
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 10,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10)
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig('charts/02_points_bar_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        max_points = df['total_points'].max()
        print(f"📈 Создан bar chart: карьерные очки топ-10 пилотов ({len(df)} пилотов)")
        print(f"   Показывает: лидер набрал {max_points} очков за карьеру")
    
    def create_horizontal_bar_chart(self):
        """3. Horizontal bar chart - Средние финиши конструкторов (Q2)"""
        query = """
        SELECT c.constructorid, c.name AS constructor, ROUND(AVG(r.position)::numeric, 2) AS avg_finish
        FROM results r
        JOIN races ra ON ra.raceid = r.raceid
        JOIN constructors c ON c.constructorid = r.constructorid
        WHERE ra.year >= 2010 AND r.position IS NOT NULL
        GROUP BY c.constructorid, constructor
        ORDER BY avg_finish ASC
        LIMIT 15;
        """
        
        df = self.execute_query(query, "Horizontal Bar - Constructor Performance")
        if df.empty:
            return
        
        plt.figure(figsize=(12, 10))
        bars = plt.barh(range(len(df)), df['avg_finish'], 
                       color=plt.cm.RdYlGn_r(np.linspace(0, 1, len(df))))
        
        plt.title('Average Finishing Position by Constructor (2010+)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Average Finishing Position (lower is better)', fontsize=12)
        plt.ylabel('Constructor', fontsize=12)
        plt.yticks(range(len(df)), df['constructor'])
        
        # Добавляем значения
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                    f'{width}', ha='left', va='center', fontsize=10)
        
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.savefig('charts/03_constructors_horizontal_bar.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        best_avg = df['avg_finish'].min()
        print(f"📈 Создан horizontal bar chart: средние позиции финиша конструкторов ({len(df)} команд)")
        print(f"   Показывает: лучшая команда финиширует в среднем на {best_avg} позиции")
    
    def create_line_chart(self):
        """4. Line chart - DNFs по годам (Q5)"""
        query = """
        SELECT ra.year, COUNT(*) AS dnfs
        FROM results r
        JOIN races ra ON ra.raceid = r.raceid
        JOIN status s ON s.statusid = r.statusid
        WHERE s.status <> 'Finished'
        GROUP BY ra.year
        ORDER BY ra.year;
        """
        
        df = self.execute_query(query, "Line Chart - DNFs by Year")
        if df.empty:
            return
        
        plt.figure(figsize=(14, 8))
        plt.plot(df['year'], df['dnfs'], marker='o', linewidth=3, markersize=6, 
                color='darkred', markerfacecolor='red')
        
        plt.title('DNFs (Did Not Finish) Trend Over Years in Formula 1', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Number of DNFs', fontsize=12)
        
        # Добавляем среднее значение
        avg_dnfs = df['dnfs'].mean()
        plt.axhline(y=avg_dnfs, color='blue', linestyle='--', alpha=0.7, 
                   label=f'Average: {avg_dnfs:.0f} DNFs')
        
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('charts/04_dnfs_line_chart.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        max_dnfs = df['dnfs'].max()
        year_max = df.loc[df['dnfs'].idxmax(), 'year']
        print(f"📈 Создан line chart: динамика DNFs по годам ({len(df)} лет)")
        print(f"   Показывает: пик сходов был в {year_max} году ({max_dnfs} DNFs)")
    
    def create_histogram(self):
        """5. Histogram - Распределение времени пит-стопов (Q6 модифицированный)"""
        query = """
        SELECT ps.milliseconds
        FROM pit_stops ps
        JOIN races ra ON ra.raceid = ps.raceid
        WHERE ra.year >= 2010 AND ps.milliseconds < 10000 AND ps.milliseconds > 1000;
        """
        
        df = self.execute_query(query, "Histogram - Pit Stop Times")
        if df.empty:
            return
        
        plt.figure(figsize=(12, 8))
        n, bins, patches = plt.hist(df['milliseconds'], bins=50, alpha=0.7, 
                                   color='skyblue', edgecolor='black')
        
        plt.title('Distribution of Pit Stop Times in Formula 1 (2010+)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Pit Stop Duration (milliseconds)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        
        # Добавляем статистику
        mean_time = df['milliseconds'].mean()
        median_time = df['milliseconds'].median()
        plt.axvline(mean_time, color='red', linestyle='--', linewidth=2, 
                   label=f'Average: {mean_time:.0f}ms')
        plt.axvline(median_time, color='green', linestyle='--', linewidth=2,
                   label=f'Median: {median_time:.0f}ms')
        
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig('charts/05_pitstops_histogram.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Создан histogram: распределение времени пит-стопов ({len(df)} пит-стопов)")
        print(f"   Показывает: среднее время {mean_time:.0f}ms, медиана {median_time:.0f}ms")
    
    def create_scatter_plot(self):
        """6. Scatter plot - Квалификация vs Гонка (Q4 модифицированный)"""
        query = """
        SELECT d.forename || ' ' || d.surname AS driver,
               q.position as quali_pos,
               r.position as race_pos,
               (r.position - q.position) AS position_delta
        FROM qualifying q
        JOIN results r ON r.raceid = q.raceid AND r.driverid = q.driverid
        JOIN drivers d ON d.driverid = q.driverid
        JOIN races ra ON ra.raceid = q.raceid
        WHERE q.position IS NOT NULL AND r.position IS NOT NULL
          AND ra.year >= 2020 AND q.position <= 20 AND r.position <= 20
        LIMIT 500;
        """
        
        df = self.execute_query(query, "Scatter Plot - Qualifying vs Race Performance")
        if df.empty:
            return
        
        plt.figure(figsize=(12, 10))
        scatter = plt.scatter(df['quali_pos'], df['race_pos'], 
                            alpha=0.6, s=50, c=df['position_delta'], 
                            cmap='RdYlBu_r', edgecolors='black', linewidth=0.5)
        
        plt.title('Qualifying vs Race Position in Formula 1 (2020+)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Qualifying Position', fontsize=12)
        plt.ylabel('Race Finishing Position', fontsize=12)
        
        # Диагональная линия (идеальное соотношение)
        plt.plot([1, 20], [1, 20], 'k--', alpha=0.5, linewidth=2,
                label='Perfect correlation (no position change)')
        
        # Цветовая шкала
        cbar = plt.colorbar(scatter)
        cbar.set_label('Position Change (+ = lost positions, - = gained)', fontsize=10)
        
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xlim(0, 21)
        plt.ylim(0, 21)
        plt.tight_layout()
        plt.savefig('charts/06_qualifying_race_scatter.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        avg_delta = df['position_delta'].mean()
        print(f"📈 Создан scatter plot: квалификация vs гонка ({len(df)} результатов)")
        print(f"   Показывает: в среднем пилоты изменяют позицию на {avg_delta:.2f} места")
    
    def create_plotly_time_slider(self):
        """7. Plotly с временным ползунком - DNFs по годам с анимацией"""
        query = """
        SELECT ra.year, COUNT(*) AS dnfs
        FROM results r
        JOIN races ra ON ra.raceid = r.raceid
        JOIN status s ON s.statusid = r.statusid
        WHERE s.status <> 'Finished' AND ra.year >= 1990
        GROUP BY ra.year
        ORDER BY ra.year;
        """
        
        df = self.execute_query(query, "Plotly Animation - DNFs Evolution")
        if df.empty:
            return
        
        # Создаем интерактивный линейный график с анимацией
        fig = px.line(df, x='year', y='dnfs', 
                     animation_frame='year',
                     title='🏎️ Evolution of DNFs (Did Not Finish) Over Time - Interactive Timeline',
                     labels={'year': 'Season Year', 'dnfs': 'Number of DNFs'},
                     range_y=[0, df['dnfs'].max() * 1.1])
        
        # Настройки анимации и стиля
        fig.update_layout(
            title_font_size=18,
            xaxis_title_font_size=14,
            yaxis_title_font_size=14,
            width=1200,
            height=700,
            showlegend=False
        )
        
        # Улучшаем анимацию
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 100
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 50
        
        # Показываем график (откроется в браузере)
        fig.show()
        
        print(f"🎬 Создан Plotly график с временным ползунком: эволюция DNFs ({len(df)} лет)")
        print(f"   Показывает: интерактивную анимацию изменения количества сходов")
        print(f"   📱 График открыт в браузере - используйте кнопки воспроизведения!")
        
        # Дополнительный интерактивный график - пит-стопы по годам  
        query2 = """
        SELECT ra.year, 
               ROUND(AVG(ps.milliseconds)::numeric, 0) as avg_pitstop_ms,
               COUNT(ps.stop) as total_pitstops
        FROM pit_stops ps
        JOIN races ra ON ra.raceid = ps.raceid
        WHERE ra.year >= 2000
        GROUP BY ra.year
        ORDER BY ra.year;
        """
        
        df2 = self.execute_query(query2, "Plotly Animation - Pitstop Evolution")
        if not df2.empty:
            fig2 = px.scatter(df2, x='year', y='avg_pitstop_ms',
                            size='total_pitstops',
                            animation_frame='year',
                            title='⏱️ Pit Stop Times Evolution - Interactive Timeline',
                            labels={'year': 'Season Year', 
                                   'avg_pitstop_ms': 'Average Pit Stop Time (ms)',
                                   'total_pitstops': 'Total Pit Stops'})
            
            fig2.update_layout(
                title_font_size=18,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                width=1200,
                height=700
            )
            
            # Улучшаем анимацию
            fig2.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 150
            fig2.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 75
            
            fig2.show()
            
            print(f"🎬 Создан второй Plotly график: эволюция времени пит-стопов ({len(df2)} лет)")
            print(f"   Показывает: как менялось время пит-стопов и их количество по годам")
    
    def close(self):
        """Закрытие подключения к БД"""
        if self.connector:
            self.connector.disconnect()

def main():
    print("🏎️  F1 DATA ANALYTICS - ASSIGNMENT 2")
    print("=" * 50)
    
    try:
        # Создание экземпляра класса
        analytics = F1Analytics()
        
        # Создаем все 6 визуализаций
        print("\n📊 Создание визуализаций...")
        analytics.create_pie_chart()
        print()
        analytics.create_bar_chart()
        print()
        analytics.create_horizontal_bar_chart()
        print()
        analytics.create_line_chart()
        print()
        analytics.create_histogram()
        print()
        analytics.create_scatter_plot()
        print()
        
        # Plotly интерактивные графики с временным ползунком
        print("\n🎬 Создание интерактивных Plotly графиков...")
        analytics.create_plotly_time_slider()
        
        chart_files = [f for f in os.listdir('charts') if f.endswith('.png')]
        print(f"\n✅ Все графики созданы успешно!")
        print(f"📁 Сохранено в папку 'charts/': {len(chart_files)} файлов")
        
        for chart in sorted(chart_files):
            print(f"   📊 {chart}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    finally:
        if 'analytics' in locals():
            analytics.close()

if __name__ == "__main__":
    main()