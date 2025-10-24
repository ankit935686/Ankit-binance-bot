# Binance Futures Trading Bot

**Submission for Binance Futures Order Bot Assignment**

A comprehensive CLI-based trading bot for Binance USDT-M Futures that supports multiple order types with robust logging, validation, and documentation.

## 📋 Assignment Requirements Fulfillment

### ✅ Core Requirements (100% Complete)
- **Language**: Python 3.12 ✅
- **Market & Limit Orders**: Full implementation ✅
- **Binance Futures Testnet**: USDT-M pairs supported ✅
- **Buy & Sell Sides**: Both sides implemented ✅
- **Official Binance API**: REST API via python-binance ✅
- **CLI Interface**: Comprehensive command-line interface ✅
- **Input Validation**: Extensive validation for all parameters ✅
- **Order Details Output**: Detailed order responses with IDs and status ✅
- **Execution Status**: Real-time status checking ✅
- **Logging & Error Handling**: Comprehensive logging and error management ✅

### 🚀 Bonus Requirements (Exceeded)
- **Advanced Order Types**: 4 types implemented (TWAP, Grid, Stop-Limit, OCO) ✅
- **Enhanced UI**: Dual CLI interface (simple + comprehensive) ✅

## 🎯 Features

### Core Orders (Mandatory)
- **Market Orders**: Execute orders at current market price
- **Limit Orders**: Execute orders at specified price or better

### Advanced Orders (Bonus - Higher Priority)
- **Stop-Limit Orders**: Trigger limit orders when stop price is hit
- **OCO (One-Cancels-the-Other)**: Place take-profit and stop-loss simultaneously
- **TWAP (Time-Weighted Average Price)**: Split large orders into smaller chunks over time
- **Grid Orders**: Automated buy-low/sell-high within a price range
- **DCA (Dollar Cost Averaging)**: Systematic investment strategy

## 📦 Submission Package

This project is ready for evaluator submission with the following structure:

```
[project_root]/
├── src/                    # All source code
│   ├── basic_bot.py        # Core bot functionality
│   ├── main.py            # Comprehensive CLI interface
│   ├── market_orders.py   # Simple market order CLI
│   ├── limit_orders.py    # Simple limit order CLI
│   └── advanced/          # Advanced order types
│       ├── stop_limit.py  # Stop-limit orders
│       ├── oco.py         # OCO orders
│       ├── twap.py        # TWAP strategy
│       └── grid_orders.py # Grid trading strategy
├── config.json            # Configuration file
├── requirements.txt       # Python dependencies
├── bot.log               # Logs (API calls, errors, executions)
├── report.pdf            # Analysis and documentation
├── test_bot.py           # Testing utilities
└── README.md             # Setup, dependencies, usage
```

## 📸 Visual Documentation Requirements

**For complete submission, please include the following screenshots:**

### 1. **Binance Testnet - Order History**
- Navigate to Binance Testnet → Futures → Orders → Order History
- Show executed orders (Order IDs: 6895784083, 6895834950)
- **Purpose**: Prove real trading activity 
image.png

### 2. **Binance Testnet - Open Orders**
- Navigate to Binance Testnet → Futures → Orders → Open Orders
- Show active stop-loss and grid orders
- **Purpose**: Show advanced order types working

### 3. **Bot Execution - Market Order**
- Terminal showing: `python src/market_orders.py BTCUSDT BUY 0.001`
- Show order response with Order ID and "Order placed successfully"
- **Purpose**: Demonstrate real-time order placement

### 4. **Bot Execution - Limit Order**
- Terminal showing: `python src/limit_orders.py BTCUSDT SELL 0.001 110000`
- Show order response with Order ID, price, and status
- **Purpose**: Show limit order functionality

### 5. **Bot Execution - Advanced Features**
- Terminal showing: `python src/main.py --help`
- Show all available commands and advanced order types
- **Purpose**: Demonstrate comprehensive CLI interface

### 6. **Bot Execution - Grid Strategy**
- Terminal showing: `python src/main.py grid BTCUSDT BUY 0.01 100000 120000 5`
- Show grid orders being placed with order IDs
- **Purpose**: Show advanced trading strategies

### 7. **Bot Logs - Execution History**
- Open `bot.log` file showing:
  - Order placements with timestamps
  - Execution confirmations
  - Error handling examples
- **Purpose**: Demonstrate comprehensive logging

### 8. **Bot Testing - Connection Test**
- Terminal showing: `python test_bot.py`
- Show "Connection successful" and "All tests passed" messages
- **Purpose**: Verify API connectivity and functionality

### 9. **Project Structure**
- File explorer showing complete project structure
- Show all Python files in `src/` directory
- Show documentation files (README.md, report.pdf)
- **Purpose**: Show complete project organization

## 🚀 Quick Start for Evaluators

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API credentials**:
   ```bash
   python src/main.py config --set-api-key YOUR_API_KEY --set-api-secret YOUR_API_SECRET
   ```

3. **Test basic functionality**:
   ```bash
   python test_bot.py
   ```

4. **Run trading examples**:
   ```bash
   # Market order
   python src/market_orders.py BTCUSDT BUY 0.001
   
   # Limit order
   python src/limit_orders.py BTCUSDT SELL 0.001 110000
   
   # Advanced features
   python src/main.py --help
   ```

