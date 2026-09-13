# Buy or Wait? Financial Affordability Agent

An AI-powered system to determine whether users can safely afford requested expenses by analyzing 90-day cash flow forecasts, payment options, and financial priorities.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Architecture

```
├── main.py                 # Entry point
├── src/
│   ├── data_loader.py     # CSV/image loading
│   ├── financial_calculator.py  # 90-day forecast
│   ├── payment_ranker.py  # Payment plan selection
│   ├── affordability_agent.py   # Core logic
│   ├── llm_explainer.py   # AI explanations
│   └── utils.py           # Utilities
└── evaluation/
    └── usage_report.md    # Token tracking
```

## Key Features

- **90-Day Safety Check**: Forecasts cash flow including recurring income/expenses
- **Payment Option Ranking**: Selects best plan by problem criteria
- **Affordability Assessment**: Determines affordable_now, affordable_with_plan, affordable_later, or not_affordable
- **Personalized Recommendations**: Respects user payment preferences and financial priorities
- **Multi-Currency Support**: INR, ZAR, IDR, USD, EUR
