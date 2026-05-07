# Implementation Guide: Terraform Architect v2.0

**Target Date**: Complete by 2026-05-28 (4 weeks)  
**Status**: Ready for Implementation  
**Owner**: Platform Engineering  

---

## Executive Summary

This guide explains how to implement the PRD for Terraform Architect v2.0, which enforces a gated pipeline to guarantee code quality. The system moves from the current "generation-centric" approach to a "quality-centric" approach with three mandatory checkpoints.

**Key Changes**:
- ✅ Enforce GENERATION → VALIDATION → REVIEW → CONFIRMATION pipeline
- ✅ Detect and fix forbidden patterns (timestamp(), random_id(), etc.)
- ✅ Generate detailed reports at each checkpoint
- ✅ Guarantee zero CRITIQUE issues before delivery
- ✅ Apply smart documentation rules

---

## Deliverables Overview

### 📋 Documents Created

| Document | Purpose | Status |
|----------|---------|--------|
| **PRD_TERRAFORM_ARCHITECT.md** | Complete requirements (12 sections, 65 details) | ✅ Created |
| **terraform-system-v2.md** | Updated system prompt (enforced pipeline) | ✅ Created |
| **TEMPLATES_CODE_REVIEW_REPORT.md** | Template for Gate 2 reviews | ✅ Created |
| **REFERENCES_FORBIDDEN_PATTERNS.md** | Pattern detection guide (8 patterns) | ✅ Created |
| **IMPROVEMENTS_PROPOSAL.md** | Analysis of v1.0 gaps | ✅ Created |
| **IMPLEMENTATION_GUIDE.md** | This document | ✅ In Progress |

### 🔧 Scripts to Create

| Script | Purpose | Gate | Status |
|--------|---------|------|--------|
| `validate_and_fix.sh` | Execute terraform validate | Gate 1 | 📋 Needed |
| `review_code.sh` | Check for forbidden patterns | Gate 2 | 📋 Needed |
| `forbidden_patterns_detector.sh` | Detect all 8 patterns | Gate 2 | 📋 Needed |
| `documentation_rules_engine.sh` | Calculate doc complexity | Delivery | 📋 Needed |
| `confirm_validation.sh` | Re-validate after fixes | Gate 3 | 📋 Needed |
| `terraform_agent.py` | LangChain integration | All | 📋 Needed |

---

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Goal**: Create and validate all documents and reference materials

**Tasks**:
- [ ] Review PRD with team
- [ ] Validate forbidden patterns list (add/remove as needed)
- [ ] Approve terraform-system-v2.md
- [ ] Approve documentation rules thresholds

**Deliverables**:
- ✅ All documents finalized
- ✅ Team sign-off on approach
- ✅ Questions/clarifications resolved

**Time**: 2-3 days

---

### Phase 2: Scripts Development (Week 2)

**Goal**: Implement validation and review scripts

#### Task 2.1: validate_and_fix.sh

**Purpose**: Execute Gate 1 - Syntax Validation

**Pseudocode**:
```bash
#!/bin/bash
for retry in {1..3}; do
  cd $TERRAFORM_DIR
  terraform init --upgrade
  if terraform validate; then
    echo "✅ GATE 1 PASSED"
    exit 0
  else
    echo "Fix attempt $retry/3..."
    # TODO: Auto-fix based on error pattern
    # For now, manual fix required
  fi
done
echo "❌ GATE 1 FAILED"
exit 1
```

**Complexity**: Low (2-3 hours)

#### Task 2.2: review_code.sh

**Purpose**: Execute Gate 2 - Code Review

