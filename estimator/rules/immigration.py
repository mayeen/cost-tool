"""
Immigration rules data
"""
#todo need to revisit to check the immigration rules  
from datetime import date
from decimal import Decimal

RULES_CHECKED = date(2026, 11, 20)

# Official sources
SOURCES = {
    "ssw_overview": {
        "title": "GOV.UK: Senior or Specialist Worker visa",
        "url": "https://www.gov.uk/senior-specialist-worker-visa",
    },
    "ssw_eligibility": {
        "title": "GOV.UK: Senior or Specialist Worker visa: eligibility",
        "url": "https://www.gov.uk/senior-specialist-worker-visa/eligibility",
    },
    "ssw_costs": {
        "title": "GOV.UK: Senior or Specialist Worker visa: how much it costs",
        "url": "https://www.gov.uk/senior-specialist-worker-visa/how-much-it-costs",
    },
    "ssw_documents": {
        "title": "GOV.UK: Senior or Specialist Worker visa: documents you'll need to apply",
        "url": "https://www.gov.uk/senior-specialist-worker-visa/documents-you-need-to-apply",
    },
    "eu_swiss_visitors": {
        "title": "GOV.UK: Visiting the UK as an EU, EEA or Swiss citizen",
        "url": "https://www.gov.uk/guidance/visiting-the-uk-as-an-eu-eea-or-swiss-citizen",
    },
    "eta_apply": {
        "title": "GOV.UK: Apply for an electronic travel authorisation (ETA)",
        "url": "https://www.gov.uk/eta/apply",
    },
    "eta_can_do": {
        "title": "GOV.UK: What you can and cannot do with an ETA",
        "url": "https://www.gov.uk/eta/what-you-can-cannot-do",
    },
    "visitor_permitted": {
        "title": "Immigration Rules: Appendix Visitor: Permitted Activities (PA 4)",
        "url": "https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-visitor-permitted-activities",
    },
    "sponsor_licence": {
        "title": "GOV.UK: Sponsorship: apply for your licence",
        "url": "https://www.gov.uk/uk-visa-sponsorship-employers/apply-for-your-licence",
    },
    "sponsor_licence_types": {
        "title": "GOV.UK: Sponsorship: types of licence",
        "url": "https://www.gov.uk/uk-visa-sponsorship-employers/types-of-licence",
    },
    "sponsor_cos": {
        "title": "GOV.UK: Sponsorship: certificates of sponsorship",
        "url": "https://www.gov.uk/uk-visa-sponsorship-employers/certificates-of-sponsorship",
    },
    "sponsor_isc": {
        "title": "GOV.UK: Sponsorship: immigration skills charge",
        "url": "https://www.gov.uk/uk-visa-sponsorship-employers/immigration-skills-charge",
    },
    "sponsor_duties": {
        "title": "GOV.UK: Sponsorship: your responsibilities",
        "url": "https://www.gov.uk/uk-visa-sponsorship-employers/your-responsibilities",
    },
    "ihs": {
        "title": "GOV.UK: Healthcare surcharge: how much you pay",
        "url": "https://www.gov.uk/healthcare-immigration-application/how-much-pay",
    },
}


