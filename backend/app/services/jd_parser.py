import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field

@dataclass
class ParsedJD:
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    all_skills: List[str] = field(default_factory=list)
    seniority_level: str = "SENIOR"
    remote_status: str = "REMOTE"
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    domain_category: str = "BI_ANALYTICS"

# Core extensible skill taxonomy
# Canonical Name -> Regex patterns / aliases
SKILL_TAXONOMY: Dict[str, List[str]] = {
    "SQL": [r"\bsql\b", r"\bstructured query language\b", r"\bpl/sql\b", r"\btsql\b", r"\bpostgre(?:sql)?\b", r"\bmysql\b"],
    "Python": [r"\bpython\b", r"\bpandas\b", r"\bnumpy\b", r"\bpyspark\b"],
    "Power BI": [r"\bpower\s?bi\b", r"\bdax\b", r"\bpower\s?query\b"],
    "Azure": [r"\bazure\b", r"\bmicrosoft cloud\b", r"\bazure synaps\w*\b", r"\bazure data factory\b"],
    "Snowflake": [r"\bsnowflake\b", r"\bsnowpark\b", r"\bsnowsql\b"],
    "dbt": [r"\bdbt\b", r"\bdata build tool\b"],
    "Looker": [r"\blooker\b", r"\blookml\b", r"\blooker studio\b"],
    "BigQuery": [r"\bbigquery\b", r"\bgcp bigquery\b", r"\bbq\b"],
    "Tableau": [r"\btableau\b", r"\btableau server\b", r"\btableau prep\b"],
    "Databricks": [r"\bdatabricks\b", r"\bdelta lake\b", r"\bspark\b"],
    "AWS": [r"\baws\b", r"\bamazon web services\b", r"\bredshift\b", r"\bs3\b", r"\bglue\b", r"\bathena\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle cloud\b", r"\bgoogle cloud platform\b"],
}

# Seniority detection patterns
SENIORITY_PATTERNS = [
    (r"\b(?:vp|vice president)\b", "VP"),
    (r"\b(?:director|head of)\b", "DIRECTOR"),
    (r"\b(?:principal|distinguished)\b", "PRINCIPAL"),
    (r"\b(?:staff)\b", "STAFF"),
    (r"\b(?:lead|team lead|tech lead)\b", "LEAD"),
    (r"\b(?:senior|sr\.?|sr\b|iii|iv)\b", "SENIOR"),
    (r"\b(?:junior|jr\.?|entry|associate|i\b|ii\b)\b", "ENTRY"),
    (r"\b(?:intern|internship)\b", "INTERN"),
]

# Remote / Workplace classification
REMOTE_PATTERNS = [
    (r"\b(?:fully remote|100% remote|remote\s?-\s?first|work from home|wfh|anywhere)\b", "REMOTE"),
    (r"\b(?:hybrid|flexible|2-3 days in office|partial remote)\b", "HYBRID"),
    (r"\b(?:on-site|onsite|in-office|office based|must be local)\b", "ON_SITE"),
]

