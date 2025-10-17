"""
Interactive Visualizer Analyst
Generates comprehensive dashboards and custom visualizations based on user requests
"""

# CRITICAL: Set matplotlib backend BEFORE importing pyplot to avoid Tkinter crashes in Flask
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from pathlib import Path
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import the existing comprehensive chart generator
from tradingagents.agents.generators.comprehensive_charts import create_comprehensive_trading_chart


def create_visualizer_analyst(llm, toolkit):
    """
    Create interactive visualizer analyst

    Features:
    - Default: Generate comprehensive 12-panel dashboard
    - Custom: Generate specific charts based on user requests
    - Interactive: Respond to user feedback for chart adjustments
    """

    # System prompt for understanding visualization requests
    VISUALIZATION_UNDERSTANDING_PROMPT = """You are a financial visualization expert. Analyze the user's request and determine what charts to generate.

User Request: {user_request}

Available chart types:
1. **dashboard** - Comprehensive 12-panel technical analysis dashboard
2. **price** - Price chart with moving averages
3. **rsi** - RSI indicator only
4. **macd** - MACD indicator only
5. **bollinger** - Bollinger Bands with price
6. **volume** - Volume analysis
7. **returns** - Returns distribution
8. **volatility** - Volatility analysis
9. **atr** - Average True Range
10. **risk_metrics** - Risk metrics table
11. **custom** - Custom combination of specific indicators

Respond in JSON format:
{{
    "chart_type": "dashboard|price|rsi|macd|bollinger|volume|returns|volatility|atr|risk_metrics|custom",
    "indicators": ["list", "of", "specific", "indicators", "if", "custom"],
    "time_period": "6mo|1y|2y|5y",
    "additional_preferences": {{
        "show_signals": true/false,
        "highlight_levels": true/false,
        "compare_stocks": ["AAPL", "MSFT"] if comparison requested
    }}
}}

If the request is unclear or just says "visualize" or "chart", default to "dashboard".
"""

    def visualizer_analyst_node(state):
        """Generate visualizations based on user preferences"""

        company_of_interest = state["company_of_interest"]
        trade_date = state["trade_date"]
        user_preferences = state.get("user_preferences", {})

        print(f"[VISUALIZER] Starting visualization for {company_of_interest}...", flush=True)

        # Extract visualization request from user preferences
        viz_request = extract_visualization_request(user_preferences)

        # Determine what to visualize
        if viz_request and viz_request.strip():
            print(f"[VISUALIZER] Custom request detected: {viz_request[:100]}...", flush=True)

            # Use LLM to understand the request
            try:
                prompt = ChatPromptTemplate.from_template(VISUALIZATION_UNDERSTANDING_PROMPT)
                llm_input = prompt.format(user_request=viz_request)
                response = llm.invoke(llm_input)

                # Parse LLM response
                viz_config = parse_llm_response(response.content)
                print(f"[VISUALIZER] LLM understood request as: {viz_config.get('chart_type', 'dashboard')}", flush=True)

            except Exception as e:
                print(f"[VISUALIZER] LLM parsing failed: {e}. Using default dashboard.", flush=True)
                viz_config = {"chart_type": "dashboard"}
        else:
            print(f"[VISUALIZER] No custom request. Generating default dashboard.", flush=True)
            viz_config = {"chart_type": "dashboard"}

        # Generate the visualization
        try:
            chart_type = viz_config.get("chart_type", "dashboard")

            if chart_type == "dashboard" or chart_type not in ["price", "rsi", "macd", "bollinger", "volume", "returns", "volatility", "atr", "risk_metrics"]:
                # Generate comprehensive dashboard (default)
                chart_path = create_comprehensive_trading_chart(company_of_interest, trade_date)
                report = generate_dashboard_report(company_of_interest, trade_date, chart_path)

            else:
                # Generate custom chart based on specific request
                chart_path = generate_custom_chart(
                    company_of_interest,
                    trade_date,
                    chart_type,
                    viz_config
                )
                report = generate_custom_chart_report(company_of_interest, chart_type, chart_path)

            # Prepare response
            if chart_path:
                report += f"\n\n**Chart saved to**: `{chart_path}`"
            else:
                report += "\n\n*Note: Chart generation encountered an issue. Please check the logs.*"

            print(f"[VISUALIZER] Visualization complete. Chart: {chart_path}", flush=True)

            return {
                "visualizer_report": report,
                "chart_path": str(chart_path) if chart_path else None,
                "messages": [HumanMessage(content=report)]
            }

        except Exception as e:
            print(f"[VISUALIZER] Error generating visualization: {e}", flush=True)
            import traceback
            traceback.print_exc()

            error_report = f"""## Visualization Error

Unable to generate visualization for {company_of_interest}.

**Error**: {str(e)}

**Suggestions**:
- Check if the ticker symbol is correct
- Verify internet connection for data fetching
- Try again or request a different visualization type
"""
            return {
                "visualizer_report": error_report,
                "chart_path": None,
                "messages": [HumanMessage(content=error_report)]
            }

    return visualizer_analyst_node


