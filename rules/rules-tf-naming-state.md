# Terraform Naming, State Management & Drift Detection Rules

<rule id="TF-RESOURCE-NAMING-010" severity="MAJOR" category="Code Quality">
<title>Resource Naming Convention</title>

<description>
Use a consistent naming pattern for all resources: `${var.environment}-${resource_type}-${index}`.
Consistent naming makes infrastructure predictable and searchable.
</description>

<problem>
Inconsistent naming causes:
- Hard to find resources in cloud console
- Duplicate/orphan resources created
- Team members confused about resource ownership
- Difficult to correlate Terraform code to cloud resources
</problem>

<pattern id="correct">
<title>✅ Consistent Naming Pattern</title>

**Pattern: `${environment}-${type}-${index}`**
```hcl
locals {
  environment = var.environment  # "dev", "staging", "prod"
}

resource "google_storage_bucket" "app_data" {
  name = "${local.environment}-gcs-data"      # dev-gcs-data
  # Pattern: {env}-{type}-{purpose}
}

resource "google_sql_database_instance" "db" {
  name = "${local.environment}-sql-primary"   # dev-sql-primary
}

resource "google_compute_instance" "web" {
  name = "${local.environment}-compute-0"     # dev-compute-0
  
  # For multiple instances, use count
  for_each = toset(["web1", "web2", "web3"])
  name     = "${local.environment}-compute-${each.value}"
  # dev-compute-web1, dev-compute-web2, dev-compute-web3
}
```

**Naming Guidelines:**
✓ All lowercase  
✓ Use hyphens (not underscores): `dev-bucket` not `dev_bucket`  
✓ Environment first (can filter by env in cloud console)  
✓ Resource type second (bucket, instance, database)  
✓ Purpose/index last (optional, for clarity)  
✓ Keep names short (most cloud limits are 63 chars)  

**Examples:**
```
Environment: dev, staging, prod
Type: gcs (bucket), sql (database), compute (instance), vpc, iam-role
Purpose: primary, replica, backup, web, db

Resources:
dev-gcs-data
staging-sql-backup
prod-compute-web0
prod-vpc-main
prod-iam-role-admin
```
</pattern>

<antipattern id="incorrect">
<title>❌ Inconsistent Naming</title>

```hcl
# ❌ WRONG: Inconsistent patterns
resource "google_storage_bucket" "app" {
  name = "myAppBucket"              # Camel case, no environment
}

resource "google_sql_database_instance" "db" {
  name = "database_prod_2024"        # Underscores, unclear version
}

resource "google_compute_instance" "server" {
  name = "ProdWebServer01"           # Caps, no environment prefix
}

resource "google_storage_bucket" "logs" {
  name = "company-prod-logs"         # Different pattern (company prefix)
}

# Result:
# - Hard to group by environment
# - Difficult to search cloud console
# - No clear pattern for new developers
```
</antipattern>

<why>
**Consistent naming enables:**
1. **Searchability**: Find all `dev-*` resources in cloud console
2. **Automation**: Scripts can identify resources by name pattern
3. **Scalability**: New team members follow existing pattern
4. **Debugging**: Can quickly correlate resource in console to Terraform code
5. **Cost allocation**: Can tag/group by environment from name alone

**Example Benefit:**
```bash
# In GCP Console, filter by name: "dev-*"
# Shows all dev resources at once
# vs.
# Searching manually for myAppBucket, database_prod_2024, ProdWebServer01
```
</why>

<when-to-apply>
**Apply to:**
- All cloud resources
- Every environment
- New and existing resources

**Naming Pattern:**
Use: `${environment}-${type}-${purpose}`

**Avoid:**
- Camel case (use hyphens)
- Underscores (use hyphens)
- Company name in every resource (use variables/tags instead)
- Timestamps (causes drift: `timestamp()`)
</when-to-apply>

<implementation-checklist>
- [ ] Define naming convention in README
- [ ] Update all resource names to follow pattern
- [ ] Use locals for environment variable
- [ ] Test: filter by environment in cloud console
- [ ] Document pattern in code comments
- [ ] Add to code review checklist: verify naming
</implementation-checklist>

