#Swiss rules for the hypothetical deductions

from decimal import Decimal


SOURCES = {
    "social_security_rates": {
        "title": "BSV - Social insurance contributions and benefits 2026 (synoptic table)",
        "url": "https://sozialversicherungen.admin.ch/de/d/6877/download",
    },
    "estv_calculator": {
        "title": "ESTV - Swiss tax calculator (income tax)",
        "url": "https://swisstaxcalculator.estv.admin.ch/#/calculator/income-wealth-tax",
    },
}


SOCIAL_SECURITY = {
    "parts": [
        {"name": "AHV/IV/EO", "rate": Decimal("0.053"), "ceiling": None},
        {"name": "ALV (unemployment)", "rate": Decimal("0.011"), "ceiling": Decimal("148200")},
    ],
    "source": ["social_security_rates"],
}

# One ESTV result for the pack's case. Other salaries use the same effective rate.
HYPO_TAX = {
    "reference_gross": Decimal("170000"),
    "reference_tax": Decimal("29578"),
    "details": "Federal, cantonal and communal income tax, city of Zurich, single, no church tax",
    "source": ["estv_calculator"],
}

ASSUMPTIONS = [
    "Hypothetical Swiss tax is the ESTV calculator result for CHF 170,000 "
    "(single, city of Zurich, no church tax). Other salaries use the same effective rate.",
    "Hypothetical Swiss social security is the employee share of AHV/IV/EO (5.3%) "
    "and ALV (1.1% up to CHF 148,200). BVG pension is not included.",
    "The same Swiss figures are used for both years.",
]
