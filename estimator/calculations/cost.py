from decimal import Decimal

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
