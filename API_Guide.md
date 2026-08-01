# Authentication APIs

## Signup

POST /api/accounts/signup/

Request

{
    "username": "john",
    "email": "john@gmail.com",
    "password": "123456",
    "role": "CANDIDATE"
}

Response

201 Created

{
    "message": "User created successfully."
}