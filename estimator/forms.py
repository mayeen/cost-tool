from django import forms

HOME_COUNTRY = [
    ("", "Select"),
    ("CH", "Switzerland"),
]
HOST_COUNTRY = [
    ("", "Select"),
    ("GB", "United Kingdom"),
]

NATIONALITY = [
    ("", "Select"),
    ("swiss", "Swiss"),
]


class EstimatorForm(forms.Form):
    home_country = forms.ChoiceField(
        label="Home country",
        choices=HOME_COUNTRY,
    )
    host_country = forms.ChoiceField(
        label="Host country",
        choices=HOST_COUNTRY,
    )
    nationality = forms.ChoiceField(
        label="Nationality",
        choices=NATIONALITY,
    )
    start_date = forms.DateField(
        label="Assignment Start",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    end_date = forms.DateField(
        label="Assignment End",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    years_with_employer = forms.IntegerField(
        label="Years with employer",
        min_value=0,
        max_value=60,
    )
    base_salary_home_country = forms.DecimalField(
        label="Annual base salary",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        help_text="home country currency: Base salary only",
        widget=forms.NumberInput(attrs={"data-currency": "home"}),

    )
    bonus_home_country = forms.DecimalField(
        label="Annual bonus",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"data-currency": "home"}),

    )
    housing_monthly_host = forms.DecimalField(
        label="Housing per month",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"data-currency": "host"}),

    )
    relocation_allowance_home = forms.DecimalField(
        label="Relocation allowance",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"data-currency": "home"}),
    )
    moving_costs_host = forms.DecimalField(
        label="Moving costs",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"data-currency": "host"}),

    )
    temporary_housing_host = forms.DecimalField(
        label="Temporary housing",
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"data-currency": "host"}),
    )

    exchange_rate = forms.DecimalField(
        label="Exchange rate",
        min_value=0.01,
        max_digits=8,
        decimal_places=4,
         help_text=(
            "How many units of home currency equal 1 unit of host currency. "
            "Example: if the home currency is CHF and the host currency is GBP, "
            "and £1 = CHF 1.10, enter 1.10."
        ),
    )

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        if start and end and end <= start:
            raise forms.ValidationError("The assignment end date must be after the start date.")
        return cleaned


