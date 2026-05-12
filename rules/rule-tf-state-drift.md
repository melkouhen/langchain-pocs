# Terraform State Drift Detection

<rule id="TF-STATE-DRIFT-010" severity="MAJOR" category="Monitoring">
<title>State Drift Detection: Regular Plan Runs</title>

<description>
Run `terraform plan` or `terraform plan -detailed-exitcode` regularly to detect drift.
Drift occurs when cloud resources are modified outside of Terraform (manual changes via console).
Detecting drift prevents inconsistencies and surprises.
</description>

<problem>
Undetected drift causes:
- Manual changes via cloud console not reflected in code
- `terraform apply` destroys manual changes (vice versa)
- Team confusion about what's actually deployed
- Difficult to understand why code doesn't match reality
- Security issues: manual changes might not follow policies
</problem>

<pattern id="correct">
<title>✅ Regular Drift Detection</title>

**Local Development (Regular Checks):**
```bash
# Before any apply, run plan to detect changes
cd envs/prod
terraform plan

# If plan shows changes you didn't make = DRIFT DETECTED
# Someone made manual changes in cloud console
```

**CI/CD Integration (Automated Checking):**
```yaml
# GitHub Actions - runs on schedule + on PR
name: Detect Drift

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM
  pull_request:

jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v2
      
      - name: Check Drift
        run: |
          cd envs/prod
          terraform init
          terraform plan -detailed-exitcode || EXIT_CODE=$?
          
          if [ $EXIT_CODE -eq 2 ]; then
            echo "❌ DRIFT DETECTED: Manual changes in cloud console"
            exit 1
          fi
```

**Exit Codes:**
- `0` = No changes (plan is clean)
- `1` = Error in plan
- `2` = Changes detected (drift!)

**Remediation Workflow:**
1. Detect drift with plan
2. Review changes: Are they intentional?
3. Option A: Import into state: `terraform import <resource> <id>`
4. Option B: Remove from code, accept as unmanaged resource
5. Option C: Reapply code to override manual changes
</pattern>

<antipattern id="incorrect">
<title>❌ Never Running Plan</title>

```bash
# ❌ WRONG: Only run plan when about to apply
# Don't run plan regularly to detect drift

# Result:
# - Engineer makes manual change in GCP console
# - 3 weeks pass
# - Next terraform apply overwrites manual change
# - Unrelated feature is now broken

# ❌ WRONG: Ignoring plan output
terraform plan
# Output shows unexpected changes
# Apply anyway without understanding changes
# "Hope it works out" approach
```

**Real-world scenario:**
```
1. DBA manually adjusts database settings via console
2. Settings improve performance significantly
3. Terraform is never run for 2 months
4. Next deploy: terraform apply runs
5. Manual settings are overwritten with Terraform defaults
6. Database performance degrades
7. Team spends 2 days debugging why performance dropped
```
</antipattern>

<why>
**Infrastructure changes can come from:**
1. Terraform (tracked in Git)
2. Cloud console (manual, not in Git)
3. APIs, SDKs, other tools
4. Security patches, auto-scaling events

**Goal:** Detect when reality ≠ code

**Drift detection enables:**
1. Quick discovery of manual changes
2. Decision: keep change or revert?
3. Opportunity to update code with good changes
4. Prevention of destructive overwrites
5. Team alignment on actual infrastructure
</why>

<when-to-apply>
**Run plan regularly for:**
- Production environments (at least weekly)
- Shared infrastructure
- Compliance-sensitive resources

**Run plan always before:**
- Any `terraform apply`
- Any deploy
- Any state file migration
</when-to-apply>

<implementation-checklist>
- [ ] Set up daily/weekly drift detection in CI/CD
- [ ] Configure `-detailed-exitcode` for drift alerting
- [ ] Document drift remediation process
- [ ] Team training: how to handle drift
- [ ] Create runbook: "Found drift, what now?"
- [ ] Alert on drift detection (Slack, email)
- [ ] Establish policy: manual changes require code update
</implementation-checklist>

<related-rules>
- TF-CI-CD-INTEGRATION-012: Automated plan in pipeline
- TF-ALWAYS-PLAN-013: Review plan before apply
</related-rules>

</rule>
