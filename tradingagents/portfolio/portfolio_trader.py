"""
Portfolio Trader - LLM-based final allocation decision maker
Integrates optimization scenarios with fundamental, technical, and sentiment analysis
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json

class PortfolioTrader:
    """LLM-based portfolio trader that makes final allocation decisions"""
    
    def __init__(self, llm_model: str = "gpt-4o"):
        self.llm = ChatOpenAI(
            model=llm_model, 
            temperature=0.1,
            base_url="https://api.laozhang.ai/v1"  # Use same endpoint as main system
        )
        
    def make_final_allocation(self, aggregated_data: Dict, optimization_scenarios: Dict, market_context: str = "") -> Dict[str, Any]:
        """
        Make final portfolio allocation decision by integrating:
        - Individual stock analysis (fundamental, technical, sentiment)
        - Multiple optimization scenarios with different philosophies
        - Market context and macroeconomic factors
        """
        
        # Prepare comprehensive input for LLM
        individual_analysis = self._format_individual_analysis(aggregated_data)
        optimization_summary = self._format_optimization_scenarios(optimization_scenarios)
        
        system_prompt = """You are an institutional portfolio manager with 20+ years of experience. 
Your task is to create the FINAL PORTFOLIO ALLOCATION by synthesizing:

1. **Individual Stock Analysis**: Fundamental strength, technical signals, sentiment
2. **Quantitative Optimization Results**: Multiple algorithms with different risk philosophies  
3. **Market Context**: Current market conditions and macroeconomic environment

CRITICAL REQUIREMENTS:
- Provide EXACT allocation percentages (e.g., NVDA: 67.3%, AAPL: 32.7%)
- Explain WHY you chose this specific allocation vs. EACH optimization scenario
- MUST analyze EVERY aspect: Fundamental (revenue, margins, growth), Technical (price trends, momentum), Sentiment (market positioning)  
- For EACH stock, evaluate: Growth potential, Risk profile, Current valuation, Market momentum
- Balance risk management with return potential across ALL analysis dimensions
- Reference specific raw data numbers in your reasoning
- Provide detailed confidence level (1-10) and time horizon with rationale

