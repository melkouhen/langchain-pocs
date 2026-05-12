# Terraform Resource Naming Convention

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
