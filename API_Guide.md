# ZecPath API Guide

## 1. Overview

ZecPath is an AI-powered recruitment platform that supports candidate and employer workflows, job management, applicant tracking, AI-based screening, interview management, subscriptions, payments, and recruiter-candidate communication.

This document explains how to start the backend, authenticate API requests, explore available endpoints, and validate the API documentation.

**Documentation source:** Django URL configuration and the generated OpenAPI schema. Refer to the running Swagger UI and actual serializers/views for exact request fields, response structures, and permission requirements.

## 2. API Documentation Interfaces

When running the Django development server locally, use:

| Resource | URL |
|---|---|
| Swagger UI | http://127.0.0.1:8000/api/docs/ |
| ReDoc | http://127.0.0.1:8000/api/redoc/ |
| OpenAPI schema | http://127.0.0.1:8000/api/schema/ |

- **Swagger UI:** Explore endpoints and execute API requests interactively.
- **ReDoc:** Browse the generated API reference in a documentation-oriented layout.
- **OpenAPI schema:** Machine-readable API specification for compatible tools.

The schema describes documented operations. Always verify business rules and implementation-specific behavior against the actual backend.

## 3. Development Setup

Run the following commands in PowerShell from the project root.

### 3.1 Activate the virtual environment

If the project's virtual environment is named `env`:

```powershell
.\env\Scripts\Activate.ps1
```

If it is already activated, continue to the next step.

### 3.2 Install dependencies

If `requirements.txt` is maintained for the current project version:

```powershell
pip install -r requirements.txt
```

### 3.3 Configure environment variables

Configure the required values in the project's local `.env` file according to the settings and integrations being used.

Depending on the enabled functionality, configuration may include database, JWT, storage, Celery/Redis, AI-provider, and payment-provider settings.

- Use valid local or development credentials.
- Do not commit `.env` files or production secrets.
- Consult the project settings and dependency documentation for the exact required variables.

### 3.4 Apply migrations

```powershell
python manage.py migrate
```

### 3.5 Start the development server

```powershell
python manage.py runserver
```

Open Swagger UI at http://127.0.0.1:8000/api/docs/.

The commands above describe a local development workflow. Production deployment requires the appropriate production environment and service configuration.

## 4. Authentication and Authorization

ZecPath uses JWT authentication for protected API endpoints.

### 4.1 Typical authentication workflow

1. Register using the signup endpoint.
2. Log in using the login endpoint.
3. Obtain the tokens returned by the login API.
4. Send the access token with requests to protected endpoints.
5. Use the refresh endpoint when an access token needs to be renewed, subject to the configured JWT policy.
6. Use the logout endpoint according to the application's token-handling implementation.

### 4.2 Authorization header

For endpoints that use Bearer JWT authentication, send:

```http
Authorization: Bearer <access_token>
```

In Swagger UI, click **Authorize** and follow the authentication scheme displayed.

### 4.3 Authentication endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/accounts/signup/` | Register a user |
| POST | `/api/accounts/login/` | Authenticate and obtain tokens |
| POST | `/api/accounts/refresh/` | Refresh authentication tokens |
| POST | `/api/accounts/logout/` | Log out according to the configured token policy |
| GET | `/api/accounts/profile/` | Access the account profile endpoint |

The precise fields, response bodies, and authentication requirements should be checked in Swagger and the corresponding serializers/views.

### 4.4 Security notes

- Never commit real passwords, JWTs, API keys, or payment credentials.
- Use test accounts and test data during development.
- Do not assume that a user can access an endpoint merely because they are authenticated.
- Verify role-based permissions and resource ownership for administrative, employer, and candidate operations.

## 5. API Endpoint Reference

The following inventory reflects the endpoint paths and HTTP methods identified in the generated project schema. It is an endpoint index, not a substitute for the exact schemas and business rules shown in Swagger.

### 5.1 Accounts and dashboards

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/accounts/signup/` | User registration |
| POST | `/api/accounts/login/` | User login |
| POST | `/api/accounts/logout/` | Logout |
| POST | `/api/accounts/refresh/` | Refresh JWT |
| GET | `/api/accounts/profile/` | Account profile |
| GET | `/api/accounts/candidate/dashboard/` | Candidate dashboard |
| GET | `/api/accounts/candidate-dashboard/` | Candidate dashboard legacy route |
| GET | `/api/accounts/employer/dashboard/` | Employer dashboard |
| GET | `/api/accounts/admin/dashboard/` | Admin dashboard |
| GET | `/api/accounts/admin/stats/` | Admin platform statistics |
| GET | `/api/accounts/admin/audit-logs/` | Administrative audit-log access |
| PATCH | `/api/accounts/admin/employers/{user_id}/approve/` | Employer approval |
| PATCH | `/api/accounts/admin/users/{user_id}/block/` | User blocking |

Administrative endpoints should be used only by authorized administrators. Confirm the permitted roles and request requirements in the implementation.

### 5.2 Jobs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/jobs/` | List or browse jobs |
| GET | `/api/jobs/featured/` | Retrieve featured jobs |
| GET | `/api/jobs/latest/` | Retrieve latest jobs |
| GET | `/api/jobs/recommended/` | Retrieve recommended jobs |
| GET | `/api/jobs/my-jobs/` | Retrieve the authenticated employer's jobs |
| GET | `/api/jobs/my-saved-jobs/` | Retrieve saved jobs |
| POST | `/api/jobs/create/` | Create a job |
| PATCH | `/api/jobs/{job_id}/update/` | Update a job |
| PATCH | `/api/jobs/{job_id}/status/` | Change job status |
| POST | `/api/jobs/{job_id}/save/` | Save a job |
| PATCH | `/api/jobs/admin/jobs/{job_id}/remove/` | Administrative job removal action |

