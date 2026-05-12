# Catégories des Règles Terraform

**Version:** 2.4  
**Date:** 2026-05-12  
**Total Règles:** 25  
**Total Catégories:** 5  
**Scopes:** 3 (cloudrun, gcs, global)

---

## 📊 Vue d'Ensemble

Les règles sont organisées en **5 catégories principales** pour une meilleure clarté et cohérence.

```
Code Quality     ████████████████████████████░░░░░░░ 7 règles (28%)
Architecture     ████████████████████████░░░░░░░░░░░ 6 règles (24%)
Security         ████████████████████████░░░░░░░░░░░ 6 règles (24%)
State Management ████████████░░░░░░░░░░░░░░░░░░░░░░ 3 règles (12%)
Operations       ████████████░░░░░░░░░░░░░░░░░░░░░░ 3 règles (12%)
```

---

## 🏗️ 1. Architecture (6 règles)

**Scope:** Structure globale du projet, organisation des fichiers, environnements, modules officiels

| ID | Gravité | Règle |
|----|---------|-------|
| CLOUDRUN-MODULE-USAGE | CRITICAL | Use Official GoogleCloudPlatform/cloud-run/google Module |
| GCS-MODULE-USAGE | CRITICAL | Use Official terraform-google-modules/cloud-storage/google Module |
| TF-STRUCTURE | CRITICAL | Project Layout Organization |
| TF-ENV-SEPARATION | CRITICAL | Environment Separation: Folders vs Workspaces |
| TF-ENV-COMPOSITION | CRITICAL | Environment Configurations Must Not Declare Resources |
| TF-ENV-ISOLATION | CRITICAL | Environment Isolation: Separate Directories and State |

**Principes clés:**
- **Utiliser les modules officiels** (Cloud Run, GCS) au lieu de ressources directes
- Structure 3 tiers: modules/ + envs/ + global/
- Dossiers séparés par environnement (pas de workspaces)
- Environnements = composition de modules (pas de ressources inline)
- Isolation complète dev/staging/prod

**Impact:** CRITIQUE - Mauvaise architecture ou absence de modules = chaos opérationnel + incohérences

---

## 🔒 2. Security (6 règles)

**Scope:** Sécurité, gestion des credentials, prévention des fuites de données, contrôle d'accès

| ID | Gravité | Règle |
|----|---------|-------|
| CLOUDRUN-INGRESS-SECURITY | CRITICAL | Restrict Ingress to Minimum Required Access |
| CLOUDRUN-SECRETS-MANAGEMENT | CRITICAL | Use Secret Manager for Sensitive Environment Variables |
| TF-NO-SECRETS | CRITICAL | No Hardcoded Secrets |
| TF-ENV-ISOLATION-BACKEND | CRITICAL | Environment Isolation: Separate Backends & State |
| TF-STATE-DELETION | CRITICAL | Never Delete State Files Directly |
| GCS-NAMING-UBLA | CRITICAL | GCS Bucket Naming Convention and UBLA |

**Principes clés:**
- Jamais de secrets hardcodés (utiliser variables sensibles ou secret managers)
- Backends séparés par environnement (isolation complète)
- Jamais supprimer les state files manuellement (risque de perte)
- Nommage conforme DNS + UBLA pour GCS
- Cloud Run: ingress restrictif (internal/internal-and-cloud-load-balancing)
- Cloud Run: Secret Manager pour env vars sensibles (pas cleartext)

**Impact:** CRITIQUE - Violation = fuite de credentials ou perte d'infrastructure

---

## 📦 3. State Management (3 règles)

**Scope:** Gestion du state Terraform, versioning, reproductibilité

| ID | Gravité | Règle |
|----|---------|-------|
| TF-BACKEND-STATE | CRITICAL | Remote State Backend via GCS |
| TF-VERSION-PINNING | CRITICAL | Version Pinning: Providers & Terraform |
| TF-PROVIDER-LOCKING | MAJOR | Provider Lock Files: Commit .terraform.lock.hcl |

**Principes clés:**
- State remote (GCS) jamais local (laptop)
- Versions pinnées (`~> X.Y`) pour reproductibilité
- Lock files committés (`.terraform.lock.hcl`) pour cohérence d'équipe

**Impact:** CRITIQUE/MAJOR - Mauvaise gestion = drift, corruption, divergence

---

## ✨ 4. Code Quality (7 règles)

**Scope:** Qualité du code, maintenabilité, bonnes pratiques de développement