<related-rules>
- TF-AVOID-HARDCODING-011: Parameterize naming
</related-rules>

</rule>


<rule id="TF-STATE-DELETION-009" severity="CRITICAL" category="Safety">
<title>Never Delete State Files Directly</title>

<description>
Never manually delete or modify `.tfstate` files. Use `terraform destroy` or proper
state management via CLI to remove resources. Direct state file deletion causes
orphaned resources and infrastructure inconsistencies.
</description>

<problem>
Direct state file deletion causes:
- Cloud resources remain running (orphaned)
- Terraform doesn't know about existing resources
- Re-creating resource causes conflict (already exists in cloud)
- Difficult and expensive to recover
- Infrastructure spirals out of sync with code
</problem>

<pattern id="correct">
<title>✅ Proper State Management</title>

**To Remove Resources (CORRECT):**
```bash
# Option 1: Destroy entire environment
cd envs/dev
terraform destroy  # Prompts for confirmation
terraform destroy -auto-approve  # In CI only

# Option 2: Remove specific resource
terraform state rm google_storage_bucket.archive
# Removes from state only (bucket still in cloud)
# Then manually delete bucket in cloud console

# Option 3: Prevent resource from being managed
terraform state rm google_storage_bucket.archive
# Then delete Terraform code block for that resource
# Resource is now unmanaged (exists in cloud, TF doesn't touch it)

# Option 4: Destroy and recreate
terraform destroy -target=google_storage_bucket.archive
# Destroys resource in cloud
# Removes from state
# Can recreate with terraform apply later
```

**Safe State Operations:**
✓ Use `terraform destroy` (deletes both state + cloud resources)  
✓ Use `terraform state rm` (removes from state, keeps cloud resources)  
✓ Use `terraform state rm` + delete code (unmanages resource)  
✓ Use `-target` flag to limit scope  
✓ Always backup state before major operations  
</pattern>

<antipattern id="incorrect">
<title>❌ Direct State File Deletion</title>

```bash
# ❌ WRONG: Delete state file directly
rm terraform.tfstate

# ❌ WRONG: Modify state file with editor
vim terraform.tfstate  # Manual editing = corruption

# ❌ WRONG: Force delete without state management
rm .terraform.tfstate.backup

# Result:
# - Terraform thinks resources don't exist
# - Resources actually exist in cloud (running, costing money)
# - terraform apply tries to recreate them
# - Cloud error: resource already exists (can't create duplicate)
# - State is now corrupted/out-of-sync
# - Expensive and time-consuming to recover
```

**Real-world scenario:**
```
1. Developer deletes terraform.tfstate file
2. Terraform has no state, thinks environment is empty
3. terraform apply runs (re-creates everything)
4. GCS bucket already exists in cloud
5. Error: Bucket name already taken
6. Developer forced to:
   - Rename/move existing bucket
   - Recreate all resources
   - Restore backups
   - 2-3 hour recovery
```
</antipattern>

<why>
**State file is the source of truth:**
- Terraform doesn't query cloud to see what exists
- State file tells TF: "these resources are managed by me"
- Without state, TF is blind

**Proper cleanup sequence:**
1. Update Terraform code (remove resource block)
2. Run `terraform plan` (should show deletion)
3. Run `terraform destroy` or `terraform apply`
4. Verify in cloud console (resource actually deleted)
5. State is updated automatically

**Never skip these steps:**
- Direct deletion = state corruption
- Corruption = infrastructure chaos
</why>

<when-to-apply>
**Always use proper methods:**
- Any state removal
- Any infrastructure destruction
- Any state file migration

**Exception:** Only exception is fresh local dev environment where state can be recreated
</when-to-apply>

<implementation-checklist>
- [ ] Never `rm terraform.tfstate`
- [ ] Always use `terraform destroy` or `terraform state rm`
- [ ] Team policy: state file is sacred
- [ ] Backup state before major operations
- [ ] Document disaster recovery procedures
- [ ] Train team on proper state management
- [ ] Set up state file versioning (in backend)
</implementation-checklist>

<related-rules>
- TF-REMOTE-STATE-008: Remote backend storage
- TF-STATE-DRIFT-010: Drift detection
</related-rules>

</rule>


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
