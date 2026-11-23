from decimal import Decimal
from ..rules import switzerland as ch
from ..rules import uk


def add_totals(sections):
    years = len(sections[0]["rows"][0]["amounts"])
    grand = [Decimal("0")] * years

    for section in sections:
        sign = -1 if section.get("subtract") else 1
        subtotal = [Decimal("0")] * years

        for row in section["rows"]:
            row["total"] = sum(a for a in row["amounts"] if a is not None)
            for i, amount in enumerate(row["amounts"]):
                if amount is not None:
                    subtotal[i] += amount

        section["subtotal"] = subtotal
        section["subtotal_total"] = sum(subtotal)
        for i in range(years):
            grand[i] += sign * subtotal[i]

    home = sections[0]["subtotal"]
    return {
        "amounts": grand,
        "total": sum(grand),
        "multiples": [g / h for g, h in zip(grand, home)],
        "multiple_total": sum(grand) / sum(home),
    }
def swiss_social_security(gross_home):
    total = Decimal("0")
    for part in ch.SOCIAL_SECURITY["parts"]:
        pay = gross_home
        if part["ceiling"] is not None:
            pay = min(pay, part["ceiling"])
        total += pay * part["rate"]
    return total

def swiss_hypo_tax(gross_home):
    """ESTV result scaled by the same effective rate, in home currency."""
    tax = ch.HYPO_TAX
    return gross_home * tax["reference_tax"] / tax["reference_gross"]

def benefit_amount(inp, benefit, year):
    """One benefit for one assignment year, in host currency. None = not paid that year."""
    if benefit["first_year_only"] and year > 1:
        return None
    amount = getattr(inp, benefit["input"]) * benefit["times_per_year"]
    if benefit["currency"] == "home":
        amount = inp.home_currency_to_host_currency(amount)
    return amount


def year_figures(inp, year):
    home_pay = inp.home_currency_to_host_currency(inp.gross_home)
    swiss_tax = inp.home_currency_to_host_currency(swiss_hypo_tax(inp.gross_home))
    swiss_ss = inp.home_currency_to_host_currency(swiss_social_security(inp.gross_home))
    net_home_pay = home_pay - swiss_tax - swiss_ss

    benefits = [(b, benefit_amount(inp, b, year)) for b in uk.BENEFITS]
    taxable_benefits = sum(
        (amount for b, amount in benefits
         if amount is not None and b["tag"] != uk.NOT_TAXABLE),
        Decimal("0"),
    )
    return {
        "home_pay": home_pay,
        "swiss_tax": swiss_tax,
        "swiss_ss": swiss_ss,
        "net_home_pay": net_home_pay,
        "benefits": benefits,
        "taxable_benefits": taxable_benefits,
        "income": net_home_pay + taxable_benefits, 
    }
#UK income tax on one year's income 
def uk_tax(income):
    rules = uk.INCOME_TAX
    over = max(Decimal("0"), income - rules["taper_threshold"])
    allowance = max(Decimal("0"), rules["personal_allowance"] - over * rules["taper_rate"])
    taxable = max(Decimal("0"), income - allowance)

    tax = Decimal("0")
    lower = Decimal("0")
    for band in rules["bands"]:
        upper = band["up_to"]
        if upper is None or taxable < upper:
            tax += (taxable - lower) * band["rate"]
            break
        tax += (upper - lower) * band["rate"]
        lower = upper
    return tax

#Solve T = UKTax(I + T)
def gross_up(income):
    rules = uk.GROSS_UP
    tax = Decimal("0")
    rounds = []
    for number in range(1, rules["max_rounds"] + 1):
        new_tax = uk_tax(income + tax)
        rounds.append({"number": number, "income": income + tax, "tax": new_tax})
        if abs(new_tax - tax) < rules["tolerance"]:
            return new_tax, rounds
        tax = new_tax
    raise ValueError("The gross-up did not settle. Check the tax rates.")


def year_result(inp, year):
    """One year: figures before the gross-up, the UK tax, and the total employer cost."""
    figures = year_figures(inp, year)
    tax, rounds = gross_up(figures["income"])
    not_taxable = sum(
        (amount for b, amount in figures["benefits"]
         if amount is not None and b["tag"] == uk.NOT_TAXABLE),
        Decimal("0"),
    )
    figures["uk_tax"] = tax
    figures["rounds"] = rounds
    figures["total_cost"] = (
        figures["income"] + tax + not_taxable + uk.SOCIAL_SECURITY["uk_employer_ni"]
    )
    return figures
