# CODE REVIEW REPORT TEMPLATE

**Project**: [Project Name]  
**Reviewer**: Terraform Architect v2.0  
**Date**: [YYYY-MM-DD]  
**Status**: COMPLETE

---

## EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| Total Issues Found | N |
| CRITIQUE Issues | N ❌ BLOCKING |
| MAJEUR Issues | N ⚠️ SHOULD FIX |
| MINEUR Issues | N ℹ️ NICE TO FIX |
| Security Review | ✓ PASSED |
| Best Practices | ✓ PASSED |
| Gate 2 Decision | ✅ APPROVED FOR CONFIRMATION |

---

## SECTION 1: CRITIQUE ISSUES (BLOCKING)

**Status**: All CRITIQUE issues must be fixed before proceeding.

### Issue #1: [Issue Title]

**Severity**: 🔴 CRITIQUE  
**File**: `path/to/file.tf`  
**Line**: [line number]  
**Category**: [Security|Drift|Syntax]

**Problem**:
```
[Detailed explanation of what's wrong and why it's critical]
```

**Code (Before)**:
```hcl
[Show problematic code]
```

**Code (After)**:
```hcl
[Show fixed code]
```

**Rationale for Fix**:
- [Reason 1]
- [Reason 2]

**Verification**:
- ✅ Fix applied to `path/to/file.tf:line`
- ✅ terraform validate: PASSED
- ✅ No new errors introduced

---

## SECTION 2: MAJEUR ISSUES (SHOULD FIX)

**Status**: MAJEUR issues are fixed or exclusion is documented.

### Issue #1: [Issue Title]

**Severity**: 🟡 MAJEUR  
**File**: `path/to/file.tf`  
**Line**: [line number]  
**Category**: [Best Practice|Maintainability|Documentation]

**Problem**:
```
[Explanation]
```

**Code (Before)**:
```hcl
[Current code]
```

**Recommended Fix**:
```hcl
[Suggested improvement]
```

**Status**: ✅ FIXED

**Changes Made**:
- [Change 1]
- [Change 2]

---

## SECTION 3: MINEUR ISSUES (NICE TO FIX)

**Status**: MINEUR issues are documented; fixing is optional.

### Issue #1: [Issue Title]

**Severity**: ℹ️ MINEUR  
**File**: `path/to/file.tf`  
**Line**: [line number]  
**Category**: Style/Naming/Optimization

**Observation**: [Description]

**Recommendation**: [Suggestion]

**Status**: ⏭️ DEFERRED

**Rationale**: [Why not fixing now - e.g., "Follows project convention", "Low priority"]

---

## SECTION 4: SECURITY REVIEW

**Review Date**: [Date]  
**Methodology**: [List of checks performed]

### Access Control
- [ ] ✓ Uniform bucket-level access configured
- [ ] ✓ IAM bindings properly scoped
- [ ] ✓ No overly permissive roles (e.g., Editor)
- [ ] ✓ Service accounts used (not user accounts)

### Secrets Management
- [ ] ✓ No hardcoded credentials in code
- [ ] ✓ Secrets marked as `sensitive = true`
- [ ] ✓ Secrets sourced from variables, not literals
- [ ] ✓ No SSH keys or API keys in code

### Encryption & Data Protection
- [ ] ✓ Encryption at rest configured (if applicable)
- [ ] ✓ Encryption in transit enabled
- [ ] ✓ Key management documented
- [ ] ✓ Backup encryption configured

### Audit & Logging
- [ ] ✓ Audit logging enabled (GCS, RDS, etc.)
- [ ] ✓ CloudTrail configured (if AWS)
- [ ] ✓ Log retention policies defined
- [ ] ✓ Log analysis/alerting setup

### Network & Isolation
- [ ] ✓ VPC/Network isolation if applicable
- [ ] ✓ Public access disabled by default
- [ ] ✓ Firewall rules minimal (least privilege)
- [ ] ✓ No overly open CIDR blocks (0.0.0.0/0)

### Compliance
- [ ] ✓ Resource tagging for compliance tracking
- [ ] ✓ Data residency requirements met
- [ ] ✓ Data retention policies defined
- [ ] ✓ PII handling documented

**Security Review Result**: ✅ PASSED

---

## SECTION 5: BEST PRACTICES REVIEW