**Pseudocode**:
```bash
#!/bin/bash
CRITIQUE_COUNT=0

# Check 1: Forbidden patterns
check_forbidden_patterns() {
  # Detect timestamp(), random_id(), date(), etc.
  # Return count of CRITIQUE issues
}

# Check 2: Variables documented
check_variables() {
  # Parse variables.tf
  # Verify all have description and type
}

# Check 3: Security basics
check_security() {
  # No hardcoded credentials
  # IAM defined (if applicable)
}

if [ $CRITIQUE_COUNT -eq 0 ]; then
  echo "✅ GATE 2 PASSED"
  exit 0
else
  echo "❌ GATE 2 FAILED: $CRITIQUE_COUNT CRITIQUE issues"
  exit 1
fi
```

**Complexity**: Medium (4-6 hours)

#### Task 2.3: forbidden_patterns_detector.sh

**Purpose**: Detect all 8 forbidden patterns

**Patterns to Detect**:
```bash
# Pattern 1: timestamp()
grep -rn "timestamp()" $DIR --include="*.tf"

# Pattern 2: date()
grep -rn "date(" $DIR --include="*.tf"

# Pattern 3: random_id() in names
grep -rn "random_id" $DIR --include="*.tf" | grep -E "(name|bucket)"

# Pattern 4: Hardcoded credentials
grep -rn "password\|secret\|api_key" $DIR --include="*.tf" | grep "="

# Pattern 5: for_each with lists
grep -rn "for_each.*\[" $DIR --include="*.tf"

# Pattern 6: for_each with array access
grep -rn "for_each.*var\.[a-z_]*\[" $DIR --include="*.tf"

# Pattern 7: Unnecessary dynamic blocks
grep -rn "dynamic" $DIR --include="*.tf" | count

# Pattern 8: Hardcoded env values
grep -rn "\"dev\"\|\"prod\"\|\"staging\"" $DIR --include="*.tf" | grep -v var
```

**Complexity**: Medium (4-6 hours)

#### Task 2.4: documentation_rules_engine.sh

**Purpose**: Calculate documentation complexity

**Logic**:
```bash
#!/bin/bash

# Count resources
RESOURCE_COUNT=$(grep -c "^resource \"" main.tf)

# Count modules
MODULE_COUNT=$(ls -d modules/* 2>/dev/null | wc -l)

# Count variables
VARIABLE_COUNT=$(grep -c "^variable \"" variables.tf)

# Determine level
if [ $RESOURCE_COUNT -le 3 ] && [ $MODULE_COUNT -le 1 ] && [ $VARIABLE_COUNT -le 10 ]; then
  echo "MINIMAL"
elif [ $RESOURCE_COUNT -gt 3 ] || [ $MODULE_COUNT -gt 1 ] || [ $VARIABLE_COUNT -gt 10 ]; then
  echo "STANDARD"
else
  echo "FULL"
fi
```

**Complexity**: Low (2-3 hours)

**Total Phase 2 Time**: 12-18 hours (1-2 days, or spread over week)

---

### Phase 3: Integration (Week 3)

**Goal**: Integrate scripts into LangChain/Claude system

#### Task 3.1: Integrate with Claude Code

**Action**: Create wrapper that calls scripts from Claude Code system

**Pseudocode**:
```python
# In terraform_agent.py
def execute_gate_1_validation(terraform_dir):
    """Execute Gate 1: Syntax Validation"""
    result = subprocess.run(
        ['bash', 'scripts/validate_and_fix.sh', terraform_dir],
        capture_output=True,
        text=True
    )
    return {
        'gate': 'GATE_1_SYNTAX',
        'status': 'PASSED' if result.returncode == 0 else 'FAILED',
        'output': result.stdout,
        'errors': result.stderr
    }

def execute_gate_2_review(terraform_dir):
    """Execute Gate 2: Code Review"""
    patterns = run_forbidden_patterns_detector(terraform_dir)
    variables = check_variables(terraform_dir)
    
    return {
        'gate': 'GATE_2_REVIEW',
        'status': 'PASSED' if len(patterns) == 0 else 'FAILED',
        'critique_issues': patterns,
        'majeur_issues': variables
    }

def execute_gate_3_confirm(terraform_dir):
    """Execute Gate 3: Confirmation Validation"""
    result = subprocess.run(
        ['bash', 'scripts/validate_and_fix.sh', terraform_dir],
        capture_output=True,
        text=True
    )
    return {
        'gate': 'GATE_3_CONFIRM',
        'status': 'PASSED' if result.returncode == 0 else 'FAILED',
        'output': result.stdout
    }
```

