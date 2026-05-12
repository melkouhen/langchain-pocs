# Terraform Rules Repository

Ce répertoire contient les **règles apprises** et les **best practices** pour la génération Terraform autonome.

---

## 📁 Structure

| Fichier | Contenu |
|---------|---------|
| **CATEGORIES.md** | 📊 Documentation des 5 catégories de règles |
| **RULES_INDEX.md** | 📇 Index complet des 21 règles par sévérité, catégorie et préfixe |
| **RULES_FORMAT.md** | 📖 Documentation complète du format XML des règles |
| **RULES_TEMPLATE.md** | 📋 Template vide à dupliquer pour créer une nouvelle règle |
| **REVIEW_REPORT.md** | 📝 Rapport de revue et consolidation des règles |
| **rule-*.md** | ✅ Règles individuelles (21 fichiers) |

---

## 🎯 Qu'est-ce qu'une Règle?

Une **règle** est un pattern documenté qui:

1. ✅ Identifie un problème ou une bonne pratique
2. ✅ Fournit des exemples correct (pattern) et incorrect (antipattern)
3. ✅ Explique la cause racine et les conséquences
4. ✅ Inclut une checklist d'implémentation et des étapes de validation
5. ✅ Est réutilisable par l'agent dans les générations futures

**Exemple:** Règle sur les version constraints (GCS-PROVIDER-VERSION)
```
Problème: terraform-google-modules/cloud-storage/google v12.3 
          nécessite Google provider >= 6.37.0
Pattern correct: version = "~> 6.0"
Antipattern: version = "~> 5.0"
Conséquence: Erreur terraform validate
```

---

## 📊 Statistiques (v2.0)

| Métrique | Valeur |
|----------|--------|
| **Total règles** | 21 |
| **Catégories** | 5 (Architecture, Security, State Management, Code Quality, Operations) |
| **CRITICAL** | 14 (67%) |
| **MAJOR** | 7 (33%) |
| **MINOR** | 0 (0%) |

### Distribution par Catégorie

```
Code Quality     ██████████████████████████████████░░ 7 règles (33%)
Architecture     ████████████████████░░░░░░░░░░░░░░░ 4 règles (19%)
Security         ████████████████████░░░░░░░░░░░░░░░ 4 règles (19%)
State Management ███████████████░░░░░░░░░░░░░░░░░░░░ 3 règles (14%)
Operations       ███████████████░░░░░░░░░░░░░░░░░░░░ 3 règles (14%)
```

Voir [CATEGORIES.md](CATEGORIES.md) pour la description complète de chaque catégorie.

---

## 🚀 Utilisation

### Pour ajouter une nouvelle règle:

1. **Consultez** [RULES_FORMAT.md](RULES_FORMAT.md) pour comprendre la structure
2. **Dupliquez** [RULES_TEMPLATE.md](RULES_TEMPLATE.md)
3. **Choisissez une catégorie** parmi: Architecture, Security, State Management, Code Quality, Operations
4. **Complétez** chaque section XML:
   - `<rule id="..." severity="..." category="...">` — Attributs obligatoires
   - `<title>` — Titre court (< 80 caractères)
   - `<description>` — Explication détaillée
   - `<context>` — Conditions d'application (module, version, provider)
   - `<problem>` — Énoncé du problème
   - `<pattern id="correct">` — Exemple(s) valide(s) avec code HCL
   - `<antipattern id="incorrect">` — Exemple(s) invalide(s)
   - `<why>` — Cause racine et explication
   - `<validation>` — Comment valider la conformité
   - `<when-to-apply>` — Conditions d'application
   - `<implementation-checklist>` — Étapes concrètes
   - `<related-rules>` — Règles connexes
   - `<references>` — Documentation externe
5. **Renommez** le fichier: `rule-{prefix}-{name}.md`
   - Préfixes: `gcs` (Google Cloud Storage), `tf` (Terraform général)
   - Exemple: `rule-gcs-logging.md`, `rule-tf-backend.md`
6. **Validez** la structure XML (fermeture correcte des balises)
7. **Ajoutez** une entrée dans [RULES_INDEX.md](RULES_INDEX.md)
8. **Committez** dans le répertoire `rules/`

### Pour l'agent (générations futures):

L'agent Terraform autonome indexera automatiquement les règles dans ChromaDB et:
- 🔍 Cherchera les règles applicables via `search_knowledge_base(query)`
  - Ex: `"security google_storage_bucket"` → GCS-NAMING-UBLA
  - Ex: `"state management backend"` → TF-BACKEND-STATE
- ✅ Validera le code généré contre les règles avec `review_and_fix_code()`
- 🔧 Corrigera les violations CRITICAL et MAJOR avant de passer en production

---

## 📚 Règles Existantes (21 règles)

### Par Catégorie

#### 🏗️ Architecture (4 règles CRITICAL)
- [TF-STRUCTURE](rule-tf-structure.md) — Project Layout Organization
- [TF-ENV-SEPARATION](rule-tf-env-separation.md) — Environment Separation: Folders vs Workspaces
- [TF-ENV-COMPOSITION](rule-tf-env-composition.md) — Environment Configurations Must Not Declare Resources
- [TF-ENV-ISOLATION](rule-tf-env-isolation.md) — Environment Isolation: Separate Directories and State

