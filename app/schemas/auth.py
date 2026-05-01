from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupRequest(BaseModel):
    organization_name: str = Field(..., min_length=2, max_length=150)
    organization_slug: str = Field(..., min_length=2, max_length=100, pattern="^[a-z0-9-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)


class SignupResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: EmailStr
    organization_name: str


class LoginRequest(BaseModel):
    organization_slug: str
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    user_id: int
    email: EmailStr
    org_id: int
    permissions: list[str]


class RefreshTokenRequest(BaseModel):
    refresh_token: str  


class OrganizationSettingsUpdate(BaseModel):
    legal_name: str | None = Field(default=None, max_length=150)
    display_name: str | None = Field(default=None, max_length=150)
    logo_url: str | None = Field(default=None, max_length=500)
    address: str | None = None
    phone: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    website: str | None = Field(default=None, max_length=255)

    country: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    tax_id: str | None = Field(default=None, max_length=50)
    gstin: str | None = Field(default=None, max_length=20)
    tax_registration_type: str | None = Field(default=None, max_length=50)
    default_tax_mode: str | None = Field(default=None, max_length=50)

    invoice_prefix: str = Field(default="INV", max_length=20)
    next_invoice_sequence: int = Field(default=1, ge=1)
    default_due_days: int = Field(default=30, ge=0, le=365)
    default_invoice_terms: str | None = None
    default_invoice_footer: str | None = None
    round_off_enabled: bool = False
    default_invoice_template: str | None = Field(default=None, max_length=100)

    inventory_enabled: bool = False
    gst_invoice_enabled: bool = False
    customer_portal_enabled: bool = False
    online_payments_enabled: bool = False
    multi_warehouse_enabled: bool = False
    advanced_reports_enabled: bool = False


class OrganizationSettingsResponse(OrganizationSettingsUpdate):
    organization_id: int

    model_config = ConfigDict(from_attributes=True)


class FeatureFlagUpdate(BaseModel):
    is_enabled: bool


class FeatureFlagResponse(BaseModel):
    flag_key: str
    is_enabled: bool

    model_config = ConfigDict(from_attributes=True)
