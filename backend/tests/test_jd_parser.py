import pytest
from app.services.jd_parser import JDParser

def test_extract_skills():
    sample_text = """
    We need an expert in SQL, Snowflake, and dbt. 
    Familiarity with Python, Looker, BigQuery, and Tableau is highly desired.
    Experience with Azure and AWS cloud environments.
    """
    skills = JDParser.extract_skills(sample_text)
    assert "SQL" in skills
    assert "Snowflake" in skills
    assert "dbt" in skills
    assert "Python" in skills
    assert "Looker" in skills
    assert "BigQuery" in skills
    assert "Tableau" in skills
    assert "Azure" in skills
    assert "AWS" in skills

def test_detect_seniority():
    assert JDParser.detect_seniority("Lead BI Engineer", "We need a leader") == "LEAD"
    assert JDParser.detect_seniority("Staff Data Architect", "") == "STAFF"
    assert JDParser.detect_seniority("Principal Analytics Consultant", "") == "PRINCIPAL"
    assert JDParser.detect_seniority("Director of Business Intelligence", "") == "DIRECTOR"
    assert JDParser.detect_seniority("Sr. Data Analyst", "") == "SENIOR"
    assert JDParser.detect_seniority("Junior BI Developer", "") == "ENTRY"

def test_detect_remote_status():
    assert JDParser.detect_remote_status("San Francisco, CA (Remote)", "100% remote position") == "REMOTE"
    assert JDParser.detect_remote_status("Seattle, WA", "Hybrid role, 2 days in office") == "HYBRID"
    assert JDParser.detect_remote_status("Austin, TX", "Must be on-site 5 days a week") == "ON_SITE"

def test_extract_compensation():
    min_sal, max_sal, curr = JDParser.extract_compensation("Base salary: $150,000 - $195,000 / year")
    assert min_sal == 150000
    assert max_sal == 195000
    assert curr == "USD"

    min_sal_k, max_sal_k, _ = JDParser.extract_compensation("Salary range: $140k to $180k")
    assert min_sal_k == 140000
    assert max_sal_k == 180000

    single_sal, _, _ = JDParser.extract_compensation("Annual compensation: $165,000")
    assert single_sal == 165000

def test_full_parse_partitioning():
    jd_text = """
    About the Role:
    Building the next generation data platform.

    Requirements:
    - 5+ years of SQL and Snowflake experience
    - Strong knowledge of dbt and data modeling

    Nice to have:
    - Experience with Looker and Python
    - Databricks knowledge
    """
    parsed = JDParser.parse("Lead Analytics Engineer", jd_text, location_hint="Remote, US")
    assert "SQL" in parsed.required_skills
    assert "Snowflake" in parsed.required_skills
    assert "dbt" in parsed.required_skills
    assert "Looker" in parsed.preferred_skills
    assert "Python" in parsed.preferred_skills
    assert parsed.seniority_level == "LEAD"
    assert parsed.remote_status == "REMOTE"