class JDParser:
    """
    Deterministic Job Description parser for extracting structured requirements,
    skills taxonomy, seniority level, and compensation signals without LLM hallucination.
    """

    @classmethod
    def extract_skills(cls, text: str) -> List[str]:
        """Extract canonical skill tags matching the extensible taxonomy."""
        if not text:
            return []
        
        found_skills = []
        lower_text = text.lower()
        
        for canonical_name, patterns in SKILL_TAXONOMY.items():
            for pat in patterns:
                if re.search(pat, lower_text, re.IGNORECASE):
                    found_skills.append(canonical_name)
                    break
                    
        return found_skills

    @classmethod
    def partition_sections(cls, text: str) -> Tuple[str, str, str]:
        """
        Partition JD into general description, required section, and preferred section.
        """
        if not text:
            return "", "", ""
        
        required_patterns = [
            r"(?:requirements|qualifications|must have|what you(?:'ll)? bring|minimum qualifications|what you need|who you are)",
        ]
        preferred_patterns = [
            r"(?:preferred|nice to have|bonus|pluses|good to have|desired|bonus points)",
        ]
        
        lines = text.split("\n")
        current_section = "general"
        general_lines, req_lines, pref_lines = [], [], []
        
        for line in lines:
            stripped = line.strip()
            lower_line = stripped.lower()
            
            # Check section header transition
            is_header = len(stripped) < 80 and (stripped.endswith(":") or stripped.isupper() or len(stripped.split()) < 6)
            
            if is_header:
                if any(re.search(pat, lower_line) for pat in preferred_patterns):
                    current_section = "preferred"
                    continue
                elif any(re.search(pat, lower_line) for pat in required_patterns):
                    current_section = "required"
                    continue
            
            if current_section == "required":
                req_lines.append(line)
            elif current_section == "preferred":
                pref_lines.append(line)
            else:
                general_lines.append(line)
                
        return "\n".join(general_lines), "\n".join(req_lines), "\n".join(pref_lines)

    @classmethod
    def detect_seniority(cls, title: str, description: str) -> str:
        """Detect seniority level from title first, falling back to description."""
        full_text = f"{title}\n{description}".lower()
        
        # Priority check on title
        title_lower = title.lower()
        for pat, level in SENIORITY_PATTERNS:
            if re.search(pat, title_lower):
                return level
                
        # Secondary check on full description
        for pat, level in SENIORITY_PATTERNS:
            if re.search(pat, full_text):
                return level
                
        return "SENIOR"  # Default target domain assumption

    @classmethod
    def detect_remote_status(cls, location_text: str, description: str) -> str:
        """Classify workplace policy as REMOTE, HYBRID, or ON_SITE."""
        combined = f"{location_text or ''} {description}".lower()
        
        for pat, status in REMOTE_PATTERNS:
            if re.search(pat, combined):
                return status
                
        if "remote" in (location_text or "").lower():
            return "REMOTE"
            
        return "REMOTE"  # Default assumption for modern senior tech roles

    @classmethod
    def extract_compensation(cls, text: str) -> Tuple[Optional[int], Optional[int], str]:
        """
        Extract salary ranges (e.g. '$130,000 - $180,000' or '$140k - $175k').
        """
        if not text:
            return None, None, "USD"
            
        # Pattern 1: $140,000 - $180,000 / yr
        range_full_pat = r"\$\s?(\d{2,3}(?:,\d{3})+|\d{5,6})\s*(?:-|to)\s*\$\s?(\d{2,3}(?:,\d{3})+|\d{5,6})"
        match = re.search(range_full_pat, text)
        if match:
            s_min = int(match.group(1).replace(",", ""))
            s_max = int(match.group(2).replace(",", ""))
            if 30000 <= s_min <= 1000000 and s_min <= s_max:
                return s_min, s_max, "USD"
                
        # Pattern 2: $140k - $180k
        range_k_pat = r"\$\s?(\d{2,3})\s*k\s*(?:-|to)\s*\$\s?(\d{2,3})\s*k"
        match_k = re.search(range_k_pat, text, re.IGNORECASE)
        if match_k:
            s_min = int(match_k.group(1)) * 1000
            s_max = int(match_k.group(2)) * 1000
            if 30000 <= s_min <= 1000000 and s_min <= s_max:
                return s_min, s_max, "USD"

        # Pattern 3: Single figure $150,000 / year
        single_pat = r"\$\s?(\d{2,3}(?:,\d{3})+|\d{5,6})"
        match_s = re.search(single_pat, text)
        if match_s:
            val = int(match_s.group(1).replace(",", ""))
            if 30000 <= val <= 1000000:
                return val, val, "USD"

        return None, None, "USD"

    @classmethod
    def parse(cls, title: str, raw_description: str, location_hint: Optional[str] = None) -> ParsedJD:
        """
        Parse raw job description into structured ParsedJD object.
        """
        raw_description = raw_description or ""
        gen_sec, req_sec, pref_sec = cls.partition_sections(raw_description)
        
        all_skills = cls.extract_skills(raw_description)
        req_skills = cls.extract_skills(req_sec)
        pref_skills = cls.extract_skills(pref_sec)
        
        # If partition didn't find specific req section, default to all found skills
        if not req_skills and all_skills:
            req_skills = all_skills
            
        seniority = cls.detect_seniority(title, raw_description)
        remote = cls.detect_remote_status(location_hint or "", raw_description)
        sal_min, sal_max, currency = cls.extract_compensation(raw_description)
        
        return ParsedJD(
            required_skills=req_skills,
            preferred_skills=pref_skills,
            all_skills=all_skills,
            seniority_level=seniority,
            remote_status=remote,
            location=location_hint,
            salary_min=sal_min,
            salary_max=sal_max,
            salary_currency=currency,
            domain_category="BI_ANALYTICS",
        )
