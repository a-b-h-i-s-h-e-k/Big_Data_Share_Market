#!/usr/bin/env python

import atexit
import logging
import pandas as pd
from datetime import datetime
from json import loads
from uuid import uuid4
from threading import Thread, RLock, Event
from confluent_kafka import Consumer

class DataProvider:
    def __init__(self, bootstrap_servers):
        """
        Initializes the DataProvider class.

        Parameters:
        - bootstrap_servers (str): The Kafka bootstrap servers.
        """
        self.lock = RLock()
        self.bootstrap_servers = bootstrap_servers
        self.indicators = {}  # Dictionary to store stock indicators.
        self.thread = None  # Thread to run the consumer.
        self.thread_stop_requested = None  # Event to stop the consumer thread.

    def get_latest_indicators(self):
        """
        Get the latest indicators for all stocks.

        Returns:
        - DataFrame: A pandas DataFrame with the latest indicators.
        """
        with self.lock:
            rows = []
            # Collect the latest indicator for each stock.
            for stock_indicators in self.indicators.values():
                rows.append([stock_indicators[-1][col] for col in ["symbol", "close", "indicator"]])
            df = pd.DataFrame(rows, columns=["symbol", "price", "signal"])
            logging.debug(f"Generating dataset with latest indicators for all {len(self.indicators)} stocks")
            return df

    def get_stock_indicators(self, symbol: str):
        """
        Get the historical indicators for a specific stock.

        Parameters:
        - symbol (str): The stock symbol.

        Returns:
        - DataFrame: A pandas DataFrame with the historical indicators.
        """
        with self.lock:
            inds = self.indicators.get(symbol, [])
            columns = ["open", "high", "low", "close", "datetime"]
            rows = []
            # Collect the historical indicators for the stock.
            for ind in inds:
                row = [datetime.fromisoformat(ind[col]) if col == "datetime" else ind[col] for col in columns]
                rows.append(row)
            df = pd.DataFrame(rows, columns=columns)
            logging.debug(f"Generating dataset with series of {len(inds)} indicators for stock {symbol}")
            return df

    def run(self):
        """
        Start the data provider thread.
        """
        if not self.thread:
            self.thread_stop_requested = Event()
            self.thread = Thread(target=self._run, args=(), daemon=True)
            logging.info("Starting data provider thread")
            self.thread.start()
            # Ensure the thread stops gracefully when the program exits.
            atexit.register(lambda: self.stop())

    def stop(self):
        """
        Stop the data provider thread.
        """
        if self.thread:
            logging.info("Stopping data provider thread")
            self.thread_stop_requested.set()
            self.thread.join()
            self.thread = None
            self.thread_stop_requested = None

    def _run(self):
        """
        The main loop for the data provider thread.
        """
        consumer = Consumer({
            "bootstrap.servers": self.bootstrap_servers,
            "group.id": "frontend"
        })
        try:
            consumer.subscribe(["indicators"])
            logging.info("Consumer subscribed")
            while not self.thread_stop_requested.is_set():
                msg = consumer.poll(.25)
                if msg is None: continue
                if msg.error():
                    logging.error(f"Error {str(msg.error())}")
                    continue
                ind = loads(msg.value())
                symbol = ind["symbol"]
                logging.debug(f"Received {ind}")
                with self.lock:
                    if symbol not in self.indicators:
                        self.indicators[symbol] = []
                    inds = self.indicators[symbol]
                    if len(inds) >= 20: 
                        inds.pop(0)  # Maintain only the latest 20 indicators.
                    inds.append(ind)
        finally:
            consumer.close()
            logging.info("Consumer stopped")