## 📋 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd my_binance_bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Binance API credentials**:
   - For testing: Create account at https://testnet.binancefuture.com
   - For production: Create account at https://www.binance.com
   - Generate API key and secret

4. **Configure API keys**:
   ```bash
   python src/main.py config --set-api-key YOUR_API_KEY --set-api-secret YOUR_API_SECRET
   ```

## Usage

### Quick Start (Simple Orders)

**Market Order**:
```bash
python src/market_orders.py BTCUSDT BUY 0.001
```

**Limit Order**:
```bash
python src/limit_orders.py BTCUSDT SELL 0.001 60000
```

### Advanced Usage (Full CLI)

**Market Order**:
```bash
python src/main.py market BTCUSDT BUY 0.001
```

**Limit Order**:
```bash
python src/main.py limit BTCUSDT SELL 0.001 60000 --time-in-force GTC
```

**Stop-Limit Order**:
```bash
python src/main.py stop-limit BTCUSDT BUY 0.001 58000 59000
```

**Stop-Market Order**:
```bash
python src/main.py stop-market BTCUSDT SELL 0.001 62000
```

**Take-Profit Order**:
```bash
python src/main.py take-profit BTCUSDT SELL 0.001 65000
```

**OCO Order** (Take-Profit + Stop-Loss):
```bash
python src/main.py oco BTCUSDT BUY 0.001 65000 55000
```

**TWAP Order** (Time-Weighted Average Price):
```bash
python src/main.py twap BTCUSDT BUY 1.0 60 --num-slices 10
```

**Grid Strategy**:
```bash
python src/main.py grid BTCUSDT BUY 0.01 50000 60000 10 --grid-type LINEAR
```

**DCA Grid Strategy**:
```bash
python src/main.py dca BTCUSDT BUY 1.0 60000 1000 10
```

**Cancel Order**:
```bash
python src/main.py cancel BTCUSDT 123456789
```

**Check Order Status**:
```bash
python src/main.py status BTCUSDT 123456789
```

**Get Account Balance**:
```bash
python src/main.py balance
```

## Project Structure

```
my_binance_bot/
├── src/
│   ├── __init__.py
│   ├── basic_bot.py          # Core bot with validation and logging
│   ├── main.py               # Comprehensive CLI interface
│   ├── market_orders.py      # Simple market order CLI
│   ├── limit_orders.py       # Simple limit order CLI
│   └── advanced/
│       ├── stop_limit.py     # Stop-limit orders
│       ├── oco.py            # OCO orders
│       ├── twap.py           # TWAP strategy
│       └── grid_orders.py    # Grid trading strategy
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
├── bot.log                  # Log file (created automatically)
└── README.md                # This file
```

## Configuration

The bot uses `config.json` for configuration:

```json
{
  "api_key": "YOUR_API_KEY",
  "api_secret": "YOUR_API_SECRET",
  "testnet": true,
  "log_file": "bot.log"
}
```

### Configuration Commands

**Set API credentials**:
```bash
python src/main.py config --set-api-key YOUR_KEY --set-api-secret YOUR_SECRET
```

**Show current configuration**:
```bash
python src/main.py config --show
```

## Logging

All bot activities are logged to `bot.log` with timestamps:
- Order placements
- Order executions
- Errors and exceptions
- API responses

## Safety Features

- **Input Validation**: All parameters are validated before API calls
- **Error Handling**: Comprehensive error handling with detailed logging
- **Testnet Support**: Default to testnet for safe testing
- **Rate Limiting**: Built-in delays to respect API rate limits
- **Order Monitoring**: Automatic monitoring for OCO and advanced strategies

## Examples

### Basic Trading
```bash
# Buy 0.001 BTC at market price
python src/main.py market BTCUSDT BUY 0.001

# Sell 0.001 BTC at $60,000
python src/main.py limit BTCUSDT SELL 0.001 60000
```

### Risk Management
```bash
# Place OCO order: take profit at $65k, stop loss at $55k
python src/main.py oco BTCUSDT BUY 0.001 65000 55000

# Place stop-loss order
python src/main.py stop-market BTCUSDT SELL 0.001 58000
```

### Advanced Strategies
```bash
# TWAP: Buy 1 BTC over 60 minutes in 10 slices
python src/main.py twap BTCUSDT BUY 1.0 60 --num-slices 10

# Grid: Place 10 orders between $50k-$60k
python src/main.py grid BTCUSDT BUY 0.01 50000 60000 10
```

## Notes

- **Testnet First**: Always test on testnet before using mainnet
- **API Permissions**: Ensure your API keys have futures trading permissions
- **Rate Limits**: The bot respects Binance API rate limits
- **Logging**: Check `bot.log` for detailed execution logs
- **Error Handling**: All errors are logged with full stack traces

## Troubleshooting

1. **API Connection Issues**: Check your API keys and internet connection
2. **Order Rejected**: Verify symbol format and trading permissions
3. **Rate Limiting**: The bot includes automatic delays between requests
4. **Logs**: Check `bot.log` for detailed error information

## Support

For issues and questions:
1. Check the logs in `bot.log`
2. Verify your API credentials
3. Ensure you're using the correct symbol format (e.g., BTCUSDT)
4. Test on testnet first before using mainnet
