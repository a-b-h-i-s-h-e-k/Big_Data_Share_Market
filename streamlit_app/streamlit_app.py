import sys
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from argparse import ArgumentParser
from datetime import datetime
from dateutil.tz import gettz
import psycopg2
from streamlit_javascript import st_javascript
import time
from json import loads
from confluent_kafka import Consumer
from threading import Thread

# Add the processor folder to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'processor'))

# Import the DataProvider from the correct module
from provider import DataProvider  # Ensure this import matches your project structure

# Parse command line options
parser = ArgumentParser(description='Streamlit based frontend displaying stock and financial data')
parser.add_argument('--bootstrap-servers', default='localhost:29092', help='Kafka bootstrap servers', type=str)
parser.add_argument('--pg-url', default='localhost:5432', help='PostgreSQL URL', type=str)
parser.add_argument('--pg-user', default='admin', help='PostgreSQL username', type=str)
parser.add_argument('--pg-password', default='admin', help='PostgreSQL password', type=str)
parser.add_argument('--pg-db', default='finance_db', help='PostgreSQL database name', type=str)
args = parser.parse_args()

# Configure webpage
st.set_page_config(layout="wide", page_title="Financial Data Monitor")

# Further customization via CSS injection
st.markdown("""
    <style>
        .appview-container .main .block-container {
            padding-top: 2em;
        }
        body {
            background-color: white;
            color: black;
            background-image: url("https://wallpapers.com/images/hd/black-and-white-cloud-fv98q3lux8c2l5ia.jpg");
            background-size: cover;
        }
    </style>
""", unsafe_allow_html=True)

# Define a function that starts the DataProvider object/thread
@st.cache_resource
def get_data_provider():
    provider = DataProvider(args.bootstrap_servers)
    provider.run()
    return provider

# Get the DataProvider
provider = get_data_provider()

# Get the browser timezone
tz_js = st_javascript("""await (async () => Intl.DateTimeFormat().resolvedOptions().timeZone)()""")
tz = gettz(tz_js) if isinstance(tz_js, str) else None

# PostgreSQL connection function
def get_pg_connection():
    return psycopg2.connect(
        dbname=args.pg_db,
        user=args.pg_user,
        password=args.pg_password,
        host=args.pg_url.split(':')[0],
        port=args.pg_url.split(':')[1]
    )

# Fetch data from PostgreSQL
def fetch_pg_data():
    conn = get_pg_connection()
    query = "SELECT * FROM stock_data_output ORDER BY datetime DESC LIMIT 100"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Process messages from Kafka
def process_messages(consumer: Consumer, processed_data: list):
    while True:
        msg = consumer.poll(0.1)
        if msg is None:
            continue
        if msg.error():
            st.error(f"Error {str(msg.error())}")
            continue
        parsed_msg = loads(msg.value())
        st.info(f"Received message: {parsed_msg}")
        processed_data.append(parsed_msg)

# Start Kafka consumer in a separate thread
@st.cache_resource
def start_kafka_consumer(bootstrap_servers: str):
    processed_data = []
    consumer = Consumer({
        "bootstrap.servers": bootstrap_servers,
        "group.id": "streamlit_consumer_group",
        "auto.offset.reset": "earliest"
    })
    consumer.subscribe(["historical_data_processed", "financial_data_processed"])
    thread = Thread(target=process_messages, args=(consumer, processed_data), daemon=True)
    thread.start()
    return processed_data

# Get the processed data
processed_data = start_kafka_consumer(args.bootstrap_servers)

# Define and layout the main UI Elements
st.markdown("<div class='navbar'><a href='#'>Home</a><a href='#'>About</a><a href='#'>Typography</a><a href='#'>Contacts</a></div>", unsafe_allow_html=True)
st.markdown("<div class='title'>It's My Passion</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>It's not just love for music also for Market</div>", unsafe_allow_html=True)

left_column, right_column = st.columns([.3, .7], gap="large")

