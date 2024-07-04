real_time_financial_data_analysis/
├── docker-compose.yml
├── kafka_producers/
│   ├── requirements.txt
│   ├── yahoo_finance_producer.py
│   --- .python-version

├── flink_processor/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── flink_processor.py
    --- .python-version
    --- flink-connector-jdbs.jar(file)
    --- flink-sql-connector-kafka.jar(file)
    --- postgresql.jar(file)

---- Pgadmin
      ---  servers.json
---- postgres
     --- init.sql   
---- processor(kafka consumer for consuming historical data and financial data)
     --- data_processor.py
     --- .python-version   
├── streamlit_app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── streamlit_app.py
     --- provide.py
     --- .python-version
├── .env
├── README.md
