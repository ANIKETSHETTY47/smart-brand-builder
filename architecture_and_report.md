# Architecture and Scalability Report
## Smart Brand & Domain Availability Platform

### 1. System Architecture
The application runs as a fully serverless micro-monolith on AWS Learner Lab, built strictly over the AWS ecosystem using managed services. 

**Text-Based Architecture Diagram**
```text
[ User (Browser) ]
      |
      | 1. HTTP POST (business_name, category)
      v
[ API Gateway (REST API) ]
      |
      | 2. Proxy Integration
      v
[ Lambda 1: brand-domain-api-lambda (Sync Handler) ]
      |
      |-- 3. SSM (Retrieve WhoisXML API Key securely)
      |-- 4. External API: WhoisXML (Check Domain Availability)
      |-- 5. Helper Modules: Domain Logic & Brand Logic Scoring
      |-- 6. External Peer API: Logo Generator (Fallback handled)
      |
      |-- 7. S3: brand-domain-logos-bucket (Store generated SVG logo)
      |-- 8. DynamoDB: brand-domain-results (Store final payload logic)
      |
      |-- 9. AWS SQS (Publish Audit Output to queue asynchronously)
      |
      \-- 10. HTTP 200 OK (Return parsed suggestions & SVG to FrontEnd)

[ SQS: brand-domain-audit-queue ]
      |
      | 11. Event Source Mapping trigger
      v
[ Lambda 2: brand-domain-audit-lambda (Async Worker) ]
      |
      | 12. Write audit log with timestamp
      v
[ DynamoDB: brand-domain-audit ]
```

### 2. API Documentation
**Endpoint:** `POST https://{API_ID}.execute-api.us-east-1.amazonaws.com/prod/api/brand-domain/`

**Request Body:**
```json
{
  "business_name": "Quantex",
  "category": "technology"
}
```

**Response Body (200 OK):**
```json
{
  "available_domains": ["quantex.io", "getquantex.com"],
  "suggested_domains": [
    {"domain": "quantex.io", "score": 1090, "available": true},
    {"domain": "getquantex.com", "score": 1086, "available": true},
    {"domain": "quantexapp.com", "score": 1086, "available": true},
    {"domain": "quantex.com", "score": 989, "available": false}
  ],
  "style": "tech",
  "icon_type": "hexagon",
  "brand_tone": "futuristic",
  "logo_svg": "<svg>...</svg>",
  "request_id": "8a32d184-e918-49ba-81c4-18451f28b2be"
}
```

### 3. Scalability & Resilience Mechanisms

* **SQS Decoupling**: The audit and logging task is computationally deferred to an SQS queue. This provides robust decoupling, ensuring that if DynamoDB experiences throttling during an audit write, or the second Lambda fails, the end-user waiting for the primary REST response remains completely unaffected.
* **Lambda Auto-Scaling**: Execution natively auto-scales depending on HTTP requests (for API Lambda) and SQS polling capacity (for Audit Lambda). Each request triggers isolated compute runtimes.
* **API Gateway Throttling & Managed Traffic**: Handled automatically by the AWS Proxy Integration. 
* **Graceful Fallbacks**:
  - **Peer API Outage:** Implemented local inline SVG generation within `logo_client.py`. If the peer API times out or crashes, the frontend gracefully loads an inferred placeholder visual representing the logic criteria.
  - **DynamoDB Write Failures:** Write operations within `storage.py` are wrapped in localized `try-except` blocks. Failing to insert an archival payload will log internally to CloudWatch but return the valid JSON dataset back to the requester rather than throwing a 500 error.

### 4. CI/CD Pipeline Benefits (GitHub Actions)
Deployments are standardized through `.github/workflows/deploy.yml`. Benefits include:
* **Automated Regression Tracking:** Built-in assertions (`pytest`) execute locally before zip-packaging, meaning broken rule parameters, domain scorings, or SVG generations act as an immediate gatekeeper preventing pushed-failures to the Lambdas.
* **Zero-Downtime Rollouts:** GitHub Actions packages minimal sized `.zip` builds natively, and hot-swaps active execution lambda pointers (`update-function-code`), yielding split-second transitions.
* **Unified Ecosystem Updates:** Front-end components inside the `/frontend/` bucket actively synchronise, pruning removed CSS assets and retaining fresh elements autonomously alongside backend updates.
