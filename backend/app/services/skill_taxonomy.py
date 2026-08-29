import re
from typing import Dict, List, Optional, Tuple, Set

# Explicit, deterministic, and auditable Senior BI / Analytics Skill Taxonomy
CANONICAL_SKILLS: Set[str] = {
    "SQL",
    "Snowflake",
    "dbt",
    "Looker",
    "Python",
    "Power BI",
    "Databricks",
    "Azure",
    "AWS",
    "BigQuery",
    "Tableau",
    "Data Modeling",
}

# Explicit aliases mapping raw requirement mentions to canonical skills
SKILL_ALIASES: Dict[str, str] = {
    # SQL
    "sql": "SQL",
    "ansi sql": "SQL",
    "complex sql": "SQL",
    "t-sql": "SQL",
    "tsql": "SQL",
    "pl/sql": "SQL",
    "plsql": "SQL",
    "postgresql": "SQL",
    "postgres": "SQL",
    "mysql": "SQL",
    
    # Snowflake
    "snowflake": "Snowflake",
    "snowflake data warehouse": "Snowflake",
    "snowflake dw": "Snowflake",
    "snowflake cloud": "Snowflake",
    
    # dbt
    "dbt": "dbt",
    "dbt core": "dbt",
    "dbt cloud": "dbt",
    "data build tool": "dbt",
    
    # Looker
    "looker": "Looker",
    "lookml": "Looker",
    "looker bi": "Looker",
    "google looker": "Looker",
    
    # Python
    "python": "Python",
    "python3": "Python",
    "pyspark": "Python",
    "pandas": "Python",
    
    # Power BI
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "power-bi": "Power BI",
    "microsoft power bi": "Power BI",
    "dax": "Power BI",
    
    # Databricks
    "databricks": "Databricks",
    "databricks lakehouse": "Databricks",
    "delta lake": "Databricks",
    "apache spark": "Databricks",
    "spark": "Databricks",
    
    # Azure
    "azure": "Azure",
    "microsoft azure": "Azure",
    "azure data factory": "Azure",
    "adf": "Azure",
    "azure synapse": "Azure",
    "synapse": "Azure",
    
    # AWS
    "aws": "AWS",
    "amazon web services": "AWS",
    "redshift": "AWS",
    "amazon redshift": "AWS",
    "athena": "AWS",
    "aws glue": "AWS",
    
    # BigQuery
    "bigquery": "BigQuery",
    "google bigquery": "BigQuery",
    "gcp bigquery": "BigQuery",
    
    # Tableau
    "tableau": "Tableau",
    "tableau server": "Tableau",
    "tableau desktop": "Tableau",
    
    # Data Modeling
    "data modeling": "Data Modeling",
    "dimensional modeling": "Data Modeling",
    "star schema": "Data Modeling",
    "kimball": "Data Modeling",
    "data marts": "Data Modeling",
}

def normalize_skill(raw_skill: str) -> Tuple[str, bool]:
    """
    Deterministically normalize a skill requirement to the canonical taxonomy.
    Returns (normalized_skill_name, is_canonical_match).
    If no taxonomy mapping exists, returns (cleaned_raw_skill, False).
    """
    cleaned = raw_skill.strip()
    lower = cleaned.lower()
    
    # Direct alias match
    if lower in SKILL_ALIASES:
        return SKILL_ALIASES[lower], True
        
    # Check if exact canonical casing
    if cleaned in CANONICAL_SKILLS:
        return cleaned, True
        
    # Substring boundary check for compound phrases (e.g. "Hands-on experience with Microsoft Power BI")
    for alias, canonical in SKILL_ALIASES.items():
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, lower):
            return canonical, True

    return cleaned, False
