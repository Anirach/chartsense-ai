# 📡 ChartSense AI API Reference

**Complete REST API Documentation with Request/Response Examples**

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Clinical Decision Support APIs](#clinical-decision-support-apis)
3. [Chart Completeness APIs](#chart-completeness-apis)
4. [Code Suggestion APIs](#code-suggestion-apis)
5. [Admin APIs](#admin-apis)
6. [Authentication & Security](#authentication--security)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## API Overview

### Base URL
```
Production: https://chartsense-ai.example.com/api/v1
Development: http://localhost:8000/api/v1
```

### Content Type
All APIs accept and return JSON with UTF-8 encoding:
```http
Content-Type: application/json; charset=utf-8
Accept: application/json
```

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Response Format
All successful responses follow this structure:
```json
{
  "data": { /* API-specific response data */ },
  "status": "success",
  "timestamp": "2026-02-15T12:43:00Z",
  "processing_time_ms": 150
}
```

---

## Clinical Decision Support APIs

### Pre-Diagnosis Generation

Generate differential diagnoses using GraphRAG knowledge graph traversal.

#### `POST /api/v1/cds/pre-diagnosis`

**Request Schema** ([`backend/app/schemas/cds.py:25-35`](../../backend/app/schemas/cds.py#L25-35)):

```json
{
  "symptoms": ["fever", "cough", "dyspnea", "chest_pain"],
  "vitals": {
    "temperature": 38.5,
    "heart_rate": 95,
    "respiratory_rate": 22,
    "systolic_bp": 130,
    "diastolic_bp": 80,
    "spo2": 92.0,
    "gcs": 15
  },
  "labs": [
    {
      "code": "WBC",
      "value": 15000,
      "unit": "cells/μL"
    },
    {
      "code": "CRP",
      "value": 120,
      "unit": "mg/L"
    }
  ],
  "pmh": ["diabetes", "hypertension"],
  "age": 65,
  "sex": "M",
  "chief_complaint": "Cough and fever for 3 days"
}
```

**Response Schema** ([`backend/app/schemas/cds.py:45-60`](../../backend/app/schemas/cds.py#L45-60)):

```json
{
  "differentials": [
    {
      "rank": 1,
      "icd_code": "J18.9",
      "description": "Community-Acquired Pneumonia",
      "description_th": "ปอดอักเสบชุมชน",
      "probability": 0.85,
      "reasoning": "High fever, productive cough, dyspnea, and elevated WBC/CRP strongly suggest bacterial pneumonia. Age >65 and diabetes are additional risk factors.",
      "evidence": [
        "Fever >38°C (38.5°C)",
        "Productive cough with dyspnea",
        "Elevated WBC count (15,000)",
        "Elevated CRP (120 mg/L)",
        "Age >65 years",
        "Diabetes mellitus (risk factor)"
      ],
      "cpg_reference": "Thai CPG Community-Acquired Pneumonia 2023"
    },
    {
      "rank": 2,
      "icd_code": "J06.9",
      "description": "Acute upper respiratory infection",
      "description_th": "การติดเชื้อระบบทางเดินหายใจส่วนต้นเฉียบพลัน",
      "probability": 0.15,
      "reasoning": "Fever and cough could indicate viral upper respiratory infection, but elevated inflammatory markers suggest bacterial infection.",
      "evidence": [
        "Fever and cough symptoms",
        "But: High CRP suggests bacterial cause",
        "But: Dyspnea suggests lower respiratory involvement"
      ],
      "cpg_reference": null
    }
  ],
  "primary_disease_group": "CAP",
  "confidence_note": "High confidence diagnosis based on classic symptoms, lab findings, and patient risk factors. Recommend chest X-ray for confirmation."
}
```

### Order Suggestions

Generate CPG-compliant clinical orders based on diagnosis.

#### `POST /api/v1/cds/order-suggestion`

**Request Schema** ([`backend/app/schemas/cds.py:75-85`](../../backend/app/schemas/cds.py#L75-85)):

```json
{
  "encounter_id": "ENC2026001",
  "primary_dx": "Community-Acquired Pneumonia",
  "icd_code": "J18.9",
  "age": 65,
  "sex": "M",
  "comorbidities": ["diabetes", "hypertension"],
  "creatinine": 1.2,
  "gfr": 70
}
```

**Response Schema** ([`backend/app/schemas/cds.py:90-105`](../../backend/app/schemas/cds.py#L90-105)):

```json
{
  "orders": [
    {
      "category": "LAB",
      "code": "CBC",
      "display_name": "Complete Blood Count",
      "priority": "ESSENTIAL",
      "rationale": "ประเมินการติดเชื้อ (WBC, Neutrophil count)",
      "cpg_source": "Thai CPG Community-Acquired Pneumonia 2023"
    },
    {
      "category": "LAB",
      "code": "BUN_Cr",
      "display_name": "BUN/Creatinine",
      "priority": "ESSENTIAL",
      "rationale": "ประเมินไต (CURB-65 component), adjust antibiotic dosing",
      "cpg_source": "Thai CPG Community-Acquired Pneumonia 2023"
    },
    {
      "category": "IMAGING",
      "code": "CXR_PA",
      "display_name": "Chest X-ray PA upright",
      "priority": "ESSENTIAL",
      "rationale": "ยืนยัน infiltrate, ประเมิน severity และ complications",
      "cpg_source": "Thai CPG Community-Acquired Pneumonia 2023"
    },
    {
      "category": "MEDICATION",
      "code": "Ceftriaxone",
      "display_name": "Ceftriaxone 2g IV q24h",
      "priority": "ESSENTIAL",
      "rationale": "Empiric antibiotic สำหรับ CAP (dose adjusted for GFR 70)",
      "cpg_source": "Thai CPG Community-Acquired Pneumonia 2023"
    },
    {
      "category": "MEDICATION",
      "code": "Azithromycin",
      "display_name": "Azithromycin 500mg IV/PO qd x 5 days",
      "priority": "ESSENTIAL",
      "rationale": "Atypical pathogen coverage (Mycoplasma, Legionella)",
      "cpg_source": "Thai CPG Community-Acquired Pneumonia 2023"
    }
  ],
  "disease_group": "CAP",
  "personalization_notes": [
    "Antibiotic dosing adjusted for GFR 70 mL/min/1.73m²",
    "Monitor blood sugar closely due to diabetes",
    "Consider ACE inhibitor hold if hypotensive"
  ]
}
```

### Admission Decision Support

Calculate risk scores and generate admission recommendations.

#### `POST /api/v1/cds/admission-decision`

**Request Schema** ([`backend/app/schemas/cds.py:110-125`](../../backend/app/schemas/cds.py#L110-125)):

```json
{
  "encounter_id": "ENC2026001",
  "primary_dx": "Community-Acquired Pneumonia",
  "icd_code": "J18.9",
  "vitals": {
    "temperature": 38.5,
    "heart_rate": 95,
    "respiratory_rate": 22,
    "systolic_bp": 130,
    "diastolic_bp": 80,
    "spo2": 92.0,
    "gcs": 15
  },
  "labs": [
    {
      "code": "BUN",
      "value": 25,
      "unit": "mg/dL"
    }
  ],
  "age": 65,
  "confusion": false,
  "urea": 25.0,
  "nursing_home": false
}
```

**Response Schema** ([`backend/app/schemas/cds.py:140-155`](../../backend/app/schemas/cds.py#L140-155)):

```json
{
  "recommendation": "ADMIT",
  "risk_level": "MODERATE",
  "risk_scores": [
    {
      "tool_name": "CURB-65",
      "score": 2,
      "max_score": 5,
      "components": {
        "confusion": 0,
        "urea": 1,
        "respiratory_rate": 0,
        "blood_pressure": 0,
        "age": 1
      },
      "interpretation": "Moderate risk - Consider admission",
      "mortality_risk": "1.5-3.2%"
    },
    {
      "tool_name": "qSOFA",
      "score": 1,
      "max_score": 3,
      "components": {
        "altered_mental_status": 0,
        "systolic_bp": 0,
        "respiratory_rate": 1
      },
      "interpretation": "Low-moderate risk for sepsis",
      "mortality_risk": null
    }
  ],
  "reasoning": "CURB-65 score of 2 indicates moderate risk with 1.5-3.2% mortality. Patient has age >65 and elevated urea (>19 mg/dL). Respiratory rate >22/min contributes to qSOFA score. Recommend hospital admission for monitoring and IV antibiotics.",
  "suggested_ward": "General Medical Ward"
}
```

---

## Chart Completeness APIs

### Chart Quality Evaluation

Assess chart completeness using 20+ configurable rules across 4 dimensions.

#### `GET /api/v1/chart-completeness/{encounter_id}`

**Path Parameters**:
- `encounter_id` (string): Unique encounter identifier

**Query Parameters**:
- `force_refresh` (boolean, optional): Force re-evaluation instead of cached result

**Example Request**:
```http
GET /api/v1/chart-completeness/ENC2026001?force_refresh=true
```

**Response Schema** ([`backend/app/schemas/chart.py:20-35`](../../backend/app/schemas/chart.py#L20-35)):

```json
{
  "encounter_id": "ENC2026001",
  "total_score": 85.5,
  "grade": "B+",
  "breakdown": [
    {
      "category": "Diagnosis",
      "score": 18.0,
      "max_score": 20.0,
      "weight": 0.30,
      "items_found": 9,
      "items_expected": 10
    },
    {
      "category": "Procedure", 
      "score": 15.0,
      "max_score": 15.0,
      "weight": 0.20,
      "items_found": 3,
      "items_expected": 3
    },
    {
      "category": "Consistency",
      "score": 22.5,
      "max_score": 25.0,
      "weight": 0.25,
      "items_found": 9,
      "items_expected": 10
    },
    {
      "category": "Documentation",
      "score": 30.0,
      "max_score": 30.0,
      "weight": 0.25,
      "items_found": 12,
      "items_expected": 12
    }
  ],
  "gaps": [
    {
      "rule_id": "DX_SECONDARY_COMPLETE",
      "category": "Diagnosis",
      "description": "Secondary diagnoses should include all active comorbidities",
      "severity": "MODERATE",
      "suggested_action": "Consider adding ICD-10 codes for documented diabetes and hypertension",
      "suggested_code": "E11.9, I10"
    },
    {
      "rule_id": "CONSISTENCY_LAB_DX_CORRELATION",
      "category": "Consistency", 
      "description": "Lab values should correlate with documented diagnoses",
      "severity": "LOW",
      "suggested_action": "Document relationship between elevated WBC (15,000) and pneumonia diagnosis",
      "suggested_code": null
    }
  ],
  "evaluated_at": "2026-02-15T12:43:15.123Z"
}
```

### Chart Evaluation Trigger

Manually trigger chart completeness evaluation.

#### `POST /api/v1/chart-completeness/evaluate`

**Request Schema** ([`backend/app/schemas/chart.py:40-45`](../../backend/app/schemas/chart.py#L40-45)):

```json
{
  "encounter_id": "ENC2026001",
  "force_refresh": true
}
```

**Response**: Same as GET endpoint above.

---

## Code Suggestion APIs

### Generate Code Suggestions

Generate AI-powered ICD-10 code suggestions with DRG impact analysis.

#### `POST /api/v1/code-suggestion/{encounter_id}/generate`

**Path Parameters**:
- `encounter_id` (string): Unique encounter identifier

**Example Request**:
```http
POST /api/v1/code-suggestion/ENC2026001/generate
```

**Response Schema** ([`backend/app/schemas/coding.py:10-25`](../../backend/app/schemas/coding.py#L10-25)):

```json
{
  "encounter_id": "ENC2026001",
  "suggestions": [
    {
      "id": 1001,
      "icd_code": "J18.9",
      "description": "Pneumonia, unspecified organism",
      "dx_type": "PRINCIPAL",
      "confidence": 0.92,
      "evidence": [
        "Chief complaint: Cough and fever for 3 days",
        "Physical exam: Crackles in right lower lobe",
        "Lab: WBC 15,000, CRP 120 mg/L",
        "CXR: Right lower lobe infiltrate"
      ],
      "rw_impact": 0.8524,
      "status": "PENDING"
    },
    {
      "id": 1002,
      "icd_code": "E11.9", 
      "description": "Type 2 diabetes mellitus without complications",
      "dx_type": "SECONDARY",
      "confidence": 0.95,
      "evidence": [
        "PMH: Diabetes mellitus documented",
        "Current medications: Metformin 500mg BID",
        "Last HbA1c: 7.2% (3 months ago)"
      ],
      "rw_impact": 0.1245,
      "status": "PENDING"
    },
    {
      "id": 1003,
      "icd_code": "I10",
      "description": "Essential hypertension", 
      "dx_type": "SECONDARY",
      "confidence": 0.88,
      "evidence": [
        "PMH: Hypertension documented",
        "Current medications: Lisinopril 10mg daily",
        "BP on admission: 145/90 mmHg"
      ],
      "rw_impact": 0.0856,
      "status": "PENDING"
    }
  ],
  "rw_before": 0.6854,
  "rw_after": 1.2479,
  "rw_delta": 0.5625,
  "revenue_impact_thb": 28500.0,
  "drg": "DRG-089 Simple Pneumonia & Pleurisy with CC"
}
```

### Accept Code Suggestions

Accept AI code suggestions and update encounter coding.

#### `POST /api/v1/code-suggestion/{encounter_id}/accept`

**Path Parameters**:
- `encounter_id` (string): Unique encounter identifier

**Request Schema** ([`backend/app/schemas/coding.py:30-35`](../../backend/app/schemas/coding.py#L30-35)):

```json
{
  "suggestion_ids": [1001, 1002, 1003]
}
```

**Response**:

```json
{
  "status": "accepted",
  "encounter_id": "ENC2026001", 
  "accepted_codes": ["J18.9", "E11.9", "I10"],
  "revenue_impact": {
    "rw_before": 0.6854,
    "rw_after": 1.2479,
    "rw_delta": 0.5625,
    "revenue_change_thb": 28500.0,
    "drg_before": "DRG-195 Simple Pneumonia without CC/MCC",
    "drg_after": "DRG-089 Simple Pneumonia & Pleurisy with CC"
  },
  "updated_at": "2026-02-15T12:45:30.456Z"
}
```

### Reject Code Suggestions

Reject specific code suggestions with reason.

#### `POST /api/v1/code-suggestion/{encounter_id}/reject`

**Request**:

```json
{
  "suggestion_ids": [1003],
  "rejection_reason": "Hypertension not actively managed during this admission"
}
```

**Response**:

```json
{
  "status": "rejected",
  "encounter_id": "ENC2026001",
  "rejected_codes": ["I10"],
  "rejection_reason": "Hypertension not actively managed during this admission",
  "rejected_at": "2026-02-15T12:46:15.789Z"
}
```

---

## Admin APIs

### Rule Management

#### List Chart Completeness Rules

**GET /api/v1/admin/rules**

**Query Parameters**:
- `category` (string, optional): Filter by rule category (Diagnosis, Procedure, Consistency, Documentation)
- `active` (boolean, optional): Filter by active status
- `limit` (integer, optional): Number of rules to return (default: 50)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response**:

```json
{
  "rules": [
    {
      "id": "DX_PRINCIPAL_REQUIRED",
      "name": "Principal Diagnosis Required",
      "category": "Diagnosis",
      "description": "Every encounter must have a principal diagnosis with valid ICD-10 code",
      "weight": 5.0,
      "active": true,
      "created_at": "2026-01-15T10:00:00Z",
      "updated_at": "2026-02-01T14:30:00Z"
    },
    {
      "id": "CONSISTENCY_VITAL_AGE",
      "name": "Age-Appropriate Vital Signs",
      "category": "Consistency", 
      "description": "Vital signs should be within age-appropriate normal ranges",
      "weight": 2.0,
      "active": true,
      "created_at": "2026-01-15T10:00:00Z",
      "updated_at": "2026-01-15T10:00:00Z"
    }
  ],
  "total": 24,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

#### Create New Rule

**POST /api/v1/admin/rules**

**Request**:

```json
{
  "id": "DX_SPECIFICITY_CHECK",
  "name": "Diagnosis Specificity Check",
  "category": "Diagnosis",
  "description": "Diagnoses should be coded to the highest level of specificity available",
  "weight": 3.0,
  "active": true,
  "validation_logic": {
    "type": "icd10_specificity",
    "parameters": {
      "min_digits": 4,
      "allow_unspecified": false
    }
  }
}
```

**Response**:

```json
{
  "id": "DX_SPECIFICITY_CHECK",
  "status": "created",
  "message": "Rule created successfully",
  "created_at": "2026-02-15T12:50:00Z"
}
```

#### Update Rule

**PUT /api/v1/admin/rules/{rule_id}**

**Request**:

```json
{
  "weight": 4.0,
  "active": false,
  "description": "Updated description for diagnosis specificity validation"
}
```

**Response**:

```json
{
  "id": "DX_SPECIFICITY_CHECK", 
  "status": "updated",
  "message": "Rule updated successfully",
  "updated_at": "2026-02-15T12:55:00Z"
}
```

### CPG Template Management

#### List CPG Templates

**GET /api/v1/admin/templates**

**Response**:

```json
{
  "templates": [
    {
      "id": "CAP_THAILAND_2023",
      "name": "Community-Acquired Pneumonia - Thai CPG 2023",
      "disease_group": "CAP",
      "version": "2023.1",
      "active": true,
      "order_sets": {
        "essential": 8,
        "recommended": 6,
        "optional": 4
      },
      "created_at": "2026-01-15T10:00:00Z"
    },
    {
      "id": "DM_COMPLICATIONS_2023",
      "name": "Diabetes Mellitus Complications - Thai CPG 2023",
      "disease_group": "DM",
      "version": "2023.1", 
      "active": true,
      "order_sets": {
        "essential": 10,
        "recommended": 8,
        "optional": 5
      },
      "created_at": "2026-01-15T10:00:00Z"
    }
  ]
}
```

### Patient & Encounter Management

#### List Patients

**GET /api/v1/admin/patients**

**Query Parameters**:
- `search` (string, optional): Search by name or HN
- `limit` (integer, optional): Results per page (default: 20)
- `offset` (integer, optional): Pagination offset

**Response**:

```json
{
  "patients": [
    {
      "id": 1,
      "hn": "HN2026001",
      "name": "สมชาย ใจดี",
      "name_en": "Somchai Jaidee",
      "gender": "M",
      "date_of_birth": "1958-03-15",
      "age": 67,
      "phone": "081-234-5678",
      "encounter_count": 3,
      "last_admission": "2026-02-10T08:30:00Z"
    }
  ],
  "total": 12,
  "limit": 20,
  "offset": 0
}
```

#### Get Encounter Details

**GET /api/v1/admin/encounters/{encounter_id}**

**Response**:

```json
{
  "id": "ENC2026001",
  "patient": {
    "id": 1,
    "hn": "HN2026001",
    "name": "สมชาย ใจดี",
    "age": 67,
    "gender": "M"
  },
  "visit_number": "V2026-02-001",
  "admission_date": "2026-02-10T08:30:00Z",
  "discharge_date": null,
  "status": "ACTIVE",
  "chief_complaint": "มีไข้ไอ เจ็บหน้าอก 3 วัน",
  "present_illness": "ผู้ป่วยมีอาการไข้สูง ไอมีเสมหะ หายใจลำบาก มา 3 วัน...",
  "principal_diagnosis": {
    "icd_code": "J18.9",
    "description": "Pneumonia, unspecified organism",
    "description_th": "ปอดอักเสบ ไม่ระบุเชื้อก่อโรค"
  },
  "secondary_diagnoses": [
    {
      "icd_code": "E11.9", 
      "description": "Type 2 diabetes mellitus without complications"
    }
  ],
  "completeness_score": 85.5,
  "code_suggestions": {
    "pending": 2,
    "accepted": 1,
    "rejected": 0
  }
}
```

---

## Authentication & Security

### API Key Authentication

All API requests require authentication via API key in the header:

```http
Authorization: Bearer your_api_key_here
X-API-Key: your_api_key_here
```

### Session-Based Authentication

For web interface, session-based authentication using cookies:

```http
Cookie: sessionid=your_session_cookie
```

### CORS Policy

The API supports cross-origin requests from approved domains:

```http
Access-Control-Allow-Origin: https://your-frontend-domain.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key
```

---

## Error Handling

### Standard Error Format

All API errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request body contains invalid data",
    "details": [
      {
        "field": "symptoms",
        "message": "symptoms field is required"
      },
      {
        "field": "age",
        "message": "age must be between 0 and 120"
      }
    ],
    "request_id": "req_2026021512430001"
  },
  "status": "error",
  "timestamp": "2026-02-15T12:43:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (duplicate) |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Request data validation failed |
| `AUTHENTICATION_REQUIRED` | 401 | API key missing or invalid |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests in time window |
| `KNOWLEDGE_GRAPH_UNAVAILABLE` | 503 | Neo4j service unavailable |
| `INSUFFICIENT_DATA` | 400 | Insufficient data for analysis |
| `PROCESSING_ERROR` | 500 | Internal processing error |

---

## Rate Limiting

### Rate Limit Headers

All responses include rate limiting headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1645875600
X-RateLimit-Window: 3600
```

### Rate Limit Tiers

| Tier | Requests per Hour | Burst Limit | Use Case |
|------|------------------|-------------|----------|
| **Development** | 1,000 | 50 | Development & testing |
| **Basic** | 10,000 | 100 | Small hospitals |
| **Professional** | 50,000 | 500 | Medium hospitals |
| **Enterprise** | 200,000 | 1,000 | Large hospital systems |

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded. Please retry after 3600 seconds.",
    "retry_after": 3600,
    "request_id": "req_2026021512430002"
  },
  "status": "error",
  "timestamp": "2026-02-15T12:43:00Z"
}
```

---

## SDK & Client Libraries

### Python SDK

```python
from chartsense_client import ChartSenseClient

client = ChartSenseClient(
    api_key="your_api_key",
    base_url="https://api.chartsense-ai.com/v1"
)

# Generate differential diagnosis
diagnosis = client.cds.pre_diagnosis(
    symptoms=["fever", "cough", "dyspnea"],
    age=65,
    sex="M"
)

# Evaluate chart completeness  
score = client.chart.evaluate_completeness("ENC2026001")

# Get code suggestions
suggestions = client.coding.generate_suggestions("ENC2026001")
```

### JavaScript SDK

```javascript
import { ChartSenseClient } from '@chartsense/client';

const client = new ChartSenseClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.chartsense-ai.com/v1'
});

// Generate differential diagnosis
const diagnosis = await client.cds.preDiagnosis({
  symptoms: ['fever', 'cough', 'dyspnea'],
  age: 65,
  sex: 'M'
});

// Evaluate chart completeness
const score = await client.chart.evaluateCompleteness('ENC2026001');

// Generate code suggestions  
const suggestions = await client.coding.generateSuggestions('ENC2026001');
```

---

*This API reference provides complete documentation for all ChartSense AI endpoints. For implementation examples and integration guides, see the [Setup Documentation](SETUP.md).*

---

**Last Updated**: February 15, 2026  
**API Version**: v1.0.0-MVP  
**OpenAPI Spec**: Available at `/docs/openapi.json`