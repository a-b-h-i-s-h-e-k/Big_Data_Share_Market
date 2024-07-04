import yfinance as yf
from confluent_kafka import Producer
import json
import pandas as pd
import time

# Function to fetch stock data with a 1-minute interval for the past day
def fetch_stock_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d", interval="1m")
    return hist.reset_index().to_dict(orient='records')

# Function to fetch the latest real-time stock data with a 1-minute interval
def fetch_real_time_data(symbol):
    stock = yf.Ticker(symbol)
    realtime_data = stock.history(period="max", interval="1m")
    return realtime_data.tail(1).reset_index().to_dict(orient='records')

# Function to fetch historical stock data for the past 5 years
def fetch_historical_data(symbol):
    stock = yf.Ticker(symbol)
    hist_data = stock.history(period="5y")
    return hist_data.reset_index().to_dict(orient='records')

# Function to fetch various financial data for the stock
def fetch_financial_data(symbol):
    stock = yf.Ticker(symbol)
    data = {
        "actions": stock.actions.reset_index().to_dict(orient='records'),
        "dividends": stock.dividends.reset_index().to_dict(orient='records'),
        "splits": stock.splits.reset_index().to_dict(orient='records'),
        "shares": stock.get_shares_full(start="2022-01-01").reset_index().to_dict(orient='records'),
        "income_stmt": stock.income_stmt.reset_index().to_dict(orient='records'),
        "quarterly_income_stmt": stock.quarterly_income_stmt.reset_index().to_dict(orient='records'),
        "balance_sheet": stock.balance_sheet.reset_index().to_dict(orient='records'),
        "quarterly_balance_sheet": stock.quarterly_balance_sheet.reset_index().to_dict(orient='records'),
        "cashflow": stock.cashflow.reset_index().to_dict(orient='records'),
        "quarterly_cashflow": stock.quarterly_cashflow.reset_index().to_dict(orient='records'),
        "major_holders": stock.major_holders.reset_index().to_dict(orient='records'),
        "institutional_holders": stock.institutional_holders.reset_index().to_dict(orient='records'),
        "mutualfund_holders": stock.mutualfund_holders.reset_index().to_dict(orient='records'),
        "insider_transactions": stock.insider_transactions.reset_index().to_dict(orient='records'),
        "insider_purchases": stock.insider_purchases.reset_index().to_dict(orient='records'),
        "insider_roster_holders": stock.insider_roster_holders.reset_index().to_dict(orient='records'),
        "recommendations": stock.recommendations.reset_index().to_dict(orient='records'),
        "recommendations_summary": stock.recommendations_summary.reset_index().to_dict(orient='records'),
        "upgrades_downgrades": stock.upgrades_downgrades.reset_index().to_dict(orient='records'),
        "earnings_dates": stock.earnings_dates.reset_index().to_dict(orient='records')
    }
    return data

# Function to convert a Pandas Timestamp to a UTC string
def convert_timestamp(ts: pd.Timestamp) -> str:
    if ts.tz is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert(tz="UTC").strftime("%Y-%m-%d %H:%M:%S")

# Recursive function to convert all timestamps in a dictionary or list to strings
def convert_timestamps(data):
    if isinstance(data, list):
        return [convert_timestamps(item) for item in data]
    elif isinstance(data, dict):
        return {
            (convert_timestamp(key) if isinstance(key, pd.Timestamp) else str(key)):
            (convert_timestamp(value) if isinstance(value, pd.Timestamp) else convert_timestamps(value))
            for key, value in data.items()
        }
    else:
        return data

# Function to flatten a nested dictionary
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

# Callback function for Kafka message delivery
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Main function to produce messages to Kafka
def produce_messages():
    producer = Producer({
        'bootstrap.servers': 'localhost:29092'
    })
    symbols = ["AAPL", "GOOGL", "MSFT"]  # List of stock symbols to fetch data for
    while True:
        for symbol in symbols:
            # Fetch and process various types of stock data
            stock_data_list = convert_timestamps(fetch_stock_data(symbol))
            stock_data = [flatten_dict(record) for record in stock_data_list]
            real_time_data_list = convert_timestamps(fetch_real_time_data(symbol))
            real_time_data = [flatten_dict(record) for record in real_time_data_list]
            historical_data_list = convert_timestamps(fetch_historical_data(symbol))
            historical_data = [flatten_dict(record) for record in historical_data_list]
            financial_data = flatten_dict(convert_timestamps(fetch_financial_data(symbol)))

            # Produce stock data to Kafka
            for record in stock_data:
                producer.produce('stock_data', key=symbol, value=json.dumps({'symbol': symbol, **record}), callback=delivery_report)
            # Produce real-time data to Kafka
            for record in real_time_data:
                producer.produce('real_time_data', key=symbol, value=json.dumps({'symbol': symbol, **record}), callback=delivery_report)
            # Produce historical data to Kafka
            for record in historical_data:
                producer.produce('historical_data', key=symbol, value=json.dumps({'symbol': symbol, **record}), callback=delivery_report)
            # Produce financial data to Kafka
            producer.produce('financial_data', key=symbol, value=json.dumps({'symbol': symbol, **financial_data}, default=str), callback=delivery_report)
        
        producer.flush()  # Ensure all messages are sent
        time.sleep(60)  # Wait for 60 seconds before fetching data again

# Entry point of the script
if __name__ == "__main__":
    produce_messages()
