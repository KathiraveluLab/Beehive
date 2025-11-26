# Security Infrastructure

This document describes the security infrastructure changes added to this repository.
These are code changes introduced on the `security/add-security-infrastructure` branch —
not a separate project or external repository.

The changes include:
- JWT validation utilities
- CSRF protection via `flask-wtf`
- Rate limiting via `flask-limiter`
- Input validation and sanitization utilities
- Secure response headers (Content-Security-Policy, HSTS, etc.)

Review the Content-Security-Policy (CSP) before deployment and adjust allowed sources
for any external scripts, fonts, CDNs, or analytics services used by the application.