# Visa: Senior or Specialist Worker (Global Business Mobility)
SSW_VISA = {
    "key": "ssw",
    "name": "Senior or Specialist Worker visa (Global Business Mobility)",

    # thresholds for the eligibility check
    "thresholds": {
        "min_salary_gbp": Decimal("52500"),
        "high_earner_gbp": Decimal("73900"),
        "min_months_with_employer": 12,
        "source": ["ssw_eligibility"],
        "visa_extra_days": 14,
        "visa_max_years": 5,
        "visa_length_source": ["ssw_overview"],
    },

    "requirements": [
        #  Work permit
        {
            "section": "work_permit",
            "title": "Senior or Specialist Worker visa",
            "summary": "For moving to an eligible job at the employer's UK branch.",
            "source": ["ssw_overview"],
        },
        {
            "section": "work_permit",
            "title": "Visa length",
            "summary": "The time on the certificate of sponsorship plus 14 days, "
                       "or 5 years, whichever is shorter.",
            "source": ["ssw_overview"],
        },

        #  Passport
        {
            "section": "passport",
            "title": "Needed for the visa application",
            "summary": "The visa application needs a valid passport or other document "
                       "showing identity and nationality.",
            "source": ["ssw_documents"],
        },

        #  Employer duties
        {
            "section": "employer_duty",
            "title": "Hold a Worker sponsor licence",
            "summary": "The Senior or Specialist Worker visa falls under the Worker licence.",
            "source": ["sponsor_licence_types", "sponsor_licence"],
        },
        {
            "section": "employer_duty",
            "title": "Assign a certificate of sponsorship",
            "summary": "The employer must pay the certificate fee for Global Business "
                       "Mobility routes and must not pass it on to the worker.",
            "source": ["sponsor_cos"],
        },
        {
            "section": "employer_duty",
            "title": "Pay the Immigration Skills Charge",
            "summary": "Applies to this visa. The exemption covers EU nationals only, "
                       "so it does not cover a Swiss national.",
            "source": ["sponsor_isc"],
        },
        {
            "section": "employer_duty",
            "title": "Ongoing sponsor duties",
            "summary": "Check right to work, keep records, track attendance and report "
                       "significant business changes within 20 working days.",
            "source": ["sponsor_duties"],
        },
    ],

    "costs": [
        {
            "key": "visa_fee",
            "name": "Visa application (from outside the UK)",
            "basis": "visa_length",
            "band_years": 3,
            "up_to_3_years": Decimal("819"),
            "over_3_years": Decimal("1618"),
            "source": ["ssw_costs"],
        },
        {
            "key": "ihs",
            "name": "Immigration Health Surcharge",
            "basis": "per_year_half_bands",
            "per_year": Decimal("1035"),
            "source": ["ihs"],
        },
        {
            "key": "cos",
            "name": "Certificate of sponsorship",
            "basis": "one_off",
            "amount": Decimal("525"),
            "source": ["sponsor_cos", "sponsor_licence_types"],
        },
        {
            "key": "isc",
            "name": "Immigration Skills Charge (medium or large sponsor)",
            "basis": "first_12_then_6",
            "first_12_months": Decimal("1320"),
            "each_extra_6_months": Decimal("660"),
            "source": ["sponsor_isc"],
        },
        {
            "key": "licence",
            "name": "Sponsor licence (medium or large)",
            "basis": "one_off",
            "amount": Decimal("1682"),
            "only_if_no_licence": True,
            "source": ["sponsor_licence"],
        },
    ],

    "timeline": [
        {
            "name": "Sponsor licence",
            "duration": "Usually under 8 weeks",
            "weeks": 8,
            "only_if_no_licence": True,
            "source": ["sponsor_licence"],
        },
        {
            "name": "Visa decision",
            "duration": "Usually 3 weeks",
            "weeks": 3,
            "source": ["ssw_overview"],
        },
    ],

    # "assumptions": [
    #     "The UK sponsor is medium or large. Small sponsors pay £611 for the licence "
    #     "and £480 + £240 per extra 6 months for the skills charge.",
    #     "The UK host company does not yet hold a sponsor licence, so the licence fee "
    #     "and its waiting time are included.",
    #     "The job is an eligible occupation and the salary meets its going rate.",
    #     "The visa salary check uses base salary only. Bonus is not counted.",
    #     "The Immigration Health Surcharge is charged on the visa length (assignment "
    #     "plus 14 days). A part year of 6 months or less costs half a year.",
    #     "For the Immigration Skills Charge, a part 6-month period counts as a full one.",

    # ],
}


# Route: Switzerland -> UK, Swiss national
CH_TO_GB_SWISS = {
    # true whichever visa is used
    "common": {
        "requirements": [
            #  Work permit
            {
                "section": "work_permit",
                "title": "Work visa needed",
                "summary": "Swiss citizens coming to work in the UK for longer than 6 months "
                           "need a visa.",
                "source": ["eu_swiss_visitors"],
            },

            #  Business visit
            {
                "section": "business_visit",
                "title": "No visa needed, but an ETA is",
                "summary": "Swiss citizens need an electronic travel authorisation (ETA) "
                           "to visit the UK without a visa.",
                "source": ["eu_swiss_visitors"],
            },
            {
                "section": "business_visit",
                "title": "What the visit can include",
                "summary": "Meetings, conferences and seminars; negotiating and signing "
                           "deals and contracts.",
                "source": ["visitor_permitted"],
            },
            {
                "section": "business_visit",
                "title": "No work allowed on the visit",
                "summary": "No paid or unpaid work for a UK company. The job can only "
                           "start once the work visa is granted.",
                "source": ["eta_can_do"],
            },
            {
                "section": "business_visit",
                "title": "ETA cost and validity",
                "summary": "£20. Valid for 2 years or until the passport expires. "
                           "Decision usually within 1 day, at most 3 working days.",
                "source": ["eta_apply"],
            },

            #  Passport
            {
                "section": "passport",
                "title": "Passport required",
                "summary": "A Swiss ID card is accepted only in specific cases, such as EU "
                           "Settlement Scheme status or a frontier worker permit. None apply "
                           "here, so the employee needs a passport.",
                "source": ["eu_swiss_visitors"],
            },
            {
                "section": "passport",
                "title": "Validity",
                "summary": "The passport must be valid for the whole time in the UK.",
                "source": ["eu_swiss_visitors"],
            },
            {
                "section": "passport",
                "title": "ETA linked to the passport",
                "summary": "The ETA is linked to the passport used to apply for it.",
                "source": ["eta_apply"],
            },
        ],

        "costs": [
            {
                "key": "eta",
                "name": "ETA for the business visit",
                "basis": "one_off",
                "amount": Decimal("20"),
                "source": ["eta_apply"],
            },
        ],

        "timeline": [
            {
                "name": "ETA for the business visit",
                "duration": "1 to 3 working days",
                "weeks": 0,
                "parallel": True,
                "source": ["eta_apply"],
            },
        ],

        # "assumptions": [
        #     "The Swiss company stays the employer; the UK subsidiary hosts the employee "
        #     "and runs payroll.",
        #     "The employer pays all immigration costs.",
        # ],
    },

    # candidate visas, each checked separately against its thresholds
    "visas": [
        SSW_VISA,
    ],
}


# Route registry (home country, host country, nationality)
ROUTES = {
    ("CH", "GB", "swiss"): CH_TO_GB_SWISS,
}

def get_route(home, host, nationality):
    return ROUTES.get((home, host, nationality))

