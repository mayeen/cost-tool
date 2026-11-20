from django import forms

HOME_COUNTRY = [
    ("", "— Select —"),
    ("CH", "Switzerland"),
]
HOST_COUNTRY = [
    ("", "— Select —"),
    ("GB", "United Kingdom"),
]

NATIONALITY = [
    ("", "— Select —"),
    ("swiss", "Swiss"),
]


class ImmigrationForm(forms.Form):
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
        help_text="home country currency: Base salary only"
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


