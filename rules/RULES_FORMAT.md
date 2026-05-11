# Format des Règles Terraform

Les règles apprises durant la génération de projets Terraform doivent suivre ce format structuré pour être intégrées au répertoire `rules/` et réutilisables par l'agent de génération.

## Structure XML Standard

Chaque règle est encapsulée dans une balise `<rule>` avec les attributs suivants:

```xml
<rule id="XXX-YYY-NNN" severity="SEVERITY" category="CATEGORY">
```

### Attributs Obligatoires

| Attribut | Valeurs | Description |
|----------|---------|-------------|
| `id` | `[A-Z]{3}-[A-Z]+-\d{3}` | Format: `PREFIX-TYPE-NUMBER` (ex: `GCS-PROVIDER-001`) |
| `severity` | `CRITICAL`, `MAJOR`, `MINOR` | Niveau d'impact de la violation |
| `category` | `Compatibility`, `Security`, `Performance`, `Maintainability`, `Naming`, `Structure` | Domaine d'application |

### Sections Obligatoires

#### 1. **`<title>`** — Titre court (< 80 caractères)
Une phrase qui résume la règle clairement.

```xml
<title>GCS Module Provider Version Constraint</title>
```

#### 2. **`<description>`** — Description détaillée
Explique le problème, le contexte, et pourquoi c'est important (3-4 phrases).

```xml
<description>
The terraform-google-modules/cloud-storage/google module has tightly coupled 
dependencies with specific Google provider versions. Version mismatches cause 
validation failures and missing API support.
</description>
```

#### 3. **`<context>`** — Contexte d'application
Conditions où cette règle s'applique (module, version, provider, etc.).

```xml
<context>
Module: terraform-google-modules/cloud-storage/google
Version: ~> 12.3
Provider Required: >= 6.37.0
</context>
```

#### 4. **`<problem>`** — Énoncé du problème
Explication claire du problème identifié.

```xml
<problem>
The module version ~> 12.3 requires Google provider >= 6.37.0.
Using version ~> 5.0 is insufficient because older provider versions lack 
required APIs and data structures needed by the module.
</problem>
```

#### 5. **Patterns — Code Examples**

##### 5a. **`<pattern id="correct">`** — Exemple correct
Un ou plusieurs exemples de code CORRECT.

```xml
<pattern id="correct">
  <title>✅ Correct Pattern</title>
  <explanation>Update required_providers block to match module requirements exactly</explanation>
  
  ```hcl
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"  # Provides >= 6.37.0 for module compatibility
    }
  }
  ```
</pattern>
```

##### 5b. **`<antipattern id="incorrect">`** — Exemple incorrect
Un ou plusieurs exemples de code INCORRECT avec le problème résultant.

```xml
<antipattern id="incorrect">
  <title>❌ Common Mistake</title>
  <explanation>Using older provider version constraint</explanation>
  
  ```hcl
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"  # ❌ WRONG: Module 12.3 needs >= 6.37.0
    }
  }
  ```
  
  <result>Error during `terraform validate`: Missing required fields or API operations 
  not available in provider version 5.x</result>
</antipattern>
```

#### 6. **`<why>`** — Explication profonde
Racine cause, conséquences, et prévention.

```xml
<why>
Module dependencies are tightly coupled to provider versions. 

**Root Cause:** The terraform-google-modules/cloud-storage/google module uses newer 
GCP APIs and data structures that only exist in Google provider version 6.37.0+.

**Consequence:** 
- terraform init: Provider downloads v5.x
- terraform validate: Fails with "unknown field" or "unsupported operation" errors
- Deployment blocked until resolved

**Prevention:** Always pin provider version to match module documentation.
</why>
```

#### 7. **`<validation>`** — Étapes de validation
Comment tester que la règle est respectée.

```xml
<validation>
  <step number="1">terraform init</step>
  <step number="2">terraform validate</step>
  <result-expected>✓ Provider version satisfies module requirements</result-expected>
  <result-failure>✗ Error: unsupported field X in resource Y (provider version too old)</result-failure>
</validation>
```

#### 8. **`<when-to-apply>`** — Quand appliquer
Conditions explicites d'application.

