from decimal import Decimal

from ..rules.immigration import SOURCES
from datetime import timedelta
import math

def format_money_string(amount):
    return f"£{amount:,.0f}"

#Check visa thresholds against the inputs.
def check_eligibility(visa, inp):

    visa_obj = visa["thresholds"]
    salary = inp.home_currency_to_host_currency(inp.base_salary_home)

    salary_ok = salary >= visa_obj["min_salary_gbp"]

    high_earner = visa_obj.get("high_earner_gbp")
    is_high_earner = high_earner is not None and salary >= high_earner

    min_months = visa_obj.get("min_months_with_employer", 0)
    time_ok = is_high_earner or inp.months_with_employer >= min_months

    return {
        "eligible": salary_ok and time_ok,
        "salary_ok": salary_ok,
        "time_ok": time_ok,
        "is_high_earner": is_high_earner,
    }


def pick_visa(route, inp):
    """First eligiblity check that passes"""
    for visa in route["visas"]:
        check = check_eligibility(visa, inp)
        if check["eligible"]:
            return visa, check

    first = route["visas"][0]
    return first, check_eligibility(first, inp)


def build_verdict(visa, check, inp):
    visa_obj = visa["thresholds"]

    if check["eligible"]:
        title = f"Work visa needed: {visa['name']}"
    else:
        title = f"Not eligible for the {visa['name']}"

    checks = [{
        "label": "Salary check",
        "text": (
            f"{'Met' if check['salary_ok'] else 'Not met'}. "
            f"{format_money_string(inp.home_currency_to_host_currency(inp.base_salary_home))} a year. "
            f"Needs at least {format_money_string(visa_obj['min_salary_gbp'])} or the job's going rate, "
            "whichever is higher."
        ),
    }]
    if "min_months_with_employer" in visa_obj:
        high = visa_obj.get("high_earner_gbp")
        if check["is_high_earner"]:
            rule = f"Not required at {format_money_string(high)} or more."
        elif high:
            rule = (f"Needs at least {visa_obj['min_months_with_employer']} months "
                    f"when earning under {format_money_string(high)}.")
        else:
            rule = f"Needs at least {visa_obj['min_months_with_employer']} months."

        checks.append({
            "label": "Time with employer",
            "text": (
                f"{'Met' if check['time_ok'] else 'Not met'}. "
                f"{inp.years_with_employer} year(s). {rule}"
            ),
        })

    return {
        "title": title,
        "checks": checks,
        "sources": [SOURCES[k] for k in visa_obj["source"]],
    }

#months between two days rounded
def months_between(start, end):
    end = end + timedelta(days=1)
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day > start.day:
        months += 1
    return months

#assignment time + extra days 
def visa_months(visa, inp):
    t = visa["thresholds"]
    visa_end = inp.end_date + timedelta(days=t["visa_extra_days"])
    return min(months_between(inp.start_date, visa_end), t["visa_max_years"] * 12)


def calculate_cost(cost, assignment_months, visa_length_months):
    basis = cost["basis"]
    if basis == "one_off":
        return cost["amount"], "One-off"
    if basis == "visa_length":
        band = cost["band_years"]
        if visa_length_months <= band * 12:
            return cost["up_to_3_years"], f"Visa up to {band} years"
        return cost["over_3_years"], f"Visa over {band} years"
    if basis == "per_year_half_bands":
        years = Decimal(visa_length_months // 12)
        rest = visa_length_months % 12
        if rest > 6:
            years += 1
        elif rest > 0:
            years += Decimal("0.5")
        return cost["per_year"] * years, f"{years} years x {format_money_string(cost['per_year'])}"
    if basis == "first_12_then_6":
        extra_blocks = math.ceil(max(assignment_months - 12, 0) / 6)
        amount = cost["first_12_months"] + extra_blocks * cost["each_extra_6_months"]
        return amount, f"First 12 months + {extra_blocks} x 6 months"

    raise ValueError(f"Unknown cost basis: {basis}")


def build_cost_rows(route, visa, inp):
    assignment_months = months_between(inp.start_date, inp.end_date)
    visa_length_months = visa_months(visa, inp)


    rows = []
    for cost in route["common"]["costs"] + visa["costs"]:
        amount, basis_text = calculate_cost(cost, assignment_months, visa_length_months)
        rows.append({
            "name": cost["name"],
            "basis": basis_text,
            "amount": amount,
            "sources": [SOURCES[k] for k in cost["source"]],
        })
    return rows
