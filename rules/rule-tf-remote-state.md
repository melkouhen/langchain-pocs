# Terraform Remote State Backend

<rule id="TF-REMOTE-STATE-008" severity="CRITICAL" category="Architecture">
<title>Remote State Backend: Never Local State</title>

<description>
Use a remote backend (GCS) for all team projects. Local state files
expose infrastructure data and prevent collaboration.
</description>

<problem>
Local state files cause:
- Sensitive data stored on developer's laptop (credentials in plaintext!)
- No locking → multiple devs apply simultaneously → state corruption
- No history/versioning → can't rollback to previous state
- Unsynced state between team members
- Easy to accidentally delete/modify state file
</problem>

<pattern id="correct">
<title>✅ Remote Backend (GCS Example)</title>

```hcl
# backend.tf
terraform {
  backend "gcs" {
    bucket  = "terraform-state-prod"
    prefix  = "prod/"
    project = "my-project"
  }
}
```

**Advantages:**
✓ State stored in managed cloud service  
✓ Automatic versioning and backups  
✓ State locking (prevents concurrent applies)  
✓ Team access control (who can read/modify)  
✓ Audit logs (who changed state, when)  
✓ No local files = no laptop exposure  

**Backend Type:**
- GCS (Google Cloud Storage) - Used for GCP projects
</pattern>

<antipattern id="incorrect">
<title>❌ Local State File</title>

```hcl
# ❌ WRONG: No backend specified (defaults to local)
terraform {
  # No backend block = terraform.tfstate in current directory
}

# Result:
# - terraform.tfstate contains secrets in plaintext
# - Stored on developer's laptop
# - Multiple devs → state file conflicts
# - No locking, corruption risk
```
</antipattern>

<why>
**State files contain:**
- Resource IDs and metadata
- Database passwords
- API keys and credentials
- Private IP addresses
- All sensitive infrastructure data

**Local state risks:**
1. **Security**: Secrets on unencrypted laptop
2. **Collaboration**: No locking → conflicts
3. **Disaster**: No backups → state loss = infrastructure loss
4. **Compliance**: Sensitive data not in managed service
</why>

<when-to-apply>
**Use remote backend for:**
- Any production environment
- Team projects (2+ developers)
- Any project with sensitive data

**Local state is OK for:**
- Personal throwaway experiments
- Learning/tutorials
</when-to-apply>

<implementation-checklist>
- [ ] Choose backend service (GCS)
- [ ] Create backend storage (bucket, enable versioning)
- [ ] Create backend.tf with credentials
- [ ] Run `terraform init` to migrate state (if migrating)
- [ ] Verify: `terraform state list` works
- [ ] Ensure backend has proper access controls
- [ ] Enable state file encryption at rest
- [ ] Document backend setup in README
- [ ] Remove local terraform.tfstate files from laptops
</implementation-checklist>

<related-rules>
- TF-ENV-ISOLATION-005: Per-environment backends
- TF-STATE-DELETION-009: State file safety
- TF-STATE-DRIFT-010: Drift detection
</related-rules>

</rule>
