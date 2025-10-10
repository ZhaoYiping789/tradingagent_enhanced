#!/usr/bin/env python3
"""
单只股票完整量化分析
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_single_stock(ticker="AAPL"):
    """分析单只股票并生成完整报告"""
    
    print(f"🚀 启动轻量化量化分析器 - 分析 {ticker}")
    print("=" * 60)
    
    try:
        # 模拟配置
        class MockLLM:
            def invoke(self, messages):
                return type('obj', (object,), {'content': 'Mock LLM response'})
        
        class MockToolkit:
            def __init__(self):
                self.config = {
                    "online_tools": False,
                    "lightweight_quantitative": True  # 启用轻量化模式
                }
        
        # 导入量化分析器
        from tradingagents.agents.analysts.quantitative_analyst import create_quantitative_analyst
        
        llm = MockLLM()
        toolkit = MockToolkit()
        
        # 创建分析器
        print("🔧 初始化量化分析器...")
        quantitative_analyst = create_quantitative_analyst(llm, toolkit)
        
        # 分析状态
        test_state = {
            "trade_date": "2025-09-16",
            "company_of_interest": ticker
        }
        
        print(f"\n📊 开始分析 {ticker}...")
        print("-" * 40)
        
        start_time = time.time()
        
        # 运行分析
        result = quantitative_analyst(test_state)
        
        total_time = time.time() - start_time
        
        if result and "quantitative_report" in result:
            report = result["quantitative_report"]
            
            print(f"\n✅ 分析完成! 总耗时: {total_time:.2f} 秒")
            print("=" * 60)
            
            # 显示完整报告
            print("\n📋 完整量化分析报告:")
            print("=" * 60)
            print(report)
            print("=" * 60)
            
            # 提取关键信息摘要
            print(f"\n📈 关键信息摘要:")
            print("-" * 40)
            
            lines = report.split('\n')
            key_info = {}
            
            for line in lines:
                if "当前价格" in line and "$" in line:
                    key_info["当前价格"] = line.strip()
                elif "最终交易信号" in line and "**" in line:
                    key_info["交易信号"] = line.strip()
                elif "预期收益" in line and "%" in line:
                    key_info["预期收益"] = line.strip()
                elif "处理时间" in line and "秒" in line:
                    key_info["处理时间"] = line.strip()
                elif "复合因子得分" in line:
                    key_info["因子得分"] = line.strip()
                elif "预测模型" in line and ":" in line:
                    key_info["预测模型"] = line.strip()
            
            for key, value in key_info.items():
                print(f"🔸 {key}: {value.replace('- **', '').replace('**:', ':').replace('**', '')}")
            
            # 检查图表文件
            if "technical_analysis" in report:
                for line in lines:
                    if "technical_analysis" in line and ".png" in line:
                        chart_path = line.split("`")[1] if "`" in line else "未找到路径"
                        print(f"🔸 技术分析图表: {chart_path}")
                        
                        # 检查文件是否存在
                        if os.path.exists(chart_path):
                            file_size = os.path.getsize(chart_path) / 1024  # KB
                            print(f"  📁 文件大小: {file_size:.1f} KB")
                        break
            
            return {
                'success': True,
                'ticker': ticker,
                'processing_time': total_time,
                'report': report,
                'key_info': key_info
            }
            
        else:
            print(f"❌ {ticker} 分析失败 - 无有效结果")
            return {'success': False, 'ticker': ticker, 'error': 'No valid result'}
            
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'ticker': ticker, 'error': str(e)}

def main():
    """主函数"""
    print("🧪 单只股票量化分析程序")
    print("=" * 60)
    
    # 可以修改这里来分析不同的股票
    target_stock = "AAPL"  # 可改为 "GOOGL", "TSLA", "MSFT" 等
    
    result = analyze_single_stock(target_stock)
    
    if result['success']:
        print(f"\n🎉 {target_stock} 分析成功完成!")
        print(f"⏱️  总处理时间: {result['processing_time']:.2f} 秒")
        print("\n轻量化量化分析器特点:")
        print("  ⚡ 快速: CPU优化，无重量级模型训练")
        print("  💡 智能: Prophet轻量预测 + 6因子分析")
        print("  📊 完整: 技术指标 + 图表 + 详细报告")
        print("  🔋 高效: 低内存占用，适合实时分析")
        
    else:
        print(f"❌ {target_stock} 分析失败")
        if 'error' in result:
            print(f"错误信息: {result['error']}")

if __name__ == "__main__":
    main()
