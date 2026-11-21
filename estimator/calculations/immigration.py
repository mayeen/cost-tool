from ..rules.immigration import SOURCES


def money(amount):
    return f"£{amount:,.0f}"


def check_eligibility(visa, inp):
    """Check visa thresholds against the inputs."""
    t = visa["thresholds"]
    salary = inp.base_salary_gbp

    salary_ok = salary >= t["min_salary_gbp"]

    high_earner = t.get("high_earner_gbp")
    is_high_earner = high_earner is not None and salary >= high_earner

    min_months = t.get("min_months_with_employer", 0)
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
    t = visa["thresholds"]

    if check["eligible"]:
        title = f"Work visa needed: {visa['name']}"
    else:
        title = f"Not eligible for the {visa['name']}"

    checks = [{
        "label": "Salary check",
        "text": (
            f"{'Met' if check['salary_ok'] else 'Not met'}. "
            f"{money(inp.base_salary_gbp)} a year. "
            f"Needs at least {money(t['min_salary_gbp'])} or the job's going rate, "
            "whichever is higher."
        ),
    }]

    if "min_months_with_employer" in t:
        high = t.get("high_earner_gbp")
        if check["is_high_earner"]:
            rule = f"Not required at {money(high)} or more."
        elif high:
            rule = (f"Needs at least {t['min_months_with_employer']} months "
                    f"when earning under {money(high)}.")
        else:
            rule = f"Needs at least {t['min_months_with_employer']} months."

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
        "sources": [SOURCES[k] for k in t["source"]],
    }
