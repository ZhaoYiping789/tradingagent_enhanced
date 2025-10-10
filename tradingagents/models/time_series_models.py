"""
Advanced Time Series Mathematical Models for Trading
Implements ARIMA, GARCH, and other sophisticated models for better trading decisions
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

try:
    from arch import arch_model
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    from statsmodels.stats.diagnostic import acorr_ljungbox
    ADVANCED_MODELS_AVAILABLE = True
except ImportError:
    ADVANCED_MODELS_AVAILABLE = False
    print("Advanced time series models not available. Install arch and statsmodels for full functionality.")


class TimeSeriesAnalyzer:
    """
    Comprehensive time series analysis for trading decisions
    """
    
    def __init__(self, price_data: pd.Series):
        """
        Initialize with price data
        
        Args:
            price_data: pandas Series with datetime index and price values
        """
        self.price_data = price_data
        self.returns = price_data.pct_change().dropna()
        self.log_returns = np.log(price_data).diff().dropna()
        
    def kelly_criterion_advanced(self, win_probability: float, avg_win: float, avg_loss: float, 
                                volatility: float) -> dict:
        """
        Enhanced Kelly Criterion with volatility adjustment and fractional sizing
        
        Args:
            win_probability: Probability of winning trade (0-1)
            avg_win: Average gain on winning trades (as decimal, e.g., 0.10 for 10%)
            avg_loss: Average loss on losing trades (as positive decimal)
            volatility: Asset volatility (annualized)
            
        Returns:
            Dictionary with Kelly fraction and adjusted position size
        """
        # Classic Kelly Criterion
        b = avg_win / avg_loss  # Odds ratio
        p = win_probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # Volatility adjustment
        vol_adjustment = min(1.0, 0.20 / volatility)  # Reduce size for high vol assets
        
        # Conservative fractional Kelly (typically 0.25 to 0.5 of full Kelly)
        fractional_kelly = kelly_fraction * 0.25 * vol_adjustment
        
        # Position size limits for risk management
        max_position = 0.20  # Never more than 20% in single position
        min_position = 0.01  # Minimum meaningful position
        
        final_position = max(min_position, min(max_position, fractional_kelly))
        
        return {
            'kelly_fraction': kelly_fraction,
            'volatility_adjustment': vol_adjustment,
            'fractional_kelly': fractional_kelly,
            'recommended_position': final_position,
            'risk_level': 'High' if final_position > 0.15 else 'Medium' if final_position > 0.08 else 'Low'
        }
    
    def arima_forecast(self, forecast_periods: int = 5) -> dict:
        """
        ARIMA model for price prediction
        
        Args:
            forecast_periods: Number of periods to forecast
            
        Returns:
            Dictionary with forecast results
        """
        if not ADVANCED_MODELS_AVAILABLE:
            return self._simple_trend_forecast(forecast_periods)
        
        try:
            # Test for stationarity
            adf_result = adfuller(self.returns)
            is_stationary = adf_result[1] < 0.05
            
            # Auto ARIMA selection (simplified)
            best_aic = float('inf')
            best_model = None
            best_order = None
            
            # Test common ARIMA orders
            orders = [(1,0,1), (1,1,1), (2,0,1), (2,1,1), (1,0,2), (2,0,2)]
            
            for order in orders:
                try:
                    model = ARIMA(self.returns, order=order)
                    fitted_model = model.fit()
                    if fitted_model.aic < best_aic:
                        best_aic = fitted_model.aic
                        best_model = fitted_model
                        best_order = order
                except:
                    continue
            
            if best_model is None:
                return self._simple_trend_forecast(forecast_periods)
            
            # Generate forecast
            forecast = best_model.forecast(steps=forecast_periods)
            forecast_se = best_model.forecast(steps=forecast_periods)
            
            # Convert to price forecast (assuming returns forecast)
            current_price = self.price_data.iloc[-1]
            price_forecast = [current_price * np.exp(np.sum(forecast[:i+1])) for i in range(forecast_periods)]
            
            return {
                'model_type': 'ARIMA',
                'model_order': best_order,
                'aic': best_aic,
                'forecast_returns': forecast.tolist(),
                'forecast_prices': price_forecast,
                'confidence_intervals': self._calculate_forecast_ci(forecast, forecast_se),
                'trend_direction': 'Bullish' if np.mean(forecast) > 0 else 'Bearish',
                'forecast_accuracy': self._estimate_forecast_accuracy(best_model)
            }
            
        except Exception as e:
            return self._simple_trend_forecast(forecast_periods)
    
    def garch_volatility_forecast(self, forecast_periods: int = 5) -> dict:
        """
        GARCH model for volatility forecasting
        
        Args:
            forecast_periods: Number of periods to forecast
            
        Returns:
            Dictionary with volatility forecast
        """
        if not ADVANCED_MODELS_AVAILABLE:
            return self._simple_volatility_forecast(forecast_periods)
        
        try:
            # Fit GARCH(1,1) model
            model = arch_model(self.returns * 100, vol='Garch', p=1, q=1, dist='normal')
            fitted_model = model.fit(disp='off')
            
            # Generate volatility forecast
            volatility_forecast = fitted_model.forecast(horizon=forecast_periods)
            vol_mean = volatility_forecast.variance.iloc[-1].values / 10000  # Convert back from percentage
            
            return {
                'model_type': 'GARCH(1,1)',
                'current_volatility': fitted_model.conditional_volatility.iloc[-1] / 100,
                'forecast_volatility': np.sqrt(vol_mean * 252),  # Annualized
                'volatility_regime': self._classify_volatility_regime(np.sqrt(vol_mean * 252)),
                'risk_adjustment': self._calculate_risk_adjustment(np.sqrt(vol_mean * 252))
            }
            
        except Exception as e:
            return self._simple_volatility_forecast(forecast_periods)
    
    def momentum_indicators(self) -> dict:
        """
        Calculate advanced momentum indicators
        
        Returns:
            Dictionary with momentum analysis
        """
        returns = self.returns
        prices = self.price_data
        
        # RSI calculation
        rsi = self._calculate_rsi(prices, 14)
        
        # MACD
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        macd_histogram = macd_line - signal_line
        
        # Bollinger Bands
        bb_middle = prices.rolling(20).mean()
        bb_std = prices.rolling(20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        bb_position = (prices.iloc[-1] - bb_lower.iloc[-1]) / (bb_upper.iloc[-1] - bb_lower.iloc[-1])
        
        # Momentum score
        momentum_score = self._calculate_momentum_score(rsi.iloc[-1], macd_histogram.iloc[-1], bb_position)
        
        return {
            'rsi': rsi.iloc[-1],
            'rsi_signal': 'Overbought' if rsi.iloc[-1] > 70 else 'Oversold' if rsi.iloc[-1] < 30 else 'Neutral',
            'macd': macd_line.iloc[-1],
            'macd_signal': signal_line.iloc[-1],
            'macd_histogram': macd_histogram.iloc[-1],
            'bollinger_position': bb_position,
            'momentum_score': momentum_score,
            'momentum_signal': 'Strong Buy' if momentum_score > 0.7 else 'Buy' if momentum_score > 0.3 else 'Hold' if momentum_score > -0.3 else 'Sell' if momentum_score > -0.7 else 'Strong Sell'
        }
    
    def risk_metrics(self) -> dict:
        """
        Calculate comprehensive risk metrics
        
        Returns:
            Dictionary with risk analysis
        """
        returns = self.returns
        
        # Value at Risk (VaR)
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        # Conditional Value at Risk (CVaR)
        cvar_95 = returns[returns <= var_95].mean()
        cvar_99 = returns[returns <= var_99].mean()
        
        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # Sharpe Ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        sharpe_ratio = (returns.mean() - risk_free_rate) / returns.std() * np.sqrt(252)
        
        # Volatility
        volatility = returns.std() * np.sqrt(252)
        
        return {
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'volatility': volatility,
            'risk_level': self._classify_risk_level(volatility, max_drawdown, sharpe_ratio)
        }
    
    def trend_analysis(self) -> dict:
        """
        Comprehensive trend analysis
        
        Returns:
            Dictionary with trend information
        """
        prices = self.price_data
        
        # Moving averages
        sma_20 = prices.rolling(20).mean()
        sma_50 = prices.rolling(50).mean()
        sma_200 = prices.rolling(200).mean()
        
        # Trend signals
        current_price = prices.iloc[-1]
        above_sma20 = current_price > sma_20.iloc[-1]
        above_sma50 = current_price > sma_50.iloc[-1]
        above_sma200 = current_price > sma_200.iloc[-1]
        
        # Trend strength
        trend_strength = sum([above_sma20, above_sma50, above_sma200]) / 3
        
        # Price position in recent range
        recent_high = prices.tail(20).max()
        recent_low = prices.tail(20).min()
        price_position = (current_price - recent_low) / (recent_high - recent_low) if recent_high != recent_low else 0.5
        
        return {
            'sma_20': sma_20.iloc[-1],
            'sma_50': sma_50.iloc[-1],
            'sma_200': sma_200.iloc[-1],
            'above_sma20': above_sma20,
            'above_sma50': above_sma50,
            'above_sma200': above_sma200,
            'trend_strength': trend_strength,
            'trend_signal': 'Strong Uptrend' if trend_strength > 0.8 else 'Uptrend' if trend_strength > 0.6 else 'Neutral' if trend_strength > 0.4 else 'Downtrend' if trend_strength > 0.2 else 'Strong Downtrend',
            'price_position': price_position
        }
    
    def generate_mathematical_signals(self) -> dict:
        """
        Generate comprehensive mathematical trading signals
        
        Returns:
            Dictionary with all mathematical indicators and final signal
        """
        # Get all analyses
        arima_results = self.arima_forecast()
        garch_results = self.garch_volatility_forecast()
        momentum_results = self.momentum_indicators()
        risk_results = self.risk_metrics()
        trend_results = self.trend_analysis()
        
        # Calculate position sizing
        # Estimate win probability from trend strength and momentum
        win_prob = max(0.3, min(0.7, (trend_results['trend_strength'] + momentum_results['momentum_score']) / 2 + 0.5))
        avg_win = 0.08  # 8% average win
        avg_loss = 0.05  # 5% average loss
        
        kelly_results = self.kelly_criterion_advanced(win_prob, avg_win, avg_loss, risk_results['volatility'])
        
        # Generate composite signal
        signal_score = self._calculate_composite_signal(arima_results, momentum_results, trend_results, risk_results)
        
        return {
            'arima_forecast': arima_results,
            'garch_volatility': garch_results,
            'momentum_analysis': momentum_results,
            'risk_metrics': risk_results,
            'trend_analysis': trend_results,
            'kelly_position_sizing': kelly_results,
            'composite_signal_score': signal_score,
            'mathematical_recommendation': self._signal_to_recommendation(signal_score),
            'confidence_level': self._calculate_confidence(signal_score, risk_results),
            'suggested_position_size': kelly_results['recommended_position'],
            'risk_adjusted_signal': self._risk_adjust_signal(signal_score, risk_results)
        }
    
    # Helper methods
    def _simple_trend_forecast(self, periods: int) -> dict:
        """Fallback simple trend forecast"""
        recent_return = self.returns.tail(5).mean()
        current_price = self.price_data.iloc[-1]
        
        forecast_prices = [current_price * (1 + recent_return) ** (i+1) for i in range(periods)]
        
        return {
            'model_type': 'Simple Trend',
            'forecast_prices': forecast_prices,
            'trend_direction': 'Bullish' if recent_return > 0 else 'Bearish',
            'forecast_accuracy': 0.6
        }
    
    def _simple_volatility_forecast(self, periods: int) -> dict:
        """Fallback simple volatility forecast"""
        current_vol = self.returns.std() * np.sqrt(252)
        
        return {
            'model_type': 'Historical Volatility',
            'current_volatility': current_vol,
            'forecast_volatility': current_vol,
            'volatility_regime': self._classify_volatility_regime(current_vol),
            'risk_adjustment': self._calculate_risk_adjustment(current_vol)
        }
    
    def _calculate_rsi(self, prices: pd.Series, periods: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_momentum_score(self, rsi: float, macd_hist: float, bb_pos: float) -> float:
        """Calculate composite momentum score"""
        rsi_score = (rsi - 50) / 50  # Normalize RSI
        macd_score = np.tanh(macd_hist * 100)  # Normalize MACD
        bb_score = (bb_pos - 0.5) * 2  # Normalize Bollinger position
        
        return (rsi_score + macd_score + bb_score) / 3
    
    def _classify_volatility_regime(self, volatility: float) -> str:
        """Classify volatility regime"""
        if volatility < 0.15:
            return 'Low Volatility'
        elif volatility < 0.25:
            return 'Normal Volatility'
        elif volatility < 0.40:
            return 'High Volatility'
        else:
            return 'Extreme Volatility'
    
    def _calculate_risk_adjustment(self, volatility: float) -> float:
        """Calculate risk adjustment factor"""
        return max(0.3, min(1.0, 0.20 / volatility))
    
    def _classify_risk_level(self, volatility: float, max_drawdown: float, sharpe_ratio: float) -> str:
        """Classify overall risk level"""
        risk_score = volatility * 2 + abs(max_drawdown) * 3 - sharpe_ratio * 0.5
        
        if risk_score < 0.3:
            return 'Low Risk'
        elif risk_score < 0.6:
            return 'Medium Risk'
        else:
            return 'High Risk'
    
    def _calculate_composite_signal(self, arima: dict, momentum: dict, trend: dict, risk: dict) -> float:
        """Calculate composite signal score"""
        # Combine different signals with weights
        trend_signal = trend['trend_strength'] * 2 - 1  # Convert to -1 to 1 scale
        momentum_signal = momentum['momentum_score']
        
        # ARIMA signal
        arima_signal = 0
        if 'trend_direction' in arima:
            arima_signal = 0.3 if arima['trend_direction'] == 'Bullish' else -0.3
        
        # Risk adjustment
        risk_adj = 1.0 if risk['risk_level'] == 'Low Risk' else 0.7 if risk['risk_level'] == 'Medium Risk' else 0.4
        
        composite = (trend_signal * 0.4 + momentum_signal * 0.4 + arima_signal * 0.2) * risk_adj
        
        return max(-1.0, min(1.0, composite))
    
    def _signal_to_recommendation(self, signal_score: float) -> str:
        """Convert signal score to recommendation"""
        if signal_score > 0.6:
            return 'STRONG BUY'
        elif signal_score > 0.2:
            return 'BUY'
        elif signal_score > -0.2:
            return 'HOLD'
        elif signal_score > -0.6:
            return 'REDUCE'
        else:
            return 'SELL'
    
    def _calculate_confidence(self, signal_score: float, risk_results: dict) -> float:
        """Calculate confidence level"""
        base_confidence = abs(signal_score)
        
        # Adjust for risk
        if risk_results['sharpe_ratio'] > 1.0:
            base_confidence *= 1.2
        elif risk_results['sharpe_ratio'] < 0:
            base_confidence *= 0.7
        
        return max(0.3, min(1.0, base_confidence))
    
    def _risk_adjust_signal(self, signal_score: float, risk_results: dict) -> str:
        """Apply risk adjustment to signal"""
        if risk_results['risk_level'] == 'High Risk':
            # More conservative in high risk environment
            if signal_score > 0.4:
                return 'ACCUMULATE GRADUALLY'
            elif signal_score < -0.4:
                return 'REDUCE GRADUALLY'
            else:
                return 'HOLD'
        else:
            return self._signal_to_recommendation(signal_score)
    
    def _calculate_forecast_ci(self, forecast, forecast_se):
        """Calculate forecast confidence intervals"""
        # Simplified confidence intervals
        return {
            'lower_95': (forecast - 1.96 * forecast_se).tolist() if hasattr(forecast_se, '__iter__') else [],
            'upper_95': (forecast + 1.96 * forecast_se).tolist() if hasattr(forecast_se, '__iter__') else []
        }
    
    def _estimate_forecast_accuracy(self, model) -> float:
        """Estimate forecast accuracy"""
        try:
            # Use AIC to estimate accuracy (simplified)
            aic = model.aic
            accuracy = max(0.5, min(0.9, 1.0 - (aic - 100) / 1000))
            return accuracy
        except:
            return 0.7