with left_column:
    st.markdown("<div class='sidebar'>", unsafe_allow_html=True)
    st.caption("Current prices:")
    prices_table = st.empty()
    kafka_table = st.empty()  # Table for Kafka data
    st.sidebar.header("Chart Options")
    show_ema5 = st.sidebar.checkbox("Show EMA5", value=True)
    show_ema15 = st.sidebar.checkbox("Show EMA15", value=True)
    show_sma = st.sidebar.checkbox("Show SMA", value=True)
    show_rsi = st.sidebar.checkbox("Show RSI", value=False)
    show_tsi = st.sidebar.checkbox("Show TSI", value=False)
    show_macd = st.sidebar.checkbox("Show MACD", value=False)
    show_adx = st.sidebar.checkbox("Show ADX", value=False)
    show_support_resistance = st.sidebar.checkbox("Show Support/Resistance", value=True)

    # Trading Strategies
    st.sidebar.header("Trading Strategies")
    use_scalping = st.sidebar.checkbox("Scalping", value=False)
    use_range_trading = st.sidebar.checkbox("Range Trading", value=False)
    use_momentum = st.sidebar.checkbox("Momentum Trading", value=False)
    use_breakout = st.sidebar.checkbox("Breakout Trading", value=False)

    # Pattern Recognition
    st.sidebar.header("Pattern Recognition")
    show_ascending_triangle = st.sidebar.checkbox("Ascending Triangle", value=False)
    show_descending_triangle = st.sidebar.checkbox("Descending Triangle", value=False)
    show_rounding_bottom = st.sidebar.checkbox("Rounding Bottom", value=False)

    # Chart Type Selection
    st.sidebar.header("Chart Type")
    chart_type = st.sidebar.selectbox("Select Chart Type", 
        ["Candlestick", "Heikin Ashi", "OHLC", "Raindrop", "Renko", "Line", "Area"])

    # Selected currency is initially 'AAPL'
    stocks = []
    selected_stock = "AAPL"

    # Update the UI every 5.0 seconds, every time getting updated data from the DataProvider
    refresh_interval = st.sidebar.number_input("Refresh interval (seconds)", min_value=1, max_value=60, value=5)
    st.markdown("</div>", unsafe_allow_html=True)

with right_column:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    currency_selector = st.empty()
    currency_plot = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

def calculate_ema(df, span):
    return df['close'].ewm(span=span, adjust=False).mean()

def calculate_sma(df, window):
    return df['close'].rolling(window=window).mean()

def calculate_rsi(df, window=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_tsi(df, long_window=25, short_window=13):
    diff = df['close'].diff(1)
    abs_diff = abs(diff)
    double_smoothed_diff = diff.ewm(span=long_window, adjust=False).mean().ewm(span=short_window, adjust=False).mean()
    double_smoothed_abs_diff = abs_diff.ewm(span=long_window, adjust=False).mean().ewm(span=short_window, adjust=False).mean()
    tsi = 100 * (double_smoothed_diff / double_smoothed_abs_diff)
    return tsi

def calculate_macd(df):
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def calculate_adx(df, window=14):
    high_diff = df['high'].diff()
    low_diff = df['low'].diff()
    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
    tr = pd.concat([df['high'] - df['low'], (df['high'] - df['close'].shift()).abs(), (df['low'] - df['close'].shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1/window, adjust=False).mean() / atr)
    minus_di = 100 * (minus_dm.ewm(alpha=1/window, adjust=False).mean() / atr)
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di)).rolling(window=window).mean()
    adx = dx.ewm(alpha=1/window, adjust=False).mean()
    return adx

def add_support_resistance_lines(fig, df):
    support_line = df['low'].min()
    resistance_line = df['high'].max()
    fig.add_hline(y=support_line, line=dict(color='blue', dash='dash'), annotation_text='Support', annotation_position='bottom right')
    fig.add_hline(y=resistance_line, line=dict(color='red', dash='dash'), annotation_text='Resistance', annotation_position='top right')

def apply_scalping_strategy(df):
    df['signal'] = 0
    df.loc[df['close'] < df['close'].rolling(window=5).min(), 'signal'] = 1
    df.loc[df['close'] > df['close'].rolling(window=5).max(), 'signal'] = -1
    return df