OUTPUT FORMAT:
```json
{{
    "final_allocation": {{"STOCK1": 0.673, "STOCK2": 0.327}},
    "rationale": "Detailed explanation of allocation decisions...",
    "confidence_level": 8,
    "time_horizon": "6-12 months",
    "risk_assessment": "Moderate risk profile...",
    "scenario_preference": "Modified Maximum Sharpe with risk adjustments",
    "key_factors": ["Factor 1", "Factor 2", "Factor 3"]
}}
```"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", f"""Please analyze the following data and provide your FINAL PORTFOLIO ALLOCATION:

## INDIVIDUAL STOCK ANALYSIS
{individual_analysis}

## QUANTITATIVE OPTIMIZATION SCENARIOS  
{optimization_summary}

## MARKET CONTEXT
{market_context}

Based on this comprehensive analysis, provide your final allocation decision as an institutional portfolio manager.""")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({})
            
            # Parse the response
            content = response.content
            
            # Extract JSON if present
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                
                try:
                    result = json.loads(json_str)
                    result['full_response'] = content
                    return result
                except json.JSONDecodeError as e:
                    print(f"JSON parse error: {e}")
                    # Fall back to basic parsing
                    return {
                        'final_allocation': {},
                        'rationale': content,
                        'confidence_level': 7,
                        'full_response': content
                    }
            else:
                return {
                    'final_allocation': {},
                    'rationale': content,
                    'confidence_level': 7,
                    'full_response': content
                }
                
        except Exception as e:
            print(f"Portfolio Trader LLM error: {e}")
            return {
                'final_allocation': {},
                'rationale': f"Error in LLM analysis: {str(e)}",
                'confidence_level': 5,
                'full_response': ''
            }
    
    def _format_individual_analysis(self, aggregated_data: Dict) -> str:
        """Format comprehensive individual stock analysis for LLM"""
        
        analysis = "### COMPREHENSIVE INDIVIDUAL STOCK ANALYSIS\n\n"
        
        for ticker, data in aggregated_data['stocks_data'].items():
            metrics = data['metrics']
            risk_metrics = data['risk_metrics']
            fundamental_table = data.get('fundamental_table', {})
            technical_table = data.get('technical_table', {})
            
            analysis += f"""**{ticker} COMPREHENSIVE DATA:**

**FUNDAMENTAL ANALYSIS:**
- Revenue: {fundamental_table.get('Revenue', 'N/A')}
- Net Income: {fundamental_table.get('Net Income', 'N/A')}
- Profit Margin: {fundamental_table.get('Profit Margin', 'N/A')}
- ROE: {fundamental_table.get('ROE', 'N/A')}
- Debt-to-Equity: {fundamental_table.get('Debt-to-Equity', 'N/A')}

**TECHNICAL ANALYSIS:**
- Current Price: ${metrics['current_price']:.2f}
- RSI: {technical_table.get('RSI', metrics.get('rsi', 50))}
- MACD: {technical_table.get('MACD', 'N/A')}
- SMA 20: {technical_table.get('SMA_20', 'N/A')}
- SMA 50: {technical_table.get('SMA_50', 'N/A')}
- Volatility: {metrics['volatility']:.1f}%
- Technical Score: {metrics['technical_score']:.1f}/10

**RISK ANALYSIS:**
- Expected Return: {metrics['expected_return']:.1f}%
- Sharpe Ratio: {metrics['sharpe_ratio']:.3f}
- VaR (95%): {risk_metrics['var_95']:.1f}%
- Max Drawdown: {risk_metrics['max_drawdown']:.1f}%
- Annual Volatility: {risk_metrics.get('annual_volatility', metrics['volatility']):.1f}%

**SENTIMENT & DECISION:**
- Final Decision: {data['final_decision']}
- Sentiment Score: {metrics['sentiment_score']:.1f}/10
- Sentiment Analysis: {self._format_sentiment_data(data.get('sentiment_analysis', {}))}

"""
        
        return analysis
    
    def _format_optimization_scenarios(self, optimization_scenarios: Dict) -> str:
        """Format detailed optimization scenarios with decision rationale for LLM"""
        
        if not optimization_scenarios:
            return "No optimization scenarios available"
            
        analysis = "### QUANTITATIVE OPTIMIZATION SCENARIOS WITH DECISION RATIONALE\n\n"
        
        for scenario_name, scenario_data in optimization_scenarios.items():
            analysis += f"""**{scenario_name.upper().replace('_', ' ')} - {scenario_data.get('philosophy', 'N/A')}:**

**Mathematical Result:**
- Expected Portfolio Return: {scenario_data.get('expected_return', 0)*100:.3f}%
- Portfolio Volatility: {scenario_data.get('volatility', 0)*100:.3f}%
- Sharpe Ratio: {scenario_data.get('sharpe_ratio', 0):.4f}
- Risk-Return Efficiency: {"High" if scenario_data.get('sharpe_ratio', 0) > 3.0 else "Moderate" if scenario_data.get('sharpe_ratio', 0) > 2.5 else "Low"}

**Precise Allocation Weights:**"""
            
            if 'weights' in scenario_data:
                for ticker, weight in sorted(scenario_data['weights'].items(), key=lambda x: x[1], reverse=True):
                    concentration = "High" if weight > 0.7 else "Moderate" if weight > 0.5 else "Low"
                    analysis += f"\n- {ticker}: {weight*100:.3f}% (Concentration: {concentration})"
                
                # Decision Logic Analysis
                analysis += f"\n\n**Algorithm Decision Logic:**"
                weights_list = list(scenario_data['weights'].values())
                max_weight = max(weights_list)
                min_weight = min(weights_list)
                
                if max_weight > 0.65:
                    analysis += f"\n- Favors higher-return asset ({list(scenario_data['weights'].keys())[weights_list.index(max_weight)]})"
                elif abs(max_weight - min_weight) < 0.15:
                    analysis += f"\n- Balanced approach with similar risk-return profiles"
                else:
                    analysis += f"\n- Moderate tilt based on risk-return optimization"
                
                # Risk Assessment
                portfolio_vol = scenario_data.get('volatility', 0) * 100
                if portfolio_vol > 35:
                    analysis += f"\n- Higher risk tolerance (Portfolio Vol: {portfolio_vol:.1f}%)"
                elif portfolio_vol < 30:
                    analysis += f"\n- Conservative risk approach (Portfolio Vol: {portfolio_vol:.1f}%)"
                else:
                    analysis += f"\n- Moderate risk tolerance (Portfolio Vol: {portfolio_vol:.1f}%)"
                    
            else:
                analysis += "\nAllocation data not available"
            
            analysis += "\n" + "-"*50 + "\n\n"
        
        return analysis
    
    def _format_sentiment_data(self, sentiment_data: Dict) -> str:
        """Format sentiment data for LLM analysis"""
        if not sentiment_data:
            return "No sentiment analysis available"
        
        sentiment_score = sentiment_data.get('overall_sentiment', 5.0)
        sentiment_label = "BULLISH" if sentiment_score > 6.5 else "BEARISH" if sentiment_score < 3.5 else "NEUTRAL"
        
        bullish = sentiment_data.get('bullish_count', 0)
        bearish = sentiment_data.get('bearish_count', 0)
        neutral = sentiment_data.get('neutral_count', 0)
        strength = sentiment_data.get('sentiment_strength', 'Weak')
        impact = sentiment_data.get('average_impact', 0.0)
        
        return f"{sentiment_label} (Score: {sentiment_score:.1f}, Strength: {strength}, Bullish: {bullish}, Bearish: {bearish}, Impact: {impact:+.1f}%)"
