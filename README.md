# US Tax Calculator (2025)

A Python tool for calculating US federal, state (New York), and local (NYC) income taxes based on 2025 tax brackets.

## Features

- Federal income tax calculation
- New York state income tax
- New York City local income tax
- Social Security tax (with wage base cap)
- Medicare tax
- Support for 401(k) contributions (traditional/pre-tax)
- Calculates marginal, nominal, and effective tax rates
- Take-home pay calculations

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Basic usage with total income
python tax_calculator.py --income 60000

# With deductions
python tax_calculator.py --income 60000 --standard-deduction 15000

# Using base salary and bonus
python tax_calculator.py --base 50000 --bonus 10000

# With 401(k) contribution
python tax_calculator.py --base 50000 --bonus 10000 --contribution-401k 23500

# Full example
python tax_calculator.py --base 50000 --bonus 10000 --contribution-401k 23500 --standard-deduction 15000 --other-deduction 0
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--income` | Total gross income | - |
| `--base` | Base salary | 0 |
| `--bonus` | Bonus amount | 0 |
| `--contribution-401k` | Traditional 401(k) contribution | 0 |
| `--standard-deduction` | Standard deduction | 15000 |
| `--other-deduction` | Other deductions | 0 |

### As a Python Module

```python
from tax_calculator import calculate_tax, TAX_BRACKETS

# Calculate taxes for $60,000 income with $15,000 deduction
result = calculate_tax(income=60000, deduction=15000, tax_brackets=TAX_BRACKETS)

# Get total tax
total_tax = result.loc['ALL', 'Tax']
print(f"Total tax: ${total_tax:,}")

# View full breakdown
print(result)
```

## Running Tests

```bash
pip install pytest
pytest test_tax_calculator.py -v
```

## Tax Brackets (2025)

The calculator uses 2025 tax brackets for:

- **Federal**: 10%, 12%, 22%, 24%, 32%, 35%, 37%
- **New York State**: 4% to 10.9%
- **New York City**: 3.078% to 3.876%
- **Social Security**: 6.2% (up to $176,100)
- **Medicare**: 1.45%

## Notes

- 401(k) contributions are assumed to be traditional (pre-tax)
- The calculator is designed for single filers in NY/NYC
- Tax brackets are hardcoded for 2025 and should be updated annually

## License

MIT
