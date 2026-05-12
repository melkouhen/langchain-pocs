# Nouvelles Règles Ajoutées - 2026-05-12

## 📋 Vue d'ensemble

3 nouvelles règles au format XML structuré ont été ajoutées, générées automatiquement par l'agent lors des tests d'évaluation.

## 🆕 Règles ajoutées

### 1. rule-gcs-naming-ubla.md
**ID:** GCS-NAMING-UBLA-001  
**Sévérité:** CRITICAL  
**Catégorie:** Naming & Security

**Sujet :** Conventions de nommage GCS et Uniform Bucket-Level Access

**Problèmes traités :**
- Noms de buckets invalides (uppercase, underscores)
- Contraintes DNS GCS (lowercase [a-z0-9-] uniquement)
- Configuration UBLA pour IAM cohérent
- Conflits entre IAM bucket-level et ACLs object-level

**Pattern correct :**
```hcl
module "gcs_bucket_dev" {
  source = "../../modules/gcs_bucket"
  
  bucket_name    = "${var.bucket_prefix}-dev"  # lowercase, hyphens
  enable_versioning = true
  
  # UBLA enabled via bucket attribute
  public_access_prevention = "enforced"
}
```

**Validation :**
```bash
echo "my-bucket-elkouhen-dev" | grep -E "^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"
terraform validate
terraform plan | grep "uniform_bucket_level_access"
```

**Références :**
- https://cloud.google.com/storage/docs/naming-buckets
- https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket

---

### 2. rule-tf-backend-state.md
**ID:** TF-BACKEND-STATE-003  
**Sévérité:** CRITICAL  
**Catégorie:** State Management

**Sujet :** Gestion d'état remote via GCS backend

**Problèmes traités :**
- State files locaux (credentials en plaintext sur laptop)
- Pas de versioning/backup
- Pas de state locking (corruption par accès concurrents)
- Pas de collaboration possible entre team members
- Risque de commit accidentel dans git

**Pattern correct :**
```hcl
# envs/dev/backend.tf
terraform {
  backend "gcs" {
    bucket  = "terraform-state-dev-beaming-botany"
    prefix  = "dev/"
    project = "beaming-botany-495511-n6"
  }
}
```

**Avantages :**
- ✓ State en GCS (managed service)
- ✓ Versioning automatique
- ✓ State locking (prévient modifications concurrentes)
- ✓ Encryption at rest
- ✓ Audit logs
- ✓ Pas de données sensibles sur laptop

**Validation :**
```bash
cat envs/dev/backend.tf | grep -A3 'backend "gcs"'
find envs/ -name "terraform.tfstate*"  # Should be empty
gsutil ls gs://terraform-state-dev-*/dev/
```

**Références :**
- https://www.terraform.io/language/settings/backends/gcs
- https://cloud.google.com/docs/terraform/best-practices

---

### 3. rule-tf-env-isolation.md
**ID:** TF-ENV-ISOLATION-002  
**Sévérité:** CRITICAL  
**Catégorie:** Infrastructure

**Sujet :** Isolation des environnements (dev/staging/prod)

**Problèmes traités :**
- Workspaces partagent le même backend (pas vraiment isolés)
- Facile d'oublier quel workspace est actif
- Modifications accidentelles de prod pendant dev
- Pas de permissions différentes par environnement
- Pas de trail audit clair

**Pattern correct :**
```
work_dir/
├── modules/
│   └── gcs_bucket/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── envs/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── backend.tf  (GCS: terraform-state-dev-*)
│   │   └── terraform.tfvars
│   ├── staging/
│   │   └── backend.tf  (GCS: terraform-state-staging-*)
│   └── prod/
│       └── backend.tf  (GCS: terraform-state-prod-*)
```

**Avantages :**
- ✓ State files complètement séparés
- ✓ Backends GCS différents par environnement
- ✓ Permissions IAM différentes (prod = restrictif)
- ✓ Audit trail clair (quel env modifié)
- ✓ Impossible de modifier prod par erreur depuis dev

**Validation :**
```bash
ls -la work_dir/envs/  # Should show: dev/ staging/ prod/
cat work_dir/envs/dev/backend.tf | grep bucket
cat work_dir/envs/prod/backend.tf | grep bucket  # Different bucket
cd envs/dev && terraform state list
cd envs/prod && terraform state list  # Different resources
```

**Références :**
- https://www.terraform.io/language/state/layouts
- https://cloud.google.com/docs/terraform/best-practices#separate_environments

---

## 🔄 Différences avec les règles existantes

### Format
- **Existantes** : Markdown avec sections libres
- **Nouvelles** : XML structuré avec balises sémantiques

### Structure XML
```xml
<rule id="..." severity="..." category="...">
  <title>...</title>
  <description>...</description>
  <context>...</context>
  <problem>...</problem>
  <pattern id="correct">...</pattern>
  <antipattern id="incorrect">...</antipattern>
  <why>...</why>
  <validation>...</validation>
  <when-to-apply>...</when-to-apply>
  <implementation-checklist>...</implementation-checklist>
  <related-rules>...</related-rules>
  <references>...</references>
</rule>
```

### Avantages du format XML
1. **Machine-parseable** : Extraction automatique des checklists
2. **Structuré** : Sections obligatoires (problem, solution, validation)
3. **Liens sémantiques** : Related rules, references
4. **Severity/Category** : Classification claire

### Inconvénients
1. **Moins lisible** : XML verbeux vs markdown simple
2. **ChromaDB** : Nécessite parsing pour extraction sémantique
3. **Édition** : Plus complexe qu'éditer markdown

---

## 📊 Statistiques

| Métrique | Valeur |
|----------|--------|
| Nouvelles règles | 3 |
| Format | XML |
| Taille totale | 18.3 KB |
| Checklists | 3 (10-15 items chacune) |
| Validations | 3 (avec commandes bash) |
| Références | 9 liens documentation |
| Sévérité | 3 CRITICAL |

---

## 🎯 Impact sur le Knowledge Base

Ces nouvelles règles seront chargées par ChromaDB au prochain `init` :

```python
from terraform_agent.knowledge_base import KnowledgeBase
kb = KnowledgeBase(config)
```

ChromaDB va :
1. Charger les 3 fichiers `.md` (contenu XML)
2. Les découper en chunks
3. Les indexer avec embeddings
4. Les rendre cherchables

**Requêtes qui matcheront :**
- "GCS bucket naming conventions"
- "Terraform remote state backend"
- "environment isolation best practices"
- "UBLA uniform bucket level access"
- "state locking terraform"

---

## 🔮 Prochaines étapes suggérées

### Court terme
1. Tester la recherche knowledge base avec ces nouvelles règles
2. Vérifier que ChromaDB les indexe correctement
3. Exécuter eval harness pour voir si agent les utilise

### Moyen terme
4. Convertir les règles XML → Markdown pour cohérence
5. Ou convertir toutes les règles Markdown → XML pour uniformité
6. Créer un parser XML pour extraction automatique des checklists

### Long terme
7. Dashboard web pour visualiser toutes les règles
8. Système de validation automatique (terraform validate + règles)
9. Génération automatique de règles par l'agent

---

## 📝 Notes

- **Source** : Ces règles ont été générées par l'agent lui-même lors du test tc01
- **Localisation d'origine** : `work/rules/*.xml`
- **Copie vers** : `rules/rule-*.md`
- **Format** : XML content avec extension `.md` (pour cohérence avec règles existantes)
- **Commit** : `b43f90b` - feat: add 3 structured XML rules from work/rules

---

**Document créé le :** 2026-05-12  
**Auteur :** Claude Sonnet 4.5  
**Version :** 1.0