def apply_range_trading_strategy(df):
    support = df['low'].min()
    resistance = df['high'].max()
    df['signal'] = 0
    df.loc[df['close'] <= support * 1.05, 'signal'] = 1
    df.loc[df['close'] >= resistance * 0.95, 'signal'] = -1
    return df

def apply_momentum_strategy(df):
    df['signal'] = 0
    df['momentum'] = df['close'] - df['close'].shift(5)
    df.loc[df['momentum'] > 0, 'signal'] = 1
    df.loc[df['momentum'] < 0, 'signal'] = -1
    return df

def apply_breakout_strategy(df):
    df['signal'] = 0
    rolling_max = df['close'].rolling(window=20).max()
    rolling_min = df['close'].rolling(window=20).min()
    df.loc[df['close'] > rolling_max.shift(), 'signal'] = 1
    df.loc[df['close'] < rolling_min.shift(), 'signal'] = -1
    return df

# Pattern recognition functions
def recognize_ascending_triangle(df):
    highs = df['high'].rolling(window=5).max()
    lows = df['low'].rolling(window=5).min()
    ascending = (highs.shift(1) < highs) & (lows.shift(1) > lows)
    df['ascending_triangle'] = ascending

def recognize_descending_triangle(df):
    highs = df['high'].rolling(window=5).max()
    lows = df['low'].rolling(window=5).min()
    descending = (highs.shift(1) > highs) & (lows.shift(1) < lows)
    df['descending_triangle'] = descending

def recognize_rounding_bottom(df):
    rolling_mean = df['close'].rolling(window=20).mean()
    bottom = (rolling_mean - rolling_mean.shift(1)).rolling(window=5).mean()
    df['rounding_bottom'] = bottom > 0

