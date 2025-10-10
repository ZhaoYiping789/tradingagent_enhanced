"""
Stock Data Aggregator
Aggregates analysis results from multiple single-stock analyses
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class StockDataAggregator:
    """Aggregate and standardize data from multiple stock analyses"""
    
    def __init__(self, base_date: str):
        self.base_date = base_date
        self.stocks_data = {}
        
    def load_stock_analysis(self, ticker: str) -> Dict[str, Any]:
        """Load analysis results prioritizing CSV over MD parsing"""
        
        # Try CSV first (new structured approach)
        csv_data = self._load_from_csv(ticker)
        if csv_data:
            print(f"SUCCESS: Loaded {ticker} from CSV files")
            return csv_data
        
        # Fallback to MD parsing
        print(f"WARNING: Loading {ticker} from MD parsing (CSV not available)")
        
        # Load from markdown report (has actual data)
        md_path = Path(f"results/{ticker}/{self.base_date}/{ticker}_comprehensive_analysis_{self.base_date}.md")
        
        if not md_path.exists():
            print(f"WARNING: No MD report found for {ticker}")
            return None
        
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Also try to load state for optimization results
            state_path = Path(f"eval_results/{ticker}/TradingAgentsStrategy_logs/full_states_log_{self.base_date}.json")
            state = {}
            if state_path.exists():
                with open(state_path, 'r') as f:
                    data = json.load(f)
                    state = data.get(self.base_date, {})
            
            # Extract key metrics from MD content
            aggregated_data = {
                'ticker': ticker,
                'date': self.base_date,
                
                # Decision (extract from MD)
                'final_decision': self._extract_decision_from_md(md_content),
                
                # Full MD content for reference
                'md_content': md_content,
                
                # Reports from state if available
                'market_report': state.get('market_report', ''),
                'fundamentals_report': state.get('fundamentals_report', ''),
                
                # Optimization results from state
                'optimization_results': state.get('optimization_results', {}),
                
                # Extract ALL numeric metrics from MD report
                'metrics': self._extract_metrics_from_md(md_content, state),
                
                # Extract risk metrics from MD
                'risk_metrics': self._extract_risk_metrics_from_md(md_content, state),
                
                # Extract tables from MD for display
                'technical_table': self._extract_technical_table(md_content),
                'fundamental_table': self._extract_fundamental_table(md_content),
                'news_summary': self._extract_news_summary(md_content)
            }
            
            print(f"SUCCESS: Loaded {ticker} analysis")
            return aggregated_data
            
        except Exception as e:
            print(f"ERROR: loading {ticker}: {e}")
            return None
    
    def _load_from_csv(self, ticker: str) -> Dict[str, Any]:
        """Load structured data from CSV files if available"""
        
        csv_dir = Path(f"results/{ticker}/{self.base_date}/csv_data")
        if not csv_dir.exists():
            return None
        
        result = {
            'ticker': ticker,
            'date': self.base_date,
            'data_source': 'csv'
        }
        
        try:
            # Load summary metrics (most important)
            summary_path = csv_dir / 'summary_metrics.csv'
            if summary_path.exists():
                summary_df = pd.read_csv(summary_path)
                if not summary_df.empty:
                    summary_row = summary_df.iloc[0]
                    result['final_decision'] = summary_row.get('final_decision', 'HOLD')
                    result['metrics'] = {
                        'expected_return': summary_row.get('expected_return', 0.0),
                        'volatility': summary_row.get('volatility', 0.0),
                        'sharpe_ratio': summary_row.get('sharpe_ratio', 0.0),
                        'current_price': summary_row.get('current_price', 0.0),
                        'rsi': 50.0,  # Will be updated from technical CSV
                        'technical_score': summary_row.get('technical_score', 7.0),
                        'sentiment_score': summary_row.get('sentiment_score', 5.0)
                    }
            
            # Load risk metrics
            risk_path = csv_dir / 'risk_metrics.csv'
            if risk_path.exists():
                risk_df = pd.read_csv(risk_path)
                if not risk_df.empty:
                    risk_row = risk_df.iloc[0]
                    result['risk_metrics'] = {
                        'var_95': risk_row.get('var_95', -2.0),
                        'cvar_95': risk_row.get('cvar_95', -3.0),
                        'max_drawdown': risk_row.get('max_drawdown', -15.0),
                        'volatility': risk_row.get('annual_volatility', 25.0)
                    }
            
            # Load technical indicators  
            technical_path = csv_dir / 'technical_indicators.csv'
            if technical_path.exists():
                tech_df = pd.read_csv(technical_path)
                if not tech_df.empty:
                    tech_row = tech_df.iloc[0]
                    result['technical_table'] = {
                        'Current Price': f"${tech_row.get('current_price', 0.0):.2f}",
                        'RSI': f"{tech_row.get('rsi', 50.0):.1f}",
                        'MACD': f"{tech_row.get('macd', 0.0):.2f}",
                        'SMA_20': f"${tech_row.get('sma_20', 0.0):.2f}",
                        'SMA_50': f"${tech_row.get('sma_50', 0.0):.2f}",
                        'ATR': f"{tech_row.get('atr', 0.0):.2f}",
                        'Volatility': f"{tech_row.get('volatility', 0.0):.1f}%"
                    }
                    # Update metrics with RSI
                    if 'metrics' in result:
                        result['metrics']['rsi'] = tech_row.get('rsi', 50.0)
                        result['metrics']['current_price'] = tech_row.get('current_price', 0.0)
            
            # Load fundamental metrics
            financial_path = csv_dir / 'financial_metrics.csv'
            if financial_path.exists():
                fin_df = pd.read_csv(financial_path)
                if not fin_df.empty:
                    fin_row = fin_df.iloc[0]
                    result['fundamental_table'] = {
                        'Revenue': f"${fin_row.get('revenue', 0.0)/1e9:.1f}B",
                        'Net Income': f"${fin_row.get('net_income', 0.0)/1e9:.1f}B",
                        'Profit Margin': f"{fin_row.get('profit_margin', 0.0):.1f}%",
                        'ROE': f"{fin_row.get('roe', 0.0):.1f}%",
                        'Debt-to-Equity': f"{fin_row.get('debt_to_equity', 0.0):.2f}"
                    }
            
            # Load optimization results
            opt_path = csv_dir / 'optimization_scenarios.csv'
            if opt_path.exists():
                opt_df = pd.read_csv(opt_path)
                if not opt_df.empty:
                    scenarios = {}
                    for _, row in opt_df.iterrows():
                        scenario_name = row.get('scenario', 'Unknown')
                        scenarios[scenario_name] = {
                            'gamma': row.get('gamma', 1.0),
                            'optimal_weight': row.get('optimal_weight', 0.0),
                            'expected_return': row.get('expected_return', 0.0),
                            'risk_tolerance': row.get('risk_tolerance', ''),
                            'philosophy': row.get('philosophy', ''),
                            'description': row.get('description', '')
                        }
                    result['optimization_results'] = {
                        'optimization_scenarios': scenarios
                    }
            
            # Load sentiment analysis (enhanced)
            sentiment_path = csv_dir / 'sentiment_analysis.csv'
            if sentiment_path.exists():
                sentiment_df = pd.read_csv(sentiment_path)
                if not sentiment_df.empty:
                    sentiment_row = sentiment_df.iloc[0]
                    result['sentiment_analysis'] = {
                        'overall_sentiment': sentiment_row.get('overall_sentiment', 5.0),
                        'bullish_count': sentiment_row.get('bullish_count', 0),
                        'bearish_count': sentiment_row.get('bearish_count', 0),
                        'neutral_count': sentiment_row.get('neutral_count', 0),
                        'sentiment_strength': sentiment_row.get('sentiment_strength', 'Weak'),
                        'average_impact': sentiment_row.get('average_impact', 0.0)
                    }
                    # Update metrics with actual sentiment score
                    if 'metrics' in result:
                        result['metrics']['sentiment_score'] = sentiment_row.get('overall_sentiment', 5.0)
            
            # Fallback: check for news analysis
            elif (csv_dir / 'news_analysis.csv').exists():
                news_df = pd.read_csv(csv_dir / 'news_analysis.csv')
                if not news_df.empty:
                    news_row = news_df.iloc[0]
                    result['sentiment_analysis'] = {
                        'overall_sentiment': news_row.get('overall_sentiment', 5.0),
                        'sentiment_strength': 'Basic'
                    }
            
            # Only return if we have meaningful data
            if len(result) > 3 and 'metrics' in result:
                return result
            
        except Exception as e:
            print(f"Error loading CSV data for {ticker}: {e}")
        
        return None
    
    def _extract_decision_from_md(self, md_content: str) -> str:
        """Extract final decision from MD"""
        if 'ACCUMULATE' in md_content.upper():
            return 'BUY'
        elif 'REDUCE' in md_content.upper():
            return 'SELL'
        else:
            return 'HOLD'
    
    def _extract_technical_table(self, md_content: str) -> Dict:
        """Extract technical indicators from MD report"""
        import re
        
        tech_data = {}
        
        # Look for technical indicators in the report
        patterns = {
            'SMA 20': r'SMA\s*20.*?(\$?[\d,]+\.?\d*)',
            'SMA 50': r'SMA\s*50.*?(\$?[\d,]+\.?\d*)',
            'RSI': r'RSI.*?(\d+\.?\d*)',
            'MACD': r'MACD.*?(\d+\.?\d*)',
            'ATR': r'ATR.*?(\$?[\d,]+\.?\d*)',
            'Current Price': r'Current Price.*?\$?([\d,]+\.?\d*)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, md_content, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1).replace(',', '').replace('$', '')
                    tech_data[key] = float(value_str)
                except:
                    pass
        
        return tech_data
    
    def _extract_fundamental_table(self, md_content: str) -> Dict:
        """Extract fundamental metrics from MD report"""
        import re
        
        fund_data = {}
        
        patterns = {
            'Revenue': r'Revenue.*?\$?([\d,]+\.?\d*)\s*(billion|million|B|M)?',
            'Net Income': r'Net Income.*?\$?([\d,]+\.?\d*)\s*(billion|million|B|M)?',
            'Gross Profit': r'Gross Profit.*?\$?([\d,]+\.?\d*)\s*(billion|million|B|M)?',
            'Profit Margin': r'Profit Margin.*?([\d,]+\.?\d*)%',
            'ROE': r'ROE.*?([\d,]+\.?\d*)%',
            'Debt-to-Equity': r'Debt.*?Equity.*?([\d,]+\.?\d*)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, md_content, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1).replace(',', '')
                    fund_data[key] = float(value_str)
                except:
                    pass
        
        return fund_data
    
    def _extract_news_summary(self, md_content: str) -> str:
        """Extract news summary section"""
        # Look for news/sentiment section
        if '## SECTION 2' in md_content:
            start = md_content.find('## SECTION 2')
            end = md_content.find('## SECTION 3')
            if end > start:
                return md_content[start:end][:500]  # First 500 chars
        return "News analysis available in full report"
    
    def _extract_metrics_from_md(self, md_content: str, state: Dict) -> Dict:
        """Extract numeric metrics from state"""
        
        metrics = {
            'expected_return': 0.0,
            'volatility': 0.0,
            'sharpe_ratio': 0.0,
            'current_price': 0.0,
            'rsi': 50.0,
            'technical_score': 5.0,
            'sentiment_score': 5.0
        }
        
        # Try to extract from optimization results
        opt_results = state.get('optimization_results', {})
        if opt_results:
            scenario_summary = opt_results.get('scenario_summary', {})
            stock_metrics = scenario_summary.get('stock_metrics', {})
            
            metrics['expected_return'] = stock_metrics.get('expected_return', 0.0)
            metrics['volatility'] = stock_metrics.get('volatility', 0.0)
            metrics['sharpe_ratio'] = stock_metrics.get('sharpe_ratio', 0.0)
            metrics['current_price'] = stock_metrics.get('current_price', 0.0)
        
        # Try to extract from market report
        market_report = state.get('market_report', '').lower()
        if 'rsi' in market_report:
            try:
                # Simple extraction - look for "rsi: XX" or "rsi XX"
                import re
                rsi_match = re.search(r'rsi[:\s]+(\d+\.?\d*)', market_report)
                if rsi_match:
                    metrics['rsi'] = float(rsi_match.group(1))
            except:
                pass
        
        # Technical score based on sentiment
        if 'bullish' in market_report:
            metrics['technical_score'] = 7.0
        elif 'bearish' in market_report:
            metrics['technical_score'] = 3.0
        
        # Sentiment score
        sentiment_report = state.get('sentiment_report', '').lower()
        if 'positive' in sentiment_report or 'bullish' in sentiment_report:
            metrics['sentiment_score'] = 7.0
        elif 'negative' in sentiment_report or 'bearish' in sentiment_report:
            metrics['sentiment_score'] = 3.0
        
        return metrics
    
    def _extract_risk_metrics(self, state: Dict) -> Dict:
        """Extract risk metrics"""
        
        opt_results = state.get('optimization_results', {})
        risk_metrics = opt_results.get('risk_metrics', {})
        
        return {
            'var_95': risk_metrics.get('var_95', -2.0),
            'cvar_95': risk_metrics.get('cvar_95', -3.0),
            'max_drawdown': risk_metrics.get('max_drawdown', -15.0),
            'volatility': risk_metrics.get('volatility', 25.0)
        }
    
    def aggregate_multiple_stocks(self, tickers: List[str]) -> Dict[str, Any]:
        """Aggregate data from multiple stocks"""
        
        print(f"Aggregating data for {len(tickers)} stocks...")
        
        for ticker in tickers:
            stock_data = self.load_stock_analysis(ticker)
            if stock_data:
                self.stocks_data[ticker] = stock_data
        
        print(f"Successfully loaded {len(self.stocks_data)}/{len(tickers)} stocks")
        
        # Create comparison dataframe
        comparison_data = []
        for ticker, data in self.stocks_data.items():
            metrics = data['metrics']
            risk = data['risk_metrics']
            
            comparison_data.append({
                'Ticker': ticker,
                'Decision': data['final_decision'],
                'Expected Return': metrics['expected_return'],  # Already in percentage
                'Volatility': metrics['volatility'],  # Already in percentage
                'Sharpe Ratio': metrics['sharpe_ratio'],
                'Current Price': metrics['current_price'],
                'RSI': metrics['rsi'],
                'Technical Score': metrics['technical_score'],
                'Sentiment Score': metrics['sentiment_score'],
                'VaR 95%': risk['var_95'],
                'Max Drawdown': risk['max_drawdown']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        return {
            'stocks_data': self.stocks_data,
            'comparison_df': comparison_df,
            'num_stocks': len(self.stocks_data)
        }
    
    def save_aggregated_data(self, output_dir: str = None):
        """Save aggregated data for portfolio optimization"""
        
        if output_dir is None:
            output_dir = f"portfolio_cache/{self.base_date}"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save summary
        summary_path = output_path / "stocks_summary.json"
        with open(summary_path, 'w') as f:
            # Convert to JSON-serializable format
            json_data = {}
            for ticker, data in self.stocks_data.items():
                json_data[ticker] = {
                    'metrics': data['metrics'],
                    'risk_metrics': data['risk_metrics'],
                    'final_decision': data['final_decision']
                }
            json.dump(json_data, f, indent=2)
        
        print(f"Saved aggregated data to {summary_path}")
        return str(summary_path)