#### 🔒 Security (4 règles CRITICAL)
- [GCS-NAMING-UBLA](rule-gcs-naming-ubla.md) — GCS Bucket Naming Convention and UBLA
- [TF-ENV-ISOLATION-BACKEND](rule-tf-env-isolation-backend.md) — Environment Isolation: Separate Backends & State
- [TF-NO-SECRETS](rule-tf-no-hardcoded-secrets.md) — No Hardcoded Secrets
- [TF-STATE-DELETION](rule-tf-state-deletion.md) — Never Delete State Files Directly

#### 📦 State Management (2 CRITICAL, 1 MAJOR)
- [TF-BACKEND-STATE](rule-tf-backend-state.md) — Remote State Management via GCS Backend (CRITICAL)
- [TF-VERSION-PINNING](rule-tf-version-pinning.md) — Version Pinning: Providers & Terraform (CRITICAL)
- [TF-PROVIDER-LOCKING](rule-tf-provider-locking.md) — Provider Lock Files: Commit .terraform.lock.hcl (MAJOR)

#### ✨ Code Quality (3 CRITICAL, 4 MAJOR)
- [GCS-BUCKET-SYNTAX](rule-gcs-bucket-syntax.md) — GCS Bucket Block vs Argument Syntax (CRITICAL)
- [GCS-INPUT-TYPES](rule-gcs-input-types.md) — Module Input Types: Map vs Scalar (CRITICAL)
- [GCS-PROVIDER-VERSION](rule-gcs-provider-version.md) — GCS Module Provider Version Constraint (CRITICAL)
- [TF-AVOID-HARDCODING](rule-tf-avoid-hardcoding.md) — Avoid Hardcoding: Use Variables & Locals (MAJOR)
- [TF-MODULES-DRY](rule-tf-modules-dry.md) — Module Creation Criteria (DRY Principle) (MAJOR)
- [TF-MODULES-SCOPE](rule-tf-modules-scope.md) — Module Scope: Shallow & Focused (MAJOR)
- [TF-RESOURCE-NAMING](rule-tf-resource-naming.md) — Resource Naming Convention (MAJOR)

#### 🚀 Operations (1 CRITICAL, 2 MAJOR)
- [TF-ALWAYS-PLAN](rule-tf-always-plan.md) — Always Review Plan Before Apply (CRITICAL)
- [TF-CICD](rule-tf-cicd-integration.md) — CI/CD Integration: Format, Validate, Plan (MAJOR)
- [TF-STATE-DRIFT](rule-tf-state-drift.md) — State Drift Detection: Regular Plan Runs (MAJOR)

### Par Sévérité

**🔴 CRITICAL (14 règles)** — Bloque la génération/déploiement:
- Toutes les règles Architecture (4)
- Toutes les règles Security (4)
- State Management: TF-BACKEND-STATE, TF-VERSION-PINNING
- Code Quality: GCS-BUCKET-SYNTAX, GCS-INPUT-TYPES, GCS-PROVIDER-VERSION
- Operations: TF-ALWAYS-PLAN

**🟠 MAJOR (7 règles)** — À corriger avant déploiement:
- State Management: TF-PROVIDER-LOCKING
- Code Quality: TF-AVOID-HARDCODING, TF-MODULES-DRY, TF-MODULES-SCOPE, TF-RESOURCE-NAMING
- Operations: TF-CICD, TF-STATE-DRIFT

---

## 🔄 Évolution

### v2.0 (2026-05-12) — Consolidation
- ✅ Consolidation de 13 catégories → **5 catégories principales**
- ✅ Suppression de 1 règle doublon (TF-REMOTE-STATE-008)
- ✅ 21 règles finales, toutes avec catégorie cohérente
- ✅ Index et documentation mis à jour

### v1.1 (Précédente)
- 13 catégories (trop granulaire)
- 21-24 règles (avec doublons)

### v1.0 (Initial)
- Première version avec règles apprises

---

## 🛠️ Maintenance

### Workflow de mise à jour

1. **Modifier une règle existante**
   - Éditer le fichier `rule-*.md`
   - Si changement de sévérité/catégorie → mettre à jour [RULES_INDEX.md](RULES_INDEX.md)
   - Re-indexer la knowledge base si nécessaire

2. **Supprimer une règle**
   - Supprimer le fichier `rule-*.md`
   - Supprimer les entrées dans [RULES_INDEX.md](RULES_INDEX.md)
   - Mettre à jour les statistiques dans [CATEGORIES.md](CATEGORIES.md)
   - Re-indexer la knowledge base

3. **Ajouter une nouvelle catégorie** (exceptionnel)
   - Mettre à jour [CATEGORIES.md](CATEGORIES.md)
   - Mettre à jour les templates et la documentation
   - Mettre à jour le prompt système dans `prompts/terraform-system.md`

---

## 📖 Documentation Complète

- **[CATEGORIES.md](CATEGORIES.md)** — Description détaillée des 5 catégories avec principes et usage
- **[RULES_INDEX.md](RULES_INDEX.md)** — Index complet avec tables par sévérité, catégorie et préfixe
- **[RULES_FORMAT.md](RULES_FORMAT.md)** — Spécification du format XML avec exemples
- **[RULES_TEMPLATE.md](RULES_TEMPLATE.md)** — Template à copier pour créer une nouvelle règle
- **[REVIEW_REPORT.md](REVIEW_REPORT.md)** — Rapport de revue et consolidation des règles

---

**Version:** 2.0  
**Dernière mise à jour:** 2026-05-12  
**Généré par:** Claude Sonnet 4.5
