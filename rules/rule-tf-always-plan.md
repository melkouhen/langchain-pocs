# Terraform: Always Review Plan Before Apply

<rule id="TF-ALWAYS-PLAN" severity="CRITICAL" category="Operations">
<title>Always Review Plan Before Apply</title>

<description>
Never run `terraform apply` without reviewing `terraform plan` first.
The plan is your "dry run" — it shows exactly what will change before making changes.
</description>

<problem>
Applying without plan review:
- Unexpected resources destroyed/modified
- Wrong variables interpreted
- Typos go unnoticed until applied
- No opportunity to stop bad changes
</problem>

<pattern id="correct">
<title>✅ Plan-Review-Apply Workflow</title>

```bash
# Step 1: Create plan
terraform plan -out=tfplan

# Step 2: REVIEW the plan carefully
# Look for:
# - Resources being destroyed (intentional?)
# - Unexpected modifications
# - Correct variables being used

# Step 3: Apply ONLY if plan looks correct
terraform apply tfplan
```

**What to Check in Plan:**
✓ Resources being created (should match intent)  
✓ Resources being modified (why? is this expected?)  
✓ Resources being destroyed (really want to delete this?)  
✓ Variable values are correct  
✓ Counts/for_each are correct  

**Rule of Thumb:** If you can't explain what each line of the plan does, don't apply it.
</pattern>

<antipattern id="incorrect">
<title>❌ Auto-Approve Apply</title>

```bash
# ❌ WRONG: Skip plan review
terraform apply -auto-approve

# ❌ WRONG: Apply without even running plan
terraform apply

# ❌ WRONG: In CI, apply without approval
# GitHub Actions: apply immediately after successful tests
# No human review of plan output
```

**Real-world incident:**
```bash
# Developer runs: terraform apply -auto-approve
# Refactored code accidentally destroys database
# Database backup 2 hours old
# 2 hours of data lost

# With plan review:
# terraform plan would show: database resource will be destroyed
# Developer sees this, stops, fixes code first
```
</antipattern>

<why>
**Terraform is powerful:**
- One command can destroy infrastructure
- No built-in "undo" (though TF can import destroyed resources)
- State drift means reality is different from code

**Plan review is your safety net:**
- Shows exactly what will happen
- Catches typos before infrastructure changes
- Opportunity to stop before damage
- Especially critical in production
</why>

<when-to-apply>
**Always apply this rule:**
- Any `terraform apply` in production
- CI/CD apply gates (approval required)
- Any destructive operations
- Any code you didn't write

**Acceptable exceptions:**
- Local development experiments (still good practice though)
</when-to-apply>

<implementation-checklist>
- [ ] Make it team policy: plan before apply always
- [ ] CI/CD: store plan artifact, require approval
- [ ] Document in runbook: show plan before apply
- [ ] Train team: what to look for in plan output
- [ ] Never use `-auto-approve` in production
- [ ] For emergency fixes: still run plan, just approval might be verbal
</implementation-checklist>

<related-rules>
- TF-CI-CD-INTEGRATION-012: Automated plan in CI/CD
</related-rules>

</rule>
