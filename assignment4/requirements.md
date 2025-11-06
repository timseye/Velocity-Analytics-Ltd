here i have lectures 6, 7 and 8. and assignment 4.

🔄
Lecture #6
Prometheus setup and data collection: deploying Prometheus with Docker, configuring scrapers, and verifying metrics from local endpoints. 
Why Prometheus if We Already Have BI Systems?
Different Tools for Different Goals
A common question is: why do we need Prometheus if BI systems (Business Intelligence) like Power BI, Tableau, or Qlik already exist? The answer lies in the difference of purpose. BI systems and monitoring systems solve fundamentally different problems. Monitoring is not about business metrics such as revenue, customer count, or average order value — its purpose is to monitor system performance and health, not business outcomes.

BI systems are designed for:

Analyzing business data (sales, finance, marketing indicators)
Preparing reports for management
Long-term analysis and forecasting
Working with aggregated and historical data
Conducting statistical analysis of business performance
Prometheus is used for:

Monitoring infrastructure and services in real time
Tracking the state of servers, databases, containers, and network devices
Setting up alerting systems for failures or overloads
Quick diagnostics and troubleshooting during incidents
Monitoring dynamic microservice architectures, where services appear and disappear automatically
Collecting and storing time-series metrics, enabling trend analysis of system performance
In short: BI systems answer “What is happening with the business?”, Prometheus answers “What is happening with the system right now?”

Key Advantages of Prometheus
1. Reliability and Autonomy

Prometheus is built for reliability — it’s the system you can trust during failures for quick diagnostics, even when other parts of your infrastructure are down.

2. Real-time Operation

Prometheus collects metrics via the HTTP pull model, providing flexible real-time queries and alerts. BI tools usually work with delayed data — from minutes to hours.

3. Multidimensional Data Model

Prometheus stores data as metrics with key-value label pairs, allowing detailed filtering and aggregation by source, HTTP code, method, region, etc.

Advantages of Multidimensional Data
Flexible Aggregation
Prometheus allows any level of query aggregation:

# All requests with status 500
http_requests_total{status="500"}

# All POST requests to a specific endpoint
http_requests_total{method="POST", endpoint="/api/orders"}

# Sum requests grouped by status
sum by (status) (http_requests_total)
Imagine a microservice architecture with 50 services.

Instead of creating 50 separate metrics, you can use one multidimensional metric:

service_response_time{
    service="auth-service",
    version="v2.1",
    region="eu-west",
    pod="auth-service-7d8f9"
}
Then you can easily answer:

What’s the average latency of all versions of auth-service?
Is there a performance difference between regions?
Which pod is the slowest?
Simple Deployment
Prometheus is written in Go and distributed as a single static binary. It’s cross-platform and easy to install — just download and run it, no dependencies required.

Powerful Query Language
PromQL (Prometheus Query Language) enables complex time-series analysis, trend detection, rate calculations, and anomaly identification.
PromQL Basics
PromQL is used to analyze and aggregate time-series data. It allows not only retrieving metric values but also performing calculations, predictions, and anomaly detection.

Instant vectors
Return metric values at a specific moment in time:
node_cpu_seconds_total
node_cpu_seconds_total{mode="idle"} # with filtter
Range vectors
Return metric values over a specific time range, e.g. the last 5 minutes:
http_requests_total[5m]
Rate of Change
Shows the rate of metric growth (e.g. requests per second in the last 5 minutes):
rate(http_requests_total[5m])
In Prometheus, counters only increase, so you must specify a time range — otherwise, the result will be calculated over the entire time period.
10:00 → 1000 requests
10:01 → 1050 requests
10:02 → 1120 requests
rate() automatically calculates: (1120 - 1000) / 120 seconds = 1 request per second

Aggregation by Labels
Allows you to group data and calculate total or average values.

# Total memory usage across all pods of a single service
sum(container_memory_usage_bytes{service="backend"})

# Average latency by region
avg by (region) (http_request_duration_seconds)

# Maximum CPU load per host
max by (instance) (node_cpu_seconds_total)
Mathematical Operations
PromQL supports arithmetic operations on metrics.

# Disk usage percentage
(node_filesystem_size_bytes - node_filesystem_free_bytes)
  / node_filesystem_size_bytes * 100

# Error-to-success request ratio
rate(http_requests_total{status=~"5.."}[5m])
  / rate(http_requests_total[5m]) * 100
Anomaly Detection
You can detect deviations from normal behavior using functions:

# Deviation from the average over the last hour
abs(
  http_request_duration_seconds -
  avg_over_time(http_request_duration_seconds[1h])
) > 0.5
Prediction (Forecasting)
PromQL can perform linear extrapolation to predict future trends:

# Predict when the disk will be full (in 4 hours)
predict_linear(node_filesystem_free_bytes[1h], 4*3600) < 0
Quantiles (Percentiles)
Used to measure value distribution, for example, the 95th percentile of response time:

histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)
Practical Examples
1. SLI (Service Level Indicator) — Request Success Rate

Percentage of successful requests in the last 5 minutes:

sum(rate(http_requests_total{status!~"5.."}[5m]))
/
sum(rate(http_requests_total[5m])) * 100
2. Alert — When SLI Drops Below 99.9%

(
  sum(rate(http_requests_total{status!~"5.."}[5m]))
  /
  sum(rate(http_requests_total[5m]))
) < 0.999
This query can be used in Alertmanager to automatically notify when service quality decreases.

3. Top 5 Slowest Endpoints

topk(5,
  avg by (endpoint) (
    rate(http_request_duration_seconds_sum[5m])
    /
    rate(http_request_duration_seconds_count[5m])
  )
)
Displays the five endpoints with the highest average response time over the last 5 minutes.

4. Predict Memory Exhaustion in 2 Hours

predict_linear(
  node_memory_MemAvailable_bytes[30m],
  2*3600
) < 1024*1024*1024  # less than 1 GB
Helps predict when available memory will drop below 1 GB, allowing you to prevent a potential failure in advance.

5. Anomalous Traffic Spike

rate(http_requests_total[5m])
>
2 * avg_over_time(rate(http_requests_total[5m])[1h:5m])
Shows a sudden traffic surge — when the current request rate is twice the average value over the last hour.

Alternatives to Prometheus
Although Prometheus is the de facto standard in system monitoring, there are several solutions that extend its capabilities in terms of scalability and long-term data storage.

1. VictoriaMetrics

A high-performance and cost-efficient time-series database. It is often used as a long-term storage backend for Prometheus, offering better data compression and query performance (up to 16× faster). Supports both single-node and cluster deployment modes.

2. Thanos

Extends Prometheus with features for long-term storage, high availability, and horizontal scalability. It relies on object storage solutions (such as S3 or GCS) for data retention. However, configuration is more complex since Thanos operates as a distributed system.

3. Grafana Mimir
A modern monitoring solution built on the Cortex/Thanos architecture. Supports both microservices and monolithic deployment modes. It is used when scaling Prometheus and enabling unlimited data retention are required.

Conclusion
Prometheus and BI systems serve fundamentally different purposes:

BI systems are designed for business analytics, strategic planning, and management decision-making.
Prometheus is used for operational monitoring, performance analysis, and infrastructure reliability.
The choice of a Prometheus alternative depends on several factors:

the scale of your infrastructure, budget, data retention requirements, and the team’s technical capacity to maintain and support the system.

FAQ for Assignment 4
1. What tools are required to work with Prometheus?
PostgreSQL или MySQL (do not delete your dataset yet)
Docker и Docker Compose
Python 3.8+
2. Where to start when setting up and launching Prometheus?
Create a docker-compose.yml file in your working directory and insert the following code:
version: '3.8'

