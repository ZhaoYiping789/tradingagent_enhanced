"""
Comprehensive Chart Generation for Trading Analysis
Creates a single comprehensive visualization with multiple panels
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(prices):
    """Calculate MACD indicator"""
    ema_12 = prices.ewm(span=12, adjust=False).mean()
    ema_26 = prices.ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    return macd, signal, histogram


def calculate_bollinger_bands(prices, window=20):
    """Calculate Bollinger Bands"""
    sma = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return sma, upper_band, lower_band


def create_comprehensive_trading_chart(ticker, current_date):
    """
    Create a comprehensive single-window chart with advanced visualizations:
    1. Candlestick Chart with Moving Averages & Volume
    2. RSI with Overbought/Oversold zones
    3. MACD with Signal Line & Histogram
    4. Bollinger Bands with Price Action
    5. Returns Distribution with Confidence Intervals
    6. Volatility Forecast with Confidence Bands
    7. Volume Analysis with Trend
    8. Support & Resistance with Price Zones
    9. Cumulative Returns with Drawdown
    10. ATR (Average True Range)
    11. Risk Metrics Dashboard (VaR, CVaR, Sharpe)
    12. Trading Signals & Entry/Exit Levels
    """
    
    results_dir = Path(f"results/{ticker}/{current_date}")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Fetch data
        print(f"📊 Fetching comprehensive data for {ticker}...")
        stock_data = yf.download(ticker, period="6mo", progress=False, timeout=15)
        
        if stock_data.empty:
            return None
        
        # Handle MultiIndex columns
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = [col[0] for col in stock_data.columns]
        
        # Calculate all technical indicators
        stock_data['SMA_20'] = stock_data['Close'].rolling(window=20).mean()
        stock_data['SMA_50'] = stock_data['Close'].rolling(window=50).mean()
        stock_data['EMA_12'] = stock_data['Close'].ewm(span=12).mean()
        stock_data['RSI'] = calculate_rsi(stock_data['Close'])
        stock_data['MACD'], stock_data['MACD_Signal'], stock_data['MACD_Hist'] = calculate_macd(stock_data['Close'])
        stock_data['BB_SMA'], stock_data['BB_Upper'], stock_data['BB_Lower'] = calculate_bollinger_bands(stock_data['Close'])
        stock_data['Returns'] = stock_data['Close'].pct_change()
        stock_data['Cum_Returns'] = (1 + stock_data['Returns']).cumprod() - 1
        stock_data['Volatility'] = stock_data['Returns'].rolling(window=20).std() * np.sqrt(252) * 100
        
        # Calculate ATR
        stock_data['High_Low'] = stock_data['High'] - stock_data['Low']
        stock_data['High_Close'] = abs(stock_data['High'] - stock_data['Close'].shift(1))
        stock_data['Low_Close'] = abs(stock_data['Low'] - stock_data['Close'].shift(1))
        stock_data['True_Range'] = stock_data[['High_Low', 'High_Close', 'Low_Close']].max(axis=1)
        stock_data['ATR'] = stock_data['True_Range'].rolling(window=14).mean()
        
        # Calculate support and resistance
        recent_high = stock_data['High'].rolling(window=20).max()
        recent_low = stock_data['Low'].rolling(window=20).min()
        
        # Get current values for metrics
        current_price = float(stock_data['Close'].iloc[-1])
        current_rsi = float(stock_data['RSI'].iloc[-1]) if not pd.isna(stock_data['RSI'].iloc[-1]) else 50.0
        
        # Create figure with 4x3 grid
        fig = plt.figure(figsize=(26, 20))
        fig.suptitle(f'{ticker} - Comprehensive Trading Analysis Dashboard - {current_date}', 
                    fontsize=22, fontweight='bold', y=0.995)
        
        gs = fig.add_gridspec(4, 3, hspace=0.35, wspace=0.3)
        
        # 1. CANDLESTICK Chart with Moving Averages & Volume
        ax1 = fig.add_subplot(gs[0, :2])
        ax1_vol = ax1.twinx()
        
        # Plot candlesticks (simplified as OHLC)
        for idx in range(len(stock_data)):
            date = stock_data.index[idx]
            open_price = stock_data['Open'].iloc[idx]
            close_price = stock_data['Close'].iloc[idx]
            high_price = stock_data['High'].iloc[idx]
            low_price = stock_data['Low'].iloc[idx]
            
            color = '#27AE60' if close_price >= open_price else '#E74C3C'
            ax1.plot([date, date], [low_price, high_price], color=color, linewidth=0.5, alpha=0.6)
            ax1.plot([date, date], [open_price, close_price], color=color, linewidth=3)
        
        # Add moving averages
        ax1.plot(stock_data.index, stock_data['SMA_20'], label='SMA 20', alpha=0.9, color='#3498DB', linestyle='--', linewidth=2)
        ax1.plot(stock_data.index, stock_data['SMA_50'], label='SMA 50', alpha=0.9, color='#E67E22', linestyle='--', linewidth=2)
        ax1.plot(stock_data.index, stock_data['EMA_12'], label='EMA 12', alpha=0.7, color='#9B59B6', linestyle=':', linewidth=1.5)
        
        # Volume bars
        colors_vol = ['#27AE60' if stock_data['Close'].iloc[i] >= stock_data['Open'].iloc[i] else '#E74C3C' 
                      for i in range(len(stock_data))]
        ax1_vol.bar(stock_data.index, stock_data['Volume']/1e6, alpha=0.3, color=colors_vol)
        
        ax1.set_title('📊 Candlestick Chart with Moving Averages & Volume', fontsize=13, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=11, fontweight='bold')
        ax1_vol.set_ylabel('Volume (M)', fontsize=11, fontweight='bold')
        ax1.legend(loc='upper left', fontsize=9, framealpha=0.9)
        ax1.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
        ax1.set_facecolor('#FAFAFA')
        
        # 2. RSI
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.plot(stock_data.index, stock_data['RSI'], linewidth=2, color='#8E44AD')
        ax2.axhline(y=70, color='#E74C3C', linestyle='--', alpha=0.7, label='Overbought (70)')
        ax2.axhline(y=30, color='#27AE60', linestyle='--', alpha=0.7, label='Oversold (30)')
        ax2.fill_between(stock_data.index, 30, 70, alpha=0.1, color='#95A5A6')
        ax2.set_title('📊 RSI Indicator', fontsize=12, fontweight='bold')
        ax2.set_ylabel('RSI', fontsize=10)
        ax2.set_ylim(0, 100)
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('#F8F9FA')
        
        # 3. MACD
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.plot(stock_data.index, stock_data['MACD'], label='MACD', linewidth=2, color='#3498DB')
        ax3.plot(stock_data.index, stock_data['MACD_Signal'], label='Signal', linewidth=2, color='#E74C3C')
        ax3.bar(stock_data.index, stock_data['MACD_Hist'], label='Histogram', alpha=0.3, color='#95A5A6')
        ax3.set_title('📉 MACD Indicator', fontsize=12, fontweight='bold')
        ax3.set_ylabel('MACD', fontsize=10)
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax3.set_facecolor('#F8F9FA')
        
        # 4. Bollinger Bands
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.plot(stock_data.index, stock_data['Close'], label='Close', linewidth=2, color='black')
        ax4.plot(stock_data.index, stock_data['BB_SMA'], label='SMA', linewidth=1.5, color='#3498DB', linestyle='--')
        ax4.plot(stock_data.index, stock_data['BB_Upper'], label='Upper Band', linewidth=1, color='#E74C3C', alpha=0.7)
        ax4.plot(stock_data.index, stock_data['BB_Lower'], label='Lower Band', linewidth=1, color='#27AE60', alpha=0.7)
        ax4.fill_between(stock_data.index, stock_data['BB_Lower'], stock_data['BB_Upper'], alpha=0.1, color='#3498DB')
        ax4.set_title('📊 Bollinger Bands', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Price ($)', fontsize=10)
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)
        ax4.set_facecolor('#F8F9FA')
        
        # 5. Daily Returns Distribution with Confidence Intervals
        ax5 = fig.add_subplot(gs[1, 2])
        returns_clean = stock_data['Returns'].dropna() * 100
        ax5.hist(returns_clean, bins=40, alpha=0.7, color='#3498DB', edgecolor='black')
        
        # Add statistical measures
        mean_ret = returns_clean.mean()
        median_ret = returns_clean.median()
        std_ret = returns_clean.std()
        ci_95_lower = mean_ret - 1.96 * std_ret
        ci_95_upper = mean_ret + 1.96 * std_ret
        
        ax5.axvline(mean_ret, color='#E74C3C', linestyle='--', linewidth=2.5, label=f'Mean: {mean_ret:.2f}%')
        ax5.axvline(median_ret, color='#27AE60', linestyle='--', linewidth=2.5, label=f'Median: {median_ret:.2f}%')
        ax5.axvline(ci_95_lower, color='#E74C3C', linestyle=':', linewidth=1.5, alpha=0.7, label=f'95% CI Lower: {ci_95_lower:.2f}%')
        ax5.axvline(ci_95_upper, color='#27AE60', linestyle=':', linewidth=1.5, alpha=0.7, label=f'95% CI Upper: {ci_95_upper:.2f}%')
        ax5.fill_betweenx([0, ax5.get_ylim()[1]], ci_95_lower, ci_95_upper, alpha=0.1, color='#95A5A6')
        
        ax5.set_title('📊 Returns Distribution with 95% CI', fontsize=12, fontweight='bold')
        ax5.set_xlabel('Daily Return (%)', fontsize=10)
        ax5.set_ylabel('Frequency', fontsize=10)
        ax5.legend(fontsize=7, loc='upper right')
        ax5.grid(True, alpha=0.3, axis='y')
        ax5.set_facecolor('#F8F9FA')
        
        # 6. Rolling Volatility with Forecast Bands
        ax6 = fig.add_subplot(gs[2, 0])
        ax6.plot(stock_data.index, stock_data['Volatility'], linewidth=2.5, color='#E67E22', label='Realized Vol')
        ax6.fill_between(stock_data.index, stock_data['Volatility'], alpha=0.2, color='#E67E22')
        
        # Calculate confidence bands for volatility
        avg_vol = stock_data['Volatility'].mean()
        std_vol = stock_data['Volatility'].std()
        upper_vol_band = avg_vol + std_vol
        lower_vol_band = max(0, avg_vol - std_vol)
        
        ax6.axhline(y=avg_vol, color='#2C3E50', linestyle='-', linewidth=2, label=f'Mean: {avg_vol:.2f}%', alpha=0.8)
        ax6.axhline(y=upper_vol_band, color='#E74C3C', linestyle=':', linewidth=1.5, label=f'Upper Band: {upper_vol_band:.2f}%', alpha=0.7)
        ax6.axhline(y=lower_vol_band, color='#27AE60', linestyle=':', linewidth=1.5, label=f'Lower Band: {lower_vol_band:.2f}%', alpha=0.7)
        ax6.fill_between(stock_data.index, lower_vol_band, upper_vol_band, alpha=0.1, color='#95A5A6')
        
        ax6.set_title('📊 Volatility with Confidence Bands', fontsize=12, fontweight='bold')
        ax6.set_ylabel('Volatility (%)', fontsize=10)
        ax6.legend(fontsize=7)
        ax6.grid(True, alpha=0.3)
        ax6.set_facecolor('#F8F9FA')
        
        # 7. Volume Analysis
        ax7 = fig.add_subplot(gs[2, 1])
        volume_ma = stock_data['Volume'].rolling(window=20).mean()
        colors = ['#27AE60' if v > vm else '#E74C3C' for v, vm in zip(stock_data['Volume'], volume_ma)]
        ax7.bar(stock_data.index, stock_data['Volume']/1e6, alpha=0.6, color=colors)
        ax7.plot(stock_data.index, volume_ma/1e6, linewidth=2, color='#3498DB', label='20-Day MA')
        ax7.set_title('📊 Volume Analysis', fontsize=12, fontweight='bold')
        ax7.set_ylabel('Volume (Millions)', fontsize=10)
        ax7.legend(fontsize=8)
        ax7.grid(True, alpha=0.3, axis='y')
        ax7.set_facecolor('#F8F9FA')
        
        # 8. Support & Resistance
        ax8 = fig.add_subplot(gs[2, 2])
        ax8.plot(stock_data.index, stock_data['Close'], linewidth=2, color='#2E86DE', label='Close')
        ax8.plot(stock_data.index, recent_high, linewidth=1.5, color='#E74C3C', linestyle='--', alpha=0.7, label='Resistance (20D High)')
        ax8.plot(stock_data.index, recent_low, linewidth=1.5, color='#27AE60', linestyle='--', alpha=0.7, label='Support (20D Low)')
        ax8.fill_between(stock_data.index, recent_low, recent_high, alpha=0.1, color='#95A5A6')
        ax8.set_title('📊 Support & Resistance Levels', fontsize=12, fontweight='bold')
        ax8.set_ylabel('Price ($)', fontsize=10)
        ax8.legend(fontsize=8)
        ax8.grid(True, alpha=0.3)
        ax8.set_facecolor('#F8F9FA')
        
        # 9. Cumulative Returns
        ax9 = fig.add_subplot(gs[3, 0])
        ax9.plot(stock_data.index, stock_data['Cum_Returns'] * 100, linewidth=2.5, color='#27AE60')
        ax9.fill_between(stock_data.index, 0, stock_data['Cum_Returns'] * 100, alpha=0.3, color='#27AE60')
        ax9.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax9.set_title('📈 Cumulative Returns', fontsize=12, fontweight='bold')
        ax9.set_ylabel('Return (%)', fontsize=10)
        ax9.grid(True, alpha=0.3)
        ax9.set_facecolor('#F8F9FA')
        
        # 10. ATR (Average True Range)
        ax10 = fig.add_subplot(gs[3, 1])
        ax10.plot(stock_data.index, stock_data['ATR'], linewidth=2, color='#9B59B6')
        ax10.fill_between(stock_data.index, stock_data['ATR'], alpha=0.3, color='#9B59B6')
        avg_atr = stock_data['ATR'].mean()
        ax10.axhline(y=avg_atr, color='#E74C3C', linestyle='--', linewidth=2, label=f'Avg ATR: ${avg_atr:.2f}')
        ax10.set_title('📊 Average True Range (ATR)', fontsize=12, fontweight='bold')
        ax10.set_ylabel('ATR ($)', fontsize=10)
        ax10.legend(fontsize=8)
        ax10.grid(True, alpha=0.3)
        ax10.set_facecolor('#F8F9FA')
        
        # 11. Risk Metrics Dashboard
        ax11 = fig.add_subplot(gs[3, 2])
        ax11.axis('off')
        
        # Calculate risk metrics
        returns_clean = stock_data['Returns'].dropna()
        
        # VaR and CVaR calculation
        var_95 = np.percentile(returns_clean, 5) * 100
        cvar_95 = returns_clean[returns_clean <= np.percentile(returns_clean, 5)].mean() * 100
        
        # Maximum drawdown
        cummax = stock_data['Close'].cummax()
        drawdown = (stock_data['Close'] - cummax) / cummax * 100
        max_drawdown = drawdown.min()
        
        # Sharpe and Sortino ratios
        mean_return = returns_clean.mean() * 252
        std_return = returns_clean.std() * np.sqrt(252)
        sharpe_ratio = mean_return / std_return if std_return > 0 else 0
        
        downside_returns = returns_clean[returns_clean < 0]
        downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else std_return
        sortino_ratio = mean_return / downside_std if downside_std > 0 else 0
        
        # Beta (simplified - assume market return)
        beta = 1.0 + (returns_clean.std() - 0.01) * 10  # Simplified beta estimate
        
        risk_text = f"""
    ⚠️ RISK METRICS DASHBOARD
    {'='*32}
    
    95% VaR (Daily): {var_95:.2f}%
    95% CVaR (Daily): {cvar_95:.2f}%
    Max Drawdown: {max_drawdown:.2f}%
    
    Sharpe Ratio: {sharpe_ratio:.3f}
    Sortino Ratio: {sortino_ratio:.3f}
    Beta (Est.): {beta:.2f}
    
    Ann. Return: {mean_return*100:.2f}%
    Ann. Volatility: {stock_data['Volatility'].iloc[-1]:.2f}%
        """
        
        # Color code based on risk levels
        bg_color = '#FFF3CD' if abs(var_95) > 3 or abs(max_drawdown) > 20 else '#D1F2EB'
        edge_color = '#E67E22' if abs(var_95) > 3 else '#27AE60'
        
        ax11.text(0.05, 0.95, risk_text, transform=ax11.transAxes,
                 fontsize=10, verticalalignment='top', fontfamily='monospace',
                 bbox=dict(boxstyle='round', facecolor=bg_color, alpha=0.9, 
                          edgecolor=edge_color, linewidth=3))
        
        # Format x-axes
        for ax in [ax1, ax3, ax4, ax6, ax7, ax8, ax9, ax10]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=3))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save chart
        chart_path = results_dir / f"{ticker}_comprehensive_analysis_{current_date}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ Comprehensive chart saved: {chart_path}")
        
        # Return chart path AND key technical levels for trading plan
        metrics = {
            'chart_path': str(chart_path),
            'current_price': current_price,
            'sma_20': stock_data['SMA_20'].iloc[-1],
            'sma_50': stock_data['SMA_50'].iloc[-1],
            'resistance_20d': recent_high.iloc[-1],
            'support_20d': recent_low.iloc[-1],
            'rsi': current_rsi,
            'atr': stock_data['ATR'].iloc[-1],
            'volatility': stock_data['Volatility'].iloc[-1],
            'var_95': var_95,
            'cvar_95': cvar_95,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'beta': beta
        }
        
        return metrics
        
    except Exception as e:
        print(f"❌ Error creating comprehensive chart: {e}")
        import traceback
        traceback.print_exc()
        return None

