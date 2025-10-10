"""
Advanced Single Stock Optimization Engine
Implements Almgren-Chriss, Optimal Stopping, and HJB-based models for single stock trading
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize, differential_evolution
from scipy import stats
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class SingleStockOptimizer:
    """
    Advanced optimization for single stock trading decisions using multiple mathematical models
    """
    
    def __init__(self, price_data: pd.Series, transaction_cost: float = 0.001):
        """
        Initialize optimizer with price data
        
        Args:
            price_data: Historical price series
            transaction_cost: Transaction cost as decimal (0.001 = 0.1%)
        """
        self.price_data = price_data
        self.returns = price_data.pct_change().dropna()
        self.transaction_cost = transaction_cost
        self.current_price = price_data.iloc[-1]
        
        # Calculate market microstructure parameters
        self.volatility = self.returns.std() * np.sqrt(252)
        self.drift = self.returns.mean() * 252
        
    def almgren_chriss_optimization(self, total_shares: int, total_time: float = 1.0,
                                   risk_aversion: float = 1e-6) -> Dict:
        """
        Almgren-Chriss optimal execution model for single stock
        
        Args:
            total_shares: Total number of shares to trade
            total_time: Time horizon in days
            risk_aversion: Risk aversion parameter
            
        Returns:
            Optimal execution strategy
        """
        # Market impact parameters (simplified)
        permanent_impact = 0.1  # Permanent market impact
        temporary_impact = 0.01  # Temporary market impact
        
        # Volatility of price
        sigma = self.volatility / np.sqrt(252)  # Daily volatility
        
        # Calculate optimal parameters
        kappa = np.sqrt(risk_aversion * sigma**2 / temporary_impact)
        
        # Optimal trajectory
        time_steps = np.linspace(0, total_time, 11)  # 10 intervals
        
        optimal_holdings = []
        for t in time_steps:
            remaining_time = total_time - t
            if remaining_time <= 0:
                optimal_holdings.append(0)
            else:
                # Exponential decay strategy
                holdings = total_shares * np.sinh(kappa * remaining_time) / np.sinh(kappa * total_time)
                optimal_holdings.append(holdings)
        
        # Calculate execution rates
        execution_rates = []
        for i in range(len(optimal_holdings) - 1):
            rate = optimal_holdings[i] - optimal_holdings[i + 1]
            execution_rates.append(rate)
        execution_rates.append(optimal_holdings[-1])  # Final execution
        
        # Calculate expected cost
        total_cost = 0
        for rate in execution_rates:
            total_cost += permanent_impact * abs(rate) + temporary_impact * rate**2
        
        return {
            'model': 'Almgren-Chriss',
            'time_steps': time_steps.tolist(),
            'optimal_holdings': optimal_holdings,
            'execution_rates': execution_rates,
            'expected_cost': total_cost,
            'execution_strategy': 'Exponential Decay',
            'market_impact_cost': total_cost * self.current_price,
            'recommended_intervals': len(time_steps) - 1
        }
    
    def optimal_stopping_entry(self, lookback_periods: int = 20, 
                              confidence_threshold: float = 0.7) -> Dict:
        """
        Optimal stopping model for entry timing using dynamic programming
        
        Args:
            lookback_periods: Number of periods to look back for patterns
            confidence_threshold: Minimum confidence to trigger entry
            
        Returns:
            Optimal entry timing strategy
        """
        # Calculate moving statistics
        rolling_mean = self.price_data.rolling(lookback_periods).mean()
        rolling_std = self.price_data.rolling(lookback_periods).std()
        
        # Z-score for mean reversion signals
        z_scores = (self.price_data - rolling_mean) / rolling_std
        
        # Calculate probability of favorable outcome
        recent_z = z_scores.tail(lookback_periods).dropna()
        
        # Entry signals based on mean reversion
        entry_probabilities = []
        for z in recent_z:
            if z < -1.5:  # Oversold
                prob = 0.8  # High probability of reversion
            elif z < -1.0:
                prob = 0.6
            elif z > 1.5:  # Overbought
                prob = 0.2  # Low probability of further gains
            elif z > 1.0:
                prob = 0.4
            else:
                prob = 0.5  # Neutral
            entry_probabilities.append(prob)
        
        current_probability = entry_probabilities[-1] if entry_probabilities else 0.5
        
        # Dynamic programming for optimal stopping
        n_periods = min(10, len(entry_probabilities))
        if n_periods < 2:
            return {
                'model': 'Optimal Stopping',
                'entry_signal': 'WAIT',
                'confidence': 0.5,
                'expected_return': 0.0,
                'optimal_time': 'Insufficient data'
            }
        
        # Value function calculation (simplified)
        continuation_values = np.zeros(n_periods)
        stopping_values = np.array(entry_probabilities[-n_periods:])
        
        # Backward induction
        for t in range(n_periods - 2, -1, -1):
            continuation_values[t] = 0.95 * max(continuation_values[t + 1], stopping_values[t + 1])
        
        # Decision rule
        should_enter = current_probability > continuation_values[0]
        
        return {
            'model': 'Optimal Stopping',
            'entry_signal': 'ENTER' if should_enter and current_probability > confidence_threshold else 'WAIT',
            'confidence': current_probability,
            'expected_return': stopping_values[-1] * 0.1,  # Expected 10% move
            'optimal_time': 'Now' if should_enter else f'Wait {np.argmax(stopping_values) + 1} periods',
            'z_score': recent_z.iloc[-1] if len(recent_z) > 0 else 0,
            'mean_reversion_signal': 'Oversold' if recent_z.iloc[-1] < -1 else 'Overbought' if recent_z.iloc[-1] > 1 else 'Neutral'
        }
    
    def hjb_portfolio_optimization(self, risk_aversion: float = 2.0, 
                                  time_horizon: float = 0.25) -> Dict:
        """
        Hamilton-Jacobi-Bellman equation approach for portfolio optimization
        
        Args:
            risk_aversion: Risk aversion coefficient
            time_horizon: Investment time horizon in years
            
        Returns:
            Optimal portfolio allocation
        """
        # Simplified HJB solution (Merton's problem)
        mu = self.drift  # Expected return
        sigma = self.volatility  # Volatility
        r = 0.02  # Risk-free rate
        
        # Optimal fraction in risky asset (Merton's solution)
        optimal_fraction = (mu - r) / (risk_aversion * sigma**2)
        
        # Adjust for transaction costs
        optimal_fraction_adjusted = optimal_fraction * (1 - 2 * self.transaction_cost)
        
        # Bound the fraction between 0 and 1 for long-only
        optimal_fraction_bounded = max(0, min(1, optimal_fraction_adjusted))
        
        # Expected utility and certainty equivalent
        expected_return = optimal_fraction_bounded * mu + (1 - optimal_fraction_bounded) * r
        portfolio_variance = (optimal_fraction_bounded * sigma)**2
        certainty_equivalent = expected_return - 0.5 * risk_aversion * portfolio_variance
        
        # Calculate Kelly criterion for comparison
        kelly_fraction = (mu - r) / sigma**2 if sigma > 0 else 0
        
        return {
            'model': 'Hamilton-Jacobi-Bellman (Merton)',
            'optimal_allocation': optimal_fraction_bounded,
            'kelly_fraction': kelly_fraction,
            'expected_return': expected_return,
            'portfolio_volatility': np.sqrt(portfolio_variance),
            'certainty_equivalent': certainty_equivalent,
            'sharpe_ratio': (expected_return - r) / np.sqrt(portfolio_variance) if portfolio_variance > 0 else 0,
            'risk_adjustment': f'Adjusted for {self.transaction_cost:.1%} transaction costs'
        }
    
    def reinforcement_learning_strategy(self, lookback: int = 50) -> Dict:
        """
        Simple Q-learning inspired strategy for single stock trading
        
        Args:
            lookback: Number of periods for feature calculation
            
        Returns:
            RL-based trading strategy
        """
        if not SKLEARN_AVAILABLE or len(self.returns) < lookback + 10:
            return {
                'model': 'Reinforcement Learning',
                'action': 'HOLD',
                'confidence': 0.5,
                'expected_reward': 0.0,
                'status': 'Insufficient data or sklearn not available'
            }
        
        # Feature engineering
        features = []
        targets = []
        
        for i in range(lookback, len(self.returns) - 5):
            # Features: recent returns, volatility, momentum
            recent_returns = self.returns.iloc[i-lookback:i]
            feature_vector = [
                recent_returns.mean(),  # Average return
                recent_returns.std(),   # Volatility
                recent_returns.iloc[-1],  # Last return
                recent_returns.iloc[-5:].mean(),  # Recent momentum
                (self.price_data.iloc[i] - self.price_data.iloc[i-10]) / self.price_data.iloc[i-10],  # 10-day return
            ]
            features.append(feature_vector)
            
            # Target: future 5-day return
            future_return = (self.price_data.iloc[i+5] - self.price_data.iloc[i]) / self.price_data.iloc[i]
            targets.append(future_return)
        
        if len(features) < 20:
            return {
                'model': 'Reinforcement Learning',
                'action': 'HOLD',
                'confidence': 0.5,
                'expected_reward': 0.0,
                'status': 'Insufficient training data'
            }
        
        # Train model
        X = np.array(features)
        y = np.array(targets)
        
        # Normalize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train random forest
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X_scaled, y)
        
        # Generate current features
        current_features = [
            self.returns.tail(lookback).mean(),
            self.returns.tail(lookback).std(),
            self.returns.iloc[-1],
            self.returns.tail(5).mean(),
            (self.current_price - self.price_data.iloc[-11]) / self.price_data.iloc[-11],
        ]
        
        current_features_scaled = scaler.transform([current_features])
        predicted_return = model.predict(current_features_scaled)[0]
        
        # Decision logic
        if predicted_return > 0.02:  # Expect >2% return
            action = 'BUY'
            confidence = min(0.9, 0.5 + abs(predicted_return) * 5)
        elif predicted_return < -0.02:  # Expect <-2% return
            action = 'SELL'
            confidence = min(0.9, 0.5 + abs(predicted_return) * 5)
        else:
            action = 'HOLD'
            confidence = 0.6
        
        return {
            'model': 'Reinforcement Learning (Random Forest)',
            'action': action,
            'confidence': confidence,
            'expected_reward': predicted_return,
            'feature_importance': dict(zip(
                ['avg_return', 'volatility', 'last_return', 'momentum', 'price_trend'],
                model.feature_importances_
            )),
            'training_samples': len(features)
        }
    
    def genetic_algorithm_optimization(self, generations: int = 50) -> Dict:
        """
        Genetic algorithm for parameter optimization
        
        Args:
            generations: Number of generations to evolve
            
        Returns:
            Optimized trading parameters
        """
        def fitness_function(params):
            """Fitness function for GA optimization"""
            ma_short, ma_long, rsi_oversold, rsi_overbought = params
            
            # Ensure valid parameters
            ma_short = max(2, min(20, int(ma_short)))
            ma_long = max(ma_short + 1, min(50, int(ma_long)))
            rsi_oversold = max(10, min(40, rsi_oversold))
            rsi_overbought = max(60, min(90, rsi_overbought))
            
            # Simulate strategy
            signals = self._simulate_strategy(ma_short, ma_long, rsi_oversold, rsi_overbought)
            
            # Calculate returns
            strategy_returns = signals * self.returns.iloc[ma_long:]
            
            if len(strategy_returns) == 0:
                return -999  # Invalid strategy
            
            # Fitness: Sharpe ratio
            sharpe = strategy_returns.mean() / strategy_returns.std() if strategy_returns.std() > 0 else 0
            return sharpe
        
        # Parameter bounds: [ma_short, ma_long, rsi_oversold, rsi_overbought]
        bounds = [(2, 20), (10, 50), (10, 40), (60, 90)]
        
        # Run genetic algorithm
        result = differential_evolution(
            lambda x: -fitness_function(x),  # Minimize negative fitness
            bounds,
            maxiter=generations,
            seed=42
        )
        
        optimal_params = result.x
        best_fitness = -result.fun
        
        # Extract optimal parameters
        ma_short = max(2, min(20, int(optimal_params[0])))
        ma_long = max(ma_short + 1, min(50, int(optimal_params[1])))
        rsi_oversold = max(10, min(40, optimal_params[2]))
        rsi_overbought = max(60, min(90, optimal_params[3]))
        
        # Generate current signal
        current_signal = self._get_current_signal(ma_short, ma_long, rsi_oversold, rsi_overbought)
        
        return {
            'model': 'Genetic Algorithm',
            'optimal_parameters': {
                'ma_short': ma_short,
                'ma_long': ma_long,
                'rsi_oversold': rsi_oversold,
                'rsi_overbought': rsi_overbought
            },
            'optimized_sharpe_ratio': best_fitness,
            'current_signal': current_signal,
            'generations_evolved': generations,
            'convergence_achieved': result.success
        }
    
    def _simulate_strategy(self, ma_short: int, ma_long: int, 
                          rsi_oversold: float, rsi_overbought: float) -> pd.Series:
        """Simulate trading strategy with given parameters"""
        if len(self.price_data) < ma_long + 14:  # Need enough data for RSI
            return pd.Series([])
        
        # Calculate indicators
        ma_short_series = self.price_data.rolling(ma_short).mean()
        ma_long_series = self.price_data.rolling(ma_long).mean()
        
        # RSI calculation
        delta = self.price_data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Generate signals
        signals = pd.Series(0, index=self.price_data.index)
        
        for i in range(ma_long, len(self.price_data)):
            ma_signal = 1 if ma_short_series.iloc[i] > ma_long_series.iloc[i] else -1
            
            if rsi.iloc[i] < rsi_oversold:
                rsi_signal = 1  # Oversold, buy signal
            elif rsi.iloc[i] > rsi_overbought:
                rsi_signal = -1  # Overbought, sell signal
            else:
                rsi_signal = 0
            
            # Combine signals
            signals.iloc[i] = ma_signal if rsi_signal == 0 else rsi_signal
        
        return signals
    
    def _get_current_signal(self, ma_short: int, ma_long: int, 
                           rsi_oversold: float, rsi_overbought: float) -> str:
        """Get current trading signal"""
        if len(self.price_data) < ma_long + 14:
            return 'INSUFFICIENT_DATA'
        
        # Current indicators
        ma_short_val = self.price_data.tail(ma_short).mean()
        ma_long_val = self.price_data.tail(ma_long).mean()
        
        # Current RSI
        delta = self.price_data.diff().tail(15)
        gain = (delta.where(delta > 0, 0)).mean()
        loss = (-delta.where(delta < 0, 0)).mean()
        if loss == 0:
            current_rsi = 100
        else:
            rs = gain / loss
            current_rsi = 100 - (100 / (1 + rs))
        
        # Generate signal
        if current_rsi < rsi_oversold:
            return 'BUY'
        elif current_rsi > rsi_overbought:
            return 'SELL'
        elif ma_short_val > ma_long_val:
            return 'BUY'
        else:
            return 'SELL'
    
    def comprehensive_optimization(self, portfolio_value: float = 100000) -> Dict:
        """
        Run all optimization models and combine results
        
        Args:
            portfolio_value: Total portfolio value for position sizing
            
        Returns:
            Comprehensive optimization results
        """
        results = {}
        
        # Run all models
        try:
            results['almgren_chriss'] = self.almgren_chriss_optimization(
                total_shares=int(portfolio_value * 0.1 / self.current_price)
            )
        except Exception as e:
            results['almgren_chriss'] = {'error': str(e)}
        
        try:
            results['optimal_stopping'] = self.optimal_stopping_entry()
        except Exception as e:
            results['optimal_stopping'] = {'error': str(e)}
        
        try:
            results['hjb_merton'] = self.hjb_portfolio_optimization()
        except Exception as e:
            results['hjb_merton'] = {'error': str(e)}
        
        try:
            results['reinforcement_learning'] = self.reinforcement_learning_strategy()
        except Exception as e:
            results['reinforcement_learning'] = {'error': str(e)}
        
        try:
            results['genetic_algorithm'] = self.genetic_algorithm_optimization(generations=20)
        except Exception as e:
            results['genetic_algorithm'] = {'error': str(e)}
        
        # Consensus decision
        consensus = self._generate_consensus(results)
        
        return {
            'individual_models': results,
            'consensus_recommendation': consensus,
            'optimization_summary': self._generate_optimization_summary(results),
            'execution_plan': self._generate_execution_plan(consensus, portfolio_value)
        }
    
    def _generate_consensus(self, results: Dict) -> Dict:
        """Generate consensus from multiple models"""
        signals = []
        confidences = []
        
        # Extract signals and confidences
        for model_name, result in results.items():
            if 'error' in result:
                continue
                
            if model_name == 'optimal_stopping':
                signal = result.get('entry_signal', 'WAIT')
                confidence = result.get('confidence', 0.5)
            elif model_name == 'hjb_merton':
                allocation = result.get('optimal_allocation', 0.5)
                if allocation > 0.7:
                    signal = 'BUY'
                elif allocation < 0.3:
                    signal = 'SELL'
                else:
                    signal = 'HOLD'
                confidence = min(0.9, allocation + 0.1)
            elif model_name == 'reinforcement_learning':
                signal = result.get('action', 'HOLD')
                confidence = result.get('confidence', 0.5)
            elif model_name == 'genetic_algorithm':
                signal = result.get('current_signal', 'HOLD')
                confidence = result.get('optimized_sharpe_ratio', 0.5)
                confidence = min(0.9, max(0.1, (confidence + 1) / 2))  # Normalize Sharpe to 0-1
            else:
                continue
            
            signals.append(signal)
            confidences.append(confidence)
        
        if not signals:
            return {
                'signal': 'HOLD',
                'confidence': 0.5,
                'consensus_strength': 0.0,
                'recommendation': 'Insufficient model output for consensus'
            }
        
        # Vote counting
        signal_votes = {}
        weighted_votes = {}
        
        for signal, confidence in zip(signals, confidences):
            signal_votes[signal] = signal_votes.get(signal, 0) + 1
            weighted_votes[signal] = weighted_votes.get(signal, 0) + confidence
        
        # Determine consensus
        max_votes = max(signal_votes.values())
        consensus_signals = [sig for sig, votes in signal_votes.items() if votes == max_votes]
        
        if len(consensus_signals) == 1:
            consensus_signal = consensus_signals[0]
            consensus_strength = max_votes / len(signals)
        else:
            # Tie-breaking by weighted votes
            consensus_signal = max(weighted_votes.keys(), key=lambda x: weighted_votes[x])
            consensus_strength = 0.6  # Moderate consensus due to tie
        
        avg_confidence = np.mean(confidences)
        
        return {
            'signal': consensus_signal,
            'confidence': avg_confidence,
            'consensus_strength': consensus_strength,
            'model_agreement': f"{max_votes}/{len(signals)} models agree",
            'recommendation': f"{consensus_signal} with {avg_confidence:.1%} confidence"
        }
    
    def _generate_optimization_summary(self, results: Dict) -> Dict:
        """Generate summary of optimization results"""
        summary = {
            'models_run': len(results),
            'successful_models': len([r for r in results.values() if 'error' not in r]),
            'failed_models': len([r for r in results.values() if 'error' in r]),
            'key_insights': []
        }
        
        # Extract key insights
        for model_name, result in results.items():
            if 'error' in result:
                summary['key_insights'].append(f"{model_name}: Failed - {result['error']}")
                continue
            
            if model_name == 'hjb_merton':
                allocation = result.get('optimal_allocation', 0)
                summary['key_insights'].append(f"HJB Model: {allocation:.1%} optimal allocation")
            elif model_name == 'genetic_algorithm':
                sharpe = result.get('optimized_sharpe_ratio', 0)
                summary['key_insights'].append(f"Genetic Algorithm: {sharpe:.3f} optimized Sharpe ratio")
            elif model_name == 'reinforcement_learning':
                reward = result.get('expected_reward', 0)
                summary['key_insights'].append(f"RL Model: {reward:.2%} expected return")
        
        return summary
    
    def _generate_execution_plan(self, consensus: Dict, portfolio_value: float) -> Dict:
        """Generate detailed professional execution plan"""
        signal = consensus['signal']
        confidence = consensus['confidence']
        
        # Advanced position sizing based on Kelly criterion and confidence
        max_position = 0.25  # 25% max position
        position_size = min(max_position, confidence * 0.3)  # Scale by confidence
        
        if signal == 'SELL':
            position_size = -position_size
        elif signal == 'HOLD' or signal == 'WAIT':
            position_size = 0
        
        dollar_amount = portfolio_value * position_size
        share_amount = int(dollar_amount / self.current_price) if self.current_price > 0 else 0
        
        # Professional execution strategy based on position size
        if abs(share_amount) > 5000:
            execution_method = 'TWAP (Time-Weighted Average Price)'
            time_horizon = '3-5 trading days'
            execution_style = 'Institutional Block Trading'
        elif abs(share_amount) > 1000:
            execution_method = 'VWAP (Volume-Weighted Average Price)'
            time_horizon = '1-3 trading days'
            execution_style = 'Algorithmic Execution'
        else:
            execution_method = 'Market Order with Smart Routing'
            time_horizon = 'Intraday (same session)'
            execution_style = 'Direct Market Access'
        
        # Advanced risk management with multiple levels
        current_vol = self.returns.std() * np.sqrt(252) if len(self.returns) > 20 else 0.20
        
        # Dynamic stop loss based on volatility
        stop_loss_distance = max(0.03, current_vol * 0.5)  # Minimum 3% or 0.5x annual volatility
        take_profit_distance = stop_loss_distance * 2.5  # 2.5:1 reward-to-risk ratio
        
        if signal == 'BUY':
            stop_loss = self.current_price * (1 - stop_loss_distance)
            take_profit_1 = self.current_price * (1 + take_profit_distance * 0.6)  # First target
            take_profit_2 = self.current_price * (1 + take_profit_distance)  # Full target
        else:
            stop_loss = self.current_price * (1 + stop_loss_distance)
            take_profit_1 = self.current_price * (1 - take_profit_distance * 0.6)
            take_profit_2 = self.current_price * (1 - take_profit_distance)
        
        return {
            'action': signal,
            'position_size_percent': position_size,
            'dollar_amount': dollar_amount,
            'share_amount': share_amount,
            'execution_method': execution_method,
            'execution_style': execution_style,
            'time_horizon': time_horizon,
            'entry_strategy': {
                'primary_entry': f'{abs(position_size * 0.6):.1%} of target position',
                'secondary_entry': f'{abs(position_size * 0.4):.1%} on pullback/breakout',
                'entry_conditions': 'Confirm with volume and momentum indicators',
                'max_slippage': '0.1% for market orders, minimize for algo orders'
            },
            'risk_management': {
                'stop_loss': stop_loss,
                'take_profit_1': take_profit_1,
                'take_profit_2': take_profit_2,
                'max_loss': abs(dollar_amount) * stop_loss_distance,
                'position_scaling': 'Scale out 50% at first target, trail remainder',
                'volatility_adjustment': f'Stop distance: {stop_loss_distance:.1%} (based on {current_vol:.1%} annual vol)',
                'risk_reward_ratio': '2.5:1 minimum target'
            },
            'monitoring_plan': {
                'key_levels': [stop_loss, take_profit_1, take_profit_2],
                'technical_invalidation': 'Close below/above key support/resistance',
                'fundamental_triggers': 'Major news, earnings, or sector rotation',
                'review_frequency': 'Daily for active positions, weekly for long-term holds'
            },
            'contingency_plans': {
                'gap_risk': 'Use options for downside protection if position > 15%',
                'liquidity_risk': 'Reduce position size if ADV < 10x target volume',
                'correlation_risk': 'Monitor sector exposure and overall portfolio beta',
                'event_risk': 'Reduce exposure before earnings or major announcements'
            }
        }


def integrate_single_stock_optimization(price_data: pd.Series, portfolio_value: float = 100000) -> Dict:
    """
    Main function to integrate single stock optimization with LLM
    
    Args:
        price_data: Historical price data
        portfolio_value: Portfolio value for position sizing
        
    Returns:
        Comprehensive optimization results for LLM integration
    """
    optimizer = SingleStockOptimizer(price_data)
    optimization_results = optimizer.comprehensive_optimization(portfolio_value)
    
    # Format for LLM consumption
    llm_integration = {
        'quantitative_signals': {
            'consensus_action': optimization_results['consensus_recommendation']['signal'],
            'confidence_level': optimization_results['consensus_recommendation']['confidence'],
            'model_agreement': optimization_results['consensus_recommendation']['consensus_strength'],
            'execution_plan': optimization_results['execution_plan']
        },
        'mathematical_evidence': {
            'hjb_allocation': optimization_results['individual_models'].get('hjb_merton', {}).get('optimal_allocation', 'N/A'),
            'optimal_stopping_signal': optimization_results['individual_models'].get('optimal_stopping', {}).get('entry_signal', 'N/A'),
            'ml_prediction': optimization_results['individual_models'].get('reinforcement_learning', {}).get('expected_reward', 'N/A'),
            'genetic_optimization': optimization_results['individual_models'].get('genetic_algorithm', {}).get('optimized_sharpe_ratio', 'N/A')
        },
        'risk_metrics': optimization_results['execution_plan']['risk_management'],
        'optimization_summary': optimization_results['optimization_summary'],
        'llm_guidance': generate_llm_guidance_text(optimization_results)
    }
    
    return llm_integration


def generate_llm_guidance_text(optimization_results: Dict) -> str:
    """Generate guidance text for LLM"""
    consensus = optimization_results['consensus_recommendation']
    execution = optimization_results['execution_plan']
    
    guidance = f"""
ADVANCED QUANTITATIVE OPTIMIZATION RESULTS:

MATHEMATICAL CONSENSUS: {consensus['signal']} 
- Confidence: {consensus['confidence']:.1%}
- Model Agreement: {consensus['consensus_strength']:.1%}
- Position Size: {execution['position_size_percent']:.1%} of portfolio

EXECUTION PARAMETERS:
- Dollar Amount: ${execution['dollar_amount']:,.0f}
- Share Amount: {execution['share_amount']:,} shares
- Method: {execution['execution_method']}
- Time Horizon: {execution['time_horizon']}

RISK CONTROLS:
- Stop Loss: ${execution['risk_management']['stop_loss']:.2f}
- Take Profit: ${execution['risk_management']['take_profit']:.2f}
- Max Loss: ${execution['risk_management']['max_loss']:,.0f}

IMPORTANT: These are mathematically optimized parameters based on multiple 
quantitative models including Almgren-Chriss execution, HJB portfolio theory, 
and machine learning predictions. The LLM should strongly consider these 
quantitative inputs when generating the final trading recommendation.
"""
    
    return guidance
