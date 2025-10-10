"""
Balanced Risk Management System
Prevents extreme decisions like "SELL ALL" and provides graduated risk management
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class RiskLimits:
    """Risk limits for portfolio management"""
    max_single_position: float = 0.25  # 25% max in single stock
    max_sector_concentration: float = 0.40  # 40% max in single sector
    max_portfolio_risk: float = 0.15  # 15% portfolio VaR
    min_cash_reserve: float = 0.05  # 5% minimum cash
    max_daily_trades: int = 5
    max_leverage: float = 1.0  # No leverage


class BalancedRiskManager:
    """
    Advanced risk management that prevents extreme decisions
    """
    
    def __init__(self, risk_limits: RiskLimits = None):
        self.risk_limits = risk_limits or RiskLimits()
        
    def evaluate_trading_decision(self, signal: str, confidence: float, 
                                 mathematical_indicators: Dict, current_position: float = 0.0,
                                 portfolio_context: Dict = None) -> Dict:
        """
        Evaluate and potentially modify trading decisions based on risk management
        
        Args:
            signal: Raw signal (BUY/SELL/HOLD etc.)
            confidence: Confidence level (0-1)
            mathematical_indicators: Output from TimeSeriesAnalyzer
            current_position: Current position size (0-1)
            portfolio_context: Portfolio information
            
        Returns:
            Modified trading decision with risk adjustments
        """
        portfolio_context = portfolio_context or {}
        
        # Extract key metrics
        volatility = mathematical_indicators.get('risk_metrics', {}).get('volatility', 0.25)
        kelly_position = mathematical_indicators.get('kelly_position_sizing', {}).get('recommended_position', 0.1)
        risk_level = mathematical_indicators.get('risk_metrics', {}).get('risk_level', 'Medium Risk')
        sharpe_ratio = mathematical_indicators.get('risk_metrics', {}).get('sharpe_ratio', 0.5)
        
        # Apply risk management logic
        risk_adjusted_decision = self._apply_risk_management(
            signal, confidence, volatility, kelly_position, risk_level, 
            sharpe_ratio, current_position, portfolio_context
        )
        
        return risk_adjusted_decision
    
    def _apply_risk_management(self, signal: str, confidence: float, volatility: float,
                              kelly_position: float, risk_level: str, sharpe_ratio: float,
                              current_position: float, portfolio_context: Dict) -> Dict:
        """Apply comprehensive risk management rules"""
        
        # Initialize risk-adjusted decision
        adjusted_decision = {
            'original_signal': signal,
            'original_confidence': confidence,
            'risk_adjusted_signal': signal,
            'risk_adjusted_confidence': confidence,
            'position_size': kelly_position,
            'risk_warnings': [],
            'risk_mitigations': [],
            'execution_approach': 'IMMEDIATE',
            'time_horizon': 'MEDIUM_TERM',
            'monitoring_frequency': 'WEEKLY'
        }
        
        # Rule 1: Prevent extreme "SELL ALL" decisions
        if signal in ['SELL', 'STRONG SELL'] and current_position > 0:
            if confidence < 0.8 or risk_level == 'High Risk':
                # Gradual reduction instead of full sell
                adjusted_decision['risk_adjusted_signal'] = 'REDUCE GRADUALLY'
                adjusted_decision['position_size'] = max(0, current_position - 0.25)  # Reduce by 25%
                adjusted_decision['execution_approach'] = 'GRADUAL_OVER_WEEKS'
                adjusted_decision['risk_warnings'].append('Preventing extreme SELL ALL decision')
                adjusted_decision['risk_mitigations'].append('Converting to gradual reduction strategy')
        
        # Rule 2: Position sizing limits
        if signal in ['BUY', 'STRONG BUY']:
            max_position = min(
                self.risk_limits.max_single_position,
                kelly_position,
                0.30 if risk_level == 'Low Risk' else 0.20 if risk_level == 'Medium Risk' else 0.10
            )
            
            if current_position + kelly_position > max_position:
                adjusted_decision['position_size'] = max_position - current_position
                adjusted_decision['risk_warnings'].append(f'Position size limited to {max_position:.1%}')
        
        # Rule 3: Volatility-based adjustments
        if volatility > 0.30:  # High volatility
            adjusted_decision['risk_adjusted_confidence'] *= 0.8
            adjusted_decision['execution_approach'] = 'GRADUAL_OVER_DAYS'
            adjusted_decision['monitoring_frequency'] = 'DAILY'
            adjusted_decision['risk_warnings'].append('High volatility detected')
            
            # Reduce position sizes in high volatility
            if signal in ['BUY', 'STRONG BUY']:
                adjusted_decision['position_size'] *= 0.7
        
        # Rule 4: Low Sharpe ratio protection
        if sharpe_ratio < 0.3:
            if signal in ['BUY', 'STRONG BUY']:
                adjusted_decision['risk_adjusted_signal'] = 'HOLD'
                adjusted_decision['position_size'] = 0
                adjusted_decision['risk_warnings'].append('Poor risk-adjusted returns detected')
                adjusted_decision['risk_mitigations'].append('Blocking new position due to low Sharpe ratio')
        
        # Rule 5: Confidence-based position scaling
        if confidence < 0.6:
            adjusted_decision['position_size'] *= confidence / 0.6  # Scale down for low confidence
            adjusted_decision['execution_approach'] = 'GRADUAL_OVER_WEEKS'
            adjusted_decision['risk_warnings'].append('Low confidence signal')
        
        # Rule 6: Anti-momentum in extreme markets
        if signal == 'STRONG SELL' and confidence > 0.8:
            # Check if this might be a capitulation signal (contrarian opportunity)
            if self._detect_oversold_conditions(portfolio_context):
                adjusted_decision['risk_adjusted_signal'] = 'HOLD'
                adjusted_decision['risk_mitigations'].append('Potential oversold contrarian opportunity')
        
        # Rule 7: Time horizon adjustments
        if risk_level == 'High Risk':
            adjusted_decision['time_horizon'] = 'SHORT_TERM'
            adjusted_decision['monitoring_frequency'] = 'DAILY'
        elif risk_level == 'Low Risk':
            adjusted_decision['time_horizon'] = 'LONG_TERM'
            adjusted_decision['monitoring_frequency'] = 'MONTHLY'
        
        # Rule 8: Generate specific execution plan
        adjusted_decision['execution_plan'] = self._generate_execution_plan(
            adjusted_decision['risk_adjusted_signal'],
            adjusted_decision['position_size'],
            adjusted_decision['execution_approach'],
            current_position
        )
        
        return adjusted_decision
    
    def _detect_oversold_conditions(self, portfolio_context: Dict) -> bool:
        """Detect potential oversold conditions for contrarian signals"""
        # Simple heuristic - in real implementation, would use more sophisticated indicators
        recent_performance = portfolio_context.get('recent_performance', 0)
        return recent_performance < -0.15  # Down more than 15%
    
    def _generate_execution_plan(self, signal: str, position_size: float, 
                                execution_approach: str, current_position: float) -> Dict:
        """Generate detailed execution plan"""
        
        plan = {
            'action': signal,
            'target_position': current_position + position_size if signal in ['BUY', 'STRONG BUY'] else current_position - position_size,
            'phases': [],
            'timeline': '',
            'order_types': []
        }
        
        if execution_approach == 'IMMEDIATE':
            plan['phases'] = [
                {'week': 1, 'action': f'{signal} {position_size:.1%}', 'reasoning': 'High confidence immediate execution'}
            ]
            plan['timeline'] = '1 week'
            plan['order_types'] = ['Market Order']
            
        elif execution_approach == 'GRADUAL_OVER_DAYS':
            daily_amount = position_size / 5  # Spread over 5 days
            plan['phases'] = [
                {'day': i+1, 'action': f'{signal} {daily_amount:.1%}', 'reasoning': 'Gradual execution to minimize market impact'}
                for i in range(5)
            ]
            plan['timeline'] = '5 trading days'
            plan['order_types'] = ['TWAP Orders', 'Limit Orders']
            
        elif execution_approach == 'GRADUAL_OVER_WEEKS':
            weekly_amount = position_size / 4  # Spread over 4 weeks
            plan['phases'] = [
                {'week': i+1, 'action': f'{signal} {weekly_amount:.1%}', 'reasoning': 'Extended execution for risk management'}
                for i in range(4)
            ]
            plan['timeline'] = '4 weeks'
            plan['order_types'] = ['VWAP Orders', 'Iceberg Orders']
        
        return plan
    
    def generate_risk_report(self, decision_analysis: Dict) -> str:
        """Generate human-readable risk report"""
        
        report = f"""
