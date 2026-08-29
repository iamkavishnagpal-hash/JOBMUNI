import pytest
from app.services.ats_connectors.greenhouse import GreenhouseConnector, clean_html
from app.services.ats_connectors.lever import LeverConnector

def test_clean_html():
    raw = "<p>We are hiring a <strong>Lead BI Engineer</strong>.</p><br><ul><li>Expert SQL</li><li>Snowflake &amp; dbt</li></ul>"
    cleaned = clean_html(raw)
    assert "<p>" not in cleaned
    assert "<strong>" not in cleaned
    assert "Snowflake & dbt" in cleaned
    assert "Expert SQL" in cleaned

def test_greenhouse_parse_payload():
    connector = GreenhouseConnector()
    mock_item = {
        "id": 123456,
        "title": "Staff Data Engineer - BI Platform",
        "updated_at": "2026-08-25T12:00:00Z",
        "absolute_url": "https://boards.greenhouse.io/snowflake/jobs/123456",
        "location": {"name": "San Mateo, CA (Remote)"},
        "content": "<p>Looking for an engineer with SQL, Python, Snowflake, and dbt experience. Compensation: $180,000 - $230,000.</p>",
        "departments": [{"name": "Data & Analytics"}],
        "offices": [{"name": "San Mateo Headquarters"}],
    }

    job = connector.parse_job_payload("Snowflake", mock_item)
    assert job is not None
    assert job.company_name == "Snowflake"
    assert job.title == "Staff Data Engineer - BI Platform"
    assert job.source == "GREENHOUSE"
    assert job.source_job_id == "123456"
    assert job.salary_min == 180000
    assert job.salary_max == 230000
    assert "SQL" in job.required_skills
    assert "Snowflake" in job.required_skills
    assert job.seniority_level == "STAFF"
    assert job.remote_status == "REMOTE"

def test_lever_parse_payload():
    connector = LeverConnector()
    mock_item = {
        "id": "lever_abc_789",
        "text": "Senior Business Intelligence Engineer",
        "createdAt": 1724500000000,
        "hostedUrl": "https://jobs.lever.co/netflix/lever_abc_789",
        "categories": {
            "location": "Los Gatos, CA",
            "commitment": "Full-time",
            "team": "Data Science & Engineering",
        },
        "workplaceType": "hybrid",
        "descriptionPlain": "We need a Senior BI Engineer proficient in SQL, Tableau, AWS, and BigQuery. Salary: $160k - $210k.",
        "lists": [
            {
                "text": "What you will do",
                "content": "Architect data pipelines and executive dashboards in Tableau."
            }
        ]
    }

    job = connector.parse_job_payload("Netflix", mock_item)
    assert job is not None
    assert job.company_name == "Netflix"
    assert job.title == "Senior Business Intelligence Engineer"
    assert job.source == "LEVER"
    assert job.source_job_id == "lever_abc_789"
    assert job.salary_min == 160000
    assert job.salary_max == 210000
    assert "SQL" in job.required_skills
    assert "Tableau" in job.required_skills
    assert job.seniority_level == "SENIOR"
    assert job.remote_status == "HYBRID"
