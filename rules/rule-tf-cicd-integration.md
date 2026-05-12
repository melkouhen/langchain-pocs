# Terraform CI/CD Integration

<rule id="TF-CI-CD-INTEGRATION-012" severity="MAJOR" category="Automation">
<title>CI/CD Integration: Format, Validate, Plan</title>

<description>
Integrate Terraform into CI/CD pipelines with automated:
1. `terraform fmt` (code formatting)
2. `terraform validate` (syntax checking)
3. `terraform plan` (preview changes)
4. Approval gate before apply

This prevents syntax errors and accidental infrastructure changes.
</description>

<problem>
Without CI/CD integration:
- Developers apply invalid code to production
- Code style inconsistencies
- No preview of changes before apply
- No audit trail of who changed what
- Manual apply = human error
</problem>

<pattern id="correct">
<title>✅ CI/CD Pipeline</title>

**GitHub Actions Example:**
```yaml
name: Terraform

on:
  pull_request:
    paths:
      - 'envs/**'
      - 'modules/**'

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.9.0

      - name: Terraform Format Check
        run: terraform fmt -check -recursive .

      - name: Terraform Validate
        run: |
          cd envs/dev && terraform init && terraform validate
          cd ../staging && terraform init && terraform validate
          cd ../prod && terraform init && terraform validate

      - name: Terraform Plan (dev)
        env:
          GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS_DEV }}
        run: |
          cd envs/dev
          terraform init
          terraform plan -out=tfplan

      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: tfplan
          path: envs/dev/tfplan

  approval:
    needs: terraform
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - name: Terraform Apply (Requires Approval)
        run: echo "Waiting for approval..."
```

**Steps in Pipeline:**
1. `terraform fmt -check` → Ensure code is formatted
2. `terraform validate` → Ensure syntax is valid
3. `terraform plan` → Show what will change
4. Approval gate → Human review before apply
5. `terraform apply` → Deploy (requires approval)

**Key Security:**
✓ All credentials in GitHub Secrets  
✓ Apply requires approval  
✓ Plan output visible to reviewers  
✓ Audit trail in GitHub Actions logs  
</pattern>

<antipattern id="incorrect">
<title>❌ Manual Terraform Apply</title>

```bash
# ❌ WRONG: Developer runs apply locally
terraform apply -auto-approve

# No review, no preview, no audit trail
# If wrong resource is destroyed, hard to undo

# ❌ WRONG: No validation in CI
# Push code → CI runs tests → No terraform validate

# ❌ WRONG: Shared credentials
# Put credentials directly in code/config
# Anyone with repo access gets credentials
```

**Consequences:**
❌ Invalid code applied to prod  
❌ No audit trail  
❌ Credentials exposed  
❌ Manual errors (typos, wrong environment)  
</antipattern>

<why>
**CI/CD Benefits:**
1. **Safety**: Validation before any cloud changes
2. **Auditability**: Every change tracked
3. **Security**: Credentials in CI/CD secrets, not code
4. **Consistency**: Same pipeline for all developers
5. **Approval**: Human review before production

**Prevents:**
- Syntax errors reaching production
- Inconsistent formatting
- Unreviewed infrastructure changes
- Credential leaks
</why>

<when-to-apply>
**Implement for:**
- Any production Terraform
- Team projects
- Any code in shared repo

**Can skip for:**
- Local throwaway tests
</when-to-apply>

<implementation-checklist>
- [ ] Create .github/workflows/terraform.yml (or equivalent for GitLab/etc.)
- [ ] Add `terraform fmt -check` step
- [ ] Add `terraform validate` step (per environment)
- [ ] Add `terraform plan` step with artifact upload
- [ ] Set up approval gate for main branch
- [ ] Store credentials in CI/CD secrets
- [ ] Test pipeline with PR (should show plan)
- [ ] Document pipeline in README
- [ ] Never run `apply -auto-approve` in CI
</implementation-checklist>

<related-rules>
- TF-ALWAYS-PLAN-013: Plan before apply
- TF-VERSION-PINNING-006: Consistent versions in CI
</related-rules>

</rule>
