# TradingAgents User Workflow Diagram

## Complete User Workflow

```mermaid
flowchart TD
    A[User Opens TradingAgents] --> B[Enter Stock Tickers<br/>NVDA, AAPL, etc.]
    B --> C[Select Analysts & Risk Profile]
    
    C --> D[Submit Analysis Request]
    D --> E[Individual Stock Analysis]
    
    E --> F[Market Analyst]
    E --> G[Fundamentals Analyst]
    E --> H[News Analyst]
    E --> I[Social Media Analyst]
    E --> J[Quantitative Analyst]
    
    F --> K[Generate Reports & Export CSV]
    G --> K
    H --> K
    I --> K
    J --> K
    
    K --> L[Portfolio Generation]
    L --> M[Aggregate Data]
    M --> N[Portfolio Optimization]
    N --> O[Generate Allocation]
    O --> P[Create Portfolio Report]
    
    P --> Q[Review Complete Analysis]
    Q --> R[Download Reports]
    R --> S[Make Investment Decision]
    
    S --> T[Implement Strategy]
    S --> U[Modify & Re-run]
    S --> V[Explore Alternatives]
```

## Key User Steps

### 1. **Input & Configuration**
- Enter stock tickers (e.g., NVDA, AAPL)
- Select analysts (Market, Fundamentals, News, Social, Quantitative)
- Set risk tolerance and investment objectives

### 2. **Analysis Execution**
- System runs individual stock analysis for each ticker
- Generates comprehensive reports and exports CSV data
- Automatically proceeds to portfolio generation

### 3. **Portfolio Generation**
- Aggregates data from individual stock analyses
- Runs multiple optimization algorithms
- Generates portfolio allocation recommendations
- Creates comprehensive portfolio report

### 4. **Review & Decision**
- Review individual stock reports
- Analyze portfolio allocation recommendations
- Make investment decisions based on results
- Download reports and data for further analysis

## System Features

- **Automated Pipeline**: Single stock analysis → Portfolio generation
- **Multi-Analyst Approach**: Comprehensive analysis from multiple perspectives
- **Portfolio Optimization**: Advanced algorithms for allocation decisions
- **Export Capabilities**: CSV data and formatted reports
- **Risk Management**: Built-in risk assessment and scenario analysis