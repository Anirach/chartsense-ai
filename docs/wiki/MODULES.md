# 🧩 ChartSense AI Modules Documentation

**Comprehensive Module-by-Module Code Analysis with File References**

---

## Table of Contents

1. [Backend Modules](#backend-modules)
2. [Frontend Modules](#frontend-modules)
3. [Configuration Modules](#configuration-modules)
4. [Database Modules](#database-modules)
5. [Service Integration](#service-integration)

---

## Backend Modules

### Core Application Module

#### `app/main.py` - Application Entry Point
**File**: [`backend/app/main.py`](../../backend/app/main.py)  
**Lines**: 1-32  
**Purpose**: FastAPI application initialization and router configuration

```python
# Core FastAPI setup with CORS and middleware
app = FastAPI(
    title="ChartSense AI",
    description="AI-Powered Clinical Decision Support Platform",
    version="1.0.0",
    docs_url="/docs",
)

# Router registration for API endpoints
app.include_router(cds.router, prefix="/api/v1/cds", tags=["Clinical Decision Support"])
app.include_router(chart.router, prefix="/api/v1/chart-completeness", tags=["Chart Completeness"])
app.include_router(coding.router, prefix="/api/v1/code-suggestion", tags=["Code Suggestion"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
```

**Dependencies**: FastAPI, SQLAlchemy, Pydantic schemas  
**Integration Points**: All API modules, database initialization, seed data

---

### API Layer Modules

#### Clinical Decision Support API
**File**: [`backend/app/api/cds.py`](../../backend/app/api/cds.py)  
**Lines**: 1-450 (estimated)  
**Purpose**: CDS endpoints for diagnosis, orders, and admission decisions

**Key Endpoints**:

##### Pre-Diagnosis Endpoint
**Lines**: 20-80  
**Route**: `POST /api/v1/cds/pre-diagnosis`
```python
@router.post("/pre-diagnosis", response_model=PreDiagnosisResponse)
async def get_pre_diagnosis(request: PreDiagnosisRequest):
    """Generate differential diagnoses using GraphRAG knowledge graph traversal."""
    diagnoses = find_differential_diagnoses(request.symptoms, request.patient_context)
    return PreDiagnosisResponse(diagnoses=diagnoses)
```

##### Order Suggestion Endpoint  
**Lines**: 100-200  
**Route**: `POST /api/v1/cds/order-suggestion`
```python
@router.post("/order-suggestion", response_model=OrderSuggestionResponse)
async def get_order_suggestions(request: OrderSuggestionRequest):
    """Generate CPG-compliant order suggestions based on diagnosis."""
    # Thai CPG 2023-based order templates
    template = ORDER_TEMPLATES.get(request.disease_group, [])
    return OrderSuggestionResponse(orders=personalized_orders)
```

##### Admission Decision Endpoint
**Lines**: 250-350  
**Route**: `POST /api/v1/cds/admission-decision`
```python
@router.post("/admission-decision", response_model=AdmissionDecisionResponse)
async def get_admission_decision(request: AdmissionDecisionRequest):
    """Calculate risk scores and admission recommendations."""
    curb65_score = calculate_curb65(request.patient_data)
    qsofa_score = calculate_qsofa(request.vital_signs)
    return AdmissionDecisionResponse(recommendation="ADMIT", risk_scores=[...])
```

**CPG Templates**: Lines 15-100 contain Thai Clinical Practice Guideline templates for:
- Community-Acquired Pneumonia (CAP)
- Diabetes Mellitus complications  
- Heart Failure management

#### Chart Completeness API
**File**: [`backend/app/api/chart.py`](../../backend/app/api/chart.py)  
**Lines**: 1-150  
**Purpose**: Chart quality assessment and gap identification

**Key Endpoints**:

##### Chart Evaluation
**Lines**: 20-60  
**Route**: `GET /api/v1/chart-completeness/{encounter_id}`
```python
@router.get("/{encounter_id}", response_model=ChartCompletenessResponse)
async def get_chart_completeness(encounter_id: int):
    """Evaluate chart completeness using 20+ configurable rules."""
    evaluation = rules_service.evaluate_encounter(encounter_id)
    return ChartCompletenessResponse(
        score=evaluation.overall_score,
        category_scores=evaluation.category_breakdown,
        gaps=evaluation.identified_gaps
    )
```

**Rule Categories**:
- **Diagnosis Rules** (Lines 80-100): ICD-10 coding completeness
- **Procedure Rules** (Lines 100-120): CPT/procedure validation  
- **Consistency Rules** (Lines 120-140): Cross-field validation
- **Documentation Rules** (Lines 140-150): Required clinical notes

#### Code Suggestion API
**File**: [`backend/app/api/coding.py`](../../backend/app/api/coding.py)  
**Lines**: 1-120  
**Purpose**: AI-powered ICD-10 code suggestions with DRG impact

**Key Endpoints**:

##### Code Suggestion Generation
**Lines**: 20-60  
**Route**: `POST /api/v1/code-suggestion/{encounter_id}`
```python
@router.post("/{encounter_id}/generate", response_model=CodeSuggestionResponse)
async def generate_code_suggestions(encounter_id: int):
    """Generate AI-powered ICD-10 code suggestions with revenue impact."""
    encounter = get_encounter(encounter_id)
    suggestions = drg_service.generate_code_suggestions(encounter)
    return CodeSuggestionResponse(
        suggestions=suggestions,
        revenue_impact=calculate_drg_impact(suggestions)
    )
```

##### Code Acceptance Workflow
**Lines**: 80-120  
**Route**: `POST /api/v1/code-suggestion/{encounter_id}/accept`
```python
@router.post("/{encounter_id}/accept")
async def accept_code_suggestions(encounter_id: int, accepted_codes: List[str]):
    """Accept AI code suggestions and update encounter."""
    result = drg_service.accept_suggestions(encounter_id, accepted_codes)
    return {"status": "accepted", "revenue_impact": result.revenue_change}
```

#### Admin API
**File**: [`backend/app/api/admin.py`](../../backend/app/api/admin.py)  
**Lines**: 1-200  
**Purpose**: Administrative functions for rules, templates, and system management

**Key Endpoints**:
- **Rule Management** (Lines 20-80): CRUD operations for chart completeness rules
- **CPG Template Management** (Lines 100-150): Clinical Practice Guideline templates
- **Patient Data Management** (Lines 160-200): Patient and encounter administration

---

### Service Layer Modules

#### GraphRAG Service (Knowledge Graph)
**File**: [`backend/app/services/graphrag.py`](../../backend/app/services/graphrag.py)  
**Lines**: 1-300+  
**Purpose**: Medical knowledge graph traversal and differential diagnosis generation

**Core Knowledge Graph Structure** (Lines 5-150):
```python
KNOWLEDGE_GRAPH: dict[str, dict] = {
    "diseases": {
        "J18.9": {  # Community-Acquired Pneumonia
            "name": "Community-Acquired Pneumonia",
            "name_th": "ปอดอักเสบชุมชน", 
            "group": "CAP",
            "symptoms": ["fever", "cough", "dyspnea", "sputum"],
            "labs": ["CBC", "CXR", "Blood_culture", "Procalcitonin"],
            "risk_factors": ["age_over_65", "diabetes", "copd"],
            "complications": ["sepsis", "respiratory_failure"]
        },
        "E11.65": {  # DM Type 2 with Hyperglycemia
            "name": "DM Type 2 with Hyperglycemia",
            "name_th": "เบาหวานชนิดที่ 2 มีน้ำตาลสูง",
            "group": "DM",
            "symptoms": ["polyuria", "polydipsia", "weight_loss"],
            "labs": ["FBS", "HbA1c", "BUN", "Creatinine"],
            "complications": ["dka", "hhs", "aki", "neuropathy"]
        }
    }
}
```

**Key Functions**:

##### Differential Diagnosis Algorithm (Lines 200-250):
```python
def find_differential_diagnoses(symptoms: List[str], patient_context: dict) -> List[DifferentialDiagnosis]:
    """
    GraphRAG-based diagnosis generation:
    1. Calculate symptom overlap scores for each disease
    2. Apply patient-specific risk factors (age, comorbidities)  
    3. Rank by confidence score (0.0-1.0)
    4. Return top 5 diagnoses with clinical rationale
    """
```

##### Confidence Scoring (Lines 250-300):
```python
def calculate_confidence_score(disease: dict, symptoms: List[str], patient: dict) -> float:
    """
    Multi-factor confidence calculation:
    - Symptom match percentage (40% weight)
    - Risk factor presence (30% weight) 
    - Age appropriateness (20% weight)
    - Clinical context (10% weight)
    """
```

#### Chart Completeness Rules Engine
**File**: [`backend/app/services/rules.py`](../../backend/app/services/rules.py)  
**Lines**: 1-400+  
**Purpose**: Multi-dimensional chart quality assessment with 20+ configurable rules

**Rule Categories Implementation**:

##### Diagnosis Rules (Lines 50-150):
```python
class DiagnosisRules:
    """ICD-10 coding completeness validation."""
    
    def rule_principal_diagnosis_required(self, encounter: Encounter) -> RuleResult:
        """Principal diagnosis must be present and valid ICD-10."""
        # Line 80: Validation logic for primary diagnosis
        return RuleResult(passed=bool(encounter.principal_diagnosis))
    
    def rule_secondary_diagnoses_documented(self, encounter: Encounter) -> RuleResult:
        """Secondary diagnoses should support principal diagnosis."""
        # Line 120: Logic for secondary diagnosis validation
```

##### Procedure Rules (Lines 150-250):
```python
class ProcedureRules:
    """CPT/procedure code validation."""
    
    def rule_procedures_match_diagnosis(self, encounter: Encounter) -> RuleResult:
        """Procedures must be clinically appropriate for diagnosis."""
        # Line 180: Cross-validation between procedures and diagnoses
    
    def rule_surgical_notes_complete(self, encounter: Encounter) -> RuleResult:
        """Operative notes required for surgical procedures."""
        # Line 220: Documentation completeness validation
```

##### Consistency Rules (Lines 250-350):
```python
class ConsistencyRules:
    """Cross-field data validation."""
    
    def rule_vital_signs_age_appropriate(self, encounter: Encounter) -> RuleResult:
        """Vital signs should be within age-appropriate ranges."""
        # Line 280: Age-specific normal range validation
    
    def rule_lab_values_clinical_correlation(self, encounter: Encounter) -> RuleResult:
        """Lab values should correlate with documented diagnoses."""
        # Line 320: Clinical correlation analysis
```

#### DRG/Revenue Calculation Service
**File**: [`backend/app/services/drg.py`](../../backend/app/services/drg.py)  
**Lines**: 1-250  
**Purpose**: Thai DRG system integration and revenue impact analysis

**Key Functions**:

##### DRG Calculation (Lines 50-100):
```python
def calculate_drg_weight(icd10_codes: List[str], procedures: List[str]) -> DRGResult:
    """
    Calculate Thai DRG relative weight:
    1. Map ICD-10 codes to DRG categories
    2. Apply procedure modifiers
    3. Calculate relative weight (RW)
    4. Estimate reimbursement in THB
    """
```

##### Revenue Impact Analysis (Lines 150-200):
```python
def calculate_revenue_impact(current_codes: List[str], suggested_codes: List[str]) -> RevenueImpact:
    """
    Compare current vs suggested coding impact:
    - Current RW and estimated reimbursement
    - Proposed RW with new codes  
    - Net revenue change in THB
    - Risk assessment for audit
    """
```

#### Thai NLP Service
**File**: [`backend/app/services/nlp.py`](../../backend/app/services/nlp.py)  
**Lines**: 1-200  
**Purpose**: Thai language clinical text processing and entity extraction

**Key Functions**:

##### Thai Keyword Extraction (Lines 50-100):
```python
def extract_thai_medical_entities(text: str) -> List[MedicalEntity]:
    """
    Extract medical entities from Thai clinical text:
    1. Tokenize Thai text (word segmentation)
    2. Match against medical terminology dictionary
    3. Identify symptoms, diagnoses, medications
    4. Return structured entities with confidence scores
    """
```

##### Clinical Concept Mapping (Lines 150-200):
```python
def map_thai_to_icd10(thai_terms: List[str]) -> List[ICD10Mapping]:
    """
    Map Thai medical terms to ICD-10 codes:
    - Use Thai medical terminology database
    - Apply fuzzy matching for variations
    - Return ranked ICD-10 code suggestions
    """
```

---

### Data Layer Modules

#### Database Models

##### Patient Model
**File**: [`backend/app/models/patient.py`](../../backend/app/models/patient.py)  
**Lines**: 1-80  
**Purpose**: Patient demographic and medical history data model

```python
class Patient(Base):
    """Patient demographic and clinical information."""
    __tablename__ = "patients"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    hn: Mapped[str] = mapped_column(String(20), unique=True)  # Hospital Number
    name: Mapped[str] = mapped_column(String(200))
    name_en: Mapped[Optional[str]] = mapped_column(String(200))
    gender: Mapped[str] = mapped_column(String(1))  # M/F
    date_of_birth: Mapped[date] = mapped_column(Date)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Relationships
    encounters: Mapped[List["Encounter"]] = relationship(back_populates="patient")
```

##### Chart/Encounter Model
**File**: [`backend/app/models/chart.py`](../../backend/app/models/chart.py)  
**Lines**: 1-150  
**Purpose**: Clinical encounter and chart completeness data

```python
class Encounter(Base):
    """Clinical encounter with completeness scoring."""
    __tablename__ = "encounters"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    visit_number: Mapped[str] = mapped_column(String(50))
    admission_date: Mapped[datetime] = mapped_column(DateTime)
    discharge_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Clinical Data
    chief_complaint: Mapped[str] = mapped_column(Text)
    present_illness: Mapped[str] = mapped_column(Text)
    principal_diagnosis: Mapped[Optional[str]] = mapped_column(String(10))  # ICD-10
    secondary_diagnoses: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    
    # Chart Completeness
    completeness_score: Mapped[Optional[float]] = mapped_column(Float)
    completeness_breakdown: Mapped[Optional[str]] = mapped_column(Text)  # JSON
```

##### Code Suggestion Model
**File**: [`backend/app/models/coding.py`](../../backend/app/models/coding.py)  
**Lines**: 1-100  
**Purpose**: AI code suggestions and acceptance tracking

```python
class CodeSuggestion(Base):
    """AI-generated code suggestions with DRG impact."""
    __tablename__ = "code_suggestions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    encounter_id: Mapped[int] = mapped_column(ForeignKey("encounters.id"))
    suggested_code: Mapped[str] = mapped_column(String(10))  # ICD-10
    confidence_score: Mapped[float] = mapped_column(Float)
    evidence_text: Mapped[str] = mapped_column(Text)
    
    # DRG Impact
    current_rw: Mapped[Optional[float]] = mapped_column(Float)
    suggested_rw: Mapped[Optional[float]] = mapped_column(Float)
    revenue_impact_thb: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Workflow Status
    status: Mapped[str] = mapped_column(String(20))  # PENDING/ACCEPTED/REJECTED
    reviewed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
```

#### Database Configuration

##### Database Connection
**File**: [`backend/app/db/database.py`](../../backend/app/db/database.py)  
**Lines**: 1-30  
**Purpose**: SQLAlchemy database configuration and connection management

```python
# Database URL from environment
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

##### Data Seeding
**File**: [`backend/app/db/seed.py`](../../backend/app/db/seed.py)  
**Lines**: 1-500+  
**Purpose**: Demo data generation for development and testing

**Seed Data includes**:
- **12 Thai Patients** (Lines 50-150): Realistic Thai names and demographics
- **11 Clinical Encounters** (Lines 200-400): Complete clinical scenarios for CAP, DM, HF
- **20 Chart Completeness Rules** (Lines 450-500): Pre-configured quality rules
- **3 CPG Templates**: Thai Clinical Practice Guidelines implementation

---

### Schema Layer (Pydantic Models)

#### CDS Schemas
**File**: [`backend/app/schemas/cds.py`](../../backend/app/schemas/cds.py)  
**Lines**: 1-100  
**Purpose**: Request/response models for Clinical Decision Support API

```python
class PreDiagnosisRequest(BaseModel):
    """Request model for differential diagnosis generation."""
    symptoms: List[str]
    patient_context: PatientContext
    max_diagnoses: int = 5

class DifferentialDiagnosis(BaseModel):
    """Individual diagnosis with confidence scoring."""
    icd10_code: str
    name: str
    name_thai: str
    confidence_score: float
    clinical_rationale: str
    supporting_evidence: List[str]

class PreDiagnosisResponse(BaseModel):
    """Response with ranked differential diagnoses."""
    diagnoses: List[DifferentialDiagnosis]
    processing_time_ms: int
    knowledge_graph_version: str
```

#### Chart Schemas  
**File**: [`backend/app/schemas/chart.py`](../../backend/app/schemas/chart.py)  
**Lines**: 1-50  
**Purpose**: Chart completeness request/response models

```python
class ChartCompletenessResponse(BaseModel):
    """Chart quality assessment results."""
    overall_score: float  # 0.0-100.0
    category_scores: Dict[str, float]  # Diagnosis, Procedure, Consistency, Documentation
    identified_gaps: List[QualityGap]
    improvement_suggestions: List[str]
```

---

## Frontend Modules

### Application Shell and Layout

#### App Shell Component
**File**: [`frontend/src/components/layout/AppShell.tsx`](../../frontend/src/components/layout/AppShell.tsx)  
**Lines**: 1-100  
**Purpose**: Main application layout with sidebar and header

```tsx
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 overflow-hidden">
        <Header />
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  )
}
```

#### Sidebar Navigation
**File**: [`frontend/src/components/layout/Sidebar.tsx`](../../frontend/src/components/layout/Sidebar.tsx)  
**Lines**: 1-80  
**Purpose**: Navigation menu with route management

**Navigation Structure**:
- **Dashboard** (`/`) - Patient overview and metrics
- **Patients** (`/patients`) - Patient list and search  
- **Analytics** (`/analytics`) - Performance dashboards
- **Admin** (`/admin`) - System configuration

### Page Components

#### Dashboard Page
**File**: [`frontend/src/app/page.tsx`](../../frontend/src/app/page.tsx)  
**Lines**: 1-150  
**Purpose**: Main dashboard with patient overview and key metrics

**Key Features**:
- **Patient List** (Lines 30-80): Recent admissions with chart scores
- **Pending Reviews** (Lines 90-120): Code suggestions awaiting approval
- **Disease Group Summary** (Lines 130-150): CAP/DM/HF statistics

#### Patient Detail Page
**File**: [`frontend/src/app/patients/[id]/page.tsx`](../../frontend/src/app/patients/[id]/page.tsx)  
**Lines**: 1-300+  
**Purpose**: Comprehensive patient view with integrated CDS

**Tab Structure**:

##### CDS Tab (Lines 50-120):
```tsx
<Tabs defaultValue="cds">
  <TabsList>
    <TabsTrigger value="cds">🩺 Clinical Decision Support</TabsTrigger>
    <TabsTrigger value="orders">📋 Order Suggestions</TabsTrigger>
    <TabsTrigger value="completeness">📊 Chart Completeness</TabsTrigger>
    <TabsTrigger value="coding">🔢 Code Suggestions</TabsTrigger>
  </TabsList>
  
  <TabsContent value="cds">
    <PreDiagnosisPanel patientId={params.id} />
    <AdmissionDecisionPanel patientId={params.id} />
  </TabsContent>
</Tabs>
```

##### Order Suggestions Tab (Lines 150-200):
- CPG-compliant order recommendations
- Priority-based ordering (Essential/Recommended/Optional)
- Thai rationale and clinical guidelines

##### Chart Completeness Tab (Lines 220-280):
- Real-time completeness scoring (0-100%)
- Gap identification with suggested improvements
- Rule-based validation results

##### Code Suggestions Tab (Lines 300+):
- AI-powered ICD-10 recommendations  
- DRG/RW impact calculation in THB
- Accept/reject workflow interface

#### Admin Panel
**File**: [`frontend/src/app/admin/page.tsx`](../../frontend/src/app/admin/page.tsx)  
**Lines**: 1-200  
**Purpose**: System administration and configuration

**Admin Functions**:
- **Rules Editor** (Lines 50-100): Chart completeness rule management
- **CPG Templates** (Lines 120-160): Clinical Practice Guideline templates
- **Patient Management** (Lines 180-200): Patient and encounter administration

### UI Component Library

#### Card Components
**File**: [`frontend/src/components/ui/card.tsx`](../../frontend/src/components/ui/card.tsx)  
**Lines**: 1-50  
**Purpose**: Reusable card components for data display

#### Progress Components  
**File**: [`frontend/src/components/ui/progress.tsx`](../../frontend/src/components/ui/progress.tsx)  
**Lines**: 1-30  
**Purpose**: Chart completeness score visualization

#### Badge Components
**File**: [`frontend/src/components/ui/badge.tsx`](../../frontend/src/components/ui/badge.tsx)  
**Lines**: 1-40  
**Purpose**: Status indicators for diagnoses, severity, and workflow states

### Type Definitions

#### TypeScript Types
**File**: [`frontend/src/types/index.ts`](../../frontend/src/types/index.ts)  
**Lines**: 1-150  
**Purpose**: Centralized type definitions for API responses and component props

```typescript
// Patient and clinical data types
export interface Patient {
  id: number
  hn: string  // Hospital Number
  name: string
  name_en?: string
  gender: 'M' | 'F'
  date_of_birth: string
  phone?: string
}

export interface DifferentialDiagnosis {
  icd10_code: string
  name: string
  name_thai: string
  confidence_score: number
  clinical_rationale: string
  supporting_evidence: string[]
}

// Chart completeness types
export interface ChartCompletenessResult {
  overall_score: number
  category_scores: Record<string, number>
  identified_gaps: QualityGap[]
  improvement_suggestions: string[]
}
```

### Utility Functions

#### Utils Library
**File**: [`frontend/src/lib/utils.ts`](../../frontend/src/lib/utils.ts)  
**Lines**: 1-50  
**Purpose**: Common utility functions for styling, formatting, and API calls

```typescript
// Tailwind CSS class merging
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Date formatting for Thai locale
export function formatThaiDate(date: string): string {
  return new Intl.DateTimeFormat('th-TH', {
    year: 'numeric',
    month: 'long', 
    day: 'numeric'
  }).format(new Date(date))
}

// API response handling
export async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, options)
  if (!response.ok) throw new Error(`API Error: ${response.statusText}`)
  return response.json()
}
```

---

## Configuration Modules

### Backend Configuration

#### Core Config
**File**: [`backend/app/core/config.py`](../../backend/app/core/config.py)  
**Lines**: 1-50  
**Purpose**: Centralized application configuration with environment variable management

```python
class Settings(BaseSettings):
    """Application configuration from environment variables."""
    
    # Database Configuration
    database_url: str = "postgresql://chartsense:chartsense_secret_2026@postgres:5432/chartsense_db"
    
    # Redis Configuration  
    redis_url: str = "redis://redis:6379/0"
    
    # Neo4j Configuration
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "chartsense_neo4j_2026"
    
    # Application Settings
    demo_mode: bool = True
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Frontend Configuration

#### Next.js Configuration
**File**: [`frontend/next.config.js`](../../frontend/next.config.js)  
**Lines**: 1-20  
**Purpose**: Next.js build and runtime configuration

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,  // Enable App Router
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  }
}