### Code Structure
- [ ] ✓ Clear separation: main.tf, variables.tf, outputs.tf
- [ ] ✓ Modular design (if > 3 resources)
- [ ] ✓ Module inputs/outputs well-defined
- [ ] ✓ No circular dependencies
- [ ] ✓ Consistent naming conventions

### Variables & Outputs
- [ ] ✓ All variables declared with `type`
- [ ] ✓ All variables documented with `description`
- [ ] ✓ Sensitive variables marked `sensitive = true`
- [ ] ✓ Default values appropriate
- [ ] ✓ Input validation where needed (e.g., `validation` blocks)
- [ ] ✓ All outputs documented
- [ ] ✓ Output descriptions clear and useful
- [ ] ✓ No output of sensitive values

### Code Quality
- [ ] ✓ No hardcoded values (all use variables)
- [ ] ✓ `for_each` used only with maps (not lists)
- [ ] ✓ `dynamic` blocks used only when necessary
- [ ] ✓ Comments explain WHY, not WHAT
- [ ] ✓ No unnecessary abstractions (KISS principle)
- [ ] ✓ DRY principle followed (no code duplication)
- [ ] ✓ Consistent formatting (indentation, spacing)

### Drift Prevention
- [ ] ✓ No `timestamp()` in resource identifiers
- [ ] ✓ No `date()` in resource names
- [ ] ✓ No `random_id()` in bucket/resource names
- [ ] ✓ Labels and tags are static or variable-driven
- [ ] ✓ Lifecycle rules properly scoped
- [ ] ✓ `ignore_changes` used appropriately

### Dependencies & Providers
- [ ] ✓ Provider versions pinned (e.g., `>= 5.0, < 6.0`)
- [ ] ✓ Terraform version constraint specified
- [ ] ✓ All provider requirements declared
- [ ] ✓ Dependencies properly expressed (avoid implicit ordering)
- [ ] ✓ `depends_on` used only when necessary

### Error Handling & Validation
- [ ] ✓ Variable validation blocks include error messages
- [ ] ✓ Bucket naming validation enforced
- [ ] ✓ Environment values validated
- [ ] ✓ Region/location values validated
- [ ] ✓ Null checks where applicable

**Best Practices Result**: ✅ PASSED

---

## SECTION 6: DOCUMENTATION REVIEW (Code Level)

### Inline Comments
- [ ] ✓ Non-obvious logic explained
- [ ] ✓ Complex blocks documented
- [ ] ✓ Security decisions justified
- [ ] ✓ No excessive/redundant comments
- [ ] ✓ Comments are current and accurate

### Variable Documentation
- [ ] ✓ All variables have descriptions
- [ ] ✓ Complex types explained (object, list, etc.)
- [ ] ✓ Default values documented
- [ ] ✓ Constraints explained (e.g., min length)

### Output Documentation
- [ ] ✓ All outputs described
- [ ] ✓ Output types clear
- [ ] ✓ Usage guidance provided (where needed)

**Documentation Result**: ✅ PASSED

---

## SECTION 7: SPECIFIC FINDINGS

### Finding #1: [Title]
**Location**: [File:Line]  
**Type**: [Type]  
**Action**: [Action taken]

---

## SECTION 8: GATE 2 DECISION

### Summary
- CRITIQUE issues: N (ALL FIXED ✅)
- MAJEUR issues: N (FIXED or DOCUMENTED ✅)
- MINEUR issues: N (DOCUMENTED ✅)
- Security: PASSED ✅
- Best Practices: PASSED ✅
- Drift Prevention: PASSED ✅

### Decision
✅ **CODE REVIEW GATE APPROVED**

This code is ready for confirmation phase (Gate 3).

### Sign-Off
**Reviewer**: Terraform Architect v2.0  
**Date**: [YYYY-MM-DD HH:MM:SS]  
**Next Step**: Execute Gate 3 - Confirmation Validation

---

## APPENDIX: Changes Summary

### Files Modified
1. `[file1.tf]` - [Summary of changes]
2. `[file2.tf]` - [Summary of changes]

### Total Changes
- Lines added: N
- Lines removed: N
- Files modified: N

### Verification Commands
```bash
# To review changes
git diff

# To apply changes
terraform plan -var-file=environments/[env]/terraform.tfvars

# To verify
terraform validate
```

---

**Report Generated**: [YYYY-MM-DD HH:MM:SS]  
**Processing Time**: [X minutes]  
**System Version**: Terraform Architect v2.0
