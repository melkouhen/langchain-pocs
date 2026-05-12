# Terraform State File Safety

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
