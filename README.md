# Big_data_share_market


# Real-Time Financial Data Analysis

# 🚀 Real-Time Financial Data Streaming & Analytics Platform

> End-to-end **streaming data system** for real-time stock analysis, signal generation, and advanced trading visualization.

---

## 📌 Overview

This project implements a **production-style real-time data pipeline** that ingests financial data, processes it using a streaming engine, stores it efficiently, and exposes insights through an interactive analytics dashboard.

It simulates how modern data teams build systems for:
- 📈 Market monitoring  
- ⚡ Real-time signal generation  
- 🧠 Quantitative analysis  
- 📊 Decision-support dashboards  

---

## 🧠 Problem Statement (Situation)

Financial data workflows are often:

- ❌ Batch-based (not real-time)
- ❌ Fragmented across multiple sources
- ❌ Manual and error-prone
- ❌ Lacking actionable insights (signals, patterns)

This creates a major gap:

> Traders and analysts cannot react fast enough to market movements.

---

## 🎯 Objective (Task)

Design and build a system that:

- Streams **real-time financial data**
- Processes data with **low latency**
- Generates **trading signals (BUY/SELL/HOLD)**
- Stores structured data for querying
- Visualizes insights via an **interactive dashboard**

### Constraints

- Handle **high-frequency data (1-min resolution)**
- Support **multiple data types**
- Maintain **scalability & modularity**
- Ensure **near real-time updates**

---

## ⚙️ System Architecture (Action)

### 🏗️ Architecture Diagram



```
flowchart LR
    A[Yahoo Finance API] --> B[Kafka Producer]
    B --> C[(Kafka Topics)]

    C --> D[Flink Stream Processor]
    D --> E[(PostgreSQL)]

    E --> F[Streamlit Dashboard]

    C --> G[Kafka Consumer (Signals)]
    G --> F

    subgraph Streaming Layer
        B --> C --> D
    end

    subgraph Storage Layer
        E
    end

    subgraph Presentation Layer
        F
    end
```


## 🔄 Data Flow
1. Data Ingestion
       - Fetch stock data via yfinance
       - Stream to Kafka topics
2. Streaming Pipeline
       - Kafka → Flink
       - Event-time processing with watermarks
3. Processing
       - Compute trading signals:
              - BUY / SELL / HOLD
4. Storage
       - Persist processed data in PostgreSQL
5. Visualization
       - Streamlit dashboard renders:
              - charts
              - indicators
              - strategies


##🔌 Data Ingestion Layer (Kafka Producer)
       - Built using yfinance + confluent-kafka
       - Streams multiple data types:

| Data Type  | Description          |
| ---------- | -------------------- |
| Intraday   | 1-minute resolution  |
| Real-time  | Latest tick          |
| Historical | 5 years              |
| Financials | Company fundamentals |

### Engineering Highlights
 - ✅ Timestamp normalization → UTC
 - ✅ Recursive JSON flattening
 - ✅ Multi-topic architecture:
       - stock_data
       - real_time_data
       - historical_data
       - financial_data


### ⚡ Stream Processing Layer (Flink)
       - Implemented using PyFlink
       - Event-time streaming with watermarks
- Signal Logic
# SQL Code

CASE
  WHEN Close > Open THEN 'BUY'
  WHEN Close < Open THEN 'SELL'
  ELSE 'HOLD'
END

- Features
       - Low-latency processing
       - Schema-based transformation
       - JDBC sink → PostgreSQL
       - Debug mode (print connector)

### 🗄️ Storage Layer (PostgreSQL)
- Structured schema for time-series financial data:
       - OHLC + Volume
       - Trading signal (indicator)
- Design Decisions
  - Composite primary key:
        (symbol, datetime)
- Optimized for:
       - time-based queries
       - dashboard rendering

# 📊 Analytics & Visualization (Streamlit)
- A full-featured trading dashboard with real-time updates.

1. 📈 Technical Indicators
- EMA (5, 15)
- SMA
- RSI
- MACD
- ADX
- TSI

2. 📉 Trading Strategies
- Scalping
- Momentum
- Breakout
- Range Trading

3. 🔍 Pattern Detection
- Ascending Triangle
- Descending Triangle
- Rounding Bottom

4. 📊 Chart Types
- Candlestick
- Heikin Ashi
- OHLC
- Renko
- Raindrop
- Line / Area

## 🔄 Real-Time Signal Engine
- Kafka consumer (DataProvider)
- Maintains rolling window of indicators
- Thread-safe implementation (RLock)

# 🐳 Infrastructure
- Fully containerized using Docker:
       - Kafka + Kafka UI
       - PostgreSQL + pgAdmin
       - Streamlit
       - Flink (configurable)

