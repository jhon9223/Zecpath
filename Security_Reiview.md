# Security Review

## Authentication
- JWT Authentication implemented
- Access Token protected APIs
- Refresh Token supported
- Logout blacklists refresh token

## Authorization
- Signup → AllowAny
- Login → AllowAny
- Logout → IsAuthenticated
- My Profile → IsAuthenticated
- Update Profile → IsAuthenticated
- Delete Profile → IsAuthenticated
- Upload Resume → IsCandidate
- Admin Profile → IsAdmin

## Resume Upload Security
- Only authenticated candidates can upload
- Allowed extensions: PDF, DOC, DOCX
- Maximum file size: 5 MB
- Stored in MEDIA_ROOT

## Pending Improvements
- Email verification
- Password reset
- Cloud storage (AWS S3/Cloudinary)
- Antivirus scanning
- Rate limiting