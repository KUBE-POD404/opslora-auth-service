from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, UniqueConstraint

from app.database import Base


class OrganizationSettings(Base):
    __tablename__ = "organization_settings"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    legal_name = Column(String(150), nullable=True)
    display_name = Column(String(150), nullable=True)
    logo_url = Column(String(500), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(150), nullable=True)
    website = Column(String(255), nullable=True)

    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    tax_id = Column(String(50), nullable=True)
    gstin = Column(String(20), nullable=True)
    tax_registration_type = Column(String(50), nullable=True)
    default_tax_mode = Column(String(50), nullable=True)

    invoice_prefix = Column(String(20), nullable=False, default="INV")
    next_invoice_sequence = Column(Integer, nullable=False, default=1)
    default_due_days = Column(Integer, nullable=False, default=30)
    default_invoice_terms = Column(Text, nullable=True)
    default_invoice_footer = Column(Text, nullable=True)
    round_off_enabled = Column(Boolean, nullable=False, default=False)
    default_invoice_template = Column(String(100), nullable=True)

    inventory_enabled = Column(Boolean, nullable=False, default=False)
    gst_invoice_enabled = Column(Boolean, nullable=False, default=False)
    customer_portal_enabled = Column(Boolean, nullable=False, default=False)
    online_payments_enabled = Column(Boolean, nullable=False, default=False)
    multi_warehouse_enabled = Column(Boolean, nullable=False, default=False)
    advanced_reports_enabled = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("organization_id", name="uq_organization_settings_org"),
    )


class OrganizationFeatureFlag(Base):
    __tablename__ = "organization_feature_flags"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    flag_key = Column(String(100), nullable=False)
    is_enabled = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("organization_id", "flag_key", name="uq_org_feature_flag"),
    )