services:

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    extra_hosts:
      - "host.docker.internal:host-gateway"
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  prometheus_data:

networks:
  monitoring:
    driver: bridge
Create another file nearby called prometheus.yml and insert the following configuration code:
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'student-monitoring'

scrape_configs:
  # Prometheus
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
3. What should be added to Docker Compose to make MySQL/PostgreSQL Exporter work?
Add the corresponding service to docker-compose.yml. For MySQL: 
  # MySQL Exporter    
  mysql_exporter:
    image: prom/mysqld-exporter:latest
    container_name: mysql_exporter
    ports:
      - "9104:9104"
    command:
      - '--mysqld.address=host:port'
      - '--mysqld.username=usr'
    environment:
      MYSQLD_EXPORTER_PASSWORD: 'pswd'
    networks:
      - monitoring
    restart: unless-stopped
For PostgreSQL:

  # PostgreSQL Exporter
  postgres_exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: postgres_exporter
    ports:
      - "9187:9187"
    environment:
      DATA_SOURCE_NAME: 
      "postgresql://usr:pswd@host:port/postgres?sslmode=disable"
    networks:
      - monitoring
    restart: unless-stopped
Replace the connection details in the environment section:
usr → your username
pswd → your password
host → your database address
For Windows / macOS, use host.docker.internal instead of host.
For Linux (Ubuntu), specify the host IP address.
port → 5432 (PostgreSQL) or 3306 (MySQL), replace if different
Add a job to the prometheus.yml file. For MySQL: 
  # MySQL
  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql_exporter:9104']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'my_mysql_db'
For PostgreSQL:

 # PostgreSQL
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres_exporter:9187']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'my_postgresql_db'
4. What to do if Prometheus cannot see the database or is not receiving metrics from the Exporter?
If you previously worked with Apache Superset in Docker, you can use the same connection parameters (host, port, username, password), since permissions are already configured.
However, if Superset was launched locally and not in a container, there might be access issues, especially on Ubuntu. In this case, follow the steps below.

Allow external connections to the database
MySQL: change bind-address = 0.0.0.0 in the my.cnf or mysqld.cnf file
PostgreSQL: change listen_addresses = '*'  in postgresql.conf and add host all all 0.0.0.0/0 scram-sha-256 to pg_hba.conf
Create a user with external access
MySQL: GRANT ALL PRIVILEGES ON *.* TO 'user'@'%' IDENTIFIED BY 'pass';
PostgreSQL: CREATE USER user WITH PASSWORD 'pass'; GRANT ALL ON DATABASE db TO user; 
Restart the database server
Determine the host IP address
Linux/Mac: hostname -I or ip route get 8.8.8.8 | awk '{print $7}'
Windows: ipconfig 
Use the IP instead of localhost in the connection string
Linux: mysql://user:pass@192.168.X.X:3306/db 
Mac: mysql://user:pass@host.docker.internal:3306/db
Windows: mysql://user:pass@host.docker.internal:3306/db 
Check firewall settings — make sure ports 3306 (MySQL) or 5432 (PostgreSQL) are open
5. What should be added to Docker Compose to make Node Exporter work?
Add the Node Exporter service to docker-compose.yml:
  # Node Exporter
  node_exporter:
    image: prom/node-exporter:latest
    container_name: node_exporter
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    networks:
      - monitoring
    restart: unless-stopped
    # Windows: delete the volumes above and leave only ports
Add a job for Node Exporter in prometheus.yml:
  # Системные метрики
  - job_name: 'node'
    static_configs:
      - targets: ['node_exporter:9100']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'my_laptop'
6. How to properly run the Prometheus stack via Docker Compose?
Start the containers: docker-compose up -d . On the first run, Docker will download the necessary images (it may take 2–5 minutes). On subsequent runs, containers will start instantly.
Check the status of all containers: docker-compose ps. You should see active services: node_exporter, mysql_exporter (or postgres_exporter), prometheus.
7. How to check if Prometheus, Node Exporter, and DB Exporter are working correctly?
Open the Prometheus web interface: http://localhost:9090. In the top menu, select Status → Targets. Make sure all services have the UP status:

prometheus (1/1 up)
mysql (1/1 up) - (or postgresql)
node (1/1 up)
custom_api (1/1 up) - Details in Lectures 7–8
Check database metrics: for MySQL http://localhost:9104/metrics (for PostgeSQL http://localhost:9187/metrics). You should see metrics like:

Check system metrics for Node Exporter: http://localhost:9100/metrics. You should see metrics like:

