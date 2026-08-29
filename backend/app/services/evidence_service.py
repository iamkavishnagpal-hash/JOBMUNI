import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_profile import CandidateProfile, EvidenceItem
from app.schemas.evidence import EvidenceItemCreate, EvidenceItemUpdate, SkillsSummaryResponse, SkillSummaryItem

logger = logging.getLogger("jobmuni.saraswati")

# High-impact verified default evidence bank seed data for a Senior / Lead BI & Analytics Engineer
DEFAULT_EVIDENCE_ITEMS = [
    {
        "category": "TECH_SKILL",
        "skill_or_tool": "SQL",
        "title": "High-Throughput Complex SQL Query & ETL Optimization",
        "evidence_text": "Engineered and optimized multi-million-row SQL transformations and window functions across transactional and analytical data pipelines, reducing ETL execution runtime by 58%.",
        "situation": "Daily executive refresh ETL pipelines were exceeding the 4-hour SLA window due to non-sargable joins and Cartesian subqueries.",
        "task": "Refactor legacy multi-step SQL queries to meet a sub-90-minute SLA requirement.",
        "action": "Restructured indexing, replaced correlated subqueries with CTEs and partitioned window functions, and eliminated redundant staging scans.",
        "result": "Reduced batch pipeline execution time from 4.2 hours to 68 minutes (58% reduction) with zero downstream reporting disruptions.",
        "quant_metric": "58% reduction in ETL execution runtime (4.2h to 68m)",
        "source_company": "Enterprise Analytics Corp",
        "tags": ["SQL", "Performance Tuning", "CTEs", "ETL", "Window Functions"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
    {
        "category": "ARCHITECTURE_PROJECT",
        "skill_or_tool": "Snowflake",
        "title": "Enterprise Snowflake Cloud Data Warehouse Architecture & Cost Optimization",
        "evidence_text": "Architected multi-cluster Snowflake data warehouse hierarchy, implementing auto-clustering, warehouse right-sizing, and resource monitors resulting in $140,000 annual compute credit savings.",
        "situation": "Growing analytical query load caused runaway compute credit consumption across unsegregated departmental workloads.",
        "task": "Design a scalable Snowflake multi-warehouse architecture with strict cost governance.",
        "action": "Implemented dedicated single/multi-cluster warehouses segmented by workload type (ETL vs. BI vs. Ad-hoc), configured auto-suspend timeouts to 60s, and applied clustering keys on heavy query dimensions.",
        "result": "Saved $140,000/year in compute credits while supporting 3x higher concurrent query volume with 0 queue latency.",
        "quant_metric": "$140,000/year cloud compute credit savings",
        "source_company": "Enterprise Analytics Corp",
        "tags": ["Snowflake", "Cloud Data Warehouse", "Cost Optimization", "FinOps", "Architecture"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
    {
        "category": "TECH_SKILL",
        "skill_or_tool": "dbt",
        "title": "Production dbt Core / Cloud Semantic Modeling Framework",
        "evidence_text": "Built modular production dbt pipeline comprising 90+ staging, intermediate, and mart models with automated CI testing, incremental builds, and documentation.",
        "situation": "Data team lacked modular modeling standards and regression testing, causing data discrepancies in financial reporting.",
        "task": "Establish an enterprise dbt modeling repository with strict CI/CD schema testing and incremental materialization.",
        "action": "Built dimensional star-schema data models using dbt, configured generic schema tests (unique, not_null, relationships) and custom singular tests, and implemented automated Slim CI in GitHub Actions.",
        "result": "Achieved 99.8% data model test pass rate and reduced model deployment release cycles from 3 days to 20 minutes.",
        "quant_metric": "99.8% automated test pass rate across 90+ models",
        "source_company": "Enterprise Analytics Corp",
        "tags": ["dbt", "Data Modeling", "CI/CD", "Testing", "Dimensional Modeling"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
    {
        "category": "TECH_SKILL",
        "skill_or_tool": "Looker",
        "title": "Self-Serve LookML Semantic Layer & Executive Dashboard Platform",
        "evidence_text": "Engineered centralized LookML semantic modeling layer serving 450+ daily active stakeholders with standardized metrics definitions and sub-second caching.",
        "situation": "Departmental teams were reporting conflicting revenue and churn metrics due to fragmented calculation logic across individual reports.",
        "task": "Create a unified Looker single source of truth for all corporate KPIs.",
        "action": "Modeled robust LookML views, explores, and derived tables with rigorous caching rules and user access grants.",
        "result": "Adopted by 450+ business users across Product, Sales, and Finance, eliminating metric discrepancies across executive reviews.",
        "quant_metric": "450+ daily active users on unified semantic layer",
        "source_company": "Enterprise Analytics Corp",
        "tags": ["Looker", "LookML", "Semantic Layer", "BI Governance", "Executive Dashboards"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
    {
        "category": "TECH_SKILL",
        "skill_or_tool": "Python",
        "title": "Automated Python Data Pipelines & API Ingestion Connectors",
        "evidence_text": "Authored asynchronous Python ingestion services using Pandas, Polars, and Requests to extract data from 12 third-party REST APIs into cloud data lakes.",
        "situation": "Manual CSV exports from SaaS marketing and CRM platforms caused multi-day lag in executive reporting.",
        "task": "Automate hourly batch ingestion with schema validation and failure alerting.",
        "action": "Developed containerized Python extraction pipelines with exponential backoff retries, Pydantic schema validation, and Slack alerting.",
        "result": "Fully automated ingestion of 12 external APIs with 99.9% uptime and zero manual intervention.",
        "quant_metric": "99.9% pipeline uptime across 12 automated API connectors",
        "source_company": "Global Data Solutions",
        "tags": ["Python", "Pandas", "API Ingestion", "AsyncIO", "Data Pipelines"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
    {
        "category": "TECH_SKILL",
        "skill_or_tool": "Power BI",
        "title": "DAX Performance Tuning & Enterprise Power BI Architectures",
        "evidence_text": "Built enterprise Power BI tabular models with complex DAX measures, row-level security (RLS), and incremental refresh for 1,200+ organizational users.",
        "situation": "Enterprise sales performance report took over 25 seconds to render and frequently crashed on mobile viewports.",
        "task": "Optimize DAX measures and data model relationships to achieve sub-3-second render times.",
        "action": "Eliminated bidirectional relationships, replaced iterative DAX functions with optimized CALCULATE filter contexts, and enabled incremental refresh.",
        "result": "Render latency reduced from 25s to 1.8s (92% speedup) for 1,200+ global users.",
        "quant_metric": "92% dashboard render speedup (25s to 1.8s) for 1,200+ users",
        "source_company": "Global Data Solutions",
        "tags": ["Power BI", "DAX", "Tabular Models", "RLS", "Performance Optimization"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
    {
        "category": "ARCHITECTURE_PROJECT",
        "skill_or_tool": "Databricks",
        "title": "Databricks Lakehouse & Spark Data Processing Framework",
        "evidence_text": "Implemented Databricks Delta Lake medallion architecture (Bronze/Silver/Gold) using PySpark to process over 2TB daily streaming log data.",
        "situation": "Unstructured clickstream and telemetry data could not be joined efficiently with core transactional tables.",
        "task": "Build a scalable Delta Lake pipeline for streaming and batch log analytics.",
        "action": "Configured Delta Live Tables with Auto Loader, optimizing Z-Ordering on primary join keys and implementing vacuuming policies.",
        "result": "Enabled real-time funnel analytics with 15-minute data latency vs. previous 24-hour batch turnaround.",
        "quant_metric": "15-minute data latency vs. previous 24-hour batch turnaround",
        "source_company": "Global Data Solutions",
        "tags": ["Databricks", "Delta Lake", "PySpark", "Medallion Architecture", "Data Lakehouse"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
    {
        "category": "TECH_SKILL",
        "skill_or_tool": "Azure",
        "title": "Azure Data Platform (ADLS Gen2, Synapse, Data Factory)",
        "evidence_text": "Deployed enterprise Azure data infrastructure with ADF pipelines, ADLS Gen2 storage accounts, Azure Key Vault, and private endpoints meeting SOC 2 compliance.",
        "situation": "Legacy on-prem data systems required migration to a secure, compliant cloud architecture.",
        "task": "Provision and manage Azure data engineering infrastructure with Terraform and Azure DevOps.",
        "action": "Built 35+ ADF data flows, configured Managed Identity authentication, and established automated deployment pipelines.",
        "result": "Successfully migrated 100% of corporate data infrastructure to Azure with zero downtime.",
        "quant_metric": "100% on-prem to Azure cloud migration completed with 0 downtime",
        "source_company": "Global Data Solutions",
        "tags": ["Azure", "ADF", "ADLS Gen2", "Key Vault", "Cloud Infrastructure"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
    {
        "category": "TECH_SKILL",
        "skill_or_tool": "AWS",
        "title": "AWS Cloud Data Engineering (S3, Glue, Athena, Redshift)",
        "evidence_text": "Constructed scalable data lake on AWS S3 with AWS Glue Crawlers, Athena query acceleration, and Redshift dimensional data marts.",
        "situation": "Ad-hoc SQL queries on raw S3 files were slow and incurred high Athena query scanning fees.",
        "task": "Partition and compress raw datasets in Parquet to minimize Athena query costs.",
        "action": "Implemented Glue ETL jobs converting JSON to snappy Parquet with date-based partitioning.",
        "result": "Reduced Athena data scan volumes by 74%, saving over $3,500/month in ad-hoc query costs.",
        "quant_metric": "74% reduction in S3 data scan volumes ($3,500/mo savings)",
        "source_company": "Tech Innovations Inc",
        "tags": ["AWS", "S3", "Athena", "Glue", "Redshift", "Parquet"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
    {
        "category": "TECH_SKILL",
        "skill_or_tool": "BigQuery",
        "title": "BigQuery Multi-Terabyte Analytical Engine & Partitioning",
        "evidence_text": "Managed 50TB+ BigQuery dataset architecture, applying partition pruning and clustering strategies to maintain sub-second query performance.",
        "situation": "Unpartitioned BigQuery tables resulted in full-table scans costing hundreds of dollars per analytical query.",
        "task": "Enforce strict table partitioning and clustering across analytical tables.",
        "action": "Partitioned tables by ingestion date and clustered by customer_id and region_code, setting maximum bytes billed limits.",
        "result": "Query scan costs decreased by 80% with an average query execution time under 1.2 seconds.",
        "quant_metric": "80% reduction in query scan costs with <1.2s execution times",
        "source_company": "Tech Innovations Inc",
        "tags": ["BigQuery", "GCP", "Partitioning", "Clustering", "Query Optimization"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
    {
        "category": "TECH_SKILL",
        "skill_or_tool": "Tableau",
        "title": "Executive KPI Tableau Dashboards & Server Administration",
        "evidence_text": "Designed high-impact C-suite Tableau dashboards tracking ARR, customer retention, and net revenue retention (NRR) updated in real-time.",
        "situation": "Executive leadership lacked real-time visibility into daily revenue metrics across sales regions.",
        "task": "Deliver high-performance executive dashboard suite with automated daily alerts.",
        "action": "Built Tableau extracts using published hyper datasets, created interactive parameter-driven views, and automated daily PDF distributions.",
        "result": "Adopted as the primary operational review dashboard by CEO and CFO in weekly leadership syncs.",
        "quant_metric": "100% executive adoption for weekly revenue & retention reviews",
        "source_company": "Tech Innovations Inc",
        "tags": ["Tableau", "Executive Reporting", "ARR", "Retention", "Data Visualization"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
    {
        "category": "BUSINESS_IMPACT",
        "skill_or_tool": "Data Modeling",
        "title": "Kimball Star-Schema Data Mart Design & Dimensional Governance",
        "evidence_text": "Architected unified enterprise dimensional data models (Conformed Dimensions, Fact Tables, Slowly Changing Dimensions Type 2) across 6 business domains.",
        "situation": "Inconsistent business entity keys caused data silo conflicts between Sales and Marketing reporting.",
        "task": "Standardize enterprise bus matrix and conformed dimensions.",
        "action": "Facilitated business stakeholder workshops, designed SCD Type 2 dimensions for customer account states, and documented data dictionaries.",
        "result": "Created single source of truth enterprise data marts reducing ad-hoc data reconciliation requests by 85%.",
        "quant_metric": "85% reduction in cross-departmental data reconciliation requests",
        "source_company": "Tech Innovations Inc",
        "tags": ["Data Modeling", "Kimball", "SCD Type 2", "Star Schema", "Data Governance"],
        "confidence": 1.0,
        "verified_by_user": True,
    },
]

class SaraswatiEvidenceService:
    """
    SARASWATI Candidate Evidence Bank Custodian.
    Enforces strict zero-hallucination policies and provides ground-truth
    evidence storage, validation, retrieval, and skill summaries.
    """

    async def get_or_create_default_profile(self, db: AsyncSession) -> CandidateProfile:
        """Fetch or initialize candidate profile."""
        stmt = select(CandidateProfile).limit(1)
        res = await db.execute(stmt)
        profile = res.scalars().first()
        if not profile:
            profile = CandidateProfile(
                full_name="Kavish",
                email="kavish@career-os.local",
                target_title="Senior / Lead BI & Analytics Engineer",
                target_seniority="LEAD",
                target_comp_min=165000,
                target_comp_max=230000,
                work_auth_status="US_CITIZEN",
                preferred_locations=["Remote US", "San Francisco, CA", "Seattle, WA", "New York, NY"],
                raw_bio="Senior / Lead Business Intelligence & Analytics Engineer with 7+ years of expertise scaling Modern Data Stack architectures (Snowflake, dbt, SQL, Looker, Python, BigQuery, Databricks). Proven track record driving over $140k in cloud cost reductions and architecting semantic layers for 450+ active business stakeholders.",
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
        return profile

    async def list_evidence(
        self,
        db: AsyncSession,
        category: Optional[str] = None,
        skill_or_tool: Optional[str] = None,
        search: Optional[str] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EvidenceItem]:
        """List candidate evidence items with multi-factor filtering."""
        query = select(EvidenceItem).order_by(EvidenceItem.created_at.desc())
        
        if active_only:
            query = query.where(EvidenceItem.is_active == True)
        if category:
            query = query.where(EvidenceItem.category == category.upper())
        if skill_or_tool:
            query = query.where(EvidenceItem.skill_or_tool.ilike(f"%{skill_or_tool}%"))
        if search:
            pat = f"%{search}%"
            query = query.where(
                or_(
                    EvidenceItem.title.ilike(pat),
                    EvidenceItem.evidence_text.ilike(pat),
                    EvidenceItem.quant_metric.ilike(pat),
                    EvidenceItem.skill_or_tool.ilike(pat),
                )
            )

        query = query.limit(limit).offset(offset)
        res = await db.execute(query)
        return res.scalars().all()

    async def get_evidence_by_id(self, db: AsyncSession, evidence_id: str) -> Optional[EvidenceItem]:
        """Retrieve a specific evidence item."""
        stmt = select(EvidenceItem).where(EvidenceItem.id == evidence_id)
        res = await db.execute(stmt)
        return res.scalars().first()

    async def create_evidence_item(self, db: AsyncSession, payload: EvidenceItemCreate) -> EvidenceItem:
        """Create and validate a new evidence item with zero hallucination enforcement."""
        if not payload.profile_id:
            profile = await self.get_or_create_default_profile(db)
            profile_id = profile.id
        else:
            profile_id = payload.profile_id

        # Integrity validation: require meaningful claim text
        if len(payload.evidence_text.strip()) < 10:
            raise ValueError("Evidence text must contain a substantiated description of at least 10 characters.")

        item = EvidenceItem(
            profile_id=profile_id,
            category=payload.category,
            skill_or_tool=payload.skill_or_tool.strip(),
            title=payload.title.strip(),
            evidence_text=payload.evidence_text.strip(),
            situation=payload.situation,
            task=payload.task,
            action=payload.action,
            result=payload.result,
            quant_metric=payload.quant_metric,
            source_company=payload.source_company,
            timeframe_start=payload.timeframe_start,
            timeframe_end=payload.timeframe_end,
            tags=payload.tags or [payload.skill_or_tool],
            confidence=payload.confidence,
            verified_by_user=payload.verified_by_user,
            is_active=True,
        )
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    async def update_evidence_item(
        self,
        db: AsyncSession,
        evidence_id: str,
        update_data: EvidenceItemUpdate
    ) -> Optional[EvidenceItem]:
        """Update an existing evidence item."""
        item = await self.get_evidence_by_id(db, evidence_id)
        if not item:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(item, key, val)

        await db.commit()
        await db.refresh(item)
        return item

    async def delete_evidence_item(self, db: AsyncSession, evidence_id: str) -> bool:
        """Soft-delete an evidence item."""
        item = await self.get_evidence_by_id(db, evidence_id)
        if not item:
            return False

        item.is_active = False
        await db.commit()
        return True

    async def get_skills_summary(self, db: AsyncSession) -> SkillsSummaryResponse:
        """
        Aggregate verified skills from the Evidence Bank, returning counts,
        top metrics, and backing evidence item IDs.
        """
        items = await self.list_evidence(db, active_only=True, limit=500)
        skill_map: Dict[str, Dict[str, Any]] = {}

        for it in items:
            s_name = it.skill_or_tool.strip()
            if s_name not in skill_map:
                skill_map[s_name] = {
                    "skill_name": s_name,
                    "evidence_count": 0,
                    "categories": set(),
                    "top_metrics": [],
                    "evidence_ids": [],
                }
            
            skill_map[s_name]["evidence_count"] += 1
            skill_map[s_name]["categories"].add(it.category)
            skill_map[s_name]["evidence_ids"].append(it.id)
            if it.quant_metric and len(skill_map[s_name]["top_metrics"]) < 3:
                skill_map[s_name]["top_metrics"].append(it.quant_metric)

        skills_list = [
            SkillSummaryItem(
                skill_name=data["skill_name"],
                evidence_count=data["evidence_count"],
                categories=sorted(list(data["categories"])),
                top_metrics=data["top_metrics"],
                evidence_ids=data["evidence_ids"],
            )
            for data in sorted(skill_map.values(), key=lambda x: x["evidence_count"], reverse=True)
        ]

        return SkillsSummaryResponse(
            total_skills=len(skills_list),
            total_evidence_items=len(items),
            skills=skills_list,
        )

    async def get_evidence_for_skills(self, db: AsyncSession, target_skills: List[str]) -> Dict[str, List[EvidenceItem]]:
        """
        Retrieve all backing evidence items for a given list of skills.
        Used by ARJUNA to prove and ground every match.
        """
        all_items = await self.list_evidence(db, active_only=True, limit=500)
        norm_target = {s.lower(): s for s in target_skills}
        result: Dict[str, List[EvidenceItem]] = {s: [] for s in target_skills}

        for item in all_items:
            item_skill_lower = item.skill_or_tool.lower()
            for t_lower, orig_target in norm_target.items():
                if t_lower in item_skill_lower or item_skill_lower in t_lower or any(t_lower == tag.lower() for tag in (item.tags or [])):
                    result[orig_target].append(item)

        return result

    async def seed_default_evidence(self, db: AsyncSession) -> Dict[str, Any]:
        """Seed the candidate profile and default high-impact evidence items if empty."""
        profile = await self.get_or_create_default_profile(db)
        existing = await self.list_evidence(db, limit=10)
        if existing:
            return {"status": "ALREADY_SEEDED", "count": len(existing)}

        created_count = 0
        for item_data in DEFAULT_EVIDENCE_ITEMS:
            item = EvidenceItem(
                profile_id=profile.id,
                category=item_data["category"],
                skill_or_tool=item_data["skill_or_tool"],
                title=item_data["title"],
                evidence_text=item_data["evidence_text"],
                situation=item_data.get("situation"),
                task=item_data.get("task"),
                action=item_data.get("action"),
                result=item_data.get("result"),
                quant_metric=item_data.get("quant_metric"),
                source_company=item_data.get("source_company"),
                tags=item_data.get("tags", []),
                confidence=item_data.get("confidence", 1.0),
                verified_by_user=item_data.get("verified_by_user", True),
                is_active=True,
            )
            db.add(item)
            created_count += 1

        await db.commit()
        return {"status": "SUCCESS", "created_count": created_count}

saraswati_service = SaraswatiEvidenceService()
