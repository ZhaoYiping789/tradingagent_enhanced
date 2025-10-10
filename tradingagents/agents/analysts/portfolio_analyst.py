from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any


def create_portfolio_analyst(llm, toolkit):
    """Create a portfolio analyst that compares multiple stocks and provides portfolio recommendations."""
    
    def portfolio_analyst_node(state):
        current_date = state["trade_date"]
        primary_ticker = state["company_of_interest"]
        
        # Define comparison tickers based on primary ticker
        comparison_tickers = get_comparison_tickers(primary_ticker)
        all_tickers = [primary_ticker] + comparison_tickers
        
        try:
            # Fetch data for all tickers
            portfolio_data = {}
            for ticker in all_tickers:
                try:
                    stock_data = yf.download(ticker, period="1y", progress=False)
                    if not stock_data.empty:
                        portfolio_data[ticker] = analyze_stock_metrics(stock_data, ticker)
                except:
                    continue
            
            if len(portfolio_data) < 2:
                return {
                    "messages": [],
                    "portfolio_report": "Insufficient data for portfolio comparison analysis."
                }
            
            # Perform comparative analysis
            comparison_df = pd.DataFrame(portfolio_data).T
            
            # Calculate portfolio metrics
            portfolio_analysis = perform_portfolio_analysis(portfolio_data, all_tickers)
            
            # Generate recommendations
            recommendations = generate_portfolio_recommendations(comparison_df, primary_ticker)
            
            # Create comprehensive report
            report = create_portfolio_report(comparison_df, portfolio_analysis, recommendations, primary_ticker, current_date)
            
        except Exception as e:
            report = f"""# Portfolio Analysis Error

An error occurred during portfolio analysis: {str(e)}

This could be due to:
- Market data availability issues
- Network connectivity problems
- Invalid ticker symbols

Please try again or contact support.

FINAL TRANSACTION PROPOSAL: **HOLD**
"""

        return {
            "messages": [],
            "portfolio_report": report
        }
    
    return portfolio_analyst_node


def get_comparison_tickers(primary_ticker):
    """Get relevant comparison tickers based on the primary ticker."""
    
    # Define sector/industry mappings
    ticker_groups = {
        # Technology
        'AAPL': ['MSFT', 'GOOGL', 'AMZN', 'META'],
        'MSFT': ['AAPL', 'GOOGL', 'AMZN', 'META'],
        'GOOGL': ['AAPL', 'MSFT', 'AMZN', 'META'],
        'AMZN': ['AAPL', 'MSFT', 'GOOGL', 'META'],
        'META': ['AAPL', 'MSFT', 'GOOGL', 'AMZN'],
        'NVDA': ['AMD', 'INTC', 'TSM', 'QCOM'],
        'AMD': ['NVDA', 'INTC', 'TSM', 'QCOM'],
        
        # Financial
        'JPM': ['BAC', 'WFC', 'C', 'GS'],
        'BAC': ['JPM', 'WFC', 'C', 'GS'],
        'WFC': ['JPM', 'BAC', 'C', 'GS'],
        
        # Healthcare
        'JNJ': ['PFE', 'UNH', 'ABBV', 'MRK'],
        'PFE': ['JNJ', 'UNH', 'ABBV', 'MRK'],
        
        # Energy
        'XOM': ['CVX', 'COP', 'SLB', 'EOG'],
        'CVX': ['XOM', 'COP', 'SLB', 'EOG'],
        
        # ETFs
        'SPY': ['QQQ', 'IWM', 'VTI', 'VOO'],
        'QQQ': ['SPY', 'IWM', 'VTI', 'VOO'],
        'VTI': ['SPY', 'QQQ', 'IWM', 'VOO'],
    }
    
    # Return specific comparisons if available, otherwise use broad market
    return ticker_groups.get(primary_ticker.upper(), ['SPY', 'QQQ', 'IWM', 'VTI'])[:4]


def analyze_stock_metrics(stock_data, ticker):
    """Analyze key metrics for a single stock."""
    
    # Calculate returns
    returns = stock_data['Close'].pct_change().dropna()
    
    # Calculate metrics
    current_price = stock_data['Close'].iloc[-1]
    price_52w_high = stock_data['High'].rolling(252).max().iloc[-1]
    price_52w_low = stock_data['Low'].rolling(252).min().iloc[-1]
    
    # Performance metrics
    ytd_return = (current_price / stock_data['Close'].iloc[0] - 1) * 100
    monthly_return = returns.tail(21).sum() * 100
    weekly_return = returns.tail(5).sum() * 100
    
    # Risk metrics
    volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility
    max_drawdown = calculate_max_drawdown(stock_data['Close']) * 100
    
    # Technical indicators
    sma_20 = stock_data['Close'].rolling(20).mean().iloc[-1]
    sma_50 = stock_data['Close'].rolling(50).mean().iloc[-1]
    rsi = calculate_rsi(stock_data['Close']).iloc[-1]
    
    # Volume analysis
    avg_volume = stock_data['Volume'].rolling(20).mean().iloc[-1]
    current_volume = stock_data['Volume'].iloc[-1]
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
    
    return {
        'current_price': current_price,
        'ytd_return': ytd_return,
        'monthly_return': monthly_return,
        'weekly_return': weekly_return,
        'volatility': volatility,
        'max_drawdown': max_drawdown,
        'price_to_52w_high': (current_price / price_52w_high) * 100,
        'price_to_52w_low': (current_price / price_52w_low) * 100,
        'sma_20': sma_20,
        'sma_50': sma_50,
        'rsi': rsi,
        'volume_ratio': volume_ratio,
        'sharpe_ratio': calculate_sharpe_ratio(returns)
    }


