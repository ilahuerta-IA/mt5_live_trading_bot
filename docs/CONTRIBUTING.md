# Contributing to MT5 Live Trading Monitor

Thank you for your interest in contributing to the MT5 Live Trading Monitor project! This document provides guidelines for contributing to this trading system.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## 🤝 Code of Conduct

### Our Standards

- **Be Respectful**: Treat all contributors with respect
- **Be Professional**: Keep discussions focused and constructive
- **Be Patient**: Remember that everyone is learning
- **Be Careful**: This is financial software - safety first

### Trading Ethics

- **No Scams**: Do not promote fraudulent trading schemes
- **No Guarantees**: Never promise specific returns or profits
- **Education First**: Focus on educational value
- **Risk Warnings**: Always emphasize trading risks

## 🎯 How Can I Contribute?

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** (if available)
3. **Include details**:
   - Python version
   - MT5 version
   - Operating system
   - Error messages (full stack trace)
   - Steps to reproduce

### Suggesting Features

1. **Open a GitHub Issue** with the `enhancement` label
2. **Describe the feature** clearly
3. **Explain the use case**
4. **Consider backwards compatibility**
5. **Be open to discussion**

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Make your changes**
4. **Write tests** (if applicable)
5. **Update documentation**
6. **Submit a pull request**

## 🔧 Development Setup

### Prerequisites

```bash
# Python 3.8+
python --version

# MetaTrader 5
# Install from: https://www.metatrader5.com/

# Git
git --version
```

### Setup Development Environment

```bash
# 1. Clone your fork
git clone https://github.com/your-username/mt5_live_trading_bot.git
cd mt5_live_trading_bot

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies (optional)
pip install pytest black flake8

# 5. Run tests
cd testing
python test_setup.py
```

## 📝 Coding Standards

### Python Style

- **Follow PEP 8** (Python Enhancement Proposal 8)
- **Use 4 spaces** for indentation (not tabs)
- **Max line length**: 88 characters (Black formatter standard)
- **Docstrings**: Use Google style docstrings

**Example:**
```python
def calculate_ema(prices, period):
    """Calculate Exponential Moving Average.
    
    Args:
        prices (pd.Series): Price data series
        period (int): EMA period
        
    Returns:
        pd.Series: EMA values
        
    Raises:
        ValueError: If period is less than 1
    """
    if period < 1:
        raise ValueError("Period must be >= 1")
    return prices.ewm(span=period).mean()
```

### Code Organization

- **One class/function per logical purpose**
- **Keep functions small** (< 50 lines when possible)
- **Use meaningful names** (`calculate_ema` not `calc_e`)
- **Add comments** for complex logic
- **Remove debug print statements** before committing

### Error Handling

```python
# Good
try:
    result = mt5.symbol_info(symbol)
    if result is None:
        raise ValueError(f"Symbol {symbol} not found")
except Exception as e:
    logger.error(f"Failed to get symbol info: {e}")
    return None

# Bad
result = mt5.symbol_info(symbol)  # No error handling
```

### Logging

- **Use Python logging module**
- **Appropriate log levels**:
  - `DEBUG`: Detailed information for debugging
  - `INFO`: General information
  - `WARNING`: Warning messages
  - `ERROR`: Error messages
  - `CRITICAL`: Critical failures

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Strategy initialized successfully")
logger.warning("High volatility detected")
logger.error(f"Failed to connect to MT5: {error}")
```

## 🧪 Testing

### Writing Tests

- **Test new features** you add
- **Test edge cases** (empty data, invalid inputs, etc.)
- **Use descriptive test names**

```python
def test_ema_calculation_valid_data():
    """Test EMA calculation with valid price data."""
    prices = pd.Series([1, 2, 3, 4, 5])
    ema = calculate_ema(prices, period=3)
    assert len(ema) == len(prices)
    assert not ema.isnull().any()

def test_ema_calculation_invalid_period():
    """Test EMA calculation with invalid period."""
    prices = pd.Series([1, 2, 3])
    with pytest.raises(ValueError):
        calculate_ema(prices, period=0)
```

### Running Tests

```bash
# Run all tests
cd testing
python test_setup.py
python test_monitor_components.py
python test_signal_detection.py

# Run with pytest (if installed)
pytest testing/
```

## 📤 Submitting Changes

### Commit Messages

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
# Good
git commit -m "feat: Add support for custom EMA periods

- Allow users to configure EMA periods per strategy
- Add validation for EMA period ranges
- Update documentation with examples"

# Bad
git commit -m "fixed stuff"
```

### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG** (if exists)
5. **Write clear PR description**:
   - What changed
   - Why it changed
   - How to test it

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
```

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g., Windows 10]
 - Python Version: [e.g., 3.9.7]
 - MT5 Version: [e.g., 5.0.37]

**Additional context**
Any other relevant information.
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem.

**Describe the solution you'd like**
Clear description of desired functionality.

**Describe alternatives you've considered**
Other solutions you've considered.

**Additional context**
Mockups, examples, or references.
```

## 📚 Resources

### Documentation
- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [MetaTrader 5 Python Documentation](https://www.mql5.com/en/docs/integration/python_metatrader5)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linter](https://flake8.pycqa.org/)
- [pytest Testing Framework](https://pytest.org/)

## ⚖️ Legal

### Contributor License Agreement

By contributing, you agree that:
- Your contributions are your own work
- You have the right to submit the work
- Your contributions will be under the MIT License
- You understand this is trading software with inherent risks

### Trading Disclaimer

**IMPORTANT:** All contributors must acknowledge:
- This is educational software
- Trading involves substantial risk of loss
- No guarantees of profitability
- Past performance ≠ future results
- Users trade at their own risk

## 🙏 Thank You!

Thank you for considering contributing to this project. Your time and effort help make this a better tool for the trading community.

**Questions?** Open a GitHub Issue or discussion.

**Happy Coding!** 🚀

---

*Last Updated: October 11, 2025*