Job creation, updates, status changes, and administrative operations may have role or ownership restrictions. Use the actual endpoint documentation to verify them.

### 5.3 Applications and Applicant Tracking System (ATS)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/applications/{job_id}/apply/` | Apply for a job |
| GET | `/api/applications/my-applications/` | Retrieve the candidate's applications |
| GET | `/api/applications/job/{job_id}/applications/` | Retrieve applications for a job |
| PATCH | `/api/applications/{application_id}/status/` | Update application status |
| GET | `/api/applications/{application_id}/ats-score/` | Retrieve application ATS score |
| GET | `/api/applications/job/{job_id}/ranked-candidates/` | Retrieve ranked candidates |
| PATCH | `/api/applications/job/{job_id}/auto-process/` | Trigger or configure job-level auto-processing |
| PATCH | `/api/applications/{application_id}/auto-process/` | Trigger or configure application-level auto-processing |
| GET | `/api/applications/analytics/` | Application analytics |
| GET | `/api/applications/job/{job_id}/analytics/` | Job-level application analytics |
| GET | `/api/applications/jobs/{job_id}/recruiter-analytics/` | Recruiter job analytics |
| GET | `/api/applications/premium-analytics/` | Premium analytics |
| GET | `/api/applications/jobs/{job_id}/premium-ranking/` | Premium candidate ranking |

ATS scoring and ranking should be interpreted according to the project's implemented scoring logic and thresholds. Verify the exact response fields and status-transition rules in the corresponding API implementation.

### 5.4 AI interviews

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/ai-interviews/schedule/` | Schedule an interview |
| POST | `/api/ai-interviews/answers/evaluate/` | Evaluate an interview answer |
| GET | `/api/ai-interviews/answers/{answer_id}/evaluation/` | Retrieve an answer evaluation |
| GET | `/api/ai-interviews/applications/{application_id}/report/` | Retrieve an application interview report |
| POST | `/api/ai-interviews/applications/{application_id}/report/` | Create or process an interview report |
| GET | `/api/ai-interviews/jobs/{job_id}/audit/` | Retrieve job interview audit information |
| GET | `/api/ai-interviews/jobs/{job_id}/reminders/` | Retrieve interview reminders |
| GET | `/api/ai-interviews/jobs/{job_id}/slots/` | Retrieve interview slots |

Interview scheduling, evaluation, report generation, and reminder behavior depend on the request fields and business logic implemented by the backend.

### 5.5 Recruiter-candidate chat

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/chat/conversations/` | List the authenticated participant's conversations |
| POST | `/api/chat/applications/{application_id}/start/` | Start or retrieve a conversation for an application |
| GET | `/api/chat/conversations/{conversation_id}/messages/` | List messages in a conversation |
| POST | `/api/chat/conversations/{conversation_id}/messages/` | Send a message |

#### Chat workflow and access rules

- Conversations are associated with a job application.
- A conversation is created or retrieved through the application-specific start endpoint.
- Candidates can initiate a conversation only when the application is shortlisted.
- Recruiters can initiate conversations for applications associated with their own jobs, subject to the implemented authorization checks.
- Once a recruiter has initiated a conversation, the candidate can reply through that conversation even if the application is not shortlisted.
- Conversation and message access is restricted to authorized participants.
- The start endpoint can return HTTP `201 Created` for a new conversation or HTTP `200 OK` when retrieving an existing conversation.

For sending a message, use the request body displayed in Swagger UI. The message serializer defines the accepted content field and the server-controlled fields.

### 5.6 Candidate profiles and resumes

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/profiles/me/` | Retrieve the current profile |
| GET | `/api/profiles/candidates/` | Retrieve candidate profiles |
| PATCH | `/api/profiles/update/` | Update a profile |
| DELETE | `/api/profiles/delete/` | Delete a profile |
| POST | `/api/profiles/upload-resume/` | Upload a resume |
| POST | `/api/resumes/parse/` | Parse a resume |

Resume upload and parsing may require multipart file data or other specific input formats. Check the endpoint's documented request schema before submitting a request. Access to candidate records may be restricted by role and ownership.

### 5.7 Audit logs

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/audit/logs/` | Retrieve audit logs |
| GET | `/api/accounts/admin/audit-logs/` | Access administrative audit logs |

Audit information may contain sensitive platform activity. Use these endpoints only with the permissions provided by the implementation.

### 5.8 Payments

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/payments/orders/` | Create a payment order |
| POST | `/api/payments/verify/` | Verify a payment |
| POST | `/api/payments/capture/` | Capture a payment |
| POST | `/api/payments/webhook/` | Receive payment-provider webhook events |

Payment operations must follow the provider's implemented verification and security requirements. Never treat a client-provided payment status as authoritative without the server-side checks implemented by the application.

### 5.9 Subscriptions and administrative billing

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/subscriptions/current/` | Retrieve the current subscription |
| GET | `/api/admin/billing/transactions/` | Retrieve billing transactions |
| GET | `/api/admin/billing/subscriptions/` | Retrieve subscription records |
| GET | `/api/admin/billing/revenue/` | Retrieve revenue information |
| GET | `/api/admin/billing/refunds/` | Retrieve refund information |
| GET | `/api/admin/billing/failures/` | Retrieve payment failures |

Administrative billing endpoints should be accessed only by appropriately authorized users.

## 6. Common HTTP Methods

| Method | Typical purpose |
|---|---|
| GET | Retrieve data |
| POST | Create a resource or initiate an operation |
| PATCH | Partially update a resource or change its state |
| DELETE | Delete a resource |

The meaning of a specific operation is