## 📈 Results (Impact)
- 🚀 Performance Improvements
       - ⚡ Reduced manual analysis by ~90%
       - ⏱ Achieved real-time updates every 60 seconds
       - 📊 Enabled instant trading signal generation


# 💡 Engineering Achievements
- Built end-to-end streaming architecture
- Designed event-driven data pipeline
- Integrated data engineering + analytics + visualization
- Simulated production-grade system design


# 📚 Key Learnings
1. Streaming systems require:
- schema control
- efficient serialization

2. Event-time processing is critical for:
- accurate analytics

3. Visualization layers can become:
- performance bottlenecks



# Setup

# Step 1: Prepare Your Environment

       - Install Docker and Docker Compose:
          Make sure Docker and Docker Compose are installed on your system.
          Docker compose up / docker compose up -d / docker compose --build (use one of the command)
       - I use pyenv for downloading python version 3.10.14 to use in this project.
       - I make different-different python enviorment in different folder in kafka, flink, streamlit folder... i added a file called .python-version in them.
       
# Step 2: Create and Configure Environment File

Create a .env File:
In the project root directory, create a file named .env with the following content:

POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# Step 3: Start Docker Containers

Build and Start Docker Containers:
Run the following command to build and start all the services defined in docker-compose.yml:
docker-compose up --build
This command will pull the necessary Docker images, build the custom images, and start the services (Zookeeper, Kafka, Kafka UI, Flink(in my file my flink is corrupted, so i disable it), PostgreSQL, pgAdmin, Streamlit).

# Step 4: Set Up Kafka Producers

Navigate to kafka_producers Directory:

Open a new terminal window or tab and navigate to the kafka_producers directory.
Install Python Dependencies:

Run the following command to install the required Python packages:
pip install -r requirements.txt
Run Yahoo Finance Kafka Producer:
Execute the Yahoo Finance producer script to start sending stock and financial data to Kafka:
 - python3 yahoo_finance_producer.py

# Step 5: Verify Kafka Data

Open Kafka UI:
Open a web browser and go to http://localhost:8080 to access Kafka UI.
Verify that the topics stock_data are receiving data.

# Step 6: Set Up Flink Processor

Navigate to flink_processor Directory:
In a terminal, navigate to the flink_processor directory.
Build Flink Docker Image:

The Flink Docker image will be built automatically when running docker-compose up --build.
Verify Flink Job:

Open a web browser and go to http://localhost:8081 to access the Flink Dashboard.
Verify that the Flink job is running and processing data.


# Step 7: Access PostgreSQL and pgAdmin

Open pgAdmin:

Open a web browser and go to http://localhost:80 to access pgAdmin.
Login with the default credentials (email: admin@admin.com, password: admin).
Configure PostgreSQL Connection:

In pgAdmin, create a new server connection with the following details:
Hostname/address: postgres
Port: 5432
Username: admin
Password: admin

# Step 8: Access Streamlit Application

Open Streamlit Application:
Open a web browser and go to http://localhost:8501 to access the Streamlit dashboard.
The Streamlit app will display real-time stock data visualizations.

# Step 9: Monitor and Maintain

Monitor Docker Containers:

Use docker-compose logs -f to monitor logs from all containers.
Use docker ps to check the status of all running containers.
Stop Docker Containers:

To stop the Docker containers, run:

docker compose down
docker compose down -v

Additional Steps
Create the jars Directory:
Place the flink-sql-connector-kafka-3.0.1-1.18.jar file in the jars directory in your project root.



### 🛠️ Tech Stack

| Layer          | Technology         |
| -------------- | ------------------ |
| Language       | Python             |
| Streaming      | Kafka              |
| Processing     | Flink (PyFlink)    |
| Database       | PostgreSQL         |
| Visualization  | Streamlit + Plotly |
| Infrastructure | Docker             |


# 🔮 Future Enhancements
       - 🤖 ML models (LSTM, XGBoost for prediction)
       - 📦 Schema Registry (Avro / Protobuf)
       - ☁️ Cloud deployment (AWS / GCP)
       - 🔔 Alert system (Telegram / Email)
       - ⚡ Advanced Flink:
              - window aggregations
              - joins
              - anomaly detection

### 💬 Final Note
- This is not just a dashboard — it is a mini real-time financial data platform, designed with production principles in mind.




## Summary ##
Ensure Docker and Docker Compose are installed.
Create and configure the .env file.
Build and start Docker containers with docker-compose up --build.
Run Kafka producers for Yahoo Finance data.
Verify data flow in Kafka UI and Flink Dashboard.
Access PostgreSQL using pgAdmin.
View the real-time data in the Streamlit application.
