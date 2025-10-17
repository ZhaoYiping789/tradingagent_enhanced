# TradingAgents Enhanced Edition

**AI-Powered Institutional-Grade Trading Analysis System**

基于 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents.git) 的多智能体协作投资分析系统，支持单股分析和投资组合优化。

---

## 🌟 选择您的版本 | Choose Your Version

本项目提供**三个专业版本**，满足不同使用场景。请根据您的需求选择合适的分支：

### 📊 **分支总览**

| 分支名称 | 适用场景 | 主要特性 | LLM支持 | 推荐用户 |
|---------|---------|---------|---------|---------|
| **[main](https://github.com/ZhaoYiping789/tradingagent_enhanced)** | 标准命令行分析 | OpenAI GPT-4, 完整分析报告 | OpenAI GPT-4 | 命令行用户、开发者 |
| **[watsonx-integration](https://github.com/ZhaoYiping789/tradingagent_enhanced/tree/watsonx-integration)** | IBM WatsonX 集成 | 支持 IBM WatsonX.ai LLM | WatsonX + OpenAI | 企业用户、WatsonX用户 |
| **[UI-version](https://github.com/ZhaoYiping789/tradingagent_enhanced/tree/UI-version)** | 网页交互式分析 | Web UI, 实时对话分析 | WatsonX + OpenAI | 所有用户、非技术用户 |

---

## 🚀 快速开始 | Quick Start

### 1️⃣ Main 分支 - 标准命令行版本

**适合**: 熟悉命令行的用户，需要标准化分析报告

#### 安装步骤

```bash
# 克隆仓库 - Main 分支
git clone https://github.com/ZhaoYiping789/tradingagent_enhanced.git
cd tradingagent_enhanced

# 安装依赖
uv sync

# 设置 OpenAI API Key
export OPENAI_API_KEY="your-openai-api-key"
```

#### 运行分析

**单股分析**:
```bash
# 编辑 main_enterprise.py 设置股票代码
# company_of_interest = "NVDA"
# portfolio_mode = False

uv run main_enterprise.py
```

**投资组合分析**:
```bash
# 编辑 main_enterprise.py 设置投资组合
# portfolio_mode = True
# portfolio_tickers = ["NVDA", "AAPL", "MSFT"]

uv run main_enterprise.py
```

**输出位置**:
- 单股报告: `results/{TICKER}/{DATE}/`
  - Markdown 报告: `{TICKER}_comprehensive_analysis_{DATE}.md`
  - Word 文档: `{TICKER}_comprehensive_analysis_{DATE}.docx`
  - 图表: `{TICKER}_comprehensive_analysis_{DATE}.png`
  - CSV 数据: `csv_data/` 目录（6个文件）

- 投资组合报告: `portfolio_results/{DATE}/portfolio_analysis_{DATE}.md`

---

### 2️⃣ WatsonX 分支 - IBM WatsonX.ai 集成版本

**适合**: IBM WatsonX 用户，企业级 AI 分析需求

#### 安装步骤

```bash
# 克隆 WatsonX 分支
git clone -b watsonx-integration https://github.com/ZhaoYiping789/tradingagent_enhanced.git
cd tradingagent_enhanced

# 安装依赖
uv sync

# 设置 WatsonX 环境变量
export WATSONX_URL="https://us-south.ml.cloud.ibm.com"
export WATSONX_APIKEY="your-watsonx-api-key"
export WATSONX_PROJECT_ID="your-project-id"
```

#### 运行分析

**WatsonX 单股分析**:
```bash
uv run main_enterprise_watsonx.py
```

**测试 WatsonX 连接**:
```bash
# Windows
RUN_WATSONX_TEST.bat

# Linux/Mac
python test_watsonx_connection.py
```

#### 推荐模型配置

在 `main_enterprise_watsonx.py` 中:

```python
config = {
    "llm_provider": "watsonx",
    "watsonx_url": "https://us-south.ml.cloud.ibm.com",
    "watsonx_project_id": "your-project-id",

    # 推荐模型组合
    "deep_think_llm": "mistralai/mixtral-8x7b-instruct-v01",  # 复杂分析
    "quick_think_llm": "ibm/granite-3-8b-instruct",           # 快速操作

    # 其他可选模型:
    # "meta-llama/llama-3-3-70b-instruct"  # Granite 3.0 - 高质量
    # "ibm/granite-3-8b-instruct"          # 轻量级
}
```

**详细文档**:
- `README_WATSONX.md` - WatsonX 完整集成指南
- `QUICK_START_WATSONX.md` - WatsonX 快速开始
- `WATSONX_SETUP.md` - WatsonX 环境配置

---

### 3️⃣ UI-version 分支 - 交互式网页版本 ⭐ **推荐新用户**

**适合**: 所有用户，特别是非技术背景的投资者

#### 安装步骤

```bash
# 克隆 UI 版本分支
git clone -b UI-version https://github.com/ZhaoYiping789/tradingagent_enhanced.git
cd tradingagent_enhanced

# 安装依赖（包含 Flask, Gradio 等 Web 框架）
uv sync

# 设置环境变量（支持 OpenAI 或 WatsonX）
export OPENAI_API_KEY="your-openai-api-key"
# 或使用 WatsonX:
export WATSONX_APIKEY="your-watsonx-api-key"
export WATSONX_PROJECT_ID="your-project-id"
```

#### 启动 Web UI

**方式 1: Flask 聊天界面**（推荐）
```bash
# Windows
LAUNCH_UI.bat

# Linux/Mac
python flask_chat_app.py
```

然后在浏览器打开: `http://localhost:5000`

**方式 2: Gradio 界面**
```bash
# Windows
RUN_INTERACTIVE_UI.bat

# Linux/Mac
python -m tradingagents.interactive.gradio_ui
```

**方式 3: 简化聊天界面**
```bash
# Windows
START_UI_SIMPLE.bat

# Linux/Mac
python -m tradingagents.interactive.simple_chat_ui
```

#### Web UI 功能特性

✨ **交互式对话分析**:
- 💬 通过自然语言对话进行股票分析
- 📊 实时生成分析报告和图表
- 🔄 迭代优化：根据反馈调整分析结果
- 📈 可视化图表自动生成

✨ **用户友好界面**:
- 🖥️ 现代化 Web 界面，无需命令行
- 📱 支持移动设备访问
- 🎨 可视化分析看板
- 💾 历史记录保存

✨ **智能交互**:
- 🤖 AI 助手自动解析用户意图
- 🎯 自动选择合适的分析师团队
- 📝 自然语言输入：如 "分析 NVDA，重点关注技术指标"
- 🔧 实时参数调整

#### UI 版本示例对话

```
用户: "帮我分析一下 NVDA 的投资机会，我比较关注短期技术指标"

系统:
✓ 已理解您的需求
✓ 启动分析师: 市场分析师, 基本面分析师
✓ 分析时间范围: 近期
✓ 侧重点: 技术指标

[开始生成分析报告...]
[显示可视化图表...]

用户: "能不能加上新闻情绪分析？"

系统:
✓ 已添加新闻分析师
✓ 重新运行分析...
[更新报告...]
```

**详细文档**:
- `README_INTERACTIVE.md` - 交互模式完整指南
- `QUICK_START_INTERACTIVE.md` - UI 版本快速开始
- `INTERACTIVE_USAGE.md` - 详细使用说明

---

## 📋 版本选择指南

### 🤔 我应该选择哪个版本？

**如果您是...**

👨‍💻 **开发者/技术用户** → 选择 **Main 分支**
- 熟悉命令行操作
- 需要完整的 OpenAI GPT-4 支持
- 想要标准化的分析流程

🏢 **企业用户/WatsonX 客户** → 选择 **WatsonX 分支**
- 已有 IBM WatsonX.ai 账户
- 需要企业级 AI 模型
- 要求私有化部署或数据合规

🌟 **投资者/分析师/新用户** → 选择 **UI-version 分支** ⭐
- 不熟悉命令行操作
- 希望通过聊天界面交互
- 需要可视化的分析过程
- 想要快速上手

### 💡 功能对比

| 功能 | Main 分支 | WatsonX 分支 | UI-version 分支 |
|-----|---------|-------------|----------------|
| 单股分析 | ✅ | ✅ | ✅ |
| 投资组合分析 | ✅ | ✅ | ✅ |
| OpenAI GPT-4 | ✅ | ✅ | ✅ |
| IBM WatsonX.ai | ❌ | ✅ | ✅ |
| 命令行界面 | ✅ | ✅ | ✅ |
| Web 界面 | ❌ | ❌ | ✅ |
| 交互式对话 | ❌ | ❌ | ✅ |
| 实时反馈优化 | ❌ | ❌ | ✅ |
| 可视化看板 | ❌ | ❌ | ✅ |

---

## 🎬 演示视频

[![TradingAgents Demo](https://img.youtube.com/vi/3vmgWtg3G60/0.jpg)](https://youtu.be/3vmgWtg3G60?feature=shared)

观看完整演示，了解多智能体分析工作流程和投资组合优化功能。

---

## 🏛️ 系统介绍

TradingAgents Enhanced Edition 是一个**AI 投资助手系统**，通过多智能体协作提供专业级的市场分析和投资建议。

### 🎯 核心能力

- **📊 机构级分析**: 模拟投资委员会，多角度评估投资机会
- **🤖 AI 智能体团队**: 市场分析师、基本面分析师、新闻分析师等专业团队
- **📈 量化优化**: Kelly 准则、VaR/CVaR 风险管理、6种优化策略
- **📑 专业报告**: 自动生成 Word/Markdown 格式的专业分析报告

### ⚠️ 重要声明

本系统生成的报告、图表和建议旨在**辅助和支持您的投资决策**，而非替代您的判断。所有分析应视为教育和决策支持材料。请在做出投资决定前进行独立研究并考虑个人财务状况。

---

## 🏗️ 系统架构

### 整体架构图
![Overall Architecture](docs/overall%20architecture.png)

### 用户工作流程
![User Workflow](docs/user%20workflow.png)

<details>
<summary><b>📊 点击查看详细分析师架构</b></summary>

### 各分析师架构

#### 市场分析师架构
![Market Analyst Architecture](docs/market%20analyst%20architecture.png)

#### 基本面分析师架构
![Fundamental Analyst Architecture](docs/fundamental%20analyst%20architecture.png)

#### 新闻分析师架构
![News Analyst Architecture](docs/news%20analyst%20architecture.png)

#### 量化分析师架构
![Quantitative Analyst Architecture](docs/quantatative%20analyst%20architecture.png)

#### 投资组合分析师架构
![Portfolio Analyst Architecture](docs/portofolio%20anaylst%20architecture.png)

### 投资组合系统架构

#### 多场景优化架构
![Multi-Scenario Optimization Architecture](docs/multi-scenario%20optimization%20architecture.png)

#### 多股票组合生成系统
![Multi-Stock Portfolio Generation System](docs/multi-stock%20portofolio%20generation%20system.png)

</details>

---

## 📊 分析结果示例

**想看看系统能做什么？** 查看我们的最新分析示例：

### 单股分析示例 (2025-10-09)
- **AAPL 分析**: [`results/AAPL/2025-10-09/`](results/AAPL/2025-10-09/) - 完整分析报告、图表、CSV数据
- **NVDA 分析**: [`results/NVDA/2025-10-09/`](results/NVDA/2025-10-09/) - 综合技术与基本面分析

### 投资组合分析示例
- **多股票组合**: [`portfolio_results/2025-10-09/portfolio_analysis_2025-10-09.md`](portfolio_results/2025-10-09/portfolio_analysis_2025-10-09.md) - 高级投资组合优化与配置建议

---

## ⚙️ 高级配置

<details>
<summary><b>🔧 点击查看详细配置选项</b></summary>

### 分析模式配置 (main_enterprise.py)

```python
# 分析范围
portfolio_mode = False  # True: 多股票组合 | False: 单股
portfolio_tickers = ["NVDA", "AAPL", "MSFT", "GOOGL"]  # 组合股票列表
company_of_interest = "NVDA"  # 单股分析目标
current_date = "2025-10-09"  # 分析日期
```

### AI 分析师团队选择

```python
selected_analysts = [
    "market",                    # 📈 技术分析: RSI, MACD, 布林带
    "fundamentals",              # 💰 财务分析: P/E, 营收, 现金流
    "news",                      # 📰 新闻情绪: 标题分析, 影响评估
    "social",                    # 🐦 社交媒体: Reddit, Twitter 情绪
    "comprehensive_quantitative", # 🔬 高级 ML: GARCH 模型, 统计预测
    "portfolio",                 # 📊 组合影响: 相关性分析, 行业分散
    "enterprise_strategy"        # 🏛️ 战略分析: 长期定位, 机构视角
]

# 快速分析配置（更快，资源占用少）
selected_analysts = ["market", "fundamentals"]
```

### LLM 模型配置

```python
config = {
    # OpenAI 配置
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o",        # 复杂分析
    "quick_think_llm": "gpt-4o-mini",  # 快速操作

    # WatsonX 配置
    # "llm_provider": "watsonx",
    # "deep_think_llm": "mistralai/mixtral-8x7b-instruct-v01",

    # 分析深度
    "enterprise_mode": True,              # 企业级功能
    "max_debate_rounds": 2,               # 多头/空头辩论轮次
    "lightweight_quantitative": False,    # 完整优化算法
}
```

### 预配置场景

**场景 1: 快速个人投资分析**
```python
selected_analysts = ["market", "fundamentals"]
config = {
    "deep_think_llm": "gpt-4o-mini",
    "max_debate_rounds": 1,
    "lightweight_quantitative": True
}
```

**场景 2: 专业顾问报告**
```python
selected_analysts = ["market", "fundamentals", "news", "social", "comprehensive_quantitative"]
config = {
    "deep_think_llm": "gpt-4o",
    "enterprise_mode": True,
    "max_debate_rounds": 2
}
```

**场景 3: 机构投资委员会**
```python
selected_analysts = [
    "market", "fundamentals", "news", "social",
    "comprehensive_quantitative", "portfolio", "enterprise_strategy"
]
config = {
    "deep_think_llm": "gpt-4o",
    "enterprise_mode": True,
    "max_debate_rounds": 3,
    "max_risk_discuss_rounds": 3
}
```

</details>

---

## 📁 项目结构

<details>
<summary><b>📂 点击查看完整目录结构</b></summary>

```
TradingAgents-main/
├── main_enterprise.py              # 主入口点（OpenAI）
├── main_enterprise_watsonx.py      # WatsonX 版本入口（WatsonX分支）
├── flask_chat_app.py               # Flask Web UI（UI-version分支）
├── main_interactive_watsonx.py     # 交互式 WatsonX（UI-version分支）
├── single_stock_analysis.py        # 轻量级单股分析
├── run_portfolio_analysis.py       # 独立组合分析
│
├── tradingagents/                  # 核心系统包
│   ├── agents/                    # AI 智能体
│   │   ├── analysts/              # 分析师团队
│   │   │   ├── market_analyst.py
│   │   │   ├── fundamentals_analyst.py
│   │   │   ├── news_analyst.py
│   │   │   ├── comprehensive_quantitative_analyst.py
│   │   │   ├── portfolio_analyst.py
│   │   │   └── visualizer_analyst.py  # UI版本新增
│   │   ├── traders/               # 交易决策
│   │   ├── researchers/           # 研究团队
│   │   ├── managers/              # 管理协调
│   │   └── generators/            # 报告生成
│   │
│   ├── interactive/               # 交互式系统（UI-version分支）
│   │   ├── gradio_ui.py           # Gradio 界面
│   │   ├── simple_chat_ui.py      # 简化聊天界面
│   │   ├── interactive_workflow.py # 交互工作流
│   │   └── user_preference_parser.py
│   │
│   ├── graph/                     # LangGraph 工作流
│   │   ├── trading_graph.py
│   │   ├── setup.py
│   │   └── conditional_logic.py
│   │
│   ├── portfolio/                 # 投资组合系统
│   │   ├── stock_data_aggregator.py
│   │   ├── multi_scenario_portfolio_optimizer.py
│   │   └── portfolio_report_generator.py
│   │
│   └── dataflows/                 # 数据流
│       ├── yfin_utils.py          # Yahoo Finance
│       ├── finnhub_utils.py       # Finnhub API
│       └── googlenews_utils.py    # 新闻抓取
│
├── results/                       # 分析结果
│   └── {TICKER}/{DATE}/
│       ├── {TICKER}_comprehensive_analysis_{DATE}.md
│       ├── {TICKER}_comprehensive_analysis_{DATE}.docx
│       ├── {TICKER}_comprehensive_analysis_{DATE}.png
│       └── csv_data/              # 6 个 CSV 文件
│
├── portfolio_results/             # 组合分析结果
│   └── {DATE}/portfolio_analysis_{DATE}.md
│
├── static/                        # Web UI 静态文件（UI-version）
│   └── chat.html
│
└── docs/                          # 架构图和文档
    ├── overall architecture.png
    ├── user workflow.png
    └── ...
```

</details>

---

## 🔧 故障排除

### 常见问题

<details>
<summary><b>1. API Key 错误</b></summary>

```bash
# 确保设置了正确的 API Key
export OPENAI_API_KEY="your-key-here"

# 或 WatsonX
export WATSONX_APIKEY="your-watsonx-key"
export WATSONX_PROJECT_ID="your-project-id"

# Windows 用户
set OPENAI_API_KEY=your-key-here
```
</details>

<details>
<summary><b>2. 依赖安装问题</b></summary>

```bash
# 重新安装依赖
uv sync --reinstall

# 或使用 pip
pip install -r requirements.txt --force-reinstall
```
</details>

<details>
<summary><b>3. 投资组合分析失败</b></summary>

```bash
# 确保单股分析已完成
# 检查 CSV 文件是否存在
ls results/{TICKER}/{DATE}/csv_data/

# 至少需要 2 只股票的完整分析结果
```
</details>

<details>
<summary><b>4. Web UI 无法启动（UI-version分支）</b></summary>

```bash
# 检查端口是否被占用
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# 更改端口
# 编辑 flask_chat_app.py，修改 port=5000 为其他端口
```
</details>

<details>
<summary><b>5. 内存不足</b></summary>

```python
# 减少分析师数量
selected_analysts = ["market", "fundamentals"]

# 使用轻量级配置
config = {
    "lightweight_quantitative": True,
    "max_debate_rounds": 1
}
```
</details>

### 日志文件位置

- 主日志: `enterprise_output.log`
- WatsonX 日志: `enterprise_watsonx_output.log`
- 智能体日志: `eval_results/{TICKER}/TradingAgentsStrategy_logs/`

---

## 🛣️ 开发路线图

### ✅ 已完成
- ✅ 单股分析系统
- ✅ 投资组合优化
- ✅ IBM WatsonX.ai 集成（watsonx-integration 分支）
- ✅ 交互式 Web UI（UI-version 分支）
- ✅ 多 LLM 支持（OpenAI + WatsonX）

### 🚧 进行中
- 🚧 增强投资组合可视化
- 🚧 移动端响应式设计
- 🚧 实时数据流集成

### 📋 计划中
- 📋 回测引擎
- 📋 RESTful API
- 📋 Claude AI 集成
- 📋 本地模型支持（Llama, Mistral）

---

## 🤝 贡献

欢迎为 TradingAgents Enhanced Edition 做出贡献！

### 优先领域
- **交互式界面改进**: UI/UX 增强
- **多语言支持**: 国际化
- **测试覆盖**: 单元测试和集成测试
- **文档完善**: 用户指南和 API 文档

### 如何贡献
1. Fork 本仓库
2. 选择合适的分支开始工作
3. 创建功能分支 (`git checkout -b feature/amazing-feature`)
4. 提交更改 (`git commit -m 'Add amazing feature'`)
5. 推送到分支 (`git push origin feature/amazing-feature`)
6. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- 基于 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents.git) 原始架构
- IBM WatsonX.ai 团队提供 LLM 集成支持
- OpenAI 提供 GPT-4 API 访问
- 开源金融分析社区

---

## 📞 支持

- 💬 **Issues**: [GitHub Issues](https://github.com/ZhaoYiping789/tradingagent_enhanced/issues)
- 📧 **Email**: 项目相关问题请通过 GitHub Issues 提交
- 📚 **文档**: 查看各分支的 README 和快速开始指南

---

**TradingAgents Enhanced Edition** - 下一代 AI 驱动的交易分析系统，具备机构级量化方法和多 LLM 支持。

*⭐ 三个专业版本可选 | 🚀 持续开发中 | 🤝 欢迎社区贡献*