def extract_visualization_request(user_preferences):
    """Extract visualization-related requests from user preferences"""
    if not user_preferences:
        return ""

    # Check for visualization keywords
    viz_keywords = ["chart", "plot", "graph", "visualize", "visualization", "show me", "draw", "display"]

    # If preferences is a dict, check various fields
    if isinstance(user_preferences, dict):
        custom_instructions = user_preferences.get("custom_instructions", "")
        focus_areas = user_preferences.get("focus_areas", [])

        # Combine all relevant text
        request_text = custom_instructions
        if focus_areas and isinstance(focus_areas, list):
            request_text += " " + " ".join(focus_areas)

        return request_text

    # If it's a string, return as-is
    return str(user_preferences)


def parse_llm_response(response_text):
    """Parse LLM JSON response"""
    try:
        # Try to extract JSON from response
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        elif "{" in response_text:
            # Find first { and last }
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            json_str = response_text[start:end]
        else:
            return {"chart_type": "dashboard"}

        config = json.loads(json_str)
        return config

    except Exception as e:
        print(f"[VISUALIZER] JSON parsing failed: {e}", flush=True)
        return {"chart_type": "dashboard"}


def generate_dashboard_report(ticker, date, chart_path):
    """Generate report for comprehensive dashboard"""

    report = f"""## 📊 Comprehensive Technical Analysis Dashboard

**Ticker**: {ticker}
**Date**: {date}

I've generated a comprehensive 12-panel technical analysis dashboard with the following visualizations:

### Panel Overview:

1. **📈 Candlestick Chart** - Price action with SMA 20/50 and EMA 12, plus volume bars
2. **📊 RSI Indicator** - Relative Strength Index with overbought (70) and oversold (30) levels
3. **📉 MACD** - Moving Average Convergence Divergence with signal line and histogram
4. **📊 Bollinger Bands** - Volatility bands showing price boundaries
5. **📊 Returns Distribution** - Histogram of daily returns with confidence intervals
6. **📈 Volatility Forecast** - Rolling volatility with confidence bands
7. **📊 Volume Analysis** - Trading volume with moving average trend
8. **📍 Support & Resistance** - Key price levels with recent highs/lows
9. **📈 Cumulative Returns** - Performance over time
10. **📊 ATR** - Average True Range measuring volatility
11. **📋 Risk Metrics** - VaR, CVaR, Sharpe Ratio, Max Drawdown
12. **🎯 Trading Signals** - Entry/exit recommendations with price targets

### Interactive Features:

You can request specific charts or customizations:
- "Show me just the RSI"
- "Plot MACD and Bollinger Bands only"
- "Compare with AAPL"
- "Show 1-year price chart with volume"

The dashboard provides a holistic view of technical indicators, risk metrics, and actionable signals for informed trading decisions.
"""

    return report


def generate_custom_chart(ticker, date, chart_type, config):
    """Generate a custom chart based on specific request"""

    results_dir = Path(f"results/{ticker}/{date}")
    results_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Fetch data
        print(f"[VISUALIZER] Fetching data for {ticker}...", flush=True)
        time_period = config.get("time_period", "6mo")
        stock_data = yf.download(ticker, period=time_period, progress=False, timeout=15)

        if stock_data.empty:
            return None

        # Handle MultiIndex columns
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = [col[0] for col in stock_data.columns]

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.suptitle(f'{ticker} - {chart_type.upper()} Analysis - {date}',
                    fontsize=16, fontweight='bold')

        # Generate specific chart based on type
        if chart_type == "price":
            plot_price_chart(ax, stock_data, ticker)
        elif chart_type == "rsi":
            plot_rsi_chart(ax, stock_data, ticker)
        elif chart_type == "macd":
            plot_macd_chart(ax, stock_data, ticker)
        elif chart_type == "bollinger":
            plot_bollinger_chart(ax, stock_data, ticker)
        elif chart_type == "volume":
            plot_volume_chart(ax, stock_data, ticker)
        elif chart_type == "returns":
            plot_returns_chart(ax, stock_data, ticker)
        elif chart_type == "volatility":
            plot_volatility_chart(ax, stock_data, ticker)
        elif chart_type == "atr":
            plot_atr_chart(ax, stock_data, ticker)
        else:
            # Default to price
            plot_price_chart(ax, stock_data, ticker)

        # Save
        chart_filename = f"{ticker}_{chart_type}_chart_{date}.png"
        chart_path = results_dir / chart_filename
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"[VISUALIZER] Custom chart saved: {chart_path}", flush=True)
        return chart_path

    except Exception as e:
        print(f"[VISUALIZER] Custom chart generation failed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return None


def plot_price_chart(ax, data, ticker):
    """Plot price with moving averages"""
    ax.plot(data.index, data['Close'], label='Close Price', linewidth=2, color='#2C3E50')

    # Add moving averages
    sma_20 = data['Close'].rolling(window=20).mean()
    sma_50 = data['Close'].rolling(window=50).mean()

    ax.plot(data.index, sma_20, label='SMA 20', alpha=0.7, linestyle='--', color='#3498DB')
    ax.plot(data.index, sma_50, label='SMA 50', alpha=0.7, linestyle='--', color='#E67E22')

    ax.set_title(f'{ticker} Price Chart with Moving Averages', fontsize=14, fontweight='bold')
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)


