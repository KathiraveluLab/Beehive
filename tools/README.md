# Security Audit Tools

This directory contains security analysis tools to help identify potential vulnerabilities in the Beehive codebase.

## Tools

### 1. Endpoint Scanner (`endpoint_scanner.py`)

Analyzes Flask routes to identify authentication and authorization issues.

**Usage:**
```bash
python tools/endpoint_scanner.py
```

**What it checks:**
- Endpoints missing authentication decorators
- Routes without proper authorization
- Sensitive operations lacking role verification

**Output:**
- Console report
- `security_audit_endpoints.txt` file

### 2. Secret Scanner (`secret_scanner.py`)

Scans the codebase for hardcoded secrets and weak credentials.

**Usage:**
```bash
python tools/secret_scanner.py
```

**What it detects:**
- Hardcoded passwords and API keys
- Connection strings with embedded credentials
- Weak or default passwords

**Output:**
- Console report
- `security_audit_secrets.txt` file

## Running All Scans

To run both scanners:

python tools/endpoint_scanner.py
python tools/secret_scanner.py

## CI/CD Integration

These tools can be integrated into CI/CD pipelines:

```yaml
- name: Security Audit
  run: |
    python tools/endpoint_scanner.py
    python tools/secret_scanner.py
```

## Best Practices

1. Run these tools before submitting pull requests
2. Address all CRITICAL findings before merging
3. Document any false positives
4. Use environment variables for all sensitive data
5. Never commit actual secrets (use .env.example as template)

## Contributing

When adding new security checks:
- Add patterns to the appropriate scanner
- Update this README
- Include test cases for new detections
- Document severity levels
