# TradingAgents Project Architecture

## System Architecture Overview

```mermaid
graph TB
    subgraph "User Interface"
        UI[main_enterprise.py<br/>single_stock_analysis.py<br/>run_portfolio_analysis.py]
    end
    
    subgraph "Core Engine"
        CE[TradingAgentsGraph<br/>LangGraph Workflow Engine]
    end
    
    subgraph "Analysis Layer"
        AL[Market Analyst<br/>Fundamentals Analyst<br/>News Analyst<br/>Social Media Analyst<br/>Quantitative Analyst<br/>Portfolio Analyst]
    end
    
    subgraph "Decision Layer"
        DL[Research Committee<br/>Risk Management<br/>Trader<br/>Investment Manager]
    end
    
    subgraph "Portfolio System"
        PS[Stock Data Aggregator<br/>Multi-Scenario Optimizer<br/>Portfolio Trader<br/>Report Generator]
    end
    
    subgraph "Data Sources"
        DS[YFinance API<br/>News APIs<br/>Social Media APIs<br/>Technical Indicators]
    end
    
    subgraph "Output"
        OUT[Reports<br/>Charts<br/>CSV Data<br/>Word Documents]
    end
    
    UI --> CE
    CE --> AL
    AL --> DL
    DL --> PS
    AL --> DS
    PS --> OUT
    DL --> OUT
```

## Detailed Architecture Layers

```mermaid
graph LR
    subgraph "Layer 1: User Interface"
        A1[main_enterprise.py]
        A2[single_stock_analysis.py]
        A3[run_portfolio_analysis.py]
    end
    
    subgraph "Layer 2: Core Engine"
        B1[TradingAgentsGraph]
        B2[GraphSetup]
        B3[ConditionalLogic]
    end
    
    subgraph "Layer 3: Analysis Agents"
        C1[Market Analyst]
        C2[Fundamentals Analyst]
        C3[News Analyst]
        C4[Social Media Analyst]
        C5[Quantitative Analyst]
        C6[Portfolio Analyst]
    end
    
    subgraph "Layer 4: Decision Making"
        D1[Bull/Bear Researchers]
        D2[Research Manager]
        D3[Risk Debators]
        D4[Risk Manager]
        D5[Trader]
    end
    
    subgraph "Layer 5: Portfolio System"
        E1[Stock Data Aggregator]
        E2[Multi-Scenario Optimizer]
        E3[Portfolio Trader]
        E4[Portfolio Report Generator]
    end
    
    subgraph "Layer 6: Data & Tools"
        F1[YFinance API]
        F2[News APIs]
        F3[Social Media APIs]
        F4[Technical Indicators]
        F5[Optimization Algorithms]
    end
    
    subgraph "Layer 7: Output"
        G1[Enhanced Reports]
        G2[Charts & Visualizations]
        G3[CSV Data Export]
        G4[Word Documents]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> E1
    
    B1 --> C1
    B1 --> C2
    B1 --> C3
    B1 --> C4
    B1 --> C5
    B1 --> C6
    
    C1 --> D1
    C2 --> D1
    C3 --> D1
    C4 --> D1
    C5 --> D1
    C6 --> D1
    
    D1 --> D2
    D2 --> D3
    D3 --> D4
    D4 --> D5
    
    D5 --> E1
    E1 --> E2
    E2 --> E3
    E3 --> E4
    
    C1 --> F1
    C2 --> F1
    C3 --> F2
    C4 --> F3
    C5 --> F4
    E2 --> F5
    
    D5 --> G1
    E4 --> G1
    G1 --> G2
    G1 --> G3
    G1 --> G4
```

## System Components Detail

### 1. User Interface Layer
- **main_enterprise.py**: Main entry point for enterprise analysis
- **single_stock_analysis.py**: Lightweight single stock analysis
- **run_portfolio_analysis.py**: Standalone portfolio analysis

### 2. Core Graph Engine
- **TradingAgentsGraph**: Main workflow orchestrator using LangGraph
- **GraphSetup**: Configures agent nodes and edges
- **ConditionalLogic**: Controls workflow branching and decision points

### 3. Agent Layer (Analysts)
- **Market Analyst**: Market conditions and macro analysis
- **Fundamentals Analyst**: Financial statement and company analysis
- **News Analyst**: News sentiment and impact analysis
- **Social Media Analyst**: Social sentiment analysis
- **Quantitative Analyst**: Technical indicators and ML forecasting
- **Portfolio Analyst**: Comparative analysis across stocks
- **Enterprise Strategy Analyst**: Strategic business analysis

### 4. Research & Risk Management
- **Bull/Bear Researchers**: Generate opposing viewpoints
- **Research Manager**: Synthesizes research findings
- **Risk Debators**: Assess risk from different perspectives
- **Risk Manager**: Final risk assessment and approval

### 5. Decision Making
- **Trader**: Generates execution plans
- **Investment Manager**: Makes final investment decisions

### 6. Report Generation
- **Enhanced Document Generator**: Creates comprehensive reports
- **Comprehensive Charts**: Generates visualizations
- **CSV Data Exporter**: Exports structured data

### 7. Portfolio System
- **Stock Data Aggregator**: Collects and standardizes data
- **Multi-Scenario Optimizer**: Runs portfolio optimization algorithms
- **Portfolio Report Generator**: Creates portfolio reports
- **Portfolio Trader**: LLM-based portfolio allocation decisions

### 8. Data & Tools
- **YFinance API**: Stock data and financial information
- **News APIs**: News sentiment analysis
- **Social Media APIs**: Social sentiment data
- **Technical Indicators**: Technical analysis calculations
- **Optimization Algorithms**: Portfolio optimization methods

### 9. State Management
- **AgentState**: TypedDict for state persistence
- **Memory Systems**: Conversation and context memory
- **Toolkit**: Shared tools and utilities