| ID | Gravité | Règle |
|----|---------|-------|
| GCS-PROVIDER-VERSION | CRITICAL | GCS Module Provider Version Constraint |
| GCS-BUCKET-SYNTAX | MAJOR | GCS Bucket Block vs Argument Syntax |
| GCS-INPUT-TYPES | MAJOR | Module Input Types: Map vs Scalar |
| TF-MODULES-DRY | MAJOR | Module Creation Criteria (DRY Principle) |
| TF-MODULES-SCOPE | MAJOR | Module Scope: Shallow & Focused |
| TF-RESOURCE-NAMING | MAJOR | Resource Naming Convention |
| TF-AVOID-HARDCODING | MAJOR | Avoid Hardcoding: Use Variables & Locals |

**Principes clés:**
- Version pinning des modules (CRITICAL - évite breaking changes)
- Respecter la syntaxe Terraform (blocks vs arguments)
- Types d'inputs corrects (maps pour per-bucket configs)
- Modules = DRY (2+ usages), shallow (pas de deep nesting)
- Naming cohérent: `${env}-${type}-${purpose}`
- Paramétrage via variables (pas de hardcoding)

**Impact:** CRITICAL (version) / MAJOR (syntaxe, qualité) - Code propre = maintenabilité + scalabilité

---

## 🚀 5. Operations (3 règles)

**Scope:** Opérations quotidiennes, CI/CD, monitoring, workflow

| ID | Gravité | Règle |
|----|---------|-------|
| TF-ALWAYS-PLAN | CRITICAL | Always Review Plan Before Apply |
| TF-CICD | MAJOR | CI/CD Integration: Format, Validate, Plan |
| TF-STATE-DRIFT | MINOR | State Drift Detection: Regular Plan Runs |

**Principes clés:**
- Toujours `terraform plan` avant `apply` (review obligatoire - CRITICAL)
- CI/CD: fmt + validate + plan + approval gate (MAJOR - qualité)
- Drift detection régulière (MINOR - monitoring, pas bloquant)

**Impact:** CRITICAL (plan obligatoire) / MAJOR (CI/CD) / MINOR (drift detection)

---

## 📈 Statistiques

### Par Gravité

| Gravité | Nombre | % |
|---------|--------|---|
| CRITICAL | 16 | 64% |
| MAJOR | 8 | 32% |
| MINOR | 1 | 4% |

### Par Catégorie + Gravité

| Catégorie | CRITICAL | MAJOR | MINOR | Total |
|-----------|----------|-------|-------|-------|
| Architecture | 6 | 0 | 0 | 6 |
| Security | 6 | 0 | 0 | 6 |
| State Management | 2 | 1 | 0 | 3 |
| Code Quality | 1 | 6 | 0 | 7 |
| Operations | 1 | 1 | 1 | 3 |
| **Total** | **16** | **8** | **1** | **25** |

---

## 🔄 Évolution des Catégories

### v1.0 (Initial) - 13 catégories
Trop granulaire, chevauchements, difficile à naviguer

### v2.0 (Actuel) - 5 catégories

**Consolidations effectuées:**

| Anciennes Catégories | → | Nouvelle Catégorie |
|---------------------|---|-------------------|
| Architecture, Structure, Infrastructure | → | **Architecture** |
| Security, Naming & Security, Safety | → | **Security** |
| State Management, Reliability | → | **State Management** |
| Code Quality, Compatibility | → | **Code Quality** |
| Best Practice, Automation, Monitoring | → | **Operations** |

**Avantages:**
- ✅ Plus simple à comprendre (5 vs 13)
- ✅ Pas de chevauchements
- ✅ Cohérence sémantique
- ✅ Facilite la recherche et navigation

---

## 🎯 Usage Recommandé

### Pour Développeurs

**Priorité 1 - CRITICAL (14 règles):**
1. Commencer par **Architecture** (4) — structure du projet
2. Puis **Security** (4) — credentials et isolation
3. Puis **State Management** (2) — backend et versioning
4. Enfin **Code Quality** (3) + **Operations** (1)

**Priorité 2 - MAJOR (7 règles):**
- Appliquer progressivement pour améliorer qualité et ops

### Pour Revue de Code

Checklist par catégorie:
- [ ] **Architecture**: Structure 3-tiers ? Envs séparés ?
- [ ] **Security**: Secrets hardcodés ? Backends isolés ?
- [ ] **State Management**: Remote backend ? Versions pinnées ?
- [ ] **Code Quality**: DRY ? Naming cohérent ? Paramétrage ?
- [ ] **Operations**: Plan avant apply ? CI/CD ? Drift detection ?

### Pour Agent IA

Stratégie de recherche knowledge base:
1. Identifier catégorie du problème
2. Rechercher règles de cette catégorie
3. Appliquer patterns corrects
4. Valider avec checklist

---

## 📚 Références

- **Index complet:** `RULES_INDEX.md`
- **Format des règles:** `RULES_FORMAT.md`
- **Rapport de revue:** `REVIEW_REPORT.md`

---

**Généré le:** 2026-05-12  
**Par:** Claude Sonnet 4.5  
**Version:** 2.0
