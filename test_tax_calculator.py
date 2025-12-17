"""Unit tests for tax_calculator.py"""

import pytest
import numpy as np
import pandas as pd

from tax_calculator import (
    calculate_tax_for_bracket,
    calculate_tax,
    TAX_BRACKETS,
)


class TestCalculateTaxForBracket:
    """Tests for calculate_tax_for_bracket function."""

    def test_zero_income(self):
        """Tax on zero income should be zero."""
        tax, rate = calculate_tax_for_bracket(0, TAX_BRACKETS['FED'])
        assert tax == 0.0
        assert rate == 0.10  # First bracket rate

    def test_negative_income(self):
        """Negative income should return zero tax."""
        tax, rate = calculate_tax_for_bracket(-1000, TAX_BRACKETS['FED'])
        assert tax == 0.0

    def test_first_bracket_only(self):
        """Income within first bracket."""
        # $10,000 income, all in 10% bracket
        tax, rate = calculate_tax_for_bracket(10000, TAX_BRACKETS['FED'])
        assert tax == 1000.0  # 10% of $10,000
        assert rate == 0.10

    def test_second_bracket(self):
        """Income spanning two brackets."""
        # $20,000 income
        # First $11,925 at 10% = $1,192.50
        # Remaining $8,075 at 12% = $969.00
        # Total = $2,161.50
        tax, rate = calculate_tax_for_bracket(20000, TAX_BRACKETS['FED'])
        expected = 11925 * 0.10 + (20000 - 11925) * 0.12
        assert abs(tax - expected) < 0.01
        assert rate == 0.12

    def test_high_income_multiple_brackets(self):
        """High income spanning multiple brackets."""
        # $200,000 income should go through several brackets
        tax, rate = calculate_tax_for_bracket(200000, TAX_BRACKETS['FED'])
        assert tax > 0
        assert rate == 0.32  # Should be in 32% bracket ($197,300 - $250,525)

    def test_social_security_cap(self):
        """Social Security tax should cap at wage base."""
        # Income above SS wage base ($176,100)
        tax_below, _ = calculate_tax_for_bracket(176100, TAX_BRACKETS['Soc Sec'])
        tax_above, _ = calculate_tax_for_bracket(200000, TAX_BRACKETS['Soc Sec'])
        # Both should be the same (capped)
        assert abs(tax_below - tax_above) < 0.01
        assert abs(tax_below - 176100 * 0.062) < 0.01


class TestCalculateTax:
    """Tests for calculate_tax function."""

    def test_basic_calculation(self):
        """Basic tax calculation returns DataFrame."""
        result = calculate_tax(60000, 15000, TAX_BRACKETS)
        assert isinstance(result, pd.DataFrame)
        assert 'Tax' in result.columns
        assert 'ALL' in result.index

    def test_all_tax_types_present(self):
        """All tax types should be in result."""
        result = calculate_tax(60000, 15000, TAX_BRACKETS)
        expected_types = ['FED', 'NY', 'NYC', 'Soc Sec', 'Med', 'ALL']
        for tax_type in expected_types:
            assert tax_type in result.index

    def test_zero_income(self):
        """Zero income should return zero taxes."""
        result = calculate_tax(0, 0, TAX_BRACKETS)
        assert result.loc['ALL', 'Tax'] == 0

    def test_deduction_exceeds_income(self):
        """Deduction greater than income should result in zero tax."""
        result = calculate_tax(50000, 60000, TAX_BRACKETS)
        # Federal, NY, NYC taxes should be zero (taxable income is 0)
        assert result.loc['FED', 'Tax'] == 0
        assert result.loc['NY', 'Tax'] == 0
        assert result.loc['NYC', 'Tax'] == 0

    def test_negative_income_raises(self):
        """Negative income should raise ValueError."""
        with pytest.raises(ValueError, match="Income cannot be negative"):
            calculate_tax(-1000, 0, TAX_BRACKETS)

    def test_negative_deduction_raises(self):
        """Negative deduction should raise ValueError."""
        with pytest.raises(ValueError, match="Deduction cannot be negative"):
            calculate_tax(50000, -1000, TAX_BRACKETS)

    def test_tax_increases_with_income(self):
        """Higher income should result in higher tax."""
        result_low = calculate_tax(50000, 15000, TAX_BRACKETS)
        result_high = calculate_tax(100000, 15000, TAX_BRACKETS)
        assert result_high.loc['ALL', 'Tax'] > result_low.loc['ALL', 'Tax']

    def test_deduction_reduces_tax(self):
        """Higher deduction should result in lower tax."""
        result_low_deduction = calculate_tax(60000, 10000, TAX_BRACKETS)
        result_high_deduction = calculate_tax(60000, 20000, TAX_BRACKETS)
        assert result_high_deduction.loc['ALL', 'Tax'] < result_low_deduction.loc['ALL', 'Tax']


class TestTaxBrackets:
    """Tests for tax bracket data integrity."""

    def test_federal_brackets_ascending(self):
        """Federal tax rates should be ascending."""
        rates = [TAX_BRACKETS['FED'][i][0] for i in range(len(TAX_BRACKETS['FED']))]
        for i in range(1, len(rates)):
            assert rates[i] > rates[i-1], "Federal rates should increase"

    def test_ny_brackets_ascending(self):
        """NY tax rates should be ascending."""
        rates = [TAX_BRACKETS['NY'][i][0] for i in range(len(TAX_BRACKETS['NY']))]
        for i in range(1, len(rates)):
            assert rates[i] > rates[i-1], f"NY rate {rates[i]} should be > {rates[i-1]}"

    def test_brackets_have_inf_upper_bound(self):
        """Last bracket should have infinite upper bound."""
        for tax_type, brackets in TAX_BRACKETS.items():
            last_bracket = max(brackets.keys())
            assert brackets[last_bracket][1] == np.inf, f"{tax_type} should end with inf"


class TestEdgeCases:
    """Edge case tests."""

    def test_very_high_income(self):
        """Calculator handles very high income."""
        result = calculate_tax(10_000_000, 100_000, TAX_BRACKETS)
        assert result.loc['ALL', 'Tax'] > 0

    def test_income_equals_deduction(self):
        """Income exactly equals deduction (zero taxable income)."""
        result = calculate_tax(50000, 50000, TAX_BRACKETS)
        # Should not raise, taxes should be zero or minimal
        assert result.loc['FED', 'Tax'] == 0

    def test_small_income(self):
        """Very small income."""
        result = calculate_tax(100, 0, TAX_BRACKETS)
        assert result.loc['FED', 'Tax'] == 10  # 10% of $100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
