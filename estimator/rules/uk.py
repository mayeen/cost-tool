"""
UK tax rules data (2026/27, England)
"""
from decimal import Decimal


SOURCES = {
    "income_tax_rates": {
        "title": "GOV.UK: Income Tax rates and Personal Allowances",
        "url": "https://www.gov.uk/income-tax-rates",
    },
    "allowance_taper": {
        "title": "GOV.UK: Income Tax rates: income over £100,000",
        "url": "https://www.gov.uk/income-tax-rates/income-over-100000",
    },
    "income_tax_bands": {
        "title": "GOV.UK: Income Tax rates and allowances for current and past years",
        "url": "https://www.gov.uk/government/publications/rates-and-allowances-income-tax/income-tax-rates-and-allowances-current-and-past",
    },
    "employer_rates": {
        "title": "GOV.UK: Rates and thresholds for employers 2026 to 2027",
        "url": "https://www.gov.uk/guidance/rates-and-thresholds-for-employers-2026-to-2027",
    },
    "social_security_ch": {
        "title": "GOV.UK: Social security contributions for workers coming to the UK from the EEA or Switzerland",
        "url": "https://www.gov.uk/guidance/social-security-contributions-for-workers-coming-to-the-uk-from-the-eea-or-switzerland",
    },
    "accommodation": {
        "title": "GOV.UK: Expenses and benefits: accommodation",
        "url": "https://www.gov.uk/expenses-and-benefits-accommodation",
    },
    "relocation_exempt": {
        "title": "GOV.UK: Expenses and benefits: relocation costs: what's exempt",
        "url": "https://www.gov.uk/expenses-and-benefits-relocation/whats-exempt",
    },
    "relocation_report": {
        "title": "GOV.UK: Expenses and benefits: relocation costs: what to report and pay",
        "url": "https://www.gov.uk/expenses-and-benefits-relocation/what-to-report-and-pay",
    },
    "tax_equalisation": {
        "title": "HMRC: Tax equalisation (HS212)",
        "url": "https://www.gov.uk/government/publications/tax-equalisation-hs212-self-assessment-helpsheet",
    },
    "gross_up": {
        "title": "HMRC PAYE Manual: PAYE72028, how to gross up",
        "url": "https://www.gov.uk/hmrc-internal-manuals/paye-manual/paye72028",
    },
}


# England income tax
INCOME_TAX = {
    "personal_allowance": Decimal("12570"),
    "taper_threshold": Decimal("100000"),   # allowance is less above this threshold
    "taper_rate": Decimal("0.5"),           # £1 of allowance lost for every £2 over
    # bands applied to different taxable income
    "bands": [
        {"name": "Basic rate", "up_to": Decimal("37700"), "rate": Decimal("0.20")},
        {"name": "Higher rate", "up_to": Decimal("125140"), "rate": Decimal("0.40")},
        {"name": "Additional rate", "up_to": None, "rate": Decimal("0.45")},
    ],
    "source": ["income_tax_rates", "allowance_taper", "income_tax_bands"],
}



# Gross-up: T = UKTax(I + T)
GROSS_UP = {
    "tolerance": Decimal("0.001"),   # stop iteration when difference is less than this
    "max_rounds": 100,               # safety limit
    "source": ["tax_equalisation", "gross_up"],
}

SOCIAL_SECURITY = {
    "applies": "Swiss",
    "uk_employer_ni": Decimal("0"),
    "title": "Social security: Swiss system applies",
    "text": (
        "The employee works for a Swiss employer and is sent to the UK temporarily, "
        "for up to 2 years. With a certificate of coverage from Switzerland, only Swiss "
        "contributions are paid, so no UK National Insurance is due for the employee "
        "or the employer."
    ),
    "source": ["social_security_ch", "employer_rates"],
}

# Benefit tags
TAXABLE_CASH = "Taxable cash"
TAXABLE_BIK = "Taxable benefit in kind"
NOT_TAXABLE = "Not taxable in the UK"

RELOCATION_EXEMPT_LIMIT = Decimal("8000")

# four type of benefits 
BENEFITS = [
    {
        "key": "housing",
        "name": "Housing in London",
        "input": "housing_monthly_host",
        "currency": "host",
        "times_per_year": 12,
        "first_year_only": False,
        "tag": TAXABLE_BIK,
        "source": ["accommodation"],
    },
    {
        "key": "relocation",
        "name": "Relocation allowance",
        "input": "relocation_allowance_home",
        "currency": "home",
        "times_per_year": 1,
        "first_year_only": True,
        "tag": TAXABLE_CASH,
        "source": ["relocation_report"],
    },
    {
        "key": "moving",
        "name": "Moving costs",
        "input": "moving_costs_host",
        "currency": "host",
        "times_per_year": 1,
        "first_year_only": True,
        "tag": NOT_TAXABLE,
        "source": ["relocation_exempt"],
    },
    {
        "key": "temporary_housing",
        "name": "Temporary housing",
        "input": "temporary_housing_host",
        "currency": "host",
        "times_per_year": 1,
        "first_year_only": True,
        "tag": TAXABLE_BIK,
        "source": ["accommodation", "relocation_exempt"],
    },
]


ASSUMPTIONS = [
    "UK 2026/27 rates are used for both years, as the brief allows. The employee is UK "
    "tax resident in both years.",
    "Moving costs are qualifying relocation costs within the £8,000 exemption.",
    "Temporary housing is not on GOV.UK's list of qualifying relocation costs, so it is "
    "treated as a taxable benefit.",
    "A certificate of coverage is issued in Switzerland, so the Swiss system applies for "
    "the whole assignment. Swiss employer contributions are not included.",
]