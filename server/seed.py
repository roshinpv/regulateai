from sqlalchemy.orm import Session
import datetime
import logging
import uuid
import bcrypt

from .models import models
from .database import SessionLocal

logger = logging.getLogger(__name__)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')


def seed_database():
    """
    Seed the database with Wells Fargo focused data.
    """
    db = SessionLocal()
    try:
        # Check if database is already seeded
        if db.query(models.User).count() > 0:
            logger.info("Database already seeded. Skipping.")
            return

        logger.info("Seeding database with Wells Fargo focused data...")

        # Create admin user with properly hashed password
        admin_user = models.User(
            username="admin",
            email="admin@wellsfargo.com",
            hashed_password=get_password_hash("password"),
            is_admin=True
        )
        db.add(admin_user)

        # Create regular user with properly hashed password
        regular_user = models.User(
            username="user",
            email="user@wellsfargo.com",
            hashed_password=get_password_hash("password"),
            is_admin=False
        )
        db.add(regular_user)

        db.commit()

        # Create jurisdictions
        us_jurisdiction = models.Jurisdiction(
            name="United States",
            code="US",
            type=models.JurisdictionType.NATIONAL
        )
        db.add(us_jurisdiction)

        db.commit()

        # Create agencies
        ''' agencies = [
            models.Agency(
                name="FDIC",
                description="Federal Deposit Insurance Corporation - Insures deposits and examines/supervises financial institutions.",
                jurisdiction_id=us_jurisdiction.id,
                website="https://www.fdic.gov/"
            ),
            models.Agency(
                name="OCC",
                description="Office of the Comptroller of the Currency - Charters, regulates, and supervises national banks.",
                jurisdiction_id=us_jurisdiction.id,
                website="https://www.occ.treas.gov/"
            ),
            models.Agency(
                name="FinCEN",
                description="Financial Crimes Enforcement Network - Safeguards the financial system from illicit use.",
                jurisdiction_id=us_jurisdiction.id,
                website="https://www.fincen.gov/"
            ),
            models.Agency(
                name="CFPB",
                description="Consumer Financial Protection Bureau - Protects consumers in the financial sector.",
                jurisdiction_id=us_jurisdiction.id,
                website="https://www.consumerfinance.gov/"
            )
        ]

        for agency in agencies:
            db.add(agency)

        db.commit()

        # Get agency references
        fdic = db.query(models.Agency).filter(models.Agency.name == "FDIC").first()
        occ = db.query(models.Agency).filter(models.Agency.name == "OCC").first()
        fincen = db.query(models.Agency).filter(models.Agency.name == "FinCEN").first()
        cfpb = db.query(models.Agency).filter(models.Agency.name == "CFPB").first()
 '''
        # Create Wells Fargo
        wells_fargo = models.Bank(
            id="bank-001",  # Fixed ID for consistency
            name="Wells Fargo",
            jurisdiction_id=us_jurisdiction.id,
            size_category="Global Systemically Important"
        )
        db.add(wells_fargo)
        db.commit()


        # Create risk assessment units
        risk_units = {
            'app_adherence': models.RiskAssessmentUnit(
                name="Application and Records Adherence",
                description="Manages application compliance and record keeping",
                category=models.UnitCategory.APPLICATION
            ),
            'app_lifecycle': models.RiskAssessmentUnit(
                name="Application LifeCycle Management",
                description="Oversees application development lifecycle",
                category=models.UnitCategory.APPLICATION
            ),
            'enterprise_arch': models.RiskAssessmentUnit(
                name="Enterprise Architecture Service",
                description="Manages enterprise architecture standards",
                category=models.UnitCategory.APPLICATION
            ),
            'sdlc': models.RiskAssessmentUnit(
                name="Software Development Lifecycle",
                description="Ensures compliance in software development",
                category=models.UnitCategory.APPLICATION
            ),
            'info_protection': models.RiskAssessmentUnit(
                name="Information Protection",
                description="Ensures data security",
                category=models.UnitCategory.SECURITY
            ),
            'reg_change': models.RiskAssessmentUnit(
                name="Business Adherence & Regulatory Change Management",
                description="Manages regulatory compliance",
                category=models.UnitCategory.GOVERNANCE
            ),
            'cloud': models.RiskAssessmentUnit(
                name="Cloud Platform",
                description="Manages cloud infrastructure",
                category=models.UnitCategory.INFRASTRUCTURE
            ),
            'disaster_recovery': models.RiskAssessmentUnit(
                name="Disaster Recovery Service",
                description="Handles disaster recovery",
                category=models.UnitCategory.INFRASTRUCTURE
            ),
            'automation': models.RiskAssessmentUnit(
                name="Foundational Automation",
                description="Manages automation processes",
                category=models.UnitCategory.OPERATIONS
            ),
            'tech_change': models.RiskAssessmentUnit(
                name="Technology Change Management",
                description="Oversees technology changes",
                category=models.UnitCategory.GOVERNANCE
            ),
            'incident_mgmt': models.RiskAssessmentUnit(
                name="Incident and Problem Management",
                description="Handles operational issues",
                category=models.UnitCategory.OPERATIONS
            ),
            'asset_mgmt': models.RiskAssessmentUnit(
                name="Service Asset and Configuration Management",
                description="Manages IT assets",
                category=models.UnitCategory.GOVERNANCE
            ),
            'workforce': models.RiskAssessmentUnit(
                name="Workforce Experience Productivity Solutions",
                description="Manages workforce tools",
                category=models.UnitCategory.OPERATIONS
            ),
            'hosting': models.RiskAssessmentUnit(
                name="Foundation Hosting Platform",
                description="Manages hosting infrastructure",
                category=models.UnitCategory.INFRASTRUCTURE
            ),
            'data_center': models.RiskAssessmentUnit(
                name="Enterprise Data Center Service",
                description="Operates data centers",
                category=models.UnitCategory.INFRASTRUCTURE
            ),
            'availability': models.RiskAssessmentUnit(
                name="Availability and Service Level Management",
                description="Ensures service availability",
                category=models.UnitCategory.OPERATIONS
            ),
            'ops_support': models.RiskAssessmentUnit(
                name="Technology Infrastructure Operations Support",
                description="Supports infrastructure",
                category=models.UnitCategory.OPERATIONS
            ),
            'iam': models.RiskAssessmentUnit(
                name="Identity and Access Management",
                description="Manages access control",
                category=models.UnitCategory.SECURITY
            ),
            'cyber_defense': models.RiskAssessmentUnit(
                name="Cyber Security Defense and Monitoring",
                description="Monitors security threats",
                category=models.UnitCategory.SECURITY
            ),
            'vulnerability': models.RiskAssessmentUnit(
                name="Infrastructure Vulnerability Management",
                description="Manages security vulnerabilities",
                category=models.UnitCategory.SECURITY
            ),
            'cyber_gov': models.RiskAssessmentUnit(
                name="Cyber Security Governance",
                description="Oversees security policies",
                category=models.UnitCategory.SECURITY
            ),
            'patch': models.RiskAssessmentUnit(
                name="Patch Management",
                description="Manages system updates",
                category=models.UnitCategory.SECURITY
            ),
            'network': models.RiskAssessmentUnit(
                name="Secure Network Services",
                description="Ensures network security",
                category=models.UnitCategory.SECURITY
            ),
            'third_party': models.RiskAssessmentUnit(
                name="Technology Third Party Management Service",
                description="Manages vendor relationships",
                category=models.UnitCategory.GOVERNANCE
            ),
            'app_security': models.RiskAssessmentUnit(
                name="Application Security",
                description="Manages application security",
                category=models.UnitCategory.SECURITY
            ),
            'tech_strategy': models.RiskAssessmentUnit(
                name="Shared Services Technology Strategy, Change Enablement & Reporting Service",
                description="Manages technology strategy",
                category=models.UnitCategory.GOVERNANCE
            ),
            'file_transfer': models.RiskAssessmentUnit(
                name="External File Transfer Services",
                description="Manages secure file transfers",
                category=models.UnitCategory.INFRASTRUCTURE
            ),
            'tech_gov': models.RiskAssessmentUnit(
                name="Technology Governance",
                description="Oversees technology standards",
                category=models.UnitCategory.GOVERNANCE
            )
        }

        for unit in risk_units.values():
            db.add(unit)
        db.commit()

        # Create regulations with unit mappings
        ''' c = [
            {
                'regulation': models.Regulation(
                    title="Basel III",
                    agency_id=fdic.id,
                    jurisdiction_id=us_jurisdiction.id,
                    impact_level=models.ImpactLevel.HIGH,
                    last_updated=datetime.datetime(2024, 2, 15),
                    summary="Basel III requirements specifically affecting Wells Fargo as a Global Systemically Important Bank (G-SIB).",
                    effective_date=datetime.datetime(2013, 1, 1),
                    compliance_deadline=datetime.datetime(2019, 1, 1)
                ),
                'categories': [
                    models.RegulationCategory.CAPITAL,
                    models.RegulationCategory.RISK
                ],
                'units': [
                    risk_units['reg_change'],
                    risk_units['tech_gov'],
                    risk_units['enterprise_arch'],
                    risk_units['asset_mgmt'],
                    risk_units['data_center']
                ]
            },
            {
                'regulation': models.Regulation(
                    title="Dodd-Frank Act",
                    agency_id=occ.id,
                    jurisdiction_id=us_jurisdiction.id,
                    impact_level=models.ImpactLevel.HIGH,
                    last_updated=datetime.datetime(2023, 11, 10),
                    summary="Dodd-Frank Act compliance requirements for Wells Fargo.",
                    effective_date=datetime.datetime(2010, 7, 21),
                    compliance_deadline=datetime.datetime(2015, 7, 21)
                ),
                'categories': [
                    models.RegulationCategory.FINANCIAL,
                    models.RegulationCategory.RISK
                ],
                'units': [
                    risk_units['reg_change'],
                    risk_units['tech_gov'],
                    risk_units['cyber_gov'],
                    risk_units['third_party'],
                    risk_units['tech_strategy']
                ]
            },
            {
                'regulation': models.Regulation(
                    title="Fair Lending Practices",
                    agency_id=occ.id,
                    jurisdiction_id=us_jurisdiction.id,
                    impact_level=models.ImpactLevel.HIGH,
                    last_updated=datetime.datetime(2023, 12, 5),
                    summary="Fair lending practices requirements for Wells Fargo's operations.",
                    effective_date=datetime.datetime(2023, 1, 1),
                    compliance_deadline=datetime.datetime(2023, 12, 31)
                ),
                'categories': [
                    models.RegulationCategory.CONSUMER_PROTECTION,
                    models.RegulationCategory.FINANCIAL
                ],
                'units': [
                    risk_units['app_adherence'],
                    risk_units['info_protection'],
                    risk_units['reg_change'],
                    risk_units['app_security']
                ]
            },
            {
                'regulation': models.Regulation(
                    title="Anti-Money Laundering (AML)",
                    agency_id=fincen.id,
                    jurisdiction_id=us_jurisdiction.id,
                    impact_level=models.ImpactLevel.HIGH,
                    last_updated=datetime.datetime(2024, 3, 1),
                    summary="AML requirements for Wells Fargo's global operations.",
                    effective_date=datetime.datetime(2024, 1, 1),
                    compliance_deadline=datetime.datetime(2024, 12, 31)
                ),
                'categories': [
                    models.RegulationCategory.AML,
                    models.RegulationCategory.FRAUD
                ],
                'units': [
                    risk_units['info_protection'],
                    risk_units['cyber_defense'],
                    risk_units['app_security'],
                    risk_units['network'],
                    risk_units['file_transfer']
                ]
            },
            {
                'regulation': models.Regulation(
                    title="Consumer Financial Protection",
                    agency_id=cfpb.id,
                    jurisdiction_id=us_jurisdiction.id,
                    impact_level=models.ImpactLevel.MEDIUM,
                    last_updated=datetime.datetime(2024, 2, 28),
                    summary="Consumer protection requirements for Wells Fargo's retail services.",
                    effective_date=datetime.datetime(2024, 1, 1),
                    compliance_deadline=datetime.datetime(2024, 12, 31)
                ),
                'categories': [
                    models.RegulationCategory.CONSUMER_PROTECTION,
                    models.RegulationCategory.FINANCIAL
                ],
                'units': [
                    risk_units['app_adherence'],
                    risk_units['info_protection'],
                    risk_units['reg_change'],
                    risk_units['app_security'],
                    risk_units['cyber_gov']
                ]
            }
        ]

        for reg_data in regulations:
            regulation = reg_data['regulation']
            categories = reg_data['categories']
            units = reg_data['units']

            db.add(regulation)
            wells_fargo.affected_regulations.append(regulation)

            # Add categories
            for category in categories:
                cat_assoc = models.RegulationCategoryAssociation(
                    regulation_id=regulation.id,
                    category=category
                )
                regulation.categories.append(cat_assoc)

            # Add units
            for unit in units:
                regulation.responsible_units.append(unit)

        db.commit()'''

        logger.info("Database seeded successfully with Wells Fargo focused data.")

    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()