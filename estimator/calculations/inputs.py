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
            exchange_rate=data["exchange_rate"],
        )

    @property
    def base_salary_gbp(self):
        return self.base_salary_home / self.exchange_rate

    @property
    def months_with_employer(self):
        return self.years_with_employer * 12
