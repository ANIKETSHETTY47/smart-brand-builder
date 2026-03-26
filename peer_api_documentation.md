# Brand & Domain Intelligence API - Peer Integration Guide

This document outlines how to consume the Brand & Domain Intelligence API. This functionality exposes our internal domain variation and scoring engine for peer applications.

## Endpoint
**POST** `https://amqf48tlgf.execute-api.us-east-1.amazonaws.com/prod/api/brand-domain/`

## 1. Request Domain Generation & Scoring
Generates curated domain variations based on your business name and intelligently scores them.

**Request Payload:**
```json
{
  "action": "generate",
  "business_name": "String (Required)",
  "category": "String (Required)"
}
```

**cURL Example:**
```bash
curl -X POST https://amqf48tlgf.execute-api.us-east-1.amazonaws.com/prod/api/brand-domain/ \
     -d '{"action": "generate", "business_name": "Duolingo", "category": "education"}'
```

**Response Payload (200 OK):**
*Note: The system returns a full brand identity payload. For domain integration, peer teams only need to parse the `suggested_domains` array.*
```json
{
  "suggested_domains": [
    {"domain": "getduolingo.com", "available": null, "score": 86},
    {"domain": "duolingo.io", "available": null, "score": 89},
    {"domain": "duolingo.com", "available": null, "score": 88},
    {"domain": "duolingoapp.com", "available": null, "score": 85}
  ],
  "available_domains": [],
  "style": "corporate",
  "icon_type": "hexagon",
  "brand_tone": "professional",
  "logo_svg": "<svg>...</svg>",
  "request_id": "uuid-v4-string"
}
```

## 2. Check Individual Domain Availability
Once the suggested domains are retrieved, you can ping the API with specific domains to verify if they are currently active and available for purchase.

**Request Payload:**
```json
{
  "action": "check_domain",
  "domain": "String (Required)"
}
```

**Return Payload (200 OK):**
```json
{
  "domain": "getduolingo.com",
  "available": false
}
```
