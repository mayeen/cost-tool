from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class EstimatorInput:
    home_country: str
    host_country: str
    nationality: str
    start_date: date
    end_date: date
    years_with_employer: int
    base_salary_home: Decimal
    bonus_home: Decimal
    housing_monthly_host: Decimal
    relocation_allowance_home: Decimal
    moving_costs_host: Decimal
    temporary_housing_host: Decimal
    exchange_rate: Decimal

    @classmethod
    def from_cleaned_data(cls, data):
        return cls(
            home_country=data["home_country"],
            host_country=data["host_country"],
            nationality=data["nationality"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            years_with_employer=data["years_with_employer"],
            base_salary_home=data["base_salary_home_country"],
            bonus_home=data["bonus_home_country"],
            housing_monthly_host=data["housing_monthly_host"],
            relocation_allowance_home=data["relocation_allowance_home"],
            moving_costs_host=data["moving_costs_host"],
            temporary_housing_host=data["temporary_housing_host"],
            exchange_rate=data["exchange_rate"],
        )


    @property
    def months_with_employer(self):
        return self.years_with_employer * 12
#Salary + bonus in home currency.
    @property
    def gross_home(self):
        return self.base_salary_home + self.bonus_home
    
#Home currency -> host currency
    def home_currency_to_host_currency(self, amount):
        return amount / self.exchange_rate

