
# ZecPath API Guide

## 1. Overview

ZecPath is an AI-powered recruitment platform. Its backend exposes APIs for authentication, user profiles, jobs, applications, interviews, subscriptions, payments, and other recruitment-related functionality.

This guide explains how to access the API documentation, authenticate requests, and test endpoints.

## 2. API Documentation

ZecPath uses drf-spectacular to generate an OpenAPI schema.

When running the Django development server locally, use these URLs:

- **Swagger UI:** http://127.0.0.1:8000/api/docs/
- **ReDoc:** http://127.0.0.1:8000/api/redoc/
- **OpenAPI schema:** http://127.0.0.1:8000/api/schema/

Swagger UI lets developers explore endpoints, view request and response schemas, and execute API requests interactively.

ReDoc provides an alternative documentation interface. The OpenAPI schema is the machine-readable API specification.

## 3. Starting the Development Server

Activate the project's virtual environment, navigate to the project directory, and run:

```powershell
python manage.py runserver
```

Open the Swagger UI URL in your browser.

## 4. Authentication

ZecPath uses JWT authentication for protected API endpoints.

The typical authentication workflow is:

1. Register an account using the signup endpoint.
2. Log in using the login endpoint.
3. Obtain the access and refresh tokens returned by the login API.
4. Use the access token to access protected endpoints.
5. Obtain a new access token using the refresh endpoint when appropriate, according to the configured token lifetime and refresh policy.

For HTTP Bearer authentication, protected requests use this header:

```http
Authorization: Bearer <access_token>
```

In Swagger UI, use the **Authorize** button and follow the authentication scheme displayed in its dialog.

Never commit real passwords, access tokens, or refresh tokens to version control.

## 5. Authentication Endpoints

### 5.1 Signup

**Method:** POST

**Endpoint:** `/api/accounts/signup/`

**Purpose:** Register a new user.

Example request:

```json
{
    "username": "john",
    "email": "john@example.com",
    "password": "Use-A-Strong-Test-Password",
    "role": "CANDIDATE"
}
```

Use the role values permitted by the application's registration logic. Do not assume that public registration permits administrator accounts.

**Successful response:** HTTP 201 Created

```json
{
    "message": "User created successfully."
}
```

### 5.2 Login

**Method:** POST

**Endpoint:** `/api/accounts/login/`

**Purpose:** Authenticate a user and obtain JWT tokens.

Use the request body displayed in Swagger UI. The exact request fields and response schema are defined by the implementation.

### 5.3 Refresh Token

**Method:** POST

**Endpoint:** `/api/accounts/refresh/`

**Purpose:** Request a new access token using a refresh token, subject to the application's JWT configuration.

Consult Swagger UI for the exact request body and response format.

### 5.4 Logout

**Method:** POST

**Endpoint:** `/api/accounts/logout/`

**Purpose:** Log out a user according to the application's configured logout and token-handling behavior.

Consult Swagger UI for the request requirements and expected response.

## 6. Exploring Other API Endpoints

Swagger UI organizes the available endpoints by tags and displays their HTTP methods, paths, parameters, request bodies, authentication requirements, and documented responses.

Examples of endpoints include:

- `GET /api/accounts/profile/` — retrieve the authenticated user's profile.
- `GET /api/accounts/candidate/dashboard/` — retrieve candidate dashboard statistics.
- `GET /api/accounts/employer/dashboard/` — retrieve employer dashboard information.

Use Swagger UI as the authoritative interactive reference for the remaining endpoints and their current schemas.

## 7. Testing an Endpoint with Swagger UI

1. Start the Django development server.
2. Open `/api/docs/`.
3. Expand the endpoint you want to test.
4. Click **Try it out**.
5. Enter the required request data using the displayed schema.
6. Click **Execute**.
7. Inspect the HTTP status code, response body, and response headers.
8. For protected endpoints, authorize the request using a valid access token.

A successful response indicates that the particular request worked under the conditions tested. It does not prove that every endpoint or permission rule works correctly.

Use test accounts and test data. Avoid sending real credentials or tokens to untrusted environments.

## 8. Schema Validation

Run these commands from the project directory:

```powershell
python manage.py check
python manage.py spectacular --file schema.yml --validate
```

The Django system check verifies project configuration. The schema validation command generates the OpenAPI specification and reports schema warnings or errors.

Review any warnings or errors before delivering documentation changes.

## 9. Developer Notes

- Keep API schemas and documentation aligned with the actual implementation.
- Document authentication requirements and relevant request and response formats.
- Use unique operation IDs for documented endpoints.
- Never commit secrets, passwords, or real JWT tokens.
- Re-run schema validation after modifying API documentation.
- Use the project's existing Git workflow to review and commit changes.