def plot_rsi_chart(ax, data, ticker):
    """Plot RSI indicator"""
    # Calculate RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    ax.plot(data.index, rsi, linewidth=2, color='#8E44AD')
    ax.axhline(y=70, color='#E74C3C', linestyle='--', alpha=0.7, label='Overbought (70)')
    ax.axhline(y=30, color='#27AE60', linestyle='--', alpha=0.7, label='Oversold (30)')
    ax.fill_between(data.index, 30, 70, alpha=0.1, color='#95A5A6')

    ax.set_title(f'{ticker} RSI Indicator', fontsize=14, fontweight='bold')
    ax.set_ylabel('RSI', fontsize=12)
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_macd_chart(ax, data, ticker):
    """Plot MACD indicator"""
    # Calculate MACD
    ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal

    ax.plot(data.index, macd, label='MACD', linewidth=2, color='#3498DB')
    ax.plot(data.index, signal, label='Signal', linewidth=2, color='#E67E22')
    ax.bar(data.index, histogram, label='Histogram', alpha=0.3, color='#95A5A6')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    ax.set_title(f'{ticker} MACD Indicator', fontsize=14, fontweight='bold')
    ax.set_ylabel('MACD', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_bollinger_chart(ax, data, ticker):
    """Plot Bollinger Bands"""
    # Calculate Bollinger Bands
    sma = data['Close'].rolling(window=20).mean()
    std = data['Close'].rolling(window=20).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)

    ax.plot(data.index, data['Close'], label='Close Price', linewidth=2, color='#2C3E50')
    ax.plot(data.index, sma, label='SMA 20', linewidth=2, color='#3498DB', linestyle='--')
    ax.plot(data.index, upper_band, label='Upper Band', linewidth=1.5, color='#E74C3C', linestyle=':')
    ax.plot(data.index, lower_band, label='Lower Band', linewidth=1.5, color='#27AE60', linestyle=':')
    ax.fill_between(data.index, lower_band, upper_band, alpha=0.1, color='#95A5A6')

    ax.set_title(f'{ticker} Bollinger Bands', fontsize=14, fontweight='bold')
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_volume_chart(ax, data, ticker):
    """Plot volume analysis"""
    colors = ['#27AE60' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#E74C3C'
              for i in range(len(data))]

    ax.bar(data.index, data['Volume']/1e6, color=colors, alpha=0.6)

    # Add volume moving average
    vol_ma = data['Volume'].rolling(window=20).mean()
    ax.plot(data.index, vol_ma/1e6, label='20-day MA', linewidth=2, color='#3498DB')

    ax.set_title(f'{ticker} Volume Analysis', fontsize=14, fontweight='bold')
    ax.set_ylabel('Volume (Millions)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_returns_chart(ax, data, ticker):
    """Plot returns distribution"""
    returns = data['Close'].pct_change().dropna() * 100

    ax.hist(returns, bins=50, alpha=0.7, color='#3498DB', edgecolor='black')
    ax.axvline(x=returns.mean(), color='#E74C3C', linestyle='--', linewidth=2, label=f'Mean: {returns.mean():.2f}%')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1)

    ax.set_title(f'{ticker} Daily Returns Distribution', fontsize=14, fontweight='bold')
    ax.set_xlabel('Return (%)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_volatility_chart(ax, data, ticker):
    """Plot volatility analysis"""
    returns = data['Close'].pct_change()
    volatility = returns.rolling(window=20).std() * np.sqrt(252) * 100

    ax.plot(data.index, volatility, linewidth=2, color='#8E44AD')
    ax.fill_between(data.index, volatility, alpha=0.3, color='#8E44AD')

    avg_vol = volatility.mean()
    ax.axhline(y=avg_vol, color='#E74C3C', linestyle='--', linewidth=2, label=f'Avg: {avg_vol:.1f}%')

    ax.set_title(f'{ticker} Annualized Volatility', fontsize=14, fontweight='bold')
    ax.set_ylabel('Volatility (%)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)


def plot_atr_chart(ax, data, ticker):
    """Plot ATR indicator"""
    # Calculate ATR
    high_low = data['High'] - data['Low']
    high_close = abs(data['High'] - data['Close'].shift(1))
    low_close = abs(data['Low'] - data['Close'].shift(1))
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=14).mean()

    ax.plot(data.index, atr, linewidth=2, color='#9B59B6')
    ax.fill_between(data.index, atr, alpha=0.3, color='#9B59B6')

    avg_atr = atr.mean()
    ax.axhline(y=avg_atr, color='#E74C3C', linestyle='--', linewidth=2, label=f'Avg ATR: ${avg_atr:.2f}')

    ax.set_title(f'{ticker} Average True Range (ATR)', fontsize=14, fontweight='bold')
    ax.set_ylabel('ATR ($)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)


def generate_custom_chart_report(ticker, chart_type, chart_path):
    """Generate report for custom chart"""

    chart_descriptions = {
        "price": "Price chart with 20-day and 50-day simple moving averages",
        "rsi": "Relative Strength Index (RSI) showing overbought and oversold levels",
        "macd": "Moving Average Convergence Divergence (MACD) with signal line and histogram",
        "bollinger": "Bollinger Bands showing volatility and price boundaries",
        "volume": "Trading volume analysis with 20-day moving average",
        "returns": "Distribution of daily returns",
        "volatility": "Rolling 20-day annualized volatility",
        "atr": "Average True Range (ATR) measuring price volatility"
    }

    description = chart_descriptions.get(chart_type, "Custom chart")

    report = f"""## 📊 {chart_type.upper()} Chart

**Ticker**: {ticker}
**Chart Type**: {description}

I've generated a focused visualization for the **{chart_type.upper()}** indicator.

### What This Chart Shows:

{get_chart_explanation(chart_type)}

### Interactive Options:

- Request the full dashboard: "Show me the complete dashboard"
- Request other indicators: "Show me RSI and MACD together"
- Compare with other stocks: "Compare {ticker} with AAPL"
- Change time period: "Show 1-year {chart_type} chart"
"""

    return report


def get_chart_explanation(chart_type):
    """Get detailed explanation for each chart type"""

    explanations = {
        "price": """
- **Close Price**: The actual closing price of the stock
- **SMA 20**: 20-day simple moving average (short-term trend)
- **SMA 50**: 50-day simple moving average (medium-term trend)
- **Trading Signal**: When SMA 20 crosses above SMA 50 (bullish), or below (bearish)
""",
        "rsi": """
- **RSI Value**: Ranges from 0 to 100
- **Overbought Zone**: RSI > 70 (potential sell signal)
- **Oversold Zone**: RSI < 30 (potential buy signal)
- **Neutral Zone**: RSI between 30-70 (normal conditions)
- **Divergence**: When price makes new highs/lows but RSI doesn't (reversal signal)
""",
        "macd": """
- **MACD Line**: Difference between 12-day and 26-day EMA
- **Signal Line**: 9-day EMA of MACD
- **Histogram**: Difference between MACD and Signal (momentum strength)
- **Bullish Signal**: MACD crosses above Signal line
- **Bearish Signal**: MACD crosses below Signal line
""",
        "bollinger": """
- **Middle Band**: 20-day SMA
- **Upper Band**: Middle Band + (2 × Standard Deviation)
- **Lower Band**: Middle Band - (2 × Standard Deviation)
- **Squeeze**: Bands narrow (low volatility, potential breakout)
- **Expansion**: Bands widen (high volatility, strong trend)
- **Price touches upper band**: Overbought (potential reversal)
- **Price touches lower band**: Oversold (potential bounce)
""",
        "volume": """
- **Volume Bars**: Green = up day, Red = down day
- **Volume MA**: 20-day average volume
- **High Volume**: Confirms price moves (strong trend)
- **Low Volume**: Weak conviction (potential reversal)
- **Volume Spike**: Important event or news
""",
        "returns": """
- **Distribution Shape**: Shows how returns are spread
- **Mean Return**: Average daily return
- **Tails**: Extreme positive/negative returns
- **Normal Distribution**: Bell curve shape = stable returns
- **Fat Tails**: Large extreme moves = high risk
""",
        "volatility": """
- **Rolling Volatility**: 20-day annualized volatility
- **High Volatility**: Large price swings (higher risk/reward)
- **Low Volatility**: Stable prices (lower risk/reward)
- **Volatility Spikes**: Market uncertainty or news events
""",
        "atr": """
- **ATR Value**: Average daily price range in dollars
- **High ATR**: Large price movements (volatile stock)
- **Low ATR**: Small price movements (stable stock)
- **Use Case**: Position sizing and stop-loss placement
- **Example**: If ATR = $5, consider stop-loss 2×ATR = $10 away
"""
    }

    return explanations.get(chart_type, "Custom visualization based on your request.")