```xml
<when-to-apply>
**Apply this rule WHENEVER:**
- Using terraform-google-modules/cloud-storage/google module
- Module version >= 12.x
- Writing required_providers block

**DO NOT apply if:**
- Using older module version (< 12.x) - check its documentation
- Using different provider (not hashicorp/google)
</when-to-apply>
```

#### 9. **`<implementation-checklist>`** — Checklist d'implémentation
Étapes concrètes pour implémenter la correction.

```xml
<implementation-checklist>
- [ ] Verify module version in registry: https://registry.terraform.io/modules/...
- [ ] Check "Required Provider Versions" section of module docs
- [ ] Update required_providers.google.version to match requirement
- [ ] Run `terraform init`
- [ ] Run `terraform validate` - should pass
- [ ] Document provider version in code comments if non-obvious
</implementation-checklist>
```

#### 10. **`<related-rules>`** — Règles connexes
Références à d'autres règles liées.

```xml
<related-rules>
- GCS-INPUT-002: Module input types (map vs scalar)
- GCS-STRUCTURE-003: Environment isolation
</related-rules>
```

#### 11. **`<references>`** — Sources et références
Documentation externe, dates, statut.

```xml
<references>
- Module Registry: https://registry.terraform.io/modules/terraform-google-modules/cloud-storage/google
- Google Provider: https://registry.terraform.io/providers/hashicorp/google/latest
- Module Changelog: Version 12.3 requires provider >= 6.37.0
- Date Discovered: 2024-01-15
- Status: Validated in production
</references>
```

---

## Convention de Nommage des Fichiers

```
rules-{PREFIX}-{DOMAIN}.md
```

**Exemples:**
- `rules-gcs-providers.md` — Règles GCS relatives aux providers
- `rules-tf-naming-state.md` — Règles Terraform sur le naming et state
- `rules-tf-security-cicd.md` — Règles Terraform sur sécurité et CI/CD

**Format ID Rule:**
- Préfixe 3 lettres: `GCS`, `TF`, etc.
- Type 2-3 lettres: `PROVIDER`, `INPUT`, `SECURITY`, `NAMING`, etc.
- Numéro: `001`, `002`, etc. (séquentiel dans le domaine)

---

## Convention de Sévérité

| Niveau | Signification | Action |
|--------|---------------|--------|
| `CRITICAL` | Bloque le déploiement, violation de sécurité ou compatibilité | Doit être corrigé immédiatement |
| `MAJOR` | Risque significatif ou non-conformité importante | Doit être corrigé avant déploiement |
| `MINOR` | Amélioration, norme de style ou optimisation | À corriger si temps disponible |

---

## Convention de Catégorie

| Catégorie | Exemple |
|-----------|---------|
| `Compatibility` | Version constraints, provider compatibility |
| `Security` | IAM, encryption, secret management |
| `Performance` | Optimization, resource sizing |
| `Maintainability` | Naming conventions, structure, documentation |
| `Naming` | Resource naming patterns |
| `Structure` | Module layout, file organization |
| `State` | State management, locking, backends |
| `CI/CD` | Automation, validation pipelines |

---

## Intégration avec l'Agent

Pour que l'agent puisse utiliser les règles apprises:

1. **Générer la règle** avec la structure complète ci-dessus
2. **Ajouter au répertoire** `rules/` du projet
3. **Indexer** dans la knowledge base (ChromaDB) lors de la prochaine exécution
4. **Agent consulte** les règles avant chaque phase de génération

### Points clés pour l'agent

- Utiliser `search_knowledge_base()` pour chercher les règles applicables
- Valider le code généré contre les règles via `validate_and_fix_code()` et `review_and_fix_code()`
- Corriger les violations selon leur sévérité:
  - ❌ **CRITICAL** → Bloquer, corriger, ré-valider
  - ⚠️ **MAJOR** → Corriger avant déploiement
  - ℹ️ **MINOR** → Documenter, corriger optionnellement

---

## Template Prêt à Utiliser

Voir `RULES_TEMPLATE.md` pour un template complet à dupliquer et remplir.