## 🛡️ RISK MANAGEMENT ANALYSIS

### Original vs Risk-Adjusted Decision
- **Original Signal**: {decision_analysis['original_signal']}
- **Risk-Adjusted Signal**: {decision_analysis['risk_adjusted_signal']}
- **Confidence**: {decision_analysis['original_confidence']:.1%} → {decision_analysis['risk_adjusted_confidence']:.1%}

### Position Sizing
- **Recommended Position**: {decision_analysis['position_size']:.1%} of portfolio
- **Execution Approach**: {decision_analysis['execution_approach']}
- **Time Horizon**: {decision_analysis['time_horizon']}

### Risk Warnings
"""
        
        for warning in decision_analysis['risk_warnings']:
            report += f"- ⚠️ {warning}\n"
        
        report += "\n### Risk Mitigations Applied\n"
        for mitigation in decision_analysis['risk_mitigations']:
            report += f"- ✅ {mitigation}\n"
        
        report += f"""
### Execution Plan
- **Timeline**: {decision_analysis['execution_plan']['timeline']}
- **Target Position**: {decision_analysis['execution_plan']['target_position']:.1%}
- **Order Types**: {', '.join(decision_analysis['execution_plan']['order_types'])}

### Monitoring Requirements
- **Frequency**: {decision_analysis['monitoring_frequency']}
- **Key Metrics**: Price movement, volume, volatility
- **Review Triggers**: 5% adverse movement, major news events
"""
        
        return report


def integrate_mathematical_models_with_llm(price_data: pd.Series, 
                                         current_position: float = 0.0,
                                         portfolio_context: Dict = None) -> Dict:
    """
    Integrate mathematical models with LLM for balanced decision making
    
    Args:
        price_data: Historical price data
        current_position: Current position size
        portfolio_context: Portfolio information
        
    Returns:
        Comprehensive analysis for LLM integration
    """
    from tradingagents.models.time_series_models import TimeSeriesAnalyzer
    
    # Mathematical analysis
    analyzer = TimeSeriesAnalyzer(price_data)
    math_signals = analyzer.generate_mathematical_signals()
    
    # Risk management
    risk_manager = BalancedRiskManager()
    risk_adjusted_decision = risk_manager.evaluate_trading_decision(
        signal=math_signals['mathematical_recommendation'],
        confidence=math_signals['confidence_level'],
        mathematical_indicators=math_signals,
        current_position=current_position,
        portfolio_context=portfolio_context
    )
    
    # Generate summary for LLM
    llm_summary = {
        'mathematical_analysis': {
            'trend_signal': math_signals['trend_analysis']['trend_signal'],
            'momentum_signal': math_signals['momentum_analysis']['momentum_signal'],
            'volatility_regime': math_signals['garch_volatility']['volatility_regime'],
            'risk_level': math_signals['risk_metrics']['risk_level'],
            'kelly_position': math_signals['kelly_position_sizing']['recommended_position'],
            'composite_score': math_signals['composite_signal_score']
        },
        'risk_management': {
            'recommended_action': risk_adjusted_decision['risk_adjusted_signal'],
            'position_size': risk_adjusted_decision['position_size'],
            'execution_plan': risk_adjusted_decision['execution_plan'],
            'risk_warnings': risk_adjusted_decision['risk_warnings'],
            'time_horizon': risk_adjusted_decision['time_horizon']
        },
        'key_insights': generate_key_insights(math_signals, risk_adjusted_decision),
        'llm_guidance': generate_llm_guidance(math_signals, risk_adjusted_decision)
    }
    
    return llm_summary


def generate_key_insights(math_signals: Dict, risk_decision: Dict) -> List[str]:
    """Generate key insights for LLM"""
    insights = []
    
    # Trend insights
    trend_strength = math_signals['trend_analysis']['trend_strength']
    if trend_strength > 0.7:
        insights.append(f"Strong uptrend detected (strength: {trend_strength:.1%})")
    elif trend_strength < 0.3:
        insights.append(f"Downtrend detected (strength: {(1-trend_strength):.1%})")
    
    # Risk insights
    volatility = math_signals['risk_metrics']['volatility']
    if volatility > 0.30:
        insights.append(f"High volatility environment ({volatility:.1%} annualized)")
    
    # Position sizing insights
    kelly_pos = math_signals['kelly_position_sizing']['recommended_position']
    if kelly_pos > 0.15:
        insights.append(f"Kelly Criterion suggests significant position ({kelly_pos:.1%})")
    elif kelly_pos < 0.05:
        insights.append(f"Kelly Criterion suggests minimal position ({kelly_pos:.1%})")
    
    # Risk management insights
    if risk_decision['risk_warnings']:
        insights.append(f"Risk management applied {len(risk_decision['risk_warnings'])} adjustments")
    
    return insights


def generate_llm_guidance(math_signals: Dict, risk_decision: Dict) -> str:
    """Generate guidance text for LLM"""
    
    confidence = risk_decision['risk_adjusted_confidence']
    position_size = risk_decision['position_size']
    
    guidance = f"""
MATHEMATICAL MODEL GUIDANCE:
- Recommended Action: {risk_decision['risk_adjusted_signal']}
- Confidence Level: {confidence:.1%}
- Position Size: {position_size:.1%} of portfolio
- Execution: {risk_decision['execution_approach']}

IMPORTANT: This analysis prevents extreme decisions like "SELL ALL" and provides 
graduated risk management. The LLM should consider these mathematical inputs 
when generating the final trading plan, ensuring balanced and risk-aware decisions.
"""
    
    return guidance