def calculate_max_drawdown(prices):
    """Calculate maximum drawdown."""
    peak = prices.cummax()
    drawdown = (prices - peak) / peak
    return drawdown.min()


def calculate_rsi(prices, window=14):
    """Calculate RSI."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate Sharpe ratio."""
    excess_returns = returns - risk_free_rate/252
    return excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0


def perform_portfolio_analysis(portfolio_data, tickers):
    """Perform portfolio-level analysis."""
    
    # Create correlation matrix
    try:
        price_data = {}
        for ticker in tickers:
            stock_data = yf.download(ticker, period="6m", progress=False)
            if not stock_data.empty:
                price_data[ticker] = stock_data['Close'].pct_change().dropna()
        
        if len(price_data) > 1:
            correlation_df = pd.DataFrame(price_data).corr()
        else:
            correlation_df = pd.DataFrame()
    except:
        correlation_df = pd.DataFrame()
    
    # Portfolio diversification score
    if not correlation_df.empty:
        avg_correlation = correlation_df.values[np.triu_indices_from(correlation_df.values, k=1)].mean()
        diversification_score = max(0, (1 - abs(avg_correlation)) * 100)
    else:
        diversification_score = 50  # Neutral score
    
    return {
        'correlation_matrix': correlation_df,
        'diversification_score': diversification_score,
        'portfolio_size': len(portfolio_data)
    }


def generate_portfolio_recommendations(comparison_df, primary_ticker):
    """Generate portfolio recommendations based on analysis."""
    
    recommendations = []
    
    # Rank stocks by different criteria
    rankings = {}
    
    # Performance ranking
    rankings['performance'] = comparison_df['ytd_return'].rank(ascending=False)
    
    # Risk-adjusted return ranking (Sharpe ratio)
    rankings['risk_adjusted'] = comparison_df['sharpe_ratio'].rank(ascending=False)
    
    # Momentum ranking (weekly + monthly returns)
    momentum_score = comparison_df['weekly_return'] * 0.3 + comparison_df['monthly_return'] * 0.7
    rankings['momentum'] = momentum_score.rank(ascending=False)
    
    # Value ranking (distance from 52-week high, lower is better for value)
    rankings['value'] = comparison_df['price_to_52w_high'].rank(ascending=True)
    
    # Overall composite score
    composite_score = (rankings['performance'] + rankings['risk_adjusted'] + 
                      rankings['momentum'] + rankings['value']) / 4
    
    # Generate specific recommendations
    primary_rank = composite_score[primary_ticker]
    total_stocks = len(comparison_df)
    
    if primary_rank <= total_stocks * 0.3:
        primary_recommendation = "STRONG BUY - Top performer in comparison group"
    elif primary_rank <= total_stocks * 0.6:
        primary_recommendation = "BUY - Above average performance"
    elif primary_rank <= total_stocks * 0.8:
        primary_recommendation = "HOLD - Average performance"
    else:
        primary_recommendation = "SELL - Below average performance"
    
    # Portfolio allocation suggestions
    sorted_stocks = composite_score.sort_values()
    top_3_stocks = sorted_stocks.head(3).index.tolist()
    
    return {
        'primary_recommendation': primary_recommendation,
        'composite_rankings': composite_score.sort_values(),
        'top_picks': top_3_stocks,
        'rankings_detail': rankings
    }


