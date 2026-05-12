# Terraform Security: No Hardcoded Secrets

<rule id="TF-NO-HARDCODED-SECRETS-009" severity="CRITICAL" category="Security">
<title>No Hardcoded Secrets</title>

<description>
Never hardcode secrets (passwords, API keys, credentials) in Terraform code.
Use variables, secret managers, or environment variables instead.
</description>

<problem>
Hardcoded secrets in code cause:
- Secrets exposed in version control history (even after deletion!)
- Secrets visible in `terraform plan` output
- Secrets stored in state files in plaintext
- Secrets accessible to anyone with repo access
- Compliance/audit violations
</problem>

<pattern id="correct">
<title>✅ Secrets Managed Safely</title>

**Option 1: Input Variables**
```hcl
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true  # ← Masks in output
}

# Usage: terraform apply -var="db_password=xxx"
# or via terraform.tfvars (added to .gitignore)
```

**Option 2: Secret Manager**
```hcl
# Use Google Secret Manager
data "google_secret_manager_secret_version" "db_password" {
  secret = "db-password"
  version = "latest"
}

resource "google_sql_database_instance" "db" {
  # Use: data.google_secret_manager_secret_version.db_password.secret_data
}
```

**Option 3: Environment Variables**
```bash
export TF_VAR_db_password="xxx"
terraform apply  # Reads from env var
```

**Best Practices:**
✓ Mark sensitive variables with `sensitive = true`  
✓ Use secret manager (not local files)  
✓ Rotate credentials regularly  
✓ Use service accounts instead of user credentials  
✓ Grant minimal permissions (least privilege)  
</pattern>

<antipattern id="incorrect">
<title>❌ Hardcoded Secrets</title>

```hcl
# ❌ WRONG: Password in code
resource "google_sql_database_instance" "db" {
  name = "production-db"
  
  root_user {
    password = "MySecurePassword123!"  # ❌ EXPOSED
  }
}

# ❌ WRONG: API key in code
variable "sendgrid_api_key" {
  default = "SG.xxxxxxxxxxxx"  # ❌ In version control forever
}

# ❌ WRONG: Service account key file committed
locals {
  gcp_credentials = file("credentials.json")  # ❌ Keys in repo
}
```

**Consequences:**
❌ Secrets in Git history (unforgettable)  
❌ Visible in `terraform plan` output  
❌ Anyone with repo access has credentials  
❌ Audit trail shows who saw the secrets  
❌ Compliance violations (HIPAA, PCI-DSS, SOC2)  
</antipattern>

<why>
**Threat Model:**
1. Repository accessed by: developers, CI/CD, contractors, consultants
2. Git history is permanent (even deleted secrets remain in history)
3. Credentials can be rotated, but compromised credentials = attacker access
4. Least privilege: developers should not know production credentials

**Secret Manager Benefits:**
- Centralized secret rotation
- Audit logs (who accessed what)
- Access control (different permissions per secret)
- Encryption at rest and in transit
</why>

<when-to-apply>
**Apply this rule:**
- ANY sensitive data: passwords, keys, tokens
- API credentials
- Service account files
- Private configuration

**Include:**
- Mark variables `sensitive = true` (masks in output)
- Use secret managers for production
</when-to-apply>

<implementation-checklist>
- [ ] Audit existing code for hardcoded secrets
- [ ] Move secrets to variables (add `sensitive = true`)
- [ ] Use secret manager for production credentials
- [ ] Update .gitignore to exclude .tfvars files
- [ ] Create terraform.tfvars.example with placeholder values
- [ ] Rotate any exposed credentials immediately
- [ ] Document secret injection in README/runbook
- [ ] Set up secret scanning in CI/CD (e.g., GitGuardian)
</implementation-checklist>

<related-rules>
- TF-AVOID-HARDCODING-011: Avoid hardcoding regions/AMIs
</related-rules>

</rule>