8. How to view database metrics in the Prometheus interface?
In the Prometheus UI → Click Graph (top menu). You will see the field for PromQL queries.
Try the following queries:
Check if DB is available: pg_up (or mysql_up)
Number of active connections: pg_stat_database_numbackends{datname="your_database_name"} (or mysql_global_status_threads_connected)
Total number of connections: sum(pg_stat_database_numbackends) (or mysql_global_variables_max_connections)
Database size (in bytes, in gigabytes): pg_database_size_bytes{datname="your_database_name"}
Database uptime (in seconds, in hours): time() - pg_postmaster_start_time_seconds (or mysql_global_status_uptime)
Transactions per second: rate(pg_stat_database_xact_commit{datname="your_database_name"}[5m]) (or rate(mysql_global_status_queries[5m]), for slow queries use rate(mysql_global_status_slow_queries[5m]))
Number of tables in the database: count(pg_stat_user_tables_seq_scan) (or sum(mysql_info_schema_table_size_data_length))
Total number of rows in all tables: sum(pg_stat_user_tables_n_live_tup)
9. How to view system metrics in the Prometheus interface?
In the Prometheus UI → Click Graph (top menu). You will see the field for PromQL queries.
Try CPU metrics
1. CPU usage (in %): 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
2. CPU usage by cores: 100 - (rate(node_cpu_seconds_total{mode="idle"}[5m]) * 100)
3. Load average (1 minute): node_load1
4. Load average for 5 and 15 minutes: node_load5, node_load15
Try RAM metrics
Total memory (in GB): node_memory_MemTotal_bytes / 1024 / 1024 / 1024
Available memory (in GB): node_memory_MemAvailable_bytes / 1024 / 1024 / 1024
Used memory (in GB): (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024 / 1024 / 1024
RAM usage (in %): 100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))
Swap usage: 100 * (1 - (node_memory_SwapFree_bytes / node_memory_SwapTotal_bytes))
Try Disk metrics
Disk usage (root FS in %): 100 - ((node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100) 
Free space (in GB): node_filesystem_avail_bytes{mountpoint="/"} / 1024 / 1024 / 1024
Disk I/O - read (bytes per second): rate(node_disk_read_bytes_total[5m])
Disk I/O - write (bytes per second): rate(node_disk_written_bytes_total[5m])
Try Network metrics
Incoming traffic (bytes per second): rate(node_network_receive_bytes_total{device!="lo"}[5m])
Outgoing traffic (bytes per second): rate(node_network_transmit_bytes_total{device!="lo"}[5m]) 
Incoming traffic in Mbit/s: rate(node_network_receive_bytes_total{device!="lo"}[5m]) * 8 / 1000000










Зачем Prometheus, если есть BI-системы?
Разные задачи — разные инструменты
Часто возникает вопрос: зачем нужен Prometheus, если уже существуют BI-системы (Business Intelligence) с готовыми интерфейсами, такие как Power BI, Tableau или Qlik? Ответ заключается в различии самих целей. BI-системы и системы мониторинга решают принципиально разные задачи. Мониторинг не должен включать бизнес-метрики, такие как прибыль, количество клиентов или средний чек. Его назначение — следить за работоспособностью и производительностью систем, а не за показателями бизнеса.

BI-системы предназначены для:

Анализа бизнес-данных: продаж, финансов, маркетинговых показателей
Подготовки аналитических отчётов для руководства
Долгосрочного анализа и прогнозирования
Работы с агрегированными и историческими данными
Проведения статистического анализа бизнес-показателей
Prometheus используется для:

Мониторинга инфраструктуры и сервисов в реальном времени
Отслеживания состояния серверов, баз данных, контейнеров и сетевого оборудования
Настройки системы оповещений (alerting) при сбоях или перегрузках
Быстрой диагностики и устранения проблем во время инцидентов
Мониторинга динамических микросервисных архитектур, где сервисы могут появляться и исчезать автоматически
Сбора и хранения метрик временных рядов (time-series data), что позволяет анализировать тенденции работы систем
Таким образом, BI-системы дают ответ на вопрос «что происходит с бизнесом?»,
а Prometheus — «что происходит с системой прямо сейчас?»

Ключевые преимущества Prometheus
1. Надёжность и автономность
Prometheus спроектирован для надёжности — это система, к которой вы обращаетесь во время сбоев для быстрой диагностики проблем, и на которую можно полагаться, даже когда другие части инфраструктуры не работают.

2. Реальное время
Prometheus собирает метрики с помощью HTTP pull-модели, что обеспечивает гибкие запросы и оповещения в реальном времени. BI-системы обычно работают с данными с задержкой от минут до часов.

3. Многомерная модель данных
Данные Prometheus хранятся в виде метрик с произвольным количеством пар ключ-значение (меток), что позволяет детализировать данные по источникам, HTTP-кодам, методам запросов и другим параметрам.



Преимущества многомерности:
Гибкая агрегация
Prometheus позволяет выполнять запросы в любой форме и глубине детализации:

# Все запросы с кодом 500, независимо от сервера
http_requests_total{status="500"}

# Все POST-запросы на конкретный endpoint
http_requests_total{method="POST", endpoint="/api/orders"}

# Суммирование по всем методам с группировкой по статусу
sum by (status) (http_requests_total)
Представим, что у вас микросервисная архитектура с 50 сервисами.

Вместо создания 50 отдельных метрик можно использовать одну многомерную:

service_response_time{
    service="auth-service",
    version="v2.1",
    region="eu-west",
    pod="auth-service-7d8f9"
}
Теперь можно легко ответить на вопросы:

Какова средняя задержка у всех версий auth-service?
Есть ли разница в производительности между регионами?
Какой pod работает медленнее остальных?
Простота развёртывания
Prometheus написан на Go и распространяется как статически скомпилированный бинарный файл. Это упрощает установку и делает систему кроссплатформенной — достаточно загрузить один исполняемый файл без внешних зависимостей.

Мощный язык запросов
PromQL — встроенный язык запросов Prometheus — позволяет выполнять сложные операции с временными рядами: анализировать тенденции, вычислять скорости изменений метрик и выявлять аномалии в поведении систем.
Основы PromQL
PromQL (Prometheus Query Language) — это язык для анализа и агрегации временных рядов.
Он позволяет не только получать значения метрик, но и выполнять вычисления, прогнозы и выявлять аномалии в работе систем.

Мгновенные векторы (Instant vectors)
Возвращают значение метрики в конкретный момент времени, 
node_cpu_seconds_total
node_cpu_seconds_total{mode="idle"} # с фильтрацией
Диапазонные векторы (Range vectors)
Отображают значения метрики за определённый период времени, например последние 5 минут:
http_requests_total[5m]
Вычисление скорости изменения (rate)
Показывает скорость прироста метрики за заданный интервал. Например: количество запросов в секунду за последние 5 минут:
rate(http_requests_total[5m])
В Prometheus счётчики (counters) только растут, поэтому нужно указывать диапазон, иначе результат будет рассчитан за всё время.
10:00 → 1000 запросов
10:01 → 1050 запросов
10:02 → 1120 запросов
rate() автоматически вычисляет: (1120 - 1000) / 120 секунд = 1 запрос/сек

Агрегация по меткам
Позволяет группировать данные и вычислять суммарные или средние значения.

# Суммарное потребление памяти по всем подам одного сервиса
sum(container_memory_usage_bytes{service="backend"})

# Средняя задержка по регионам
avg by (region) (http_request_duration_seconds)

# Максимальная загрузка CPU по каждому хосту
max by (instance) (node_cpu_seconds_total)
Математические операции
PromQL поддерживает арифметику над метриками.

# Процент использования диска
(node_filesystem_size_bytes - node_filesystem_free_bytes)
  / node_filesystem_size_bytes * 100

# Соотношение ошибок к успешным запросам
rate(http_requests_total{status=~"5.."}[5m])
  / rate(http_requests_total[5m]) * 100
Выявление аномалий
Можно определять отклонения от нормы с помощью функций:

# Отклонение от среднего за последний час
abs(
  http_request_duration_seconds -
  avg_over_time(http_request_duration_seconds[1h])
) > 0.5
Предсказание (прогнозирование)
PromQL умеет выполнять линейную экстраполяцию:

# Предсказать, когда диск заполнится (через 4 часа)
predict_linear(node_filesystem_free_bytes[1h], 4*3600) < 0
Квантили (процентили)
Позволяют измерять распределение значений, например, 95-й процентиль времени ответа:

histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)
Практический примеры:
1. SLI (Service Level Indicator) — успешность запросов

Процент успешных запросов за последние 5 минут:

sum(rate(http_requests_total{status!~"5.."}[5m]))
/
sum(rate(http_requests_total[5m])) * 100
2. Алерт: если SLI упал ниже 99.9%

(
  sum(rate(http_requests_total{status!~"5.."}[5m]))
  /
  sum(rate(http_requests_total[5m]))
) < 0.999
Этот запрос можно использовать в Alertmanager для автоматического уведомления о снижении качества сервиса.

3. Топ-5 самых медленных эндпоинтов

topk(5,
  avg by (endpoint) (
    rate(http_request_duration_seconds_sum[5m])
    /
    rate(http_request_duration_seconds_count[5m])
  )
)
Показывает пять эндпоинтов с наибольшим средним временем ответа за последние 5 минут.

4. Прогноз заполнения памяти через 2 часа

predict_linear(
  node_memory_MemAvailable_bytes[30m],
  2*3600
) < 1024*1024*1024  # меньше 1 GB
Помогает предсказать, когда свободная память опустится ниже 1 ГБ, чтобы предупредить возможный сбой.

5. Аномальный всплеск трафика

rate(http_requests_total[5m])
>
2 * avg_over_time(rate(http_requests_total[5m])[1h:5m])
Показывает резкий рост трафика — если текущий поток запросов вдвое превышает среднее значение за последний час.

Альтернативы Prometheus
Хотя Prometheus является стандартом де-факто в мониторинге, существуют решения, расширяющие его возможности по масштабируемости и хранению данных.

1. VictoriaMetrics

Высокопроизводительная и экономичная база данных временных рядов. Используется как долгосрочное хранилище для Prometheus, обеспечивает лучшее сжатие и скорость обработки запросов (до 16 раз быстрее). Поддерживает развёртывание в режимах single-node и cluster.

2. Thanos

Расширяет Prometheus функциями долгосрочного хранения, высокой доступности и масштабирования. Использует объектное хранилище (S3, GCS). Однако настройка сложнее, так как это распределённая система.

3. Grafana Mimir
Современное решение, основанное на архитектуре Cortex/Thanos. Поддерживает как микросервисный, так и монолитный режимы работы. Применяется при необходимости масштабирования Prometheus и неограниченного хранения данных.

