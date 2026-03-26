Smart Brand & Domain Availability Platform
MSc Cloud Computing CA1 Assignment - NCI

Author: Aniket Shetty
Date: March 2026

Project Structure:
- /backend       -> Contains the 8 modular Python 3.11 files representing the Serverless application logic
- /frontend      -> Contains index.html (Vanilla JS, HTML, CSS application)
- /tests         -> Pytest automated testing suite
- .github/       -> GitHub Actions deploying CI/CD pipeline
- architecture_and_report.md -> System architecture, API docs, and scalability explanation
- aws_setup.sh   -> 100% complete bash script for initial Learner Lab configuration

How to Run Tests:
Simply type `pytest tests/` in the project root to run locally (Dependencies: pip install pytest).

How to Deploy to Learner Lab:
1. Ensure AWS CLI is configured with Learner Lab credentials (aws_session_token loaded).
2. Inside `aws_setup.sh`, modify "YOUR_WHOISXML_API_KEY_HERE" to your genuine free-tier API key.
3. Apply executing rights: `chmod +x aws_setup.sh`.
4. Run `./aws_setup.sh`. It will map roles, build tables, SQS, S3 buckets, Lambdas, and print the live endpoints to standard output natively.
5. In your `frontend/index.html` file, replace the placeholder `API_URL` variable with the URL output from step 4.
6. Push changes to GitHub (if using Actions) or simply upload the frontend directly to your S3 `frontend-bucket` to view the live dashboard.
