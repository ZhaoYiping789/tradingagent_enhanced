# TradingAgents Portfolio System Architecture

## Portfolio System Overview

```mermaid
graph TB
    subgraph "Portfolio System Entry Point"
        A[main_enterprise.py Portfolio Mode]
        B[run_portfolio_analysis.py]
    end
    
    subgraph "Data Aggregation Layer"
        C[StockDataAggregator]
        D[CSV Data Loading]
        E[MD Report Parsing]
        F[Data Standardization]
    end
    
    subgraph "Portfolio Optimization Engine"
        G[MultiScenarioPortfolioOptimizer]
        H[Returns Matrix Construction]
        I[Covariance Matrix Calculation]
        J[Optimization Algorithms]
    end
    
    subgraph "Optimization Algorithms"
        K[Max Sharpe Ratio]
        L[Minimum Variance]
        M[Risk Parity]
        N[Max Diversification]
        O[Hierarchical Risk Parity]
    end
    
    subgraph "LLM Decision Making"
        P[PortfolioTrader]
        Q[Raw Data Integration]
        R[Optimization Results Analysis]
        S[Final Allocation Decision]
    end
    
    subgraph "Report Generation"
        T[PortfolioReportGenerator]
        U[Comparative Tables]
        V[Visualization Charts]
        W[Final Portfolio Report]
    end
    
    A --> C
    B --> C
    
    C --> D
    C --> E
    C --> F
    
    F --> G
    G --> H
    H --> I
    I --> J
    
    J --> K
    J --> L
    J --> M
    J --> N
    J --> O
    
    K --> P
    L --> P
    M --> P
    N --> P
    O --> P
    
    P --> Q
    Q --> R
    R --> S
    
    S --> T
    T --> U
    U --> V
    V --> W
```

## Stock Data Aggregator Detailed Architecture

```mermaid
graph TB
    subgraph "StockDataAggregator Class"
        A[__init__ base_date]
        B[load_stock_analysis ticker]
        C[aggregate_multiple_stocks tickers]
        D[save_aggregated_data]
    end
    
    subgraph "Data Loading Methods"
        E[_load_from_csv<br/>_extract_decision_from_md<br/>_extract_technical_table<br/>_extract_fundamental_table<br/>_extract_news_summary]
    end
    
    subgraph "CSV Data Sources"
        J[summary_metrics.csv<br/>risk_metrics.csv<br/>technical_indicators.csv<br/>financial_metrics.csv<br/>optimization_scenarios.csv<br/>sentiment_analysis.csv]
    end
    
    subgraph "Data Processing"
        P[Data Validation<br/>Metric Extraction<br/>Sentiment Processing<br/>Risk Calculation]
    end
    
    subgraph "Output Structure"
        T[Individual Stock Data<br/>Aggregated Portfolio Data<br/>Standardized Metrics<br/>JSON Cache File]
    end
    
    A --> B
    B --> C
    C --> D
    
    B --> E
    B --> F
    B --> G
    B --> H
    B --> I
    
    E --> J
    E --> K
    E --> L
    E --> M
    E --> N
    E --> O
    
    E --> P
    P --> Q
    Q --> R
    R --> S
    
    S --> T
    T --> U
    U --> V
    V --> W
```

## Multi-Scenario Portfolio Optimizer Detailed Architecture

```mermaid
graph TB
    subgraph "MultiScenarioPortfolioOptimizer Class"
        A[__init__ returns_data, stock_metrics]
        B[optimize_all_scenarios]
        C[_calculate_covariance_matrix]
    end
    
    subgraph "Optimization Methods"
        D[max_sharpe_optimization<br/>min_variance_optimization<br/>risk_parity_optimization<br/>max_diversification_optimization<br/>hierarchical_risk_parity]
    end
    
    subgraph "Mathematical Framework"
        I[CVXPY Solver<br/>SCIPY Optimization<br/>Risk Aversion Parameters<br/>Constraint Handling]
    end
    
    subgraph "Risk Metrics Calculation"
        M[Expected Return<br/>Volatility<br/>Sharpe Ratio<br/>Maximum Drawdown<br/>VaR/CVaR]
    end
    
    subgraph "Output Generation"
        R[Optimization Results]
        S[Weight Allocations]
        T[Risk-Return Profiles]
        U[Algorithm Philosophies]
    end
    
    A --> B
    B --> C
    
    B --> D
    B --> E
    B --> F
    B --> G
    B --> H
    
    D --> I
    E --> I
    F --> J
    G --> I
    H --> J
    
    I --> K
    J --> K
    K --> L
    
    L --> M
    M --> N
    N --> O
    O --> P
    P --> Q
    
    Q --> R
    R --> S
    S --> T
    T --> U
```