Итог
Prometheus и BI-системы решают принципиально разные задачи:

BI-системы используются для бизнес-аналитики, стратегического планирования и принятия управленческих решений.
Prometheus — для операционного мониторинга, анализа производительности и обеспечения надёжности инфраструктуры.
Выбор альтернативы Prometheus зависит от конкретных факторов: масштаба инфраструктуры, бюджета, требований к хранению данных и возможностей команды по поддержке системы.

FAQ for Assignment 4
1. Какие инструменты необходимы для работы с Prometheus?
PostgreSQL или MySQL (пока не удаляйте свой датасет)
Docker и Docker Compose
Python 3.8+
2. С чего начать настройку и запуск Prometheus?
Создайте файл docker-compose.yml в рабочей директории и вставьте следующий код:
version: '3.8'

services:

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.enable-lifecycle'
    extra_hosts:
      - "host.docker.internal:host-gateway"
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  prometheus_data:

networks:
  monitoring:
    driver: bridge
Создайте рядом файл prometheus.yml и вставьте следующий код конфигурации:
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'student-monitoring'

scrape_configs:
  # Prometheus
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
3. Что нужно добавить в Docker Compose, чтобы заработал MySQL/PostgreSQL Exporter?
Добавьте в docker-compose.yml соответствующий сервис. Если MySQL: 
  # MySQL Exporter    
  mysql_exporter:
    image: prom/mysqld-exporter:latest
    container_name: mysql_exporter
    ports:
      - "9104:9104"
    command:
      - '--mysqld.address=host:port'
      - '--mysqld.username=usr'
    environment:
      MYSQLD_EXPORTER_PASSWORD: 'pswd'
    networks:
      - monitoring
    restart: unless-stopped
для PostgreSQL:

  # PostgreSQL Exporter
  postgres_exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: postgres_exporter
    ports:
      - "9187:9187"
    environment:
      DATA_SOURCE_NAME: 
      "postgresql://usr:pswd@host:port/postgres?sslmode=disable"
    networks:
      - monitoring
    restart: unless-stopped
Замените данные подключения в секции environment:
usr → ваш логин
pswd → ваш пароль
host → адрес базы данных
Для Windows / macOS используйте host.docker.internal вместо host.
Для Linux (Ubuntu) укажите IP-адрес хоста.
port → 5432 (PostgreSQL) или 3306 (MySQL), если отличается — замените
Добавьте job в файл prometheus.yml. Если MySQL: 
  # MySQL
  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql_exporter:9104']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'my_mysql_db'
для PostgreSQL:

 # PostgreSQL
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres_exporter:9187']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'my_postgresql_db'
4. Что делать, если Prometheus не видит базу данных или не получает метрики от Exporter?
Если вы ранее работали с Apache Superset в Docker, можно использовать те же параметры подключения (host, port, username, password), поскольку доступы и права уже настроены.
Однако если Superset запускался локально, а не в контейнере, могут возникнуть проблемы с правами доступа, особенно в Ubuntu. В этом случае выполните следующие шаги.
Разрешите внешние подключения к базе данных
MySQL: изменитеbind-address = 0.0.0.0 в файле my.cnf или mysqld.cnf
PostgreSQL: изменитеlisten_addresses = '*' в файле postgresql.conf и добавьте host all all 0.0.0.0/0 scram-sha-256 в pg_hba.conf 
Создайте пользователя с внешним доступом
MySQL: GRANT ALL PRIVILEGES ON *.* TO 'user'@'%' IDENTIFIED BY 'pass';
PostgreSQL: CREATE USER user WITH PASSWORD 'pass'; GRANT ALL ON DATABASE db TO user; 
Перезапустите сервер базы данных
Определите IP-адрес хоста
Linux/Mac: hostname -I или ip route get 8.8.8.8 | awk '{print $7}'
Windows: ipconfig 
Используйте IP вместо localhost в строке подключения
Linux: mysql://user:pass@192.168.X.X:3306/db 
Mac: mysql://user:pass@host.docker.internal:3306/db
Windows: mysql://user:pass@host.docker.internal:3306/db 
Проверьте настройки брандмауэра (firewall) - разрешите порты 3306 (MySQL) или 5432 (PostgreSQL)
5. Что нужно добавить в Docker Compose, чтобы заработал Node Exporter?
Добавьте в docker-compose.yml сервис Node Exporter:
  # Node Exporter
  node_exporter:
    image: prom/node-exporter:latest
    container_name: node_exporter
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    networks:
      - monitoring
    restart: unless-stopped
    # Windows: удалить volumes выше и оставить только ports
Добавьте job для Node Exporter в prometheus.yml:
  # Системные метрики
  - job_name: 'node'
    static_configs:
      - targets: ['node_exporter:9100']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'my_laptop'
6. Как корректно запустить стек Prometheus через Docker Compose?
Запустите контейнеры: docker-compose up -d . При первом запуске Docker загрузит необходимые образы (это может занять 2–5 минут). При последующих запусках контейнеры стартуют мгновенно.
Проверьте статус всех контейнеров: docker-compose ps. В списке должны быть активные сервисы: node_exporter, mysql_exporter (или postgres_exporter), prometheus.
7. Как проверить, что Prometheus, Node Exporter и DB Exporter работают корректно?
Откройте веб-интерфейс Prometheus: http://localhost:9090. В верхнем меню выберите Status → Targets. Убедитесь, что все сервисы имеют статус UP:

prometheus (1/1 up)
mysql (1/1 up) - (или postgresql)
node (1/1 up)
custom_api (1/1 up) - Подробности в Лекции 7-8
Проверьте метрики базы данных: для MySQL http://localhost:9104/metrics (для PostgeSQL http://localhost:9187/metrics). Вы должны увидеть метрики типа:

Проверьте системные метрики Node Exporter: http://localhost:9100/metrics. Вы должны увидеть метрики типа:

