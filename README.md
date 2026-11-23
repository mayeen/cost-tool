# Cost-tool

A Django tool that estimates what it costs an employer to send an employee abroad,
and what the employee needs to work there legally.

- **Tab 1, Cost:** tax-equalised employer cost per year and for the whole assignment,
  with the UK tax grossed up by iteration (T = UKTax(I + T)).
- **Tab 2, Immigration:** work permit, business visit, passport, employer duties,
  time and cost.

Covered route: Switzerland (Zurich) -> United Kingdom (London), Swiss national.
Every rule on the page links to its official source.

## Run it

Needs Python 3.12 or newer.

```bash
git clone https://github.com/mayeen/cost-tool
cd cost-tool
python3 -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt
cp .env.example .env
```

Create a secret key and paste it after `DJANGO_SECRET_KEY=` in `.env`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Then:

```bash
python manage.py migrate           # only silences a warning, the tool stores no data
python manage.py runserver
```

Open http://127.0.0.1:8000/

### Test case in one click

```
http://127.0.0.1:8000/?home_country=CH&host_country=GB&nationality=swiss&start_date=2026-04-06&end_date=2028-04-05&years_with_employer=3&base_salary_home_country=150000&bonus_home_country=20000&housing_monthly_host=3000&relocation_allowance_home=5000&moving_costs_host=6000&temporary_housing_host=4000&exchange_rate=1.10&submit=1
```

Expected result:

|                      | Year 1       | Year 2       | Total        |
| -------------------- | ------------ | ------------ | ------------ |
| Total employer cost  | £276,421.65 | £254,884.46 | £531,306.11 |
| Multiple of home pay | 1.79x        | 1.65x        | 1.72x        |

## Run the tests

```bash
python manage.py test
```

13 tests: visa eligibility, immigration fees, UK tax bands and taper, the gross-up
totals for the test case, every rule source exists, and both pages (including a
readable error for bad input).

## How it is built

```
estimator/
  rules/            data only: rates, thresholds, fees, tags, assumptions, source links
    uk.py           UK income tax 2026/27, gross-up settings, benefit tags, social security
    switzerland.py  hypothetical Swiss tax (ESTV) and social security (AHV/IV/EO, ALV)
    immigration.py  visa rules, fees, timeline
  calculations/     pure Python, no Django: takes inputs + rules, returns numbers
    inputs.py       EstimatorInput dataclass built from the form
    cost.py         Swiss deductions, benefits, UK tax, gross-up, totals
    immigration.py  eligibility, visa choice, fees
  views.py          turns results into the page data
  forms.py          one form shared by both tabs, validation
  tests.py
```

Rules are kept apart from logic so a rate change (every April) is a one-line data
edit, and each rule carries its source next to the number.

### The cost calculation

1. Home pay H = (salary + bonus) / exchange rate.
2. Hypothetical deductions D = Swiss income tax + Swiss social security
   (what the employee would have paid at home).
3. Net home pay N = H - D.
4. I = N + taxable benefits (moving costs are exempt, so not included).
5. The employer pays the UK tax T, and T is itself taxable, so solve
   T = UKTax(I + T): start with T = 0, repeat, stop when T changes by less than £0.001.
6. Total employer cost = H + benefits + T + UK employer NI - D.
7. Multiple = total cost / home pay.

All money uses `Decimal`. Values are rounded only for display.

## Assumptions

Listed on each tab under "Assumptions". The main ones:

- UK 2026/27 rates for both years; the employee is UK tax resident in both years.
- Hypothetical Swiss tax is the ESTV calculator result for CHF 170,000 (city of
  Zurich, single, no church tax); other salaries use the same effective rate.
- Swiss social security applies (certificate of coverage), so no UK National
  Insurance. Swiss employer contributions are not included.
- Moving costs are within the £8,000 relocation exemption; temporary housing is
  treated as a taxable benefit.
- Each started assignment year is costed as a full tax year.

## Use of AI tools

I used Claude (Anthropic) during this assignment:

- **Research:** finding and checking official sources (GOV.UK, HMRC manuals,
  BSV, ESTV), tax rates, visa fees and rules. I opened each source myself and
  checked the figures used in the tool.
- **Learning Django:** explanations of forms, views, templates and tests, as I am
  new to Django.
- Dummy Data Generation: Dummy data has been generated in between the implementation and the
  object has been made using AI, the structure was given by myself.
- HTML and CSS has been modified and bug fixed with the help of AI.
- Testcases has been researched with the help of AI. Code has been implemented by me.
- The README.md file has also been generated using AI
- 

The final figures were checked by hand against the brief and by the tests.

## Demo

Loom: [drive.google.com/file/d/1GxMrEYfrYg0WWJwecjtzbxzqGJivmCvB/view?usp=drive_link](https://drive.google.com/file/d/1GxMrEYfrYg0WWJwecjtzbxzqGJivmCvB/view?usp=drive_link)<loom-link></loom>
