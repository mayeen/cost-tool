from datetime import date
from decimal import Decimal

from django.test import SimpleTestCase
from django.urls import reverse

from .calculations.immigration import build_cost_rows, check_eligibility, pick_visa
from .calculations.inputs import EstimatorInput
from .rules.immigration import SSW_VISA, get_route


def make_input(**changes):
    """The brief's test case. Pass keyword arguments to change single values."""
    values = {
        "home_country": "CH",
        "host_country": "GB",
        "nationality": "swiss",
        "start_date": date(2026, 4, 6),
        "end_date": date(2028, 4, 5),
        "years_with_employer": 3,
        "base_salary_home": Decimal("150000"),
        "exchange_rate": Decimal("1.10"),


    }
    values.update(changes)
    return EstimatorInput(**values)



FORM_DATA = {
    "home_country": "CH",
    "host_country": "GB",
    "nationality": "swiss",
    "start_date": "2026-04-06",
    "end_date": "2028-04-05",
    "years_with_employer": "3",
    "base_salary_home_country": "150000",
    "exchange_rate": "1.10",
    "submit": "1",
    "bonus_home_country": "20000",
    "housing_monthly_host": "3000",
    "relocation_allowance_home": "5000",
    "moving_costs_host": "6000",
    "temporary_housing_host": "4000",
}


class EligibilityTests(SimpleTestCase):
    def test_brief_case_is_eligible(self):
        check = check_eligibility(SSW_VISA, make_input())
        self.assertTrue(check["eligible"])
        self.assertTrue(check["is_high_earner"])

    def test_salary_below_minimum_fails(self):
        # CHF 50,000 / 1.10 = about £45,455, under £52,500
        check = check_eligibility(SSW_VISA, make_input(base_salary_home=Decimal("50000")))
        self.assertFalse(check["salary_ok"])
        self.assertFalse(check["eligible"])

# CHF 66,000 / 1.10 = £60,000: above £52,500 but under £73,900
    def test_under_12_months_fails_below_high_earner(self):

        check = check_eligibility(
            SSW_VISA,
            make_input(base_salary_home=Decimal("66000"), years_with_employer=0),
        )
        self.assertTrue(check["salary_ok"])
        self.assertFalse(check["time_ok"])
        self.assertFalse(check["eligible"])

    def test_high_earner_skips_12_month_rule(self):
        check = check_eligibility(SSW_VISA, make_input(years_with_employer=0))
        self.assertTrue(check["eligible"])


class CostTests(SimpleTestCase):
    def test_brief_case_costs(self):
        inp = make_input()
        route = get_route("CH", "GB", "swiss")
        visa, _ = pick_visa(route, inp)
        rows = build_cost_rows(route, visa, inp)
        amounts = {row["name"]: row["amount"] for row in rows}

        # visa is 24 months + 14 days -> 2.5 years x £1,035
        self.assertEqual(amounts["Immigration Health Surcharge"], Decimal("2587.50"))
        self.assertEqual(sum(amounts.values()), Decimal("8273.50"))


class PageTests(SimpleTestCase):
    def test_end_before_start_shows_readable_error(self):
        data = {**FORM_DATA, "end_date": "2026-01-01"}
        response = self.client.get(reverse("cost"), data)
        self.assertContains(response, "The assignment end date must be after the start date.")

    def test_immigration_tab_shows_visa(self):
        response = self.client.get(reverse("immigration"), FORM_DATA)
        self.assertContains(response, "Work visa needed")
        self.assertContains(response, "8,273.50")
