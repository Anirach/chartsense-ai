# 🔄 ChartSense AI Data Flow Documentation

**Comprehensive Data Pipeline & Sequence Diagrams**

---

## Table of Contents

1. [Data Flow Overview](#data-flow-overview)
2. [Clinical Decision Support Flow](#clinical-decision-support-flow)
3. [Chart Completeness Processing](#chart-completeness-processing)
4. [Code Suggestion Pipeline](#code-suggestion-pipeline)
5. [Knowledge Graph Integration](#knowledge-graph-integration)
6. [Real-time Processing](#real-time-processing)
7. [Data Persistence Patterns](#data-persistence-patterns)

---

## Data Flow Overview

ChartSense AI implements a **multi-tier data processing architecture** with clear separation between transactional data (PostgreSQL), graph-based medical knowledge (Neo4j), and high-performance caching (Redis).

### System Data Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        A[Hospital Information System<br/>HL7/FHIR]
        B[Manual Data Entry<br/>Web Interface]
        C[Clinical Documentation<br/>Thai Text]
    end

    subgraph "Data Processing Layer"
        D[FastAPI Data Ingestion<br/>Validation & Normalization]
        E[Thai NLP Service<br/>Entity Extraction]
        F[Clinical Rules Engine<br/>Quality Assessment]
        G[GraphRAG Service<br/>Knowledge Inference]
    end

    subgraph "Data Storage Layer"
        H[(PostgreSQL<br/>Transactional Data)]
        I[(Neo4j<br/>Medical Knowledge Graph)]
        J[(Redis<br/>Cache & Sessions)]
    end

    subgraph "Data Consumers"
        K[Web Dashboard<br/>Real-time Updates]
        L[API Clients<br/>3rd Party Integration]
        M[Analytics Engine<br/>Reporting]
    end

    A --> D
    B --> D
    C --> E
    D --> H
    E --> H
    F --> H
    G --> I
    D --> J
    H --> K
    I --> G
    J --> K
    H --> L
    H --> M

    classDef source fill:#e3f2fd
    classDef processing fill:#f1f8e9
    classDef storage fill:#fff3e0
    classDef consumer fill:#fce4ec

    class A,B,C source
    class D,E,F,G processing
    class H,I,J storage
    class K,L,M consumer
```

---

## Clinical Decision Support Flow

### Pre-Diagnosis Generation Pipeline

The CDS system processes patient symptoms through a sophisticated GraphRAG knowledge traversal pipeline.

```mermaid
sequenceDiagram
    participant Client as Frontend Client
    participant API as FastAPI Server
    participant Cache as Redis Cache
    participant CDS as CDS Service
    participant Graph as Neo4j Knowledge Graph
    participant NLP as Thai NLP Service
    participant DB as PostgreSQL

    Note over Client,DB: Pre-Diagnosis Generation Workflow

    Client->>API: POST /api/v1/cds/pre-diagnosis
    Note right of Client: {symptoms, vitals, labs, patient_context}

    API->>API: Validate request schema
    API->>Cache: Check cached diagnosis
    Note right of Cache: Key: patient_symptoms_hash

    alt Cache Hit
        Cache-->>API: Return cached result
        API-->>Client: Cached differential diagnosis
    else Cache Miss
        API->>CDS: analyze_symptoms(request)
        
        CDS->>NLP: extract_clinical_entities(symptoms)
        NLP-->>CDS: normalized_entities
        
        CDS->>Graph: MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
        Note right of Graph: GraphRAG Query
        Graph-->>CDS: matching_diseases[]
        
        CDS->>CDS: calculate_confidence_scores()
        Note right of CDS: Multi-factor scoring algorithm
        
        CDS->>CDS: rank_by_probability()
        CDS->>CDS: generate_clinical_rationale()
        
        CDS-->>API: differential_diagnoses[]
        API->>Cache: store_result(ttl=300s)
        API->>DB: log_cds_request()
        
        API-->>Client: JSON response with ranked diagnoses
    end

    Note over Client,DB: Average Processing Time: 150-300ms
```

### Order Suggestion Generation

CPG-compliant order suggestions are generated using template-based personalization.

```mermaid
sequenceDiagram
    participant Client as Frontend Client
    participant API as FastAPI Server
    participant CDS as CDS Service
    participant Templates as CPG Templates
    participant Rules as Personalization Rules
    participant DB as PostgreSQL
    participant Cache as Redis Cache

    Note over Client,Cache: Order Suggestion Generation

    Client->>API: POST /api/v1/cds/order-suggestion
    Note right of Client: {diagnosis, patient_context, comorbidities}

    API->>CDS: generate_orders(diagnosis, patient)
    
    CDS->>Templates: get_cpg_template(disease_group)
    Templates-->>CDS: base_order_set[]
    Note right of Templates: Thai CPG 2023 templates
    
    CDS->>Rules: personalize_orders(base_orders, patient)
    Note right of Rules: Age, weight, GFR, allergies
    
    Rules->>Rules: adjust_medication_dosing()
    Rules->>Rules: filter_contraindications()
    Rules->>Rules: add_monitoring_orders()
    
    Rules-->>CDS: personalized_orders[]
    
    CDS->>CDS: categorize_by_priority()
    Note right of CDS: ESSENTIAL, RECOMMENDED, OPTIONAL
    
    CDS->>DB: log_order_suggestions()
    CDS-->>API: order_response
    
    API->>Cache: cache_orders(encounter_id)
    API-->>Client: JSON with prioritized orders

    Note over Client,Cache: Includes Thai rationale and CPG references
```

### Admission Decision Calculation

Risk stratification using validated clinical scoring systems.

```mermaid
flowchart TD
    A[Patient Data Input] --> B[Extract Clinical Parameters]
    
    B --> C[CURB-65 Calculation]
    B --> D[qSOFA Calculation]
    B --> E[Custom Risk Factors]
    
    C --> F{CURB-65 Score}
    F -->|0-1| G[Low Risk<br/>Outpatient Possible]
    F -->|2| H[Moderate Risk<br/>Consider Admission]
    F -->|3-5| I[High Risk<br/>Hospital Admission]
    
    D --> J{qSOFA Score}
    J -->|0-1| K[Low Sepsis Risk]
    J -->|2-3| L[High Sepsis Risk<br/>ICU Consider]
    
    E --> M[Comorbidity Assessment]
    M --> N[Social Factors]
    
    G --> O[Final Recommendation]
    H --> O
    I --> O
    K --> O
    L --> O
    N --> O
    
    O --> P[Generate Clinical Rationale]
    P --> Q[Select Appropriate Ward]
    Q --> R[Return Decision Response]

    classDef input fill:#e3f2fd
    classDef process fill:#f1f8e9
    classDef decision fill:#fff3e0
    classDef output fill:#fce4ec

    class A input
    class B,C,D,E,M,N,P,Q process
    class F,J decision
    class G,H,I,K,L,O,R output
```

---

## Chart Completeness Processing

### Multi-Dimensional Quality Assessment

Chart completeness evaluation uses a sophisticated rule engine with 20+ configurable rules.

```mermaid
sequenceDiagram
    participant Client as Frontend Client
    participant API as FastAPI Server
    participant Rules as Rules Engine
    participant DB as PostgreSQL
    participant Cache as Redis Cache
    participant Config as Rule Configuration

    Note over Client,Config: Chart Completeness Evaluation

    Client->>API: GET /chart-completeness/ENC2026001
    
    API->>Cache: check_cached_score(encounter_id)
    
    alt Cache Hit & Recent
        Cache-->>API: Return cached evaluation
        API-->>Client: Cached completeness score
    else Cache Miss or Expired
        API->>Rules: evaluate_encounter(encounter_id)
        
        Rules->>DB: fetch_encounter_data(encounter_id)
        DB-->>Rules: encounter_details
        
        Rules->>Config: get_active_rules()
        Config-->>Rules: rule_definitions[]
        
        loop For each rule category
            Rules->>Rules: apply_diagnosis_rules()
            Note right of Rules: Principal diagnosis, secondary diagnoses
            
            Rules->>Rules: apply_procedure_rules() 
            Note right of Rules: CPT codes, surgical notes
            
            Rules->>Rules: apply_consistency_rules()
            Note right of Rules: Cross-field validation
            
            Rules->>Rules: apply_documentation_rules()
            Note right of Rules: Required clinical notes
        end
        
        Rules->>Rules: calculate_category_scores()
        Rules->>Rules: calculate_overall_score()
        Rules->>Rules: identify_gaps()
        Rules->>Rules: generate_suggestions()
        
        Rules-->>API: completeness_result
        
        API->>Cache: cache_evaluation(ttl=1800s)
        API->>DB: store_evaluation_log()
        
        API-->>Client: JSON with score & gaps
    end

    Note over Client,Config: Real-time quality feedback
```

### Rule Engine Processing Flow

```mermaid
flowchart TD
    A[Encounter Data] --> B[Rule Engine Initialization]
    
    B --> C[Load Active Rules]
    C --> D[Parse Rule Configuration]
    
    D --> E[Diagnosis Category Rules]
    D --> F[Procedure Category Rules] 
    D --> G[Consistency Category Rules]
    D --> H[Documentation Category Rules]
    
    E --> E1[Principal Diagnosis Check]
    E --> E2[Secondary Diagnoses Validation]
    E --> E3[ICD-10 Code Specificity]
    
    F --> F1[Procedure-Diagnosis Correlation]
    F --> F2[Surgical Documentation]
    F --> F3[CPT Code Completeness]
    
    G --> G1[Age-Appropriate Vitals]
    G --> G2[Lab-Diagnosis Correlation]
    G --> G3[Medication Consistency]
    
    H --> H1[Progress Notes Completeness]
    H --> H2[Discharge Summary]
    H --> H3[Clinical Documentation]
    
    E1 --> I[Category Score Calculation]
    E2 --> I
    E3 --> I
    F1 --> I
    F2 --> I
    F3 --> I
    G1 --> I
    G2 --> I
    G3 --> I
    H1 --> I
    H2 --> I
    H3 --> I
    
    I --> J[Weighted Score Aggregation]
    J --> K[Overall Score Calculation]
    K --> L[Gap Identification]
    L --> M[Suggestion Generation]
    M --> N[Final Report]

    classDef input fill:#e3f2fd
    classDef category fill:#f1f8e9
    classDef rule fill:#fff3e0
    classDef output fill:#fce4ec

    class A input
    class E,F,G,H category
    class E1,E2,E3,F1,F2,F3,G1,G2,G3,H1,H2,H3 rule
    class I,J,K,L,M,N output
```

---

## Code Suggestion Pipeline

### AI-Powered ICD-10 Code Generation

The code suggestion system combines NLP analysis with DRG impact calculation.

```mermaid
sequenceDiagram
    participant Client as Frontend Client
    participant API as FastAPI Server
    participant Coding as Coding Service
    participant NLP as Thai NLP Service
    participant DRG as DRG Calculator
    participant DB as PostgreSQL
    participant Cache as Redis Cache

    Note over Client,Cache: Code Suggestion Generation

    Client->>API: POST /code-suggestion/ENC2026001/generate
    
    API->>Coding: generate_suggestions(encounter_id)
    
    Coding->>DB: fetch_encounter_clinical_data()
    DB-->>Coding: clinical_documentation
    
    Coding->>NLP: extract_medical_entities(thai_text)
    NLP->>NLP: tokenize_thai_text()
    NLP->>NLP: match_medical_terminology()
    NLP-->>Coding: medical_entities[]
    
    Coding->>Coding: map_entities_to_icd10()
    Coding->>Coding: rank_by_confidence()
    
    loop For each suggested code
        Coding->>DRG: calculate_rw_impact(current_codes, suggested_code)
        DRG->>DRG: apply_drg_logic()
        DRG->>DRG: calculate_reimbursement()
        DRG-->>Coding: rw_impact_data
    end
    
    Coding->>Coding: compile_evidence_trails()
    Coding->>Coding: generate_clinical_rationale()
    
    Coding->>DB: store_suggestions()
    Coding-->>API: suggestion_response
    
    API->>Cache: cache_suggestions(encounter_id)
    API-->>Client: JSON with codes & revenue impact

    Note over Client,Cache: Includes confidence scores and evidence
```

### DRG Impact Calculation Flow

```mermaid
flowchart TD
    A[Current ICD-10 Codes] --> B[DRG Grouper Logic]
    C[Suggested Additional Codes] --> B
    
    B --> D[Calculate Current DRG]
    B --> E[Calculate Proposed DRG]
    
    D --> F[Current Relative Weight]
    E --> G[Proposed Relative Weight]
    
    F --> H[Current Reimbursement<br/>THB Calculation]
    G --> I[Proposed Reimbursement<br/>THB Calculation]
    
    H --> J[Revenue Impact Analysis]
    I --> J
    
    J --> K{Impact Assessment}
    K -->|Positive| L[Revenue Increase]
    K -->|Neutral| M[No Financial Impact]
    K -->|Negative| N[Revenue Decrease]
    
    L --> O[Risk Assessment]
    M --> O
    N --> O
    
    O --> P[Audit Risk Evaluation]
    P --> Q[Final Recommendation]
    
    Q --> R[Present to Medical Coder]

    classDef input fill:#e3f2fd
    classDef process fill:#f1f8e9
    classDef decision fill:#fff3e0
    classDef output fill:#fce4ec

    class A,C input
    class B,D,E,F,G,H,I,J,O,P process
    class K decision
    class L,M,N,Q,R output
```

---

## Knowledge Graph Integration

### Medical Knowledge Graph Structure

The Neo4j knowledge graph stores medical relationships and enables GraphRAG queries.

```mermaid
graph TD
    subgraph "Disease Nodes"
        A[Disease: J18.9<br/>CAP]
        B[Disease: E11.65<br/>DM Hyperglycemia]
        C[Disease: I50.9<br/>Heart Failure]
    end

    subgraph "Symptom Nodes"
        D[Symptom: Fever]
        E[Symptom: Cough]
        F[Symptom: Dyspnea]
        G[Symptom: Polyuria]
        H[Symptom: Chest Pain]
    end

    subgraph "Lab Test Nodes"
        I[Lab: CBC]
        J[Lab: CRP]
        K[Lab: FBS]
        L[Lab: HbA1c]
        M[Lab: BNP]
    end

    subgraph "Risk Factor Nodes"
        N[Risk: Age >65]
        O[Risk: Diabetes]
        P[Risk: Hypertension]
        Q[Risk: Smoking]
    end

    subgraph "Treatment Nodes"
        R[Treatment: Antibiotics]
        S[Treatment: Insulin]
        T[Treatment: ACE Inhibitor]
    end

    A -->|HAS_SYMPTOM| D
    A -->|HAS_SYMPTOM| E
    A -->|HAS_SYMPTOM| F
    A -->|REQUIRES_LAB| I
    A -->|REQUIRES_LAB| J
    A -->|RISK_FACTOR| N
    A -->|RISK_FACTOR| O
    A -->|TREATED_WITH| R

    B -->|HAS_SYMPTOM| G
    B -->|HAS_SYMPTOM| F
    B -->|REQUIRES_LAB| K
    B -->|REQUIRES_LAB| L
    B -->|TREATED_WITH| S

    C -->|HAS_SYMPTOM| F
    C -->|HAS_SYMPTOM| H
    C -->|REQUIRES_LAB| M
    C -->|RISK_FACTOR| P
    C -->|TREATED_WITH| T

    O -->|INCREASES_RISK| A
    O -->|INCREASES_RISK| C

    classDef disease fill:#ffcdd2
    classDef symptom fill:#c8e6c9
    classDef lab fill:#fff3e0
    classDef risk fill:#e1bee7
    classDef treatment fill:#bbdefb

    class A,B,C disease
    class D,E,F,G,H symptom
    class I,J,K,L,M lab
    class N,O,P,Q risk
    class R,S,T treatment
```

### GraphRAG Query Processing

```mermaid
sequenceDiagram
    participant CDS as CDS Service
    participant Graph as Neo4j Database
    participant Cache as Redis Cache

    Note over CDS,Cache: Knowledge Graph Query Processing

    CDS->>Cache: check_query_cache(symptoms_hash)
    
    alt Cache Hit
        Cache-->>CDS: Return cached results
    else Cache Miss
        CDS->>Graph: Begin transaction
        
        CDS->>Graph: MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
        Note right of Graph: Primary symptom matching
        
        CDS->>Graph: WHERE s.name IN $symptoms
        Graph-->>CDS: matching_diseases[]
        
        CDS->>Graph: MATCH (d:Disease)-[:RISK_FACTOR]->(r:Risk)
        Note right of Graph: Risk factor evaluation
        Graph-->>CDS: risk_relationships[]
        
        CDS->>Graph: MATCH (d:Disease)-[:REQUIRES_LAB]->(l:Lab)
        Note right of Graph: Supporting lab tests
        Graph-->>CDS: recommended_labs[]
        
        CDS->>Graph: MATCH (d:Disease)-[:CAN_CAUSE]->(c:Complication)
        Note right of Graph: Potential complications
        Graph-->>CDS: complications[]
        
        CDS->>Graph: Commit transaction
        
        CDS->>Cache: store_query_result(ttl=300s)
    end
    
    CDS->>CDS: aggregate_graph_results()
    CDS->>CDS: calculate_disease_scores()
    
    Note over CDS,Cache: Optimized graph traversal with caching
```

---

## Real-time Processing

### WebSocket Data Streaming

For real-time dashboard updates and live chart completeness scoring.

```mermaid
sequenceDiagram
    participant Client as Web Client
    participant WS as WebSocket Server
    participant API as FastAPI Server
    participant DB as PostgreSQL
    participant Cache as Redis Cache

    Note over Client,Cache: Real-time Data Streaming

    Client->>WS: WebSocket connection
    WS-->>Client: Connection established
    
    Client->>WS: Subscribe to encounter updates
    WS->>Cache: register_subscription(client_id, encounter_id)
    
    Note over Client,Cache: Background processing...
    
    API->>DB: Update encounter data
    API->>Cache: publish_update(encounter_id, update_data)
    
    Cache->>WS: Notification: encounter_updated
    WS->>WS: check_subscriptions(encounter_id)
    
    WS-->>Client: Real-time update
    Note right of Client: Chart score: 85.5% → 88.2%
    
    Client->>Client: Update UI components
    
    Note over Client,Cache: Continuous real-time updates
```

### Event-Driven Architecture

```mermaid
flowchart TD
    A[Clinical Data Update] --> B[Event Publisher]
    
    B --> C[Chart Completeness Event]
    B --> D[Code Suggestion Event]
    B --> E[CDS Update Event]
    
    C --> F[Rules Engine Processor]
    D --> G[Coding Service Processor]
    E --> H[Knowledge Graph Processor]
    
    F --> I[Update Chart Score]
    G --> J[Generate New Codes]
    H --> K[Refresh Diagnoses]
    
    I --> L[Notification Service]
    J --> L
    K --> L
    
    L --> M[WebSocket Broadcast]
    L --> N[Email Notifications]
    L --> O[Dashboard Updates]
    
    M --> P[Real-time UI Updates]
    N --> Q[Clinical Staff Alerts]
    O --> R[Management Reports]

    classDef event fill:#e3f2fd
    classDef processor fill:#f1f8e9
    classDef output fill:#fce4ec

    class A,C,D,E event
    class F,G,H,I,J,K,L processor
    class M,N,O,P,Q,R output
```

---

## Data Persistence Patterns

### Multi-Database Data Distribution

```mermaid
erDiagram
    PATIENTS ||--o{ ENCOUNTERS : has
    ENCOUNTERS ||--o{ CHART_COMPLETENESS : evaluated
    ENCOUNTERS ||--o{ CODE_SUGGESTIONS : generates
    ENCOUNTERS ||--o{ CDS_REQUESTS : triggers
    
    PATIENTS {
        int id PK
        string hn UK
        string name
        string name_en
        char gender
        date date_of_birth
        string phone
        timestamp created_at
        timestamp updated_at
    }
    
    ENCOUNTERS {
        int id PK
        int patient_id FK
        string visit_number UK
        datetime admission_date
        datetime discharge_date
        text chief_complaint
        text present_illness
        string principal_diagnosis
        json secondary_diagnoses
        float completeness_score
        json completeness_breakdown
        timestamp created_at
        timestamp updated_at
    }
    
    CHART_COMPLETENESS {
        int id PK
        int encounter_id FK
        float total_score
        string grade
        json category_breakdown
        json identified_gaps
        timestamp evaluated_at
    }
    
    CODE_SUGGESTIONS {
        int id PK
        int encounter_id FK
        string suggested_code
        string dx_type
        float confidence_score
        json evidence_trail
        float rw_impact
        string status
        int reviewed_by FK
        timestamp reviewed_at
        timestamp created_at
    }
    
    CDS_REQUESTS {
        int id PK
        int encounter_id FK
        string request_type
        json input_data
        json output_data
        int processing_time_ms
        timestamp created_at
    }
```

### Caching Strategy

```mermaid
flowchart TD
    A[API Request] --> B{Cache Check}
    
    B -->|Hit| C[Return Cached Data]
    B -->|Miss| D[Process Request]
    
    D --> E[Database Query]
    E --> F[Business Logic]
    F --> G[Generate Response]
    
    G --> H[Store in Cache]
    H --> I[Return Response]
    
    C --> J[Update Cache TTL]
    I --> K[Log Performance Metrics]
    J --> K
    
    subgraph "Cache Layers"
        L[Application Cache<br/>In-Memory]
        M[Redis Cache<br/>Distributed]
        N[Database Query Cache<br/>PostgreSQL]
    end
    
    H --> L
    H --> M
    E --> N

    classDef cache fill:#fff3e0
    classDef process fill:#f1f8e9
    classDef data fill:#e3f2fd

    class B,C,H,J,L,M,N cache
    class D,F,G,K process
    class A,E,I data
```

### Data Lifecycle Management

```mermaid
gantt
    title Data Lifecycle in ChartSense AI
    dateFormat YYYY-MM-DD
    section Patient Data
    Active Records     :active, patient-active, 2026-01-01, 2026-12-31
    Archived Records   :archive, after patient-active, 365d
    
    section Clinical Data
    Real-time Processing :crit, clinical-rt, 2026-01-01, 1d
    Short-term Cache     :cache-st, 2026-01-01, 30d
    Long-term Storage    :storage-lt, 2026-01-01, 2031-12-31
    
    section Analytics
    Daily Aggregation    :daily, 2026-01-01, 365d
    Monthly Reports      :monthly, 2026-01-01, 2026-12-31
    Annual Archives      :yearly, 2026-01-01, 2031-12-31
    
    section Compliance
    Audit Logs          :audit, 2026-01-01, 2033-12-31
    Privacy Anonymization :privacy, 2026-01-01, 90d
```

---

## Performance Optimization

### Query Optimization Patterns

```mermaid
flowchart TD
    A[Incoming Request] --> B{Request Type}
    
    B -->|CDS| C[Knowledge Graph Query]
    B -->|Chart| D[Rules Engine Query]
    B -->|Coding| E[NLP + DRG Query]
    
    C --> F[Neo4j Optimization]
    D --> G[PostgreSQL Optimization]
    E --> H[Hybrid Optimization]
    
    F --> F1[Index Management]
    F --> F2[Query Caching]
    F --> F3[Connection Pooling]
    
    G --> G1[B-tree Indexes]
    G --> G2[Partial Indexes]
    G --> G3[Query Planner]
    
    H --> H1[Result Caching]
    H --> H2[Async Processing]
    H --> H3[Batch Operations]
    
    F1 --> I[Response Generation]
    F2 --> I
    F3 --> I
    G1 --> I
    G2 --> I
    G3 --> I
    H1 --> I
    H2 --> I
    H3 --> I
    
    I --> J[Performance Monitoring]
    J --> K[Response Delivery]

    classDef query fill:#e3f2fd
    classDef optimize fill:#f1f8e9
    classDef technique fill:#fff3e0

    class A,B query
    class C,D,E,F,G,H optimize
    class F1,F2,F3,G1,G2,G3,H1,H2,H3 technique
```

---

*This data flow documentation provides comprehensive insight into ChartSense AI's data processing pipelines. For implementation details, see the [Modules Documentation](MODULES.md) and [Setup Guide](SETUP.md).*

---

**Last Updated**: February 15, 2026  
**Data Flow Version**: 1.0.0-MVP  
**Average Processing Time**: 150-300ms per request