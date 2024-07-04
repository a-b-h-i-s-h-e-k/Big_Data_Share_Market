CREATE TABLE stock_data_output (
    symbol VARCHAR,
    datetime TIMESTAMP,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume BIGINT,
    dividends DOUBLE PRECISION,
    stock_splits DOUBLE PRECISION,
    indicator VARCHAR,
    PRIMARY KEY (symbol, datetime)
);



