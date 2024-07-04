from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from pathlib import Path

# Flag to determine if the run is a dry run (i.e., print output instead of writing to the database)
dry_run = False

# Database connection details
db_url = "jdbc:postgresql://localhost:5432/finance_db"
db_username = "admin"
db_password = "admin"

def get_output_connector_config(table: str):
    """
    Returns the configuration for the output connector.
    If dry_run is True, it configures to print to stdout.
    Otherwise, it configures to write to a JDBC table in the database.
    """
    if dry_run:
        # On dry-run mode, print to stdout, including table name as prefix
        return f"""
            'connector' = 'print',
            'print-identifier' = '{table}'
            """
    else:
        # Otherwise, write data to corresponding DB table using JDBC connector
        return f"""
            'connector' = 'jdbc',
            'table-name' = '{table}',
            'url' = '{db_url}',
            'username' = '{db_username}',
            'password' = '{db_password}'
            """

def main():
    # Create a StreamExecutionEnvironment
    env = StreamExecutionEnvironment.get_execution_environment()
    
    # Resolve the script directory and add necessary JAR files for Kafka and JDBC connectors
    script_dir = Path(__file__).parent.resolve()
    env.add_jars(Path(script_dir, "flink-sql-connector-kafka-3.1.0-1.18.jar").as_uri())
    env.add_jars(Path(script_dir, "flink-connector-jdbc-3.1.2-1.18.jar").as_uri())
    env.add_jars(Path(script_dir, "postgresql-42.7.3.jar").as_uri())
    
    # Create a StreamTableEnvironment
    table_env = StreamTableEnvironment.create(env)
    
    # Kafka bootstrap servers
    bootstrap_servers = "localhost:29092"

    # Define a source table 'stock_data' reading from Kafka
    table_env.execute_sql(f"""
        CREATE TABLE `stock_data` (
            `symbol` STRING,
            `Datetime` STRING,
            `ts` AS TO_TIMESTAMP_LTZ(UNIX_TIMESTAMP(`Datetime`, 'yyyy-MM-dd HH:mm:ss'), 0),
            `Open` DOUBLE,
            `High` DOUBLE,
            `Low` DOUBLE,
            `Close` DOUBLE,
            `Volume` BIGINT,
            `Dividends` DOUBLE,
            `Stock_Splits` DOUBLE,
            WATERMARK FOR `ts` AS `ts` - INTERVAL '1' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'stock_data',
            'properties.bootstrap.servers' = '{bootstrap_servers}',
            'properties.group.id' = 'processor-python',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json',
            'json.ignore-parse-errors' = 'True'
        )
    """)

    # Define a sink table 'stock_data_output' to write the processed data
    table_env.execute_sql(f"""
        CREATE TABLE `stock_data_output` (
            `symbol` STRING,
            `datetime` TIMESTAMP,
            `open` DOUBLE,
            `high` DOUBLE,
            `low` DOUBLE,
            `close` DOUBLE,
            `volume` BIGINT,
            `dividends` DOUBLE,
            `stock_splits` DOUBLE,
            `indicator` STRING,
            PRIMARY KEY (`symbol`, `datetime`) NOT ENFORCED
        ) WITH ({get_output_connector_config("stock_data_output")})
    """)

    # Define the buy/sell indicator logic and create a query
    stock_data_query = table_env.sql_query("""
        SELECT
            `symbol`,
            `ts` AS `datetime`,
            `Open`,
            `High`,
            `Low`,
            `Close`,
            `Volume`,
            `Dividends`,
            `Stock_Splits`,
            CASE
                WHEN `Close` > `Open` THEN 'BUY'
                WHEN `Close` < `Open` THEN 'SELL'
                ELSE 'HOLD'
            END AS `indicator`
        FROM
            `stock_data`
    """)

    # Create a statement set to execute multiple SQL statements
    statements_to_execute = table_env.create_statement_set()
    
    # Add the insert statement to the statement set
    statements_to_execute.add_insert("stock_data_output", stock_data_query)
 
    # Execute the statement set and wait for the job to finish
    statements_to_execute.execute().wait()

if __name__ == '__main__':
    main()