**Complexity**: Medium (6-8 hours)

#### Task 3.2: Add TaskCreate/TaskUpdate Integration

**Action**: Track checkpoint progress using tasks

```python
def track_gate_progress(gate_name, status):
    """Create/update task for gate progress"""
    TaskCreate(
        subject=f"Execute {gate_name}",
        description=f"Run {gate_name} validation"
    )
    TaskUpdate(
        taskId=task_id,
        status="in_progress" if starting else "completed"
    )
```

**Complexity**: Low (2-3 hours)

#### Task 3.3: Generate Checkpoint Reports

**Action**: Create detailed reports at each gate

```python
def generate_gate_report(gate_name, results):
    """Generate checkpoint report"""
    return f"""
    ✅/❌ {gate_name}: {results['status']}
    
    Issues Found: {len(results['issues'])}
    
    [Details of issues and fixes]
    
    Next Step: [proceed to next gate or fix and retry]
    """
```

**Complexity**: Medium (4-6 hours)

**Total Phase 3 Time**: 12-17 hours (2-3 days)

---

### Phase 4: Testing (Week 4)

**Goal**: Validate system works on real cases

#### Test Case 1: Simple GCS Bucket (sample.json)
- [ ] Run through all 3 gates
- [ ] Verify timestamp() is detected and fixed
- [ ] Verify documentation rule = MINIMAL
- [ ] Verify final output is production-ready

**Time**: 2-3 hours

#### Test Case 2: Multi-Module RDS Stack
- [ ] Run through all 3 gates
- [ ] Verify multiple modules handled correctly
- [ ] Verify security checks pass
- [ ] Verify documentation rule = STANDARD

**Time**: 2-3 hours

#### Test Case 3: Forbidden Pattern Detection
- [ ] Create code with each pattern
- [ ] Verify all detected
- [ ] Verify auto-fix works
- [ ] Verify re-validation passes

**Time**: 2-3 hours

#### Test Case 4: Documentation Rules
- [ ] Test MINIMAL case (≤3 resources)
- [ ] Test STANDARD case (>3 resources)
- [ ] Test FULL case (multi-region)
- [ ] Verify correct files generated

**Time**: 1-2 hours

**Total Phase 4 Time**: 7-11 hours (2-3 days)

---

### Phase 5: Refinement & Release (Week 5)

**Goal**: Polish, document, and release

#### Task 5.1: Edge Case Handling
- [ ] Test error scenarios (invalid HCL, missing modules)
- [ ] Test retry logic (max retries behavior)
- [ ] Test timeout scenarios
- [ ] Verify error messages are clear

**Time**: 4-6 hours

#### Task 5.2: Documentation
- [ ] Create user guide for v2.0
- [ ] Document all changes from v1.0
- [ ] Create troubleshooting guide
- [ ] Create migration guide for existing projects

**Time**: 4-6 hours

#### Task 5.3: Release & Communication
- [ ] Tag version 2.0 in git
- [ ] Publish to repository
- [ ] Announce to team
- [ ] Update onboarding docs

**Time**: 2-3 hours

**Total Phase 5 Time**: 10-15 hours (2-3 days)

---

## Total Implementation Effort

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 1: Foundation | Week 1 | 2-3 days |
| Phase 2: Scripts | Week 2 | 1-2 days |
| Phase 3: Integration | Week 3 | 2-3 days |
| Phase 4: Testing | Week 4 | 2-3 days |
| Phase 5: Release | Week 5 | 2-3 days |
| **Total** | **4 weeks** | **9-14 days** |

---

## Success Criteria

