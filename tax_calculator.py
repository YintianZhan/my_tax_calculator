import pandas as pd
import numpy as np
pd.options.display.float_format = '{:.2%}'.format

# tax rates and brackets are 2025 numbers
tax_brackets = {}
tax_brackets['FED'] = {0:(0.1,11925),
                       1:(0.12,48475),
                       2:(0.22,103350),
                       3:(0.24,197300),
                       4:(0.32,250525),
                       5:(0.35,626350),
                       6:(0.37,np.inf)}
tax_brackets['NY'] = {0:(0.04,8500),
                       1:(0.045,11700),
                       2:(0.0525,13900),
                       3:(0.055,80650),
                       4:(0.06,215400),
                       5:(0.0685,1077550),
                       6:(0.0965,5e6),
                       7:(0.103,2.5e7),
                       8:(0.0109,np.inf)}
tax_brackets['NYC'] = {0:(0.03078,12000),
                       1:(0.03762,25000),
                       2:(0.03819,50000),
                       3:(0.03876,np.inf)}
tax_brackets['Soc Sec'] = {0:(0.062,176100),
                       1:(0.0,np.inf)}
tax_brackets['Med'] = {0:(0.0145,np.inf)}

def calculate_tax_helper(taxable_income, tax_bracket):
    tax = 0
    lower_bound = 0
    i = 0
    upper_bound = tax_bracket[0][1]
    tax_rate = tax_bracket[0][0]
    while taxable_income > upper_bound:
        tax += tax_rate * (upper_bound-lower_bound)
        i += 1
        lower_bound = upper_bound
        upper_bound = tax_bracket[i][1]
        tax_rate = tax_bracket[i][0]
    tax += tax_rate * (taxable_income-lower_bound)
    return tax, tax_rate

def calculate_tax(income, deduction, tax_brackets):
    summary = pd.DataFrame()
    for key, tax_brackets_key in tax_brackets.items():
        tax, marginal_rate = calculate_tax_helper(max(income - deduction, 0), tax_brackets_key)
        summary[key] = pd.Series([tax, tax/(income - deduction), marginal_rate, tax/income], index = ['Tax', 'Nominal Tax Rate', 'Marginal Tax Rate', 'Effective Tax Rate'])

    summary['ALL'] = summary.sum(axis = 1)
    summary = summary.T
    summary['Tax'] = summary['Tax'].astype(int)
    return summary

if __name__ == "__main__":
    base = 50000
    bonus = 10000
    income = base + bonus
    fook = 23500
    standard_deduction = 15000
    other_deduction = 0
    # this is assuming all 401k is traditional. If all roth, do not subtract 401k amount from income
    deduction = standard_deduction + fook + other_deduction

    tax_summary = calculate_tax(income, deduction, tax_brackets)
    tax = tax_summary.loc['ALL', 'Tax']
    tax_summary['Tax'] = tax_summary['Tax'].apply(lambda x: '${:,}'.format(x))
    take_home_rate = (income-fook-tax)/income
    sep = f"\n\n{'-'*100}\n\n"
    print(sep,f'Income: ${income:,}, Tax: ${tax:,}, 401K: ${fook:,}',sep)
    print(f'Take-Home Rate: {take_home_rate:.2%}, Monthly Post-Tax Base: ${base*take_home_rate/12:,.0f}, Monthly Post-Tax: ${income*take_home_rate/12:,.0f}', sep)
    print(tax_summary, sep)
