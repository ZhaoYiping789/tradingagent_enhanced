#!/usr/bin/env python3
"""
TradingAgents Enterprise Edition
Enhanced trading analysis system with sophisticated trading plans and institutional-grade reports
Supports both single-stock and multi-stock portfolio analysis
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.analysts.enterprise_strategy_analyst import create_enterprise_strategy_analyst
from tradingagents.agents.generators.enhanced_quantitative_document_generator import create_enhanced_quantitative_document_generator
from tradingagents.agents.trader.enterprise_trader import create_enterprise_trader
from tradingagents.portfolio.stock_data_aggregator import StockDataAggregator
from tradingagents.portfolio.multi_scenario_portfolio_optimizer import MultiScenarioPortfolioOptimizer
from tradingagents.portfolio.portfolio_report_generator import PortfolioReportGenerator
from datetime import date
import os
import sys
import time
import pandas as pd
import yfinance as yf

def main():
    """Enterprise-level main function with sophisticated trading strategy generation."""
    
    # 设置控制台编码
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    
    # 创建日志文件用于前端监控
    log_file = "enterprise_output.log"
    
    def log_print(text):
        """同时输出到控制台和日志文件"""
        print(text)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(text + '\n')
    
    # 清空之前的日志
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("")
    
    log_print("🏛️ TRADINGAGENTS ENTERPRISE EDITION")
    log_print("=" * 80)
    log_print("🎯 Institutional-Grade Analysis with Advanced Trading Strategies")
    log_print("=" * 80)
    
    # Set API key
    os.environ["OPENAI_API_KEY"] = "set your key here"
    
    # Create enhanced enterprise config
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "openai"
    config["backend_url"] = "https://api.laozhang.ai/v1"
    config["deep_think_llm"] = "gpt-4o"  # Use more powerful model for enterprise
    config["quick_think_llm"] = "gpt-4o-mini"
    config["max_debate_rounds"] = 2  # More thorough debate
    config["max_risk_discuss_rounds"] = 2  # Enhanced risk analysis
    config["online_tools"] = True
    config["lightweight_quantitative"] = False  # Enable full optimization algorithms
    config["enterprise_mode"] = True  # Enable enterprise features
    config["use_comprehensive_quantitative"] = True  # Enable comprehensive quantitative analysis
    config["include_optimization_results"] = True  # Include mathematical optimization

    # Enhanced analyst selection for enterprise analysis with full sentiment
    selected_analysts = [
        "market",          # Advanced technical analysis
        "social",          # Sentiment analysis with social signals
        "news",            # Comprehensive news analysis
        "fundamentals",    # Deep fundamental analysis
        "comprehensive_quantitative",  # ENHANCED: Comprehensive quantitative with optimization
        "portfolio",       # Portfolio impact analysis
        "enterprise_strategy"  # NEW: Enterprise strategy analyst
    ]
    
    log_print(f"📊 Enterprise Analysts Selected: {', '.join(selected_analysts)}")
    log_print("")
    
    # Initialize the enterprise trading agents graph
    log_print("🔧 Initializing Enterprise TradingAgents System...")
    ta = TradingAgentsGraph(
        selected_analysts=selected_analysts,
        debug=True, 
        config=config
    )
    
    # Enterprise components are integrated through selected_analysts
    log_print("⚡ Enterprise Components Integrated Successfully...")
    
    # Get current date and tickers for analysis
    current_date = "2025-10-10"  
    
    # PORTFOLIO MODE: Analyze multiple stocks
    portfolio_mode = True  
    portfolio_tickers = ["NVDA", "AAPL", "MSFT", "GOOGL", "TSLA"]  
    
    log_print(f"📅 ANALYSIS DATE: {current_date}")
    
    if portfolio_mode:
        log_print(f"📊 PORTFOLIO MODE: Analyzing {len(portfolio_tickers)} stocks")
        log_print(f"🎯 TARGET SECURITIES: {', '.join(portfolio_tickers)}")
    else:
        ticker = "NVDA"
        log_print(f"🎯 TARGET SECURITY: {ticker}")
    
    log_print("=" * 80)
    
    # Start comprehensive enterprise analysis
    log_print("🚀 INITIATING ENTERPRISE-LEVEL ANALYSIS...")
    log_print("")
    log_print("📋 ANALYSIS COMPONENTS:")
    log_print("   🔍 Advanced Technical Analysis")
    log_print("   📊 Multi-Source Sentiment Analysis") 
    log_print("   📰 Comprehensive News Intelligence")
    log_print("   💰 Deep Fundamental Analysis")
    log_print("   🤖 Machine Learning Forecasting")
    log_print("   🏛️ Investment Committee Debate")
    log_print("   ⚖️ Advanced Risk Assessment")
    log_print("   🎯 Enterprise Strategy Generation")
    log_print("   💼 Institutional Trading Plan")
    log_print("   📊 Professional Report Generation")
    log_print("")
    
    try:
        start_time = time.time()
        
        if portfolio_mode:
            # PORTFOLIO MODE: Analyze each stock then generate portfolio
            log_print("⏳ Running Multi-Stock Analysis Pipeline...")
            log_print("")
            
            stock_results = {}
            for i, ticker in enumerate(portfolio_tickers, 1):
                log_print(f"📊 [{i}/{len(portfolio_tickers)}] Analyzing {ticker}...")
                log_print("-" * 80)
                
                try:
                    final_state, decision = ta.propagate(ticker, current_date)
                    stock_results[ticker] = {
                        'state': final_state,
                        'decision': decision
                    }
                    log_print(f"✅ {ticker} Analysis Complete - Decision: {decision}")
                    log_print("")
                except Exception as e:
                    log_print(f"❌ {ticker} Analysis Failed: {e}")
                    log_print("")
            
            analysis_time = time.time() - start_time
            
            # Generate Portfolio Report
            if len(stock_results) >= 2:
                log_print("")
                log_print("=" * 80)
                log_print("📊 GENERATING PORTFOLIO ANALYSIS")
                log_print("=" * 80)
                
                try:
                    # Aggregate stock data
                    aggregator = StockDataAggregator(current_date)
                    aggregated_result = aggregator.aggregate_multiple_stocks(list(stock_results.keys()))
                    
                    if aggregated_result['num_stocks'] >= 2:
                        log_print(f"✅ Loaded {aggregated_result['num_stocks']} stock analyses")
                        
                        # Get returns data
                        log_print("📈 Fetching price data for optimization...")
                        returns_data = {}
                        for ticker in stock_results.keys():
                            stock_data = yf.download(ticker, period='6mo', progress=False)
                            if not stock_data.empty:
                                # Handle MultiIndex columns from yfinance
                                if isinstance(stock_data.columns, pd.MultiIndex):
                                    close_prices = stock_data[('Close', ticker)]
                                else:
                                    close_prices = stock_data['Close']
                                
                                returns = close_prices.pct_change().dropna()
                                returns_data[ticker] = returns
                        
                        returns_df = pd.DataFrame(returns_data).dropna()
                        log_print(f"✅ Returns matrix: {returns_df.shape}")
                        
                        # Run portfolio optimization
                        log_print("🎯 Running multi-scenario portfolio optimization...")
                        stock_metrics = {ticker: data['metrics'] for ticker, data in aggregated_result['stocks_data'].items()}
                        optimizer = MultiScenarioPortfolioOptimizer(returns_df, stock_metrics)
                        optimization_scenarios = optimizer.optimize_all_scenarios()
                        log_print(f"✅ Generated {len(optimization_scenarios)} portfolio scenarios")
                        
                        # Generate portfolio report
                        log_print("📄 Generating portfolio report...")
                        report_gen = PortfolioReportGenerator(aggregated_result, optimization_scenarios, current_date)
                        portfolio_report_path = report_gen.generate_comprehensive_report()
                        log_print(f"✅ Portfolio report: {portfolio_report_path}")
                    else:
                        log_print("⚠️  Insufficient data for portfolio optimization")
                        
                except Exception as e:
                    log_print(f"❌ Portfolio generation failed: {e}")
                    import traceback
                    traceback.print_exc()
        else:
            # SINGLE STOCK MODE
            log_print("⏳ Running Multi-Agent Analysis Pipeline...")
            final_state, decision = ta.propagate(ticker, current_date)
            analysis_time = time.time() - start_time
        
        log_print("")
        log_print("=" * 80)
        log_print("✅ ENTERPRISE ANALYSIS COMPLETE!")
        log_print(f"⏱️  Total Analysis Time: {analysis_time:.1f} seconds")
        log_print("=" * 80)
        
        # Display comprehensive results
        log_print("")
        log_print("📊 EXECUTIVE SUMMARY:")
        log_print(f"   🎯 Final Decision: {decision}")
        log_print(f"   💪 Confidence Level: {final_state.get('decision_confidence', 'Medium')}")
        
        if final_state.get("enterprise_strategy"):
            log_print(f"   📈 Strategy Generated: Advanced Trading Plan")
            
        if final_state.get("enterprise_document"):
            log_print(f"   📄 Enterprise Report: Institutional-Grade Document")
            
        # Show individual component results
        log_print("")
        log_print("🔍 ANALYSIS COMPONENT STATUS:")
        
        components = [
            ("market_report", "Technical Analysis"),
            ("sentiment_report", "Sentiment Analysis"), 
            ("news_report", "News Analysis"),
            ("fundamentals_report", "Fundamental Analysis"),
            ("quantitative_report", "Quantitative Forecasting"),
            ("enterprise_strategy", "Enterprise Strategy"),
            ("enterprise_trader_decision", "Institutional Trading Plan"),
            ("enterprise_document", "Professional Report")
        ]
        
        for key, name in components:
            status = "✅ Complete" if final_state.get(key) else "❌ Missing"
            log_print(f"   {status}: {name}")
        
        # Research and risk analysis status
        log_print("")
        log_print("🏛️ INSTITUTIONAL DECISION PROCESS:")
        
        investment_debate = final_state.get("investment_debate_state", {})
        if investment_debate.get("judge_decision"):
            log_print("   ✅ Investment Committee Debate: Complete")
            
        risk_debate = final_state.get("risk_debate_state", {})
        if risk_debate.get("judge_decision"):
            log_print("   ✅ Risk Committee Assessment: Complete")
            
        if final_state.get("enterprise_trader_decision"):
            log_print("   ✅ Senior Portfolio Manager Decision: Complete")
        
        # Show file locations
        log_print("")
        log_print("📁 OUTPUT LOCATIONS:")
        
        results_dir = f"results/{ticker}/{current_date}"
        log_print(f"   📊 Standard Reports: {results_dir}/")
        
        if final_state.get("enterprise_document_path"):
            log_print(f"   🏛️ Enterprise Report: {final_state['enterprise_document_path']}")
        
        eval_dir = f"eval_results/{ticker}/TradingAgentsStrategy_logs"
        log_print(f"   📋 Detailed Logs: {eval_dir}/")
        
        # Show key trading parameters if available
        if final_state.get("position_size"):
            log_print("")
            log_print("💰 TRADING PARAMETERS:")
            pos_size = final_state["position_size"]
            if isinstance(pos_size, dict):
                if "dollar_amount" in pos_size:
                    log_print(f"   💵 Position Size: ${pos_size['dollar_amount']:,.0f}")
                if "portfolio_percent" in pos_size:
                    log_print(f"   📊 Portfolio Allocation: {pos_size['portfolio_percent']:.1f}%")
        
        if final_state.get("risk_parameters"):
            risk_params = final_state["risk_parameters"]
            if isinstance(risk_params, dict):
                if "stop_loss" in risk_params:
                    log_print(f"   🛡️ Stop Loss: ${risk_params['stop_loss']:.2f}")
                if "max_risk" in risk_params:
                    log_print(f"   ⚠️ Maximum Risk: ${risk_params['max_risk']:,.0f}")
        
        log_print("")
        log_print("=" * 80)
        log_print("🎉 ENTERPRISE TRADINGAGENTS ANALYSIS COMPLETE!")
        log_print(f"🎯 INSTITUTIONAL RECOMMENDATION: {decision}")
        log_print("🏛️ Ready for Investment Committee Review")
        log_print("=" * 80)
        
    except Exception as e:
        log_print("")
        log_print("❌ ERROR DURING ENTERPRISE ANALYSIS")
        log_print(f"Error Details: {str(e)}")
        log_print("Please check your configuration and try again.")
        log_print("")
        import traceback
        traceback.print_exc()
        return
    
    log_print("")
    log_print("📊 Enterprise analysis complete. Review generated reports for detailed insights.")

if __name__ == "__main__":
    main()