### Functional Success
- [ ] All 3 gates executable and automated
- [ ] All 8 forbidden patterns detected
- [ ] All fixes applied and verified
- [ ] Reports generated at each gate
- [ ] Documentation rules applied correctly

### Quality Success
- [ ] 100% of validation gates pass
- [ ] 0 CRITIQUE issues reach delivery
- [ ] 0 timestamp() patterns in production code
- [ ] All variables documented
- [ ] Zero manual intervention needed for gates

### User Success
- [ ] Clear reports at each checkpoint
- [ ] Fast execution (< 5 min per gate)
- [ ] Easy to understand failures
- [ ] Easy path to recovery

---

## Rollout Plan

### Week 1-2: Internal Validation
- Test with sample.json case (GCS bucket)
- Gather feedback from internal team
- Fix any issues found

### Week 3: Beta Release
- Release v2.0-beta to brave users
- Collect feedback
- Document edge cases

### Week 4: Production Release
- Release v2.0 to all users
- Announce in team channels
- Provide support for adoption

### Ongoing: Improvement
- Monitor for issues
- Collect user feedback
- Plan v2.1 enhancements

---

## File Structure After Implementation

```
audit-tools/test-langchain/
├── PRD_TERRAFORM_ARCHITECT.md (✅ Complete requirements)
├── IMPROVEMENTS_PROPOSAL.md (✅ Gap analysis)
├── IMPLEMENTATION_GUIDE.md (✅ This file)
├── TEMPLATES_CODE_REVIEW_REPORT.md (✅ Report template)
├── REFERENCES_FORBIDDEN_PATTERNS.md (✅ Pattern detection)
│
├── prompts/
│   ├── terraform-system.md (old v1.0)
│   └── terraform-system-v2.md (✅ NEW - enforced pipeline)
│
├── scripts/ (📋 TO CREATE)
│   ├── validate_and_fix.sh (Gate 1)
│   ├── review_code.sh (Gate 2)
│   ├── forbidden_patterns_detector.sh (Gate 2 helper)
│   ├── documentation_rules_engine.sh (Deliverable)
│   └── confirm_validation.sh (Gate 3)
│
├── terraform_agent/ (✅ Existing - to enhance)
│   ├── agent.py (add gate execution)
│   ├── tools.py (add gate tools)
│   └── __init__.py
│
└── work/ (Test project)
    └── terraform/ (test code)
```

---

## Next Steps

### Immediate (This Week)
- [ ] Stakeholder review of PRD
- [ ] Get approval to proceed with Phase 2
- [ ] Identify who will implement scripts

### This Month
- [ ] Complete all phases 1-5
- [ ] Test on real projects
- [ ] Release v2.0

### Next Month
- [ ] Monitor adoption
- [ ] Collect feedback
- [ ] Plan v2.1 enhancements

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Scripts fail to detect patterns | Start with grep-based detection, manually verify |
| Integration with Claude takes longer | Create mock tools first, integrate later |
| Tests fail on real code | Gather test cases, build incrementally |
| Team doesn't adopt | Good documentation + training sessions |
| Performance issues | Profile scripts, optimize if needed |

---

## Questions & Support

### For Implementation Leads
- Who owns Phase 2 (scripts)?
- Who owns Phase 3 (integration)?
- How are bugs reported/fixed?
- What's the support escalation path?

### For Users (after release)
- See terraform-system-v2.md for usage
- See troubleshooting section in user guide
- Contact team for edge cases

---

## Success Metrics (Post-Release)

**Track these metrics after v2.0 release:**

1. **Code Quality**
   - % of deployments passing all 3 gates
   - % of CRITIQUE issues caught before delivery
   - % of forbidden patterns eliminated

2. **User Experience**
   - Average time per gate execution
   - User satisfaction score
   - Support tickets related to gates

3. **Adoption**
   - % of users migrated from v1.0
   - Number of new projects using v2.0
   - Feedback quality and quantity

---

**Document Version**: 1.0  
**Status**: Ready for Implementation Planning  
**Last Updated**: 2026-05-07
