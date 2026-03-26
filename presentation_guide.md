# 🚀 Presentation Guide: Smart Brand Builder
*Use this quick 4-minute reference guide to lead your professor through your architecture.*

---

## 📍 1. Where are the 3 APIs Implemented?
Your professor will ask to see exactly where each API is consumed/created. Have your IDE open and ready to point to these three files:

### A. "My API" (The one you built)
* **File to show:** `backend/lambda_main.py` 
* **Explanation:** This is your core orchestrator API deployed dynamically via API Gateway. Point to the `def lambda_handler(event, context):` function. Show how it routes traffic based on the JSON `action` field to either generate full branding payloads or check specific domains.

### B. "Peer API" (Classmate's Logo Service)
* **File to show:** `backend/logo_client.py`
* **Explanation:** Explain that this file synchronously connects to your classmate's logo generator. 
* *Point to line 4:* `PEER_API_URL` which holds the endpoint. 
* Show the elegant **Fallback Architecture**: Look at `def generate_logo():` and explain that if the peer API times out or fails (via `try-except`), your code doesn't crash—it gracefully intercepts the error and dynamically builds an inline placeholder SVG using `get_fallback_svg()`.

### C. "Public API" (WhoisXML Domain Checker)
* **File to show:** `backend/domain_checker.py`
* **Explanation:** This consumes a public domain availability service. Show the `requests.get()` call inside `def check_domains()`. Mention that for security best practices, the API key is **never hardcoded** in this file. It is dynamically pulled during runtime from AWS Systems Manager Parameter Store via `get_api_key()`.

---

## 🛠 2. AWS Cloud Services Used
Your system is a highly scalable, fully serverless micro-monolith. Mention the rubric requirement to use *"queues, FaaS, autoscaling, etc."* and explain how your design hits every single one perfectly:
1. **Frontend Hosting (S3):** Boundlessly scalable static website delivery mechanism for your Single Page App.
2. **Compute / FaaS (AWS Lambda):** Provides real-time event-driven autoscaling.
3. **API Routing (API Gateway):** Manages inbound HTTP REST traffic securely to the Lambdas.
4. **NoSQL Database (DynamoDB):** Offers single-digit millisecond latency storage for the main records and audit logs.
5. **Decoupling Queue (AWS SQS):** Proves asynchronous scalability. Removes heavy logging operations from the critical user-facing path.
6. **Secrets Management (SSM):** Secures the WhoisXML API Key.

---

## 🔀 3. High-Level Data Flow Summary
*(Read this as the lifecycle of a user request)*

**Phase 1: Generation Flow**
1. The user enters a Business Name on the **S3 Frontend** and clicks Generate.
2. The browser hits **API Gateway**, triggering your `lambda_main.py` Function (**My API**).
3. The Lambda applies rule-based logic to score Domain variations and map brand aesthetics (Tech/Fitness/etc).
4. The Lambda makes a synchronous HTTP call to the **Peer API** to fetch the Logo SVG file.
5. The Lambda rapidly saves everything to **DynamoDB** and drops the `.svg` into a secondary **S3 Bucket**.
6. At the exact same time, the Lambda fires off a tiny JSON message securely onto the **SQS Queue**.
7. The Lambda answers the browser with a `200 OK` JSON response containing the Logo and Domain Suggestions.

**Phase 2: Asynchronous Auditing**
1. In the background, completely invisible to the user, **SQS** triggers a second function (`lambda_audit.py`).
2. That audit function safely writes a timestamped access log to a secondary **DynamoDB** table. If it errors out, the user doesn't suffer because SQS safely decouples it.

**Phase 3: Deep Verification Flow (Public API)**
1. The user clicks "Check Availability" next to a specific domain name on the frontend.
2. A separate fast ping hits `lambda_main.py` with an `action: check_domain` payload.
3. The Lambda queries the **Public API** (WhoisXML) securely and immediately confirms if the domain is registered.