def plot_heikin_ashi(df):
    heikin_ashi_df = df.copy()
    heikin_ashi_df['close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    heikin_ashi_df['open'] = (df['open'].shift(1) + df['close'].shift(1)) / 2
    heikin_ashi_df['high'] = df[['open', 'close', 'high']].max(axis=1)
    heikin_ashi_df['low'] = df[['open', 'close', 'low']].min(axis=1)
    return heikin_ashi_df

def plot_ohlc(df):
    fig = go.Figure()
    fig.add_trace(go.Ohlc(
        x=df['datetime'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        name='OHLC'
    ))
    return fig

def plot_renko(df):
    renko_df = df.copy()
    renko_df['close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    renko_df['open'] = renko_df['close'].shift(1)
    renko_df = renko_df.dropna()
    return renko_df

def plot_raindrop(df):
    raindrop_df = df.copy()
    raindrop_df['volume_up'] = df['volume'] * (df['close'] > df['open'])
    raindrop_df['volume_down'] = df['volume'] * (df['close'] <= df['open'])
    return raindrop_df

def plot_line(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['close'],
        mode='lines',
        name='Line',
        line=dict(color='blue')
    ))
    return fig

def plot_area(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['datetime'],
        y=df['close'],
        mode='lines',
        fill='tozeroy',
        name='Area',
        line=dict(color='blue')
    ))
    return fig



def color_increase_decrease(df):
    df['color'] = df['close'].diff().apply(lambda x: 'green' if x > 0 else 'red')
    return df

i = 0
while True:
    # Fetch data from PostgreSQL
    df_all = fetch_pg_data()

    # Display stock prices in a table
    prices_table.dataframe(df_all, width=1200, height=600)

    # Handle stock selection
    new_stocks = df_all["symbol"].unique().tolist()
    new_stocks.sort()
    if new_stocks != stocks:
        stocks = new_stocks
        prev_selected_stock_idx = stocks.index(selected_stock) if selected_stock in stocks else 0
        selected_stock = currency_selector.selectbox("Select stock to plot", stocks, index=prev_selected_stock_idx, key=f"select-stock-{i}")

    # Get past data of currently selected stock, converting timezone from UTC to browser one
    df = df_all[df_all["symbol"] == selected_stock]
    if tz and not df.empty:
        df = df.copy()
        df["datetime"] = pd.to_datetime(df["datetime"]).dt.tz_localize('UTC').dt.tz_convert(tz)

    # Calculate EMAs and SMA
    df['ema5'] = calculate_ema(df, 5) if show_ema5 else None
    df['ema15'] = calculate_ema(df, 15) if show_ema15 else None
    df['sma'] = calculate_sma(df, 20) if show_sma else None
    df['rsi'] = calculate_rsi(df) if show_rsi else None
    df['tsi'] = calculate_tsi(df) if show_tsi else None
    df['macd'], df['macd_signal'] = calculate_macd(df) if show_macd else (None, None)
    df['adx'] = calculate_adx(df) if show_adx else None

    # Apply trading strategies
    if use_scalping:
        df = apply_scalping_strategy(df)
    if use_range_trading:
        df = apply_range_trading_strategy(df)
    if use_momentum:
        df = apply_momentum_strategy(df)
    if use_breakout:
        df = apply_breakout_strategy(df)

    # Pattern recognition
    if show_ascending_triangle:
        recognize_ascending_triangle(df)
    if show_descending_triangle:
        recognize_descending_triangle(df)
    if show_rounding_bottom:
        recognize_rounding_bottom(df)

    # Plot based on selected chart type
    if chart_type == "Candlestick":
        df = color_increase_decrease(df)
        fig = go.Figure(layout=go.Layout(height=600))
        fig.add_trace(go.Candlestick(name="price", x=df["datetime"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
                                     increasing_line_color='green', decreasing_line_color='red'))
    elif chart_type == "Heikin Ashi":
        heikin_ashi_df = plot_heikin_ashi(df)
        heikin_ashi_df = color_increase_decrease(heikin_ashi_df)
        fig = go.Figure(layout=go.Layout(height=600))
        fig.add_trace(go.Candlestick(name="Heikin Ashi", x=heikin_ashi_df["datetime"], open=heikin_ashi_df["open"], high=heikin_ashi_df["high"],
                                     low=heikin_ashi_df["low"], close=heikin_ashi_df["close"],
                                     increasing_line_color='green', decreasing_line_color='red'))
    elif chart_type == "OHLC":
        df = color_increase_decrease(df)
        fig = go.Figure(layout=go.Layout(height=600))
        fig.add_trace(go.Ohlc(name="OHLC", x=df["datetime"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
                              increasing_line_color='green', decreasing_line_color='red'))
    elif chart_type == "Raindrop":
        raindrop_df = plot_raindrop(df)
        raindrop_df = color_increase_decrease(raindrop_df)
        fig = go.Figure(layout=go.Layout(height=600))
        fig.add_trace(go.Bar(name="Raindrop Up Volume", x=raindrop_df["datetime"], y=raindrop_df["volume_up"], marker=dict(color='green')))
        fig.add_trace(go.Bar(name="Raindrop Down Volume", x=raindrop_df["datetime"], y=raindrop_df["volume_down"], marker=dict(color='red')))
    elif chart_type == "Renko":
        renko_df = plot_renko(df)
        renko_df = color_increase_decrease(renko_df)
        fig = go.Figure(layout=go.Layout(height=600))
        fig.add_trace(go.Candlestick(name="Renko", x=renko_df.index, open=renko_df["open"], high=renko_df["high"], low=renko_df["low"],
                                     close=renko_df["close"], increasing_line_color='green', decreasing_line_color='red'))
    elif chart_type == "Line":
        df = color_increase_decrease(df)
        fig = go.Figure(layout=go.Layout(height=600))
        fig.add_trace(go.Scatter(name="Line", x=df["datetime"], y=df["close"], mode='lines', line=dict(color='green')))
    elif chart_type == "Area":
        df = color_increase_decrease(df)
        fig = go.Figure(layout=go.Layout(height=600))
        fig.add_trace(go.Scatter(name="Area", x=df["datetime"], y=df["close"], fill='tozeroy', line=dict(color='green')))

    fig.add_trace(go.Bar(name='volume', x=df['datetime'], y=df['volume'], marker=dict(color='gray'), yaxis='y2'))

    if show_ema5:
        fig.add_trace(go.Scatter(name="ema5", x=df["datetime"], y=df['ema5'], line=dict(color='blue')))
    if show_ema15:
        fig.add_trace(go.Scatter(name="ema15", x=df["datetime"], y=df['ema15'], line=dict(color='red')))
    if show_sma:
        fig.add_trace(go.Scatter(name="sma", x=df["datetime"], y=df['sma'], line=dict(color='green')))
    if show_rsi:
        fig.add_trace(go.Scatter(name="rsi", x=df["datetime"], y=df['rsi'], line=dict(color='orange')))
    if show_tsi:
        fig.add_trace(go.Scatter(name="tsi", x=df["datetime"], y=df['tsi'], line=dict(color='purple')))
    if show_macd:
        fig.add_trace(go.Scatter(name="MACD", x=df["datetime"], y=df['macd'], line=dict(color='cyan')))
        fig.add_trace(go.Scatter(name="MACD Signal", x=df["datetime"], y=df['macd_signal'], line=dict(color='magenta')))
    if show_adx:
        fig.add_trace(go.Scatter(name="ADX", x=df["datetime"], y=df['adx'], line=dict(color='yellow')))
    if show_support_resistance:
        add_support_resistance_lines(fig, df)

    # Add signals from trading strategies
    if 'signal' in df.columns:
        buy_signals = df[df['signal'] == 1]
        sell_signals = df[df['signal'] == -1]
        fig.add_trace(go.Scatter(name="Buy Signal", x=buy_signals["datetime"], y=buy_signals['close'], mode='markers', marker=dict(color='green', symbol='triangle-up', size=10)))
        fig.add_trace(go.Scatter(name="Sell Signal", x=sell_signals["datetime"], y=sell_signals['close'], mode='markers', marker=dict(color='red', symbol='triangle-down', size=10)))

    # Visualize patterns
    if 'ascending_triangle' in df.columns:
        ascending_triangle = df[df['ascending_triangle']]
        fig.add_trace(go.Scatter(name="Ascending Triangle", x=ascending_triangle["datetime"], y=ascending_triangle['high'], mode='markers+lines', line=dict(color='cyan', dash='dot'), marker=dict(color='cyan', symbol='diamond', size=10)))

    if 'descending_triangle' in df.columns:
        descending_triangle = df[df['descending_triangle']]
        fig.add_trace(go.Scatter(name="Descending Triangle", x=descending_triangle["datetime"], y=descending_triangle['low'], mode='markers+lines', line=dict(color='magenta', dash='dot'), marker=dict(color='magenta', symbol='diamond', size=10)))

    if 'rounding_bottom' in df.columns:
        rounding_bottom = df[df['rounding_bottom']]
        fig.add_trace(go.Scatter(name="Rounding Bottom", x=rounding_bottom["datetime"], y=rounding_bottom['close'], mode='markers+lines', line=dict(color='yellow', dash='dot'), marker=dict(color='yellow', symbol='circle', size=10)))

    fig.update_layout(
        xaxis_rangeslider_visible=False, 
        legend=dict(orientation="h", entrywidth=100, yanchor="bottom", y=1.01, xanchor="center", x=0.5),
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
            showgrid=False,
        ),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="minute", stepmode="backward"),
                    dict(count=5, label="5m", step="minute", stepmode="backward"),
                    dict(count=15, label="15m", step="minute", stepmode="backward"),
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            type="date"
        )
    )
    currency_plot.plotly_chart(fig, use_container_width=True)

    # Display the Kafka-consumed data table
    # kafka_df = pd.DataFrame(processed_data)
    # if not kafka_df.empty:
    #    kafka_table.dataframe(kafka_df, width=1200, height=400)

    # Display the current trend
    if df['close'].iloc[-1] > df['close'].iloc[0]:
        trend = "Uptrend"
    else:
        trend = "Downtrend"

    st.sidebar.markdown(f"**Current Trend:** {trend}")

    # Pause before next UI refresh iteration
    time.sleep(refresh_interval)
    i += 1