def create_portfolio_report(comparison_df, portfolio_analysis, recommendations, primary_ticker, current_date):
    """Create comprehensive portfolio analysis report."""
    
    report = f"""# Portfolio Comparative Analysis for {primary_ticker}
*Analysis Date: {current_date}*

## Executive Summary

**Primary Stock Recommendation**: {recommendations['primary_recommendation']}

**Top 3 Portfolio Picks**:
"""
    
    for i, ticker in enumerate(recommendations['top_picks'], 1):
        ytd_return = comparison_df.loc[ticker, 'ytd_return']
        sharpe = comparison_df.loc[ticker, 'sharpe_ratio']
        report += f"{i}. **{ticker}** - YTD Return: {ytd_return:.1f}%, Sharpe Ratio: {sharpe:.2f}\n"
    
    report += f"""
**Portfolio Diversification Score**: {portfolio_analysis['diversification_score']:.1f}/100
{'(Well diversified)' if portfolio_analysis['diversification_score'] > 70 else '(Moderately diversified)' if portfolio_analysis['diversification_score'] > 40 else '(Low diversification)'}

## Comparative Performance Analysis

| Ticker | Current Price | YTD Return | Monthly Return | Weekly Return | Volatility | Sharpe Ratio | RSI |
|--------|---------------|------------|----------------|---------------|------------|--------------|-----|"""
    
    for ticker in comparison_df.index:
        row = comparison_df.loc[ticker]
        report += f"\n| {ticker} | ${row['current_price']:.2f} | {row['ytd_return']:.1f}% | {row['monthly_return']:.1f}% | {row['weekly_return']:.1f}% | {row['volatility']:.1f}% | {row['sharpe_ratio']:.2f} | {row['rsi']:.1f} |"
    
    report += f"""

## Risk Analysis

| Ticker | Max Drawdown | Distance from 52W High | Distance from 52W Low | Volume Ratio |
|--------|--------------|------------------------|----------------------|--------------|"""
    
    for ticker in comparison_df.index:
        row = comparison_df.loc[ticker]
        report += f"\n| {ticker} | {row['max_drawdown']:.1f}% | {100-row['price_to_52w_high']:.1f}% | {row['price_to_52w_low']-100:.1f}% | {row['volume_ratio']:.1f}x |"
    
    report += f"""

## Technical Analysis Summary

| Ticker | Price vs SMA20 | Price vs SMA50 | Technical Signal |
|--------|----------------|----------------|------------------|"""
    
    for ticker in comparison_df.index:
        row = comparison_df.loc[ticker]
        sma20_signal = "Above" if row['current_price'] > row['sma_20'] else "Below"
        sma50_signal = "Above" if row['current_price'] > row['sma_50'] else "Below"
        
        # Technical signal based on multiple factors
        if (row['current_price'] > row['sma_20'] and row['current_price'] > row['sma_50'] and 
            row['rsi'] < 70 and row['weekly_return'] > 0):
            tech_signal = "BULLISH"
        elif (row['current_price'] < row['sma_20'] and row['current_price'] < row['sma_50'] and 
              row['rsi'] > 30 and row['weekly_return'] < 0):
            tech_signal = "BEARISH"
        else:
            tech_signal = "NEUTRAL"
        
        report += f"\n| {ticker} | {sma20_signal} | {sma50_signal} | {tech_signal} |"
    
    # Correlation analysis
    if not portfolio_analysis['correlation_matrix'].empty:
        report += f"""

## Correlation Analysis

**Average Correlation**: {portfolio_analysis['correlation_matrix'].values[np.triu_indices_from(portfolio_analysis['correlation_matrix'].values, k=1)].mean():.2f}

### Correlation Matrix
"""
        corr_matrix = portfolio_analysis['correlation_matrix']
        report += "| Ticker |" + "|".join([f" {col} " for col in corr_matrix.columns]) + "|\n"
        report += "|" + "|".join(["--------"] * (len(corr_matrix.columns) + 1)) + "|\n"
        
        for ticker in corr_matrix.index:
            row_values = [f" {corr_matrix.loc[ticker, col]:.2f} " for col in corr_matrix.columns]
            report += f"| {ticker} |" + "|".join(row_values) + "|\n"
    
    report += f"""

## Portfolio Recommendations

### Asset Allocation Suggestion
Based on risk-adjusted returns and diversification:

"""
    
    # Simple portfolio allocation based on rankings
    total_score = recommendations['composite_rankings'].sum()
    for ticker in recommendations['composite_rankings'].head(4).index:
        weight = (5 - recommendations['composite_rankings'][ticker]) / 10 * 100  # Simple weighting
        report += f"- **{ticker}**: {weight:.1f}%\n"
    
    report += f"""

### Key Investment Insights

1. **Best Performer**: {comparison_df['ytd_return'].idxmax()} with {comparison_df['ytd_return'].max():.1f}% YTD return
2. **Most Stable**: {comparison_df['volatility'].idxmin()} with {comparison_df['volatility'].min():.1f}% volatility
3. **Best Risk-Adjusted**: {comparison_df['sharpe_ratio'].idxmax()} with {comparison_df['sharpe_ratio'].max():.2f} Sharpe ratio
4. **Momentum Leader**: {comparison_df['weekly_return'].idxmax()} with {comparison_df['weekly_return'].max():.1f}% weekly return

### Risk Considerations
- **Highest Risk**: {comparison_df['max_drawdown'].idxmin()} (Max Drawdown: {comparison_df['max_drawdown'].min():.1f}%)
- **Diversification**: {'High' if portfolio_analysis['diversification_score'] > 70 else 'Medium' if portfolio_analysis['diversification_score'] > 40 else 'Low'} correlation among assets
- **Market Timing**: Consider current market conditions and entry points

## Conclusion

{recommendations['primary_recommendation']}

**Overall Portfolio Strategy**: 
{'Focus on growth momentum with moderate risk management' if comparison_df['ytd_return'].mean() > 5 else 'Emphasize value opportunities and risk management' if comparison_df['ytd_return'].mean() < 0 else 'Balanced approach with selective stock picking'}

*This analysis is based on historical data and technical indicators. Consider fundamental analysis and market conditions before making investment decisions.*

FINAL TRANSACTION PROPOSAL: **{recommendations['primary_recommendation'].split(' - ')[0]}**
"""
    
    return report
