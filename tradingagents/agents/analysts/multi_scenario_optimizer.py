"""
Multi-Scenario Portfolio Optimization
Clean implementation for testing different risk preferences
"""

import pandas as pd
import numpy as np
import yfinance as yf


def create_multi_scenario_optimizer(llm, toolkit):
    """Create multi-scenario optimization analyst"""
    
    def multi_scenario_optimizer_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        
        print(f"🎯 Multi-Scenario Optimization for {ticker}...")
        
        try:
            # Get price data
            if toolkit.config.get("online_tools", False):
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1y")
                price_data = hist['Close']
            else:
                # Fallback
                dates = pd.date_range(start='2024-01-01', end='2025-10-03', freq='D')
                price_data = pd.Series(np.random.lognormal(5, 0.02, len(dates)), index=dates)
            
            if price_data is None or len(price_data) < 50:
                return {
                    "messages": [],
                    "optimization_results": {},
                    "quantitative_report": "Insufficient data for optimization"
                }
            
            # Calculate metrics
            returns = price_data.pct_change().dropna()
            mu = returns.mean() * 252  # Annualized return
            sigma = returns.std() * np.sqrt(252)  # Annualized volatility
            r = 0.025  # Risk-free rate
            current_price = float(price_data.iloc[-1])
            
            # Risk metrics
            var_95 = np.percentile(returns, 5) * 100
            cvar_95 = returns[returns <= np.percentile(returns, 5)].mean() * 100
            cummax = price_data.cummax()
            drawdown = (price_data - cummax) / cummax
            max_drawdown = drawdown.min() * 100
            sharpe = (mu - r) / sigma if sigma > 0 else 0
            
            print(f"   Stock metrics: Return={mu*100:.1f}%, Vol={sigma*100:.1f}%, Sharpe={sharpe:.2f}")
            
            # SCENARIO 1: Conservative (γ=15)
            gamma_cons = 15.0
            opt_cons = max(0, min(1, (mu - r) / (gamma_cons * sigma**2)))
            
            # SCENARIO 2: Moderate (γ=10)
            gamma_mod = 10.0
            opt_mod = max(0, min(1, (mu - r) / (gamma_mod * sigma**2)))
            
            # SCENARIO 3: Aggressive (γ=6)
            gamma_agg = 6.0
            opt_agg = max(0, min(1, (mu - r) / (gamma_agg * sigma**2)))
            
            # SCENARIO 4: Volatility-Focused (γ=12 + penalty)
            gamma_vol = 12.0
            vol_penalty = 1.5 if sigma > 0.40 else 1.0
            opt_vol = max(0, min(1, (mu - r) / (gamma_vol * vol_penalty * sigma**2)))
            
            # SCENARIO 5: Return-Focused (γ=5)
            gamma_ret = 5.0
            opt_ret = max(0, min(1, (mu - r) / (gamma_ret * sigma**2)))
            
            # SCENARIO 6: Sharpe-Optimized (adaptive γ)
            gamma_sharpe = 8.0 if sharpe > 1.5 else 10.0 if sharpe > 1.0 else 12.0
            opt_sharpe = max(0, min(1, (mu - r) / (gamma_sharpe * sigma**2)))
            
            scenarios = {
                'conservative': {
                    'gamma': gamma_cons,
                    'optimal_weight': opt_cons,
                    'philosophy': 'Risk-Averse Institutional',
                    'description': 'Capital preservation focus',
                    'risk_tolerance': 'Low',
                    'rationale': f'γ={gamma_cons} heavily penalizes volatility'
                },
                'moderate': {
                    'gamma': gamma_mod,
                    'optimal_weight': opt_mod,
                    'philosophy': 'Balanced Institutional',
                    'description': 'Standard risk-return balance',
                    'risk_tolerance': 'Medium',
                    'rationale': f'γ={gamma_mod} industry standard approach'
                },
                'aggressive': {
                    'gamma': gamma_agg,
                    'optimal_weight': opt_agg,
                    'philosophy': 'Growth-Oriented',
                    'description': 'Higher risk for growth',
                    'risk_tolerance': 'High',
                    'rationale': f'γ={gamma_agg} accepts volatility for returns'
                },
                'volatility_focused': {
                    'gamma': gamma_vol,
                    'optimal_weight': opt_vol,
                    'philosophy': 'Volatility-Minimizing',
                    'description': 'Stability emphasis',
                    'risk_tolerance': 'Low-Medium',
                    'rationale': f'γ={gamma_vol} + {vol_penalty}x vol penalty'
                },
                'return_focused': {
                    'gamma': gamma_ret,
                    'optimal_weight': opt_ret,
                    'philosophy': 'Return-Maximizing',
                    'description': 'Maximize returns',
                    'risk_tolerance': 'High',
                    'rationale': f'γ={gamma_ret} focus on upside'
                },
                'sharpe_optimized': {
                    'gamma': gamma_sharpe,
                    'optimal_weight': opt_sharpe,
                    'philosophy': 'Sharpe-Optimized',
                    'description': 'Risk-adjusted quality',
                    'risk_tolerance': 'Medium',
                    'rationale': f'γ={gamma_sharpe} adapts to Sharpe={sharpe:.2f}'
                }
            }
            
            weights = [s['optimal_weight'] for s in scenarios.values()]
            consensus = np.median(weights)
            
            print(f"   ✅ Scenarios generated:")
            print(f"      Conservative: {opt_cons:.2%}")
            print(f"      Moderate: {opt_mod:.2%}")
            print(f"      Aggressive: {opt_agg:.2%}")
            print(f"      Consensus: {consensus:.2%}")
            
            optimization_results = {
                'optimization_scenarios': scenarios,
                'scenario_summary': {
                    'consensus_weight': consensus,
                    'weight_range': (min(weights), max(weights)),
                    'num_scenarios': len(scenarios),
                    'stock_metrics': {
                        'expected_return': mu,
                        'volatility': sigma,
                        'sharpe_ratio': sharpe,
                        'current_price': current_price
                    }
                },
                'risk_metrics': {
                    'var_95': var_95,
                    'cvar_95': cvar_95,
                    'max_drawdown': max_drawdown,
                    'sharpe_ratio': sharpe,
                    'volatility': sigma * 100
                }
            }
            
            report = f"""# Multi-Scenario Optimization Results for {ticker}

Generated {len(scenarios)} scenarios with different risk preferences.
Consensus: {consensus:.2%} | Range: {min(weights):.2%} - {max(weights):.2%}
"""
            
            return {
                "messages": [],
                "optimization_results": optimization_results,
                "comprehensive_quantitative_report": report,
                "quantitative_report": report
            }
            
        except Exception as e:
            print(f"❌ Optimization failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "messages": [],
                "optimization_results": {},
                "quantitative_report": f"Optimization failed: {str(e)}"
            }
    
    return multi_scenario_optimizer_node