## Portfolio Trader LLM Architecture

```mermaid
graph TB
    subgraph "PortfolioTrader Class"
        A[__init__ llm_model]
        B[make_final_allocation]
        C[_format_individual_analysis]
        D[_format_optimization_scenarios]
        E[_format_sentiment_data]
    end
    
    subgraph "Input Data Processing"
        F[Aggregated Stock Data]
        G[Optimization Scenarios]
        H[Market Context]
        I[Raw Metrics]
    end
    
    subgraph "LLM Prompt Engineering"
        J[System Message]
        K[Individual Analysis Format]
        L[Optimization Results Format]
        M[Decision Framework]
    end
    
    subgraph "Analysis Integration"
        N[Fundamental Analysis]
        O[Technical Analysis]
        P[Sentiment Analysis]
        Q[Risk Assessment]
    end
    
    subgraph "Decision Output"
        R[Final Allocation Weights]
        S[Decision Rationale]
        T[Risk Considerations]
        U[Implementation Strategy]
    end
    
    A --> B
    B --> C
    B --> D
    B --> E
    
    B --> F
    B --> G
    B --> H
    B --> I
    
    C --> J
    D --> K
    E --> L
    B --> M
    
    J --> N
    K --> O
    L --> P
    M --> Q
    
    N --> R
    O --> R
    P --> R
    Q --> R
    
    R --> S
    S --> T
    T --> U
```

## Portfolio Report Generator Architecture

```mermaid
graph TB
    subgraph "PortfolioReportGenerator Class"
        A[__init__ aggregated_data, optimization_scenarios]
        B[generate_comprehensive_report]
        C[_create_markdown_report]
    end
    
    subgraph "Data Integration"
        D[Individual Stock Data]
        E[Optimization Results]
        F[LLM Decision]
        G[Market Context]
    end
    
    subgraph "Report Sections"
        H[Executive Summary]
        I[Individual Stock Comparison]
        J[Optimization Algorithm Results]
        K[LLM Analysis Integration]
        L[Final Recommendations]
    end
    
    subgraph "Comparative Analysis"
        M[Technical Metrics Table]
        N[Fundamental Metrics Table]
        O[Risk Metrics Table]
        P[Sentiment Analysis Table]
    end
    
    subgraph "Visualization"
        Q[Color-Coded Tables]
        R[Performance Charts]
        S[Risk-Return Scatter]
        T[Allocation Pie Charts]
    end
    
    subgraph "Output Generation"
        U[Markdown Report]
        V[Formatted Tables]
        W[Decision Summary]
        X[Implementation Guide]
    end
    
    A --> B
    B --> C
    
    B --> D
    B --> E
    B --> F
    B --> G
    
    C --> H
    H --> I
    I --> J
    J --> K
    K --> L
    
    I --> M
    I --> N
    I --> O
    I --> P
    
    M --> Q
    N --> Q
    O --> Q
    P --> Q
    
    Q --> R
    R --> S
    S --> T
    
    T --> U
    U --> V
    V --> W
    W --> X
```

## Data Flow Architecture

```mermaid
graph TD
    A[User Input] --> B[main_enterprise.py]
    B --> C[Single Stock Analysis]
    C --> D[CSV Data Export]
    D --> E[Stock Data Aggregator]
    E --> F[Load CSV Data]
    F --> G[Multi-Scenario Optimizer]
    G --> H[Portfolio Optimization]
    H --> I[Portfolio Trader LLM]
    I --> J[Final Allocation Decision]
    J --> K[Portfolio Report Generator]
    K --> L[Comprehensive Report]
    L --> M[User Output]
```