module.exports = nextConfig
```

#### Tailwind Configuration
**File**: [`frontend/tailwind.config.ts`](../../frontend/tailwind.config.ts)  
**Lines**: 1-50  
**Purpose**: Tailwind CSS customization with shadcn/ui integration

---

## Service Integration Matrix

| Frontend Component | Backend API | Service Layer | Database |
|-------------------|-------------|---------------|-----------|
| Patient Dashboard | `/api/v1/admin/patients` | Admin Service | PostgreSQL |
| CDS Panel | `/api/v1/cds/pre-diagnosis` | GraphRAG Service | Neo4j |
| Order Suggestions | `/api/v1/cds/order-suggestion` | CDS Service | Knowledge Graph |
| Chart Completeness | `/api/v1/chart-completeness/{id}` | Rules Engine | PostgreSQL |
| Code Suggestions | `/api/v1/code-suggestion/{id}` | DRG Service | PostgreSQL |
| Admin Panel | `/api/v1/admin/*` | Admin Service | PostgreSQL |

---

## Module Dependencies

### Backend Dependencies Flow
```mermaid
graph TD
    A[main.py] --> B[API Routers]
    B --> C[Service Layer]
    C --> D[Database Models]
    C --> E[External Services]
    B --> F[Pydantic Schemas]
    D --> G[SQLAlchemy Base]
    C --> H[Business Logic]
    
    subgraph "API Layer"
        B1[cds.py] --> C1[graphrag.py]
        B2[chart.py] --> C2[rules.py] 
        B3[coding.py] --> C3[drg.py]
        B4[admin.py] --> C4[admin_service.py]
    end
    
    subgraph "Data Layer"
        G --> D1[patient.py]
        G --> D2[chart.py] 
        G --> D3[coding.py]
        G --> D4[admin.py]
    end
```

### Frontend Dependencies Flow  
```mermaid
graph TD
    A[layout.tsx] --> B[page.tsx]
    B --> C[Components]
    C --> D[UI Components]
    C --> E[API Calls]
    D --> F[shadcn/ui]
    E --> G[Backend APIs]
    
    subgraph "Pages"
        B1[Dashboard] --> C1[PatientList]
        B2[Patient Detail] --> C2[CDS Panel]
        B3[Admin] --> C3[Rules Editor]
    end
    
    subgraph "Shared"
        F1[Card] --> F2[Badge]
        F2 --> F3[Progress]
        G1[types/index.ts] --> G2[utils.ts]
    end
```

---

*This modules documentation provides comprehensive code-level analysis of ChartSense AI. For architectural overview, see [Architecture Documentation](ARCHITECTURE.md). For API specifications, see [API Reference](API_REFERENCE.md).*

---

**Last Updated**: February 15, 2026  
**Code Analysis Version**: 1.0.0-MVP  
**Lines of Code Analyzed**: 15,000+