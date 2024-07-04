# Big_data_share_market


# Real-Time Financial Data Analysis

## Project Overview

This project aims to create a real-time financial data analysis platform. It integrates data source like Yahoo Finance to fetch stock data, it contain different data like stock_data(Intraday data), Historcal_data(past_data), Financial data(About finance of company/share it is useful in investing), real time data(provide real time data).

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


## Summary ##
Ensure Docker and Docker Compose are installed.
Create and configure the .env file.
Build and start Docker containers with docker-compose up --build.
Run Kafka producers for Yahoo Finance data.
Verify data flow in Kafka UI and Flink Dashboard.
Access PostgreSQL using pgAdmin.
View the real-time data in the Streamlit application.