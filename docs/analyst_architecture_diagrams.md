# TradingAgents Analyst Architecture Diagrams

## 1. Market Analyst Architecture

```mermaid
graph TB
    subgraph "Market Analyst Node"
        A[market_analyst_node Function]
        B[State Input Processing]
        C[Tool Selection Logic]
        D[LLM Chain Creation]
        E[Tool Execution]
        F[Response Processing]
    end
    
    subgraph "Data Sources"
        G[YFinance API]
        H[StockStats Indicators]
    end
    
    subgraph "Technical Indicators"
        I[Moving Averages<br/>- 50 SMA<br/>- 200 SMA<br/>- 10 EMA]
        J[MACD Family<br/>- MACD<br/>- MACD Signal<br/>- MACD Histogram]
        K[Momentum<br/>- RSI]
        L[Volatility<br/>- Bollinger Bands<br/>- ATR]
        M[Volume<br/>- VWMA]
    end
    
    subgraph "Analysis Process"
        N[Indicator Selection<br/>Max 8 indicators]
        O[Complementary Analysis]
        P[Trend Identification]
        Q[Market Context Assessment]
    end
    
    subgraph "Output Generation"
        R[Detailed Market Report]
        S[Markdown Table Summary]
        T[English Language Report]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    
    C --> G
    C --> H
    
    G --> I
    G --> J
    G --> K
    G --> L
    G --> M
    
    E --> N
    N --> O
    O --> P
    P --> Q
    
    F --> R
    R --> S
    S --> T
```

## 2. Fundamentals Analyst Architecture

```mermaid
graph TB
    subgraph "Fundamentals Analyst Node"
        A[fundamentals_analyst_node Function]
        B[State Processing]
        C[Tool Configuration]
        D[LLM Chain Setup]
        E[Tool Execution]
        F[Response Processing]
    end
    
    subgraph "Data Sources"
        G[Yahoo Finance API]
        H[SimFin API Fallback]
    end
    
    subgraph "Financial Statements"
        I[Balance Sheet<br/>- Assets<br/>- Liabilities<br/>- Equity]
        J[Income Statement<br/>- Revenue<br/>- Expenses<br/>- Net Income]
        K[Cash Flow Statement<br/>- Operating<br/>- Investing<br/>- Financing]
    end
    
    subgraph "Company Analysis"
        L[Company Profile]
        M[Financial History]
        N[Insider Transactions]
        O[Insider Sentiment]
    end
    
    subgraph "Analysis Framework"
        P[Financial Health Assessment]
        Q[Growth Analysis]
        R[Profitability Metrics]
        S[Liquidity Analysis]
        T[Debt Analysis]
    end
    
    subgraph "Output Generation"
        U[Comprehensive Report]
        V[Financial Metrics Table]
        W[Investment Insights]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    
    C --> G
    C --> H
    
    G --> I
    G --> J
    G --> K
    
    E --> L
    E --> M
    E --> N
    E --> O
    
    F --> P
    P --> Q
    Q --> R
    R --> S
    S --> T
    
    T --> U
    U --> V
    V --> W
```

## 3. News Analyst Architecture

```mermaid
graph TB
    subgraph "News Analyst Node"
        A[news_analyst_node Function]
        B[State Processing]
        C[Tool Configuration]
        D[LLM Chain Setup]
        E[Tool Execution]
        F[Response Processing]
    end
    
    subgraph "Data Sources"
        G[News APIs]
        H[Web Scraping]
        I[Financial News Sites]
    end
    
    subgraph "News Processing"
        J[Article Collection]
        K[Content Filtering]
        L[Relevance Scoring]
        M[Sentiment Analysis]
    end
    
    subgraph "Analysis Components"
        N[Market Impact Assessment]
        O[Company-Specific News]
        P[Industry Trends]
        Q[Regulatory Changes]
        R[Earnings Announcements]
    end
    
    subgraph "Sentiment Analysis"
        S[Positive Sentiment]
        T[Negative Sentiment]
        U[Neutral Sentiment]
        V[Impact Scoring]
    end
    
    subgraph "Output Generation"
        W[News Summary Report]
        X[Sentiment Analysis]
        Y[Impact Assessment]
        Z[Markdown Table]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    
    C --> G
    C --> H
    C --> I
    
    E --> J
    J --> K
    K --> L
    L --> M
    
    F --> N
    N --> O
    O --> P
    P --> Q
    Q --> R
    
    M --> S
    M --> T
    M --> U
    M --> V
    
    F --> W
    W --> X
    X --> Y
    Y --> Z
```

## 4. Social Media Analyst Architecture

```mermaid
graph TB
    subgraph "Social Media Analyst Node"
        A[social_media_analyst_node Function]
        B[State Processing]
        C[Tool Configuration]
        D[LLM Chain Setup]
        E[Tool Execution]
        F[Response Processing]
    end
    
    subgraph "Data Sources"
        G[Social Media APIs]
        H[Twitter/X API]
        I[Reddit API]
        J[Financial Forums]
    end
    
    subgraph "Data Collection"
        K[Post Collection]
        L[Comment Analysis]
        M[Engagement Metrics]
        N[User Sentiment]
    end
    
    subgraph "Sentiment Processing"
        O[Text Preprocessing]
        P[Sentiment Classification]
        Q[Emotion Detection]
        R[Influence Scoring]
    end
    
    subgraph "Analysis Framework"
        S[Community Sentiment]
        T[Trending Topics]
        U[Influencer Opinions]
        V[Retail Investor Sentiment]
    end
    
    subgraph "Output Generation"
        W[Social Sentiment Report]
        X[Sentiment Metrics]
        Y[Community Insights]
        Z[Markdown Summary]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    
    C --> G
    C --> H
    C --> I
    C --> J
    
    E --> K
    K --> L
    L --> M
    M --> N
    
    F --> O
    O --> P
    P --> Q
    Q --> R
    
    R --> S
    S --> T
    T --> U
    U --> V
    
    F --> W
    W --> X
    X --> Y
    Y --> Z
```

## 5. Quantitative Analyst Architecture

```mermaid
graph TB
    subgraph "Quantitative Analyst Node"
        A[comprehensive_quantitative_analyst_node Function]
        B[State Processing]
        C[Tool Configuration]
        D[LLM Chain Setup]
        E[Tool Execution]
        F[Response Processing]
    end
    
    subgraph "Data Sources"
        G[YFinance Historical Data]
        H[Technical Indicators]
        I[Market Data]
    end
    
    subgraph "Technical Analysis"
        J[Moving Averages]
        K[Oscillators]
        L[Volume Indicators]
        M[Volatility Measures]
    end
    
    subgraph "Machine Learning"
        N[Time Series Models]
        O[Regression Analysis]
        P[Pattern Recognition]
        Q[Forecasting Models]
    end
    
    subgraph "Optimization Engine"
        R[Multi-Scenario Optimization]
        S[Risk-Return Analysis]
        T[Portfolio Allocation]
        U[Gamma Parameter Tuning]
    end
    
    subgraph "Output Generation"
        V[Quantitative Report]
        W[Optimization Scenarios]
        X[Risk Metrics]
        Y[Technical Analysis]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    
    C --> G
    C --> H
    C --> I
    
    E --> J
    E --> K
    E --> L
    E --> M
    
    F --> N
    N --> O
    O --> P
    P --> Q
    
    Q --> R
    R --> S
    S --> T
    T --> U
    
    F --> V
    V --> W
    W --> X
    X --> Y
```

## 6. Portfolio Analyst Architecture

```mermaid
graph TB
    subgraph "Portfolio Analyst Node"
        A[portfolio_analyst_node Function]
        B[State Processing]
        C[Tool Configuration]
        D[LLM Chain Setup]
        E[Tool Execution]
        F[Response Processing]
    end
    
    subgraph "Data Sources"
        G[Multiple Stock Data]
        H[Comparative Metrics]
        I[Market Benchmarks]
    end
    
    subgraph "Comparative Analysis"
        J[Performance Comparison]
        K[Risk Comparison]
        L[Valuation Comparison]
        M[Sector Analysis]
    end
    
    subgraph "Portfolio Metrics"
        N[Correlation Analysis]
        O[Diversification Metrics]
        P[Risk-Adjusted Returns]
        Q[Sharpe Ratios]
    end
    
    subgraph "Allocation Analysis"
        R[Weight Optimization]
        S[Risk Budgeting]
        T[Rebalancing Strategy]
        U[Performance Attribution]
    end
    
    subgraph "Output Generation"
        V[Portfolio Report]
        W[Comparative Tables]
        X[Allocation Recommendations]
        Y[Risk Analysis]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    
    C --> G
    C --> H
    C --> I
    
    E --> J
    E --> K
    E --> L
    E --> M
    
    F --> N
    N --> O
    O --> P
    P --> Q
    
    Q --> R
    R --> S
    S --> T
    T --> U
    
    F --> V
    V --> W
    W --> X
    X --> Y
```

## 7. Enterprise Strategy Analyst Architecture

```mermaid
graph TB
    subgraph "Enterprise Strategy Analyst Node"
        A[enterprise_strategy_analyst_node Function]
        B[State Processing]
        C[Tool Configuration]
        D[LLM Chain Setup]
        E[Tool Execution]
        F[Response Processing]
    end
    
    subgraph "Data Sources"
        G[Company Filings]
        H[Industry Reports]
        I[Competitive Intelligence]
        J[Market Research]
    end
    
    subgraph "Strategic Analysis"
        K[Business Model Analysis]
        L[Competitive Positioning]
        M[Market Share Analysis]
        N[Growth Strategy]
    end
    
    subgraph "Industry Analysis"
        O[Industry Trends]
        P[Regulatory Environment]
        Q[Technology Disruption]
        R[Market Dynamics]
    end
    
    subgraph "Investment Thesis"
        S[Value Proposition]
        T[Risk Factors]
        U[Growth Catalysts]
        V[Competitive Moat]
    end
    
    subgraph "Output Generation"
        W[Strategic Report]
        X[Investment Thesis]
        Y[Risk Assessment]
        Z[Recommendations]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    
    C --> G
    C --> H
    C --> I
    C --> J
    
    E --> K
    E --> L
    E --> M
    E --> N
    
    F --> O
    O --> P
    P --> Q
    Q --> R
    
    R --> S
    S --> T
    T --> U
    U --> V
    
    F --> W
    W --> X
    X --> Y
    Y --> Z
```

## 8. Multi-Scenario Optimizer Architecture

```mermaid
graph TB
    subgraph "Multi-Scenario Optimizer Node"
        A[create_multi_scenario_optimizer Function]
        B[State Processing]
        C[Data Extraction]
        D[Optimization Engine]
        E[Scenario Generation]
        F[Response Processing]
    end
    
    subgraph "Data Input"
        G[Stock Price Data]
        H[Historical Returns]
        I[Volatility Data]
        J[Market Data]
    end
    
    subgraph "Optimization Scenarios"
        K[Conservative<br/>γ = 20.0]
        L[Moderate<br/>γ = 10.0]
        M[Aggressive<br/>γ = 5.0]
        N[Volatility-Focused<br/>γ = 15.0]
        O[Return-Focused<br/>γ = 3.0]
        P[Sharpe-Optimized<br/>γ = 8.0]
    end
    
    subgraph "Risk Metrics"
        Q[Expected Return]
        R[Volatility]
        S[Sharpe Ratio]
        T[Maximum Drawdown]
        U[VaR 95%]
        V[CVaR 95%]
    end
    
    subgraph "Output Generation"
        W[Optimization Results]
        X[Scenario Summary]
        Y[Risk Metrics]
        Z[Optimal Weights]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    
    C --> G
    C --> H
    C --> I
    C --> J
    
    D --> K
    D --> L
    D --> M
    D --> N
    D --> O
    D --> P
    
    E --> Q
    E --> R
    E --> S
    E --> T
    E --> U
    E --> V
    
    F --> W
    W --> X
    X --> Y
    Y --> Z
```