8. Как просмотреть метрики базы данных в интерфейсе Prometheus?
В Prometheus UI → Нажмите Graph (верхнее меню). Вы увидите поле для PromQL запросов.
Попробуйте следующие запросы:
Проверка что БД доступна: pg_up (или mysql_up)
Количество активных подключений: pg_stat_database_numbackends{datname="your_database_name"} (или mysql_global_status_threads_connected)
Общее количество подключений: sum(pg_stat_database_numbackends) (или mysql_global_variables_max_connections)
Размер базы данных (в байтах, в гигабайтах): pg_database_size_bytes{datname="your_database_name"}
Uptime БД (в секундах, в часах): time() - pg_postmaster_start_time_seconds (или mysql_global_status_uptime)
Транзакции в секунду: rate(pg_stat_database_xact_commit{datname="your_database_name"}[5m]) (или rate(mysql_global_status_queries[5m]), для медленных запросов rate(mysql_global_status_slow_queries[5m]))
Количество таблиц в БД: count(pg_stat_user_tables_seq_scan) (или sum(mysql_info_schema_table_size_data_length))
Общее количество строк во всех таблицах: sum(pg_stat_user_tables_n_live_tup)
9. Как просмотреть системные метрики в интерфейсе Prometheus?
В Prometheus UI → Нажмите Graph (верхнее меню). Вы увидите поле для PromQL запросов.
Попробуйте метрики CPU
CPU usage (процент использования): 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) 
CPU usage по ядрам: 100 - (rate(node_cpu_seconds_total{mode="idle"}[5m]) * 100) 
Load average (1 минута):node_load1 
Load average за 5 и 15 минут:node_load5, node_load15 
Попробуйте метрики RAM
Общая память (в GB): node_memory_MemTotal_bytes / 1024 / 1024 / 1024
Доступная память (в GB):node_memory_MemAvailable_bytes / 1024 / 1024 / 1024 
Используемая память (в GB):(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / 1024 / 1024 / 1024 
RAM usage (в процентах):100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))
Swap usage:100 * (1 - (node_memory_SwapFree_bytes / node_memory_SwapTotal_bytes))
Попробуйте метрики Disk
Disk usage (корневая FS в процентах): 100 - ((node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100)
Свободное место (в GB): node_filesystem_avail_bytes{mountpoint="/"} / 1024 / 1024 / 1024 
Disk I/O - чтение (байт в секунду): rate(node_disk_read_bytes_total[5m])
Disk I/O - запись (байт в секунду):rate(node_disk_written_bytes_total[5m])
Попробуйте метрики Network
Входящий трафик (байт в секунду): rate(node_network_receive_bytes_total{device!="lo"}[5m])
Исходящий трафик (байт в секунду): rate(node_network_transmit_bytes_total{device!="lo"}[5m])
Входящий трафик в Мбит/сек: rate(node_network_receive_bytes_total{device!="lo"}[5m]) * 8 / 1000000 


🔄
Lecture #7-8
Grafana basics: connecting to Prometheus as a data source, exploring dashboards, and creating analytics with tables, maps, and heatmaps. APIs and external data sources: integrating open data (e.g., weather APIs) with Grafana and combining external metrics with course datasets
What is Grafana
Grafana is an open-source analytics and visualization platform designed for monitoring, analyzing, and visualizing data from multiple sources.

It is often used together with Prometheus but can connect to almost any system — from databases and cloud services to external APIs.

Key Advantages of Grafana
Support for multiple data sources
Grafana can connect to Prometheus, MySQL, PostgreSQL, InfluxDB, Elasticsearch, Loki, OpenWeather, Google Sheets, and many others. This allows combining technical metrics and business data in a single dashboard.

Flexible visualization
It includes over 20 built-in visualization types: tables, histograms, heatmaps, gauges, pie charts, bar gauges, world maps, time series, etc.

You can create interactive panels, filters, and drill-down transitions between dashboards.

Customizable dashboards and templates
It allows you to quickly assemble complex reports from ready-made blocks. All elements support variables, tags, and unified themes.

Alerting and notifications
You can create alert rules and send notifications via Email, Slack, Telegram, Discord, Microsoft Teams, and other channels.

Alerts support thresholds, metric conditions, and message templates.

Collaboration and security
Grafana can run locally or in the cloud, supports multi-user roles, authentication, and dashboard folders.

It is secure: data stays in your environment, and Grafana only visualizes it.

Extensibility through plugins
You can install plugins for new data sources, visualizations, and integrations (for example, IoT panels, JSON API, Worldmap Panel, BigQuery, etc.).

Alternatives to Grafana
Grafana is the leading tool for visual monitoring, but there are other solutions in the ecosystem that address similar tasks.

Chronograf
Part of the TICK stack (Telegraf, InfluxDB, Chronograf, Kapacitor). Used for visualizing metrics from InfluxDB, creating simple panels and alerts. Less flexible than Grafana but ideal for InfluxDB users.

Datadog
A cloud platform with powerful monitoring, alerting, and tracing features. It supports service auto-discovery, and integrations with Kubernetes and microservices. The main downside — it’s paid and cloud-dependent.

Zabbix
A classic enterprise-grade monitoring system. Supports agent-based and agentless metric collection, SNMP, alerts, and automated reports. Less modern visually, but reliable and often used in large organizations.

Netdata
A lightweight and visually appealing solution for real-time server and container monitoring. Installed with a single command, it automatically collects hundreds of metrics without additional setup.

Useful Locations in Grafana Interface
Connecting Prometheus (Data Source)
Connections → Data Sources → Add data source → Prometheus → In the URL field, specify:
http://prometheus:9090
→ Click Save & Test — you will see a green message “Data source is working”.

Creating a New Dashboard
Dashboards → New → New Dashboard → Add Visualization → Select the panel type (Time series, Gauge, Bar chart, Table, etc.) → Click Run queries to load data from Prometheus.

Managing Panels
Drag & Drop: rearrange panels to change the layout
Refresh rate: set auto-refresh (e.g., Refresh every 10s)
Variables: create variables via Dashboard settings → Variables
Theme: switch between Dark/Light via User settings → Preferences
Exporting and Importing Dashboards
Dashboards → Manage → Export (Export → JSON) → You can save the file or paste the JSON code on another machine via Import.
Setting Up Alert Rules
Alerting → Alert Rules → New Alert Rule → Specify condition (for example, node_cpu_seconds_total > 0.8) → Configure notifications (Telegram, Email, Slack, Discord).

Setting Filters and Variables
Dashboard settings → Variables → Add variable
Specify:

Name: city (or instance, region, service, etc.)
Type: Query
Data source: Prometheus
Query: for example label_values(weather_temperature_celsius, city)
Save settings → the variable will appear in the top filter panel.


External APIs for Custom Exporter
Grafana and Prometheus can visualize not only internal system metrics but also external open data obtained through APIs. Such APIs can be used to create your own dashboards in the Custom Exporter section.

Popular Open APIs

Open-Meteo
OpenWeatherMap
ExchangeRate.host
CoinGecko
NASA Open API
FAQ for Assignment 4
1. What tools are required to work with Grafana?
PostgreSQL или MySQL (do not delete your dataset yet)
Docker и Docker Compose
Python 3.8+
Prometheus
2. Where to start when setting up and launching Grafana? 
Open your docker-compose.yml. At the end of the file, add a new service for Grafana and create an additional volume grafana_data. If you don’t have a docker-compose.yml yet, go back to Lecture 6 and follow the Prometheus setup steps.
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  prometheus_data: # already exists
  grafana_data:
GF_SECURITY_ADMIN_USER and GF_SECURITY_ADMIN_PASSWORD set the username and password for logging into the Grafana web interface.

3. What should be added to Docker Compose to make Custom Exporter work?
Nothing needs to be added to docker-compose.yml. The Custom Exporter will be launched manually on port 8000 (see FAQ4).
Add a job to the prometheus.yml file. 
  # Custom API exporter
  - job_name: 'custom_api'
    static_configs:
      - targets: ['host.docker.internal:8000']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'external_apis'
Specify the correct address depending on your OS:
macOS / Windows: use host.docker.internal
Linux (Ubuntu): specify the external IP address of your machine
4. How to start the server for Custom Exporter with data from an external API?
Create a virtual environment: python3 -m venv venv
Activate it: source venv/bin/activate
Install dependencies: pip install prometheus_client requests
Create a file custom_exporter.py next to your YAML configurations. In this example, three metrics are created (temperature, wind speed, and API status). In your assignment, you must implement at least 10 metrics. You can choose another API: weather, currencies, cryptocurrencies, transport, sensors, etc.
"""
Custom API Exporter
Example: collecting weather data for Astana (Open-Meteo API)
"""

from prometheus_client import start_http_server, Gauge, Info
import requests
import time

# Метрики погоды (Астана)
weather_temperature = Gauge(
    'weather_temperature_celsius',
    'Current temperature in Astana',
    ['city', 'country']
)

weather_windspeed = Gauge(
    'weather_windspeed_kmh',
    'Current wind speed in Astana',
    ['city', 'country']
)

weather_api_status = Gauge(
    'weather_api_status',
    'Weather API status (1=up, 0=down)'
)


def fetch_weather_data():
    """
    Get weather data for Astana via Open-Meteo API (no registration requir)
    """
    
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': 51.1694,
            'longitude': 71.4491,
            'current_weather': 'true',
            'timezone': 'Asia/Almaty'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data['current_weather']
        
        weather_temperature.labels(
            city='Astana',
            country='Kazakhstan'
        ).set(current['temperature'])
        
        weather_windspeed.labels(
            city='Astana',
            country='Kazakhstan'
        ).set(current['windspeed'])
             
        weather_api_status.set(1)        
        return True
        
    except requests.exceptions.RequestException:
        weather_api_status.set(0)
        return False


if __name__ == '__main__':
    # Set exporter info
    exporter_info.info({
        'version': '1.0',
        'author': 'Student',
        'sources': 'weather,crypto'
    })
    
    # Start HTTP server on port 8000
    start_http_server(8000)
    
    # Infinite metrics collection loop
    while True:
        try:
            fetch_weather_data()
        except KeyboardInterrupt:
            break
        except Exception as e:
        
        # Update every 30 seconds
        time.sleep(30)
Run the Custom Exporter: python custom_exporter.py
What happens here:

The prometheus_client module starts an HTTP server on port 8000, where Prometheus can collect metrics.
Each metric is created using Gauge(), where you specify the metric name (weather_temperature_celsius), description, and optional labels (city, country).
The fetch_weather_data() function requests data from the external API, updates metric values, and sets the API status (1 = running, 0 = unavailable).
5. How to properly run the Grafana stack via Docker Compose?
Restart the containers: docker-compose up -d. If the containers do not restart correctly, run: docker-compose down.
Check the status of all containers: docker-compose ps. Along with your existing node_exporter, mysql_exporter (or postgres_exporter), and prometheus, there should now be grafana.
6. How to check if Grafana and Custom Exporter are working correctly?
Open the Prometheus web interface: http://localhost:9090. In the top menu, select Status → Targets. Make sure all services have the UP status:

prometheus (1/1 up)
mysql (1/1 up) - (or postgresql)
node (1/1 up)
custom_api (1/1 up) - a new status should appear
Check system metrics for Custom Exporter: http://localhost:9100/metrics. You should see metrics like:

Check Grafana: http://localhost:3000. The web interface will open. On the first login, a login window will appear — enter the username and password specified earlier in FAQ 2 (default: admin / admin).

7. How to view Custom Exporter metrics in the Prometheus interface? 
In the Prometheus UI → Click Graph (top menu). You will see the field for PromQL queries.
Try the metrics from the FAQ4 example:
weather_temperature_celsius{city="Astana"}
weather_windspeed_kmh{city="Astana"}
weather_api_status










Что такое Grafana
Grafana — это платформа визуальной аналитики с открытым исходным кодом, предназначенная для мониторинга, анализа и визуализации данных из множества источников.

Она часто используется совместно с Prometheus, но может подключаться почти к любым системам — от баз данных и облачных сервисов до внешних API.

Ключевые преимущества Grafana
Поддержка множества источников данных
Grafana может подключаться к Prometheus, MySQL, PostgreSQL, InfluxDB, Elasticsearch, Loki, OpenWeather, Google Sheets и десяткам других систем. Это позволяет объединять технические метрики и бизнес-данные в одной панели.

Гибкая визуализация
Встроено более 20 типов графиков: таблицы, гистограммы, heatmap, gauge, pie chart, bar gauge, world map, time series и др.

Можно создавать интерактивные панели, фильтры и drill-down переходы между дашбордами.

Настраиваемые дашборды и шаблоны
Позволяет быстро собирать комплексные отчёты из готовых блоков. Все элементы поддерживают переменные, теги и единые темы оформления.

Алертинг и уведомления
Можно создавать правила оповещения и отправлять уведомления в Email, Slack, Telegram, Discord, Microsoft Teams и другие каналы.

Алерты поддерживают пороговые значения, условия по метрикам и шаблоны сообщений.

Совместная работа и безопасность
Grafana может быть запущена локально или в облаке, поддерживает мультипользовательские роли, авторизацию и папки дашбордов.

Это безопасно: данные остаются в вашем окружении, а Grafana лишь визуализирует их.

Расширяемость через плагины
Можно устанавливать плагины для новых источников данных, визуализаций и интеграций (например, IoT-панели, JSON API, Worldmap Panel, BigQuery и т.д.).

Альтернативы Grafana
Grafana — флагман среди инструментов визуального мониторинга, но в экосистеме существуют и другие решения, которые решают схожие задачи.

Chronograf
Часть стека TICK (Telegraf, InfluxDB, Chronograf, Kapacitor). Используется для визуализации метрик из InfluxDB, создания простых панелей и алертов. Менее гибок, чем Grafana, но идеально подходит для тех, кто уже использует InfluxDB.

Datadog
Облачная платформа с мощным функционалом мониторинга, алертинга и трассировки. Имеет автообнаружение сервисов, интеграции с Kubernetes и микросервисами. Главный минус — платная модель и зависимость от облака.

Zabbix
Классическая система мониторинга корпоративного уровня. Поддерживает агентский и безагентский сбор метрик, SNMP, алерты и автоматические отчёты. Менее современен визуально, но надёжен и часто используется в крупных организациях.

Netdata
Лёгкое и визуально привлекательное решение для real-time мониторинга серверов и контейнеров. Устанавливается в одну команду, автоматически собирает сотни метрик без дополнительной настройки.

Полезные локации в интерфейсе Grafana
Подключение Prometheus (Data Source)
Connections → Data Sources → Add data source → Prometheus→ В поле URL укажите:
http://prometheus:9090
→ Нажмите Save & Test — появится зелёная надпись “Data source is working”.

Создание нового Dashboard
Dashboards → New → New Dashboard → Add Visualization→ Выберите тип панели (Time series, Gauge, Bar chart, Table и т.д.)→ Нажмите Run queries, чтобы подгрузить данные из Prometheus.

Управление панелями
Drag & Drop: перетаскивайте панели для изменения макета
Refresh rate: настройте автообновление (например, Refresh every 10s)
Variables: создайте переменные через Dashboard settings → Variables
Theme: переключайте Dark/Light через User settings → Preferences
Экспорт и импорт Dashboard
Dashboards → Manage → Экспорт (Export → JSON)→ Можно сохранить файл или вставить JSON-код на другой машине через Import.
Настройка Alert Rules (Оповещения)
Alerting → Alert Rules → New Alert Rule → Укажите условие (например, node_cpu_seconds_total > 0.8)→ Настройте уведомления (Telegram, Email, Slack, Discord).

Установка фильтров и переменных
Dashboard settings → Variables → Add variable
Укажите:

Name: city (или instance, region, service и т.д.)
Type: Query
Data source: Prometheus
Query: например label_values(weather_temperature_celsius, city)
Сохраните настройки → переменная появится в верхней панели фильтров.


Внешние API для Custom Exporter
Grafana и Prometheus могут визуализировать не только внутренние системные метрики, но и внешние открытые данные, полученные через API. Такие API можно использовать для создания собственных дашбордов в разделе Custom Exporter.

Популярные открытые API

Open-Meteo
OpenWeatherMap
ExchangeRate.host
CoinGecko
NASA Open API
FAQ for Assignment 4
1. Какие инструменты необходимы для работы с Grafana?
PostgreSQL или MySQL (пока не удаляйте свой датасет)
Docker и Docker Compose
Python 3.8+
Prometheus
2. С чего начать настройку и запуск Grafana? 
Откройте свой docker-compose.yml . В конец файла добавьте новый сервис для Grafana и создайте дополнительный volumes grafana_data. Если у вас ещё нет docker-compose.yml, вернитесь к Лекции 6 и выполните шаги по настройке Prometheus.
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  prometheus_data: # Уже есть
  grafana_data:
GF_SECURITY_ADMIN_USER и GF_SECURITY_ADMIN_PASSWORD задают логин и пароль для входа в веб-интерфейс Grafana.

3. Что нужно добавить в Docker Compose, чтобы заработал Custom Exporter?
В docker-compose.yml ничего добавлять не нужно. Custom Exporter будет запущен вручную на порту 8000 (см. FAQ4).
Добавьте job в файл prometheus.yml.
  # Custom API exporter
  - job_name: 'custom_api'
    static_configs:
      - targets: ['host.docker.internal:8000']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
        replacement: 'external_apis'
Укажите правильный адрес в зависимости от ОС:
macOS / Windows: используйте host.docker.internal
Linux (Ubuntu): укажите внешний IP-адрес машины
4. Как поднять сервер для Custom Exporter с данными с внешнего API?
Создайте виртуальное окружение: python3 -m venv venv
Активируйте его: source venv/bin/activate 
Установите зависимости: pip install prometheus_client requests
Создайте файл custom_exporter.py рядом с вашими YAML-конфигурациями.
В этом примере создаются три метрики (температура, скорость ветра и статус API).
В вашем ассайнменте необходимо реализовать не менее 10 метрик, вы можете выбрать другое API: погода, валюты, криптовалюты, транспорт, сенсоры и т. д.
"""
Custom API Exporter
Пример: сбор данных о погоде в Астане (Open-Meteo API)
"""

from prometheus_client import start_http_server, Gauge, Info
import requests
import time

# Метрики погоды (Астана)
weather_temperature = Gauge(
    'weather_temperature_celsius',
    'Current temperature in Astana',
    ['city', 'country']
)

weather_windspeed = Gauge(
    'weather_windspeed_kmh',
    'Current wind speed in Astana',
    ['city', 'country']
)

weather_api_status = Gauge(
    'weather_api_status',
    'Weather API status (1=up, 0=down)'
)


def fetch_weather_data():
    """
    Получить данные о погоде Астаны через Open-Meteo API (без регистрации)
    """
    
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': 51.1694,
            'longitude': 71.4491,
            'current_weather': 'true',
            'timezone': 'Asia/Almaty'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data['current_weather']
        
        weather_temperature.labels(
            city='Astana',
            country='Kazakhstan'
        ).set(current['temperature'])
        
        weather_windspeed.labels(
            city='Astana',
            country='Kazakhstan'
        ).set(current['windspeed'])
             
        weather_api_status.set(1)        
        return True
        
    except requests.exceptions.RequestException:
        weather_api_status.set(0)
        return False


if __name__ == '__main__':
    # Установить информацию об exporter
    exporter_info.info({
        'version': '1.0',
        'author': 'Student',
        'sources': 'weather,crypto'
    })
    
    # Запустить HTTP сервер на порту 8000
    start_http_server(8000)
    
    # Бесконечный цикл сбора метрик
    while True:
        try:
            fetch_weather_data()
        except KeyboardInterrupt:
            break
        except Exception as e:
        
        # Обновлять каждые 30 секунд
        time.sleep(30)
Запустите Custom Exporter: python custom_exporter.py 
Что здесь происходит:

Модуль prometheus_client поднимает HTTP-сервер на порту 8000, на котором Prometheus сможет собирать метрики.
Каждая метрика создаётся с помощью Gauge(), где указывается имя метрики (weather_temperature_celsius), её описание, и опциональные лейблы (city, country).
Функция fetch_weather_data() запрашивает данные с внешнего API, обновляет значения метрик и выставляет статус API (1 = работает, 0 = недоступен).
5. Как корректно запустить стек Grafana через Docker Compose?
Запустите заново контейнеры: docker-compose up -d . Если контейнеры не перезапускаются корректно, выполните: docker-compose down.
Проверьте статус всех контейнеров: docker-compose ps. К вашим существующим node_exporter, mysql_exporter (или postgres_exporter), prometheus должна добавиться grafana.
6. Как проверить, что Grafana и Custom Exporter работают корректно?
Откройте веб-интерфейс Prometheus: http://localhost:9090. В верхнем меню выберите Status → Targets. Убедитесь, что все сервисы имеют статус UP:

prometheus (1/1 up)
mysql (1/1 up) - (или postgresql)
node (1/1 up)
custom_api (1/1 up) - Должен появиться новый статус
Проверьте метрики Custom Exporter: http://localhost:8000/metrics. Вы должны увидеть метрики типа:

Проверьте Grafana: http://localhost:3000. У вас откроется веб-интерфейс. При первом входе появится окно авторизации: введите логин и пароль, указанные ранее в FAQ 2 (по умолчанию: admin / admin).

7. Как просмотреть метрики Custom Exporter в интерфейсе Prometheus?
В Prometheus UI → Нажмите Graph (верхнее меню). Вы увидите поле для PromQL запросов.
Попробуйте метрики из примера FAQ4 
weather_temperature_celsius{city="Astana"}
weather_windspeed_kmh{city="Astana"}
weather_api_status


🔄
Assignment #4
Important Information
Deadline — Week 9 (you can submit within 2 weeks after the topic explanation).
If you cannot attend in person for valid reasons, you can defend your project online only after getting approval in Teams. Without approval, online defense is not allowed.
All completed assignments must be uploaded to Moodle. If a student does not provide a GitHub link in Moodle or via Teams, and does not defend the project, the grade will be 0.
After each assignment, update your GitHub repository before uploading the work to Moodle.
The defense must be done by running the scripts live. All scripts must be fully written and saved in advance.
Late submission penalties: 1–2 days late — 5% deduction; 3–7 days late — 15% deduction; up to 2 weeks late — 30% deduction; more than 2 weeks late — 50% deduction.
Goal
In this assignment, you will learn to work with Prometheus — a system for real-time monitoring and metric collection. Unlike the previous task with Apache Superset, where you analyzed data inside databases, here the focus is on system monitoring and collecting metrics from different sources.

Be sure to read Lectures 6–7–8 in order and check the FAQ.
They explain step by step how to run Prometheus and Grafana, and how to launch DB Exporter, Node Exporter, and Custom Exporter.

What We Will Monitor

Tasks
General Conditions:

You must create three dashboards:

Database Exporter (PostgreSQL/MySQL) — 30 points
Node Exporter (System Monitoring) — 25 points
Custom Exporter (External APIs) — 45 points
To earn points for a dashboard, all checklist items must be completed. If even one point is missing — you get 0 points for that dashboard. (Partial defense is not allowed. Make sure everything is ready before your presentation.)

№	Requirement	Done
1	Prometheus and Grafana are successfully running and connected	+/-
2	The corresponding Exporter (DB/Node/Custom) is running and available at http://localhost:port	+/-
3	At least 10 PromQL queries are created for this dashboard	+/-
4	At least 60% of the queries use functions (avg, rate, sum, count, time(), etc.) or time filters ([5m], by(), grouping)	+/-
5	All 10 PromQL queries are tested in Prometheus and correctly return data (demonstrated during defense)	+/-
6	Metrics were collected for 1–5 hours (you can simulate load if needed)	+/-
7	Dashboard contains ≥10 visualizations, with at least 4 different types (e.g., 3-time series, 3-gauge, 1-heatmap, 3-bar)	+/-
8	A global filter (dashboard variable) is configured and works across all panels	+/-
9	At least one alert rule in Grafana (with visible trigger condition and status)	+/-
10	All data is displayed correctly (values update in real time)	+/-
11	Dashboard JSON file is exported and uploaded to GitHub. The GitHub repo also includes: docker-compose.yml, prometheus.yml, custom_exporter.py, README.md	+/-
12	During defense, you show: container status, Targets (all “UP”), PromQL query results, and Grafana visualizations	+/-
(30 points) Dashboard 1 — Database Exporter (PostgreSQL / MySQL)
This dashboard shows the performance and internal statistics of your SQL server (load, size, activity).

Key metrics to visualize in Grafana (you can add your own to reach 10 PromQL queries):

Number of active connections
Database size (bytes, GB)
Uptime
Read/write operations rate
Query processing speed (QPS)
Number of users and privileges
Total number of tables and rows
(25 points) Dashboard 2 — Node Exporter (System Metrics)
This dashboard monitors your computer or server resources in real time.

Main metrics (you can add your own to reach 10 PromQL queries):

CPU usage (per core)
Load average (1, 5, 15 min)
Total, available, and used memory (in GB)
RAM usage (%)
Free disk space (GB)
Disk I/O — read and write (bytes/sec)
Network traffic — incoming/outgoing (Mbit/sec)
CPU temperature
Battery level and health (for laptops)
Experiment: baseline → load → analysis (measure changes after load)
(Optional) number of active processes, system uptime, swap usage, CPU frequency, GPU usage
(45 points) Dashboard 3 — Custom Exporter (External APIs)
This dashboard demonstrates how to collect and visualize data from external APIs using a custom Python exporter.

You can choose any open API (OpenWeather, Exchange Rates, GitHub, NASA, Air Quality, etc.)

Additional Requirements:

Develop and run a custom script custom_exporter.py that publishes metrics via prometheus_client. Update frequency - every 20 seconds.
Implement at least 10 custom metrics (e.g., temperature, currency rate, pollution level, user activity, number of commits, etc.)
Create at least 10 PromQL queries with mathematical functions, filters, or groupings.
All metrics must be successfully collected in Prometheus and visualized in Grafana.
Other requirements follow the general checklist above.










Важная информация:
Дедлайн — 9-ая неделя (можно сдавать в течение 2 недель после объяснения темы). 
Если вы не сможете присутствовать по уважительным причинам, можно защитить проект онлайн, но только после согласования в Teams. Без согласования онлайн-защита не допускается.
Все выполненные задания необходимо прикреплять в Moodle. Если студент не предоставит ссылку на GitHub в Moodle или не отправит её через Teams, а также не защитит проект, то оценка за задание будет 0 баллов.
После каждого выполненного ассайнмента обязательно обновляйте свой репозиторий перед загрузкой работы в Moodle. 
Скриншоты с заданиями загружать в GitHub запрещено. Защита проводится только через запуск скриптов в реальном времени. Все скрипты должны быть полностью прописаны и сохранены заранее.
Также у нас будет система штрафов. За опоздание на 1-2 дня — штраф 5% от остатка, на 3-7 дней — 15% от остатка, на срок до 2 недель — 30% от остатка, свыше 2 недель — 50% от остатка.
Цель
В этом задании вы научитесь работать с Prometheus - системой мониторинга и сбора метрик в реальном времени. В отличие от предыдущего задания с Apache Superset, где вы анализировали данные внутри баз данных, здесь фокус на мониторинге состояния систем и сборе метрик из различных источников.

Обязательно ознакомьтесь с Лекциями 6–7–8 по порядку и прочитайте FAQ.
Там подробно описано, как поднять Prometheus и Grafana пошагово, а также как запускать DB Exporter, Node Exporter и Custom Exporter.

Что мы будем мониторить? 

Задания
Общие условия: 

Вы должны создать три дашборда:

Database Exporter (PostgreSQL/MySQL) - 30 баллов
Node Exporter (System Monitoring) - 25 баллов
Custom Exporter (External APIs) - 45 баллов
Чтобы получить баллы за конкретный дашборд, необходимо выполнить все пункты чеклиста ниже. Если хотя бы один пункт отсутствует — за данный дашборд выставляется 0 баллов (Частичная защита не допускается. Убедитесь, что все необходимые элементы подготовлены заранее.)

№	Требование	Выполнено
1	Prometheus и Grafana успешно подняты и связаны между собой	+/-
2	Соответствующий Exporter (DB/Node/Custom) запущен и доступен по http://localhost:port	+/-
3	Создано не менее 10 PromQL-запросов для данного дашборда	+/-
4	Минимум 60% запросов содержат функции (avg, rate, sum, count, time() и т.п.) или фильтры по времени ([5m], by(), grouping)	+/-
5	Все 10 PromQL-запросов проверены в Prometheus, они корректно возвращают данные, и продемонстрированы во время защиты	+/-
6	Метрики собирались в течение 1–5 часов (допускается имитация нагрузки)	+/-
7	На дашборде ≥10 визуализаций, из них 4 разных типов минимум (например, 3-time series, 3-gauge, 1-heatmap, 3-bar)	+/-
8	Настроен глобальный фильтр (dashboard variable) для всего дашборда	+/-
9	Все данные отображаются корректно (значения обновляются в реальном времени)	+/-
10	Добавлен хотя бы один alert (правило оповещения) в Grafana с видимым условием срабатывания и текущим статусом.	+/-
11	Экспортирован JSON-дашборд и загружен в GitHub. А также в GitHub присутствуют все необходимые файлы: docker-compose.yml, prometheus.yml, custom_exporter.py, README.md	+/-
12	Во время защиты продемонстрировано: работа контейнеров, статус Targets (все “UP”), выполнение PromQL-запросов и визуализация в Grafana	+/-
(30 баллов) ДАШБОРД 1 — Database Exporter (PostgreSQL / MySQL)
Этот дашборд демонстрирует работу базы данных и внутренние показатели SQL-сервера (нагрузка, размер, активность).

Ключевые метрики для визуализации в Grafana ниже. Для достижения 10 PromQL-запросов по требованию можно дополнить список собственными идеями.

Количество активных подключений
Размер базы данных (в байтах, в гигабайтах)
Время работы (Uptime)
Интенсивность операций чтения/записи
Скорость обработки запросов (QPS)
Количество пользователей и их привилегии
Общее количество таблиц и строк
(25 баллов) ДАШБОРД 2 — Node Exporter (Системные метрики)
Этот дашборд позволяет наблюдать ресурсы ноутбука или сервера в реальном времени.

Ключевые метрики ниже. Для достижения 10 PromQL-запросов по требованию можно дополнить список собственными идеями.

CPU usage (по ядрам)
Load average (1, 5, 15 минут)
Общая, доступная и используемая память (в GB)
RAM usage (в процентах)
Свободное место на диске (в GB)
Disk I/O — чтение и запись (байт/сек)
Входящий и исходящий сетевой трафик (в Мбит/сек)
Температура процессора
Ёмкость и состояние батареи ноутбука
Эксперимент: baseline → нагрузка → анализ (измерение изменений после нагрузки)
(дополнительно по желанию) количество активных процессов, системный uptime, swap usage, частота CPU или использование GPU, если доступно
(45 баллов) ДАШБОРД 3 — Custom Exporter (внешние API)
Этот дашборд иллюстрирует сбор и визуализацию внешних данных через Custom Python Exporter.

Вы можете выбрать любой открытый API (OpenWeather, Exchange Rates, GitHub, NASA, Air Quality и т. д.)

Дополнительные требования:

Разработайте и запустите собственный скрипт custom_exporter.py, который публикует метрики через prometheus_client. Частота обновления - каждые 20 секунд.
Реализуйте не менее 10 кастомных метрик (например: температура, курс валют, уровень загрязнения, активность пользователей, количество коммитов и т. д.)
Создайте не менее 10 PromQL-запросов с математическими функциями, фильтрами или группировками
Все метрики должны успешно собираться в Prometheus и корректно отображаться в Grafana
Остальные пункты требований смотрите в общем чеклисте


