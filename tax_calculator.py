"""
US Tax Calculator for 2025

Calculates federal, state (NY), and local (NYC) income taxes,
along with Social Security and Medicare taxes.
"""

import argparse
from typing import Dict, Tuple

import numpy as np
import pandas as pd

pd.options.display.float_format = '{:.2%}'.format

# Tax rates and brackets are 2025 numbers
# Format: {bracket_index: (rate, upper_bound)}
TAX_BRACKETS: Dict[str, Dict[int, Tuple[float, float]]] = {
    'FED': {
        0: (0.10, 11925),
        1: (0.12, 48475),
        2: (0.22, 103350),
        3: (0.24, 197300),
        4: (0.32, 250525),
        5: (0.35, 626350),
        6: (0.37, np.inf),
    },
    'NY': {
        0: (0.04, 8500),
        1: (0.045, 11700),
        2: (0.0525, 13900),
        3: (0.055, 80650),
        4: (0.06, 215400),
        5: (0.0685, 1077550),
        6: (0.0965, 5e6),
        7: (0.103, 2.5e7),
        8: (0.109, np.inf),  # Fixed: was 0.0109 (typo)
    },
    'NYC': {
        0: (0.03078, 12000),
        1: (0.03762, 25000),
        2: (0.03819, 50000),
        3: (0.03876, np.inf),
    },
    'Soc Sec': {
        0: (0.062, 176100),
        1: (0.0, np.inf),
    },
    'Med': {
        0: (0.0145, np.inf),
    },
}


def calculate_tax_for_bracket(
    taxable_income: float,
    tax_bracket: Dict[int, Tuple[float, float]]
) -> Tuple[float, float]:
    """
    Calculate tax amount for a given taxable income using specified tax brackets.

    Args:
        taxable_income: The income amount to calculate tax on.
        tax_bracket: Dictionary mapping bracket index to (rate, upper_bound) tuples.

    Returns:
        A tuple of (total_tax, marginal_rate) where:
        - total_tax: The calculated tax amount
        - marginal_rate: The tax rate for the highest bracket reached
    """
    if taxable_income <= 0:
        return 0.0, tax_bracket[0][0]

    tax = 0.0
    lower_bound = 0.0
    i = 0
    upper_bound = tax_bracket[0][1]
    tax_rate = tax_bracket[0][0]

    while taxable_income > upper_bound:
        tax += tax_rate * (upper_bound - lower_bound)
        i += 1
        lower_bound = upper_bound
        upper_bound = tax_bracket[i][1]
        tax_rate = tax_bracket[i][0]

    tax += tax_rate * (taxable_income - lower_bound)
    return tax, tax_rate


def calculate_tax(
    income: float,
    deduction: float,
    tax_brackets: Dict[str, Dict[int, Tuple[float, float]]]
) -> pd.DataFrame:
    """
    Calculate comprehensive tax summary across all tax types.

    Args:
        income: Gross income amount.
        deduction: Total deductions to subtract from income.
        tax_brackets: Dictionary of tax bracket definitions by tax type.

    Returns:
        DataFrame with tax amounts and rates for each tax type.

    Raises:
        ValueError: If income is negative or deduction exceeds income.
    """
    if income < 0:
        raise ValueError("Income cannot be negative")
    if deduction < 0:
        raise ValueError("Deduction cannot be negative")

    taxable_income = max(income - deduction, 0)
    summary = pd.DataFrame()

    for key, bracket in tax_brackets.items():
        tax, marginal_rate = calculate_tax_for_bracket(taxable_income, bracket)

        # Avoid division by zero
        nominal_rate = tax / taxable_income if taxable_income > 0 else 0.0
        effective_rate = tax / income if income > 0 else 0.0

        summary[key] = pd.Series(
            [tax, nominal_rate, marginal_rate, effective_rate],
            index=['Tax', 'Nominal Tax Rate', 'Marginal Tax Rate', 'Effective Tax Rate']
        )

    summary['ALL'] = summary.sum(axis=1)
    summary = summary.T
    summary['Tax'] = summary['Tax'].astype(int)
    return summary


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Calculate US federal, state (NY), and local (NYC) income taxes for 2025.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --income 60000
  %(prog)s --income 60000 --deduction 15000
  %(prog)s --base 50000 --bonus 10000 --contribution-401k 23500
        """
    )
    parser.add_argument(
        '--income', type=float,
        help='Total gross income (alternative to --base/--bonus)'
    )
    parser.add_argument(
        '--base', type=float, default=0,
        help='Base salary'
    )
    parser.add_argument(
        '--bonus', type=float, default=0,
        help='Bonus amount'
    )
    parser.add_argument(
        '--contribution-401k', type=float, default=0,
        help='401(k) contribution (traditional, pre-tax)'
    )
    parser.add_argument(
        '--standard-deduction', type=float, default=15000,
        help='Standard deduction amount (default: 15000)'
    )
    parser.add_argument(
        '--other-deduction', type=float, default=0,
        help='Other deductions'
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the tax calculator."""
    args = parse_args()

    # Calculate income from either --income or --base + --bonus
    if args.income is not None:
        income = args.income
    else:
        income = args.base + args.bonus

    if income <= 0:
        print("Error: Income must be greater than 0")
        return

    contribution_401k = args.contribution_401k
    standard_deduction = args.standard_deduction
    other_deduction = args.other_deduction

    # Total deduction: standard + 401k + other
    # Note: 401k contribution reduces taxable income (assuming traditional 401k)
    deduction = standard_deduction + contribution_401k + other_deduction

    tax_summary = calculate_tax(income, deduction, TAX_BRACKETS)
    total_tax = tax_summary.loc['ALL', 'Tax']

    # Format tax column for display
    tax_summary_display = tax_summary.copy()
    tax_summary_display['Tax'] = tax_summary_display['Tax'].apply(lambda x: '${:,}'.format(x))

    # Calculate take-home rate (after 401k and taxes)
    take_home_rate = (income - contribution_401k - total_tax) / income

    sep = f"\n\n{'-' * 100}\n\n"
    print(sep)
    print(f'Income: ${income:,.0f}, Tax: ${total_tax:,}, 401K: ${contribution_401k:,.0f}')
    print(sep)
    print(f'Take-Home Rate: {take_home_rate:.2%}')
    if args.base > 0:
        print(f'Monthly Post-Tax Base: ${args.base * take_home_rate / 12:,.0f}')
    print(f'Monthly Post-Tax Total: ${income * take_home_rate / 12:,.0f}')
    print(sep)
    print(tax_summary_display)
    print(sep)


if __name__ == "__main__":
    main()
