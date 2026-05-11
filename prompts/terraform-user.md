# Spécifications Utilisateur - Projet Terraform

**Rôle:** Senior Cloud Engineer & Terraform Architect.

**Tâche:** Générer une structure de projet Terraform production-ready pour déployer des buckets Google Cloud Storage (GCS).

**Vue d'Ensemble du Projet:**
- **Objectif:** Créer une infrastructure GCS résiliente et maintainable avec isolation dev/prod
- **Scope:** GCS buckets avec versioning, lifecycle rules, et IAM
- **Bénéficiaires:** Équipe DevOps, développeurs, infrastructures

**Spécifications Techniques:**

**Ressources:**
- GCS buckets (environnements dev et prod)
  - Bucket dev: `{{BUCKET_PREFIX}}-dev` (ex: `my-bucket-elkouhen-dev`)
  - Bucket prod: `{{BUCKET_PREFIX}}-prod` (ex: `my-bucket-elkouhen-prod`)
- Configuration IAM: Admins, Viewers, Creators
- Versioning: Activé sur les deux buckets
- Lifecycle Rules: Suppression automatique après 30 jours (dev), 365 jours (prod)

**Infrastructure Cloud:**
- **Provider:** GCP (Google Cloud Platform)
- **Région:** `{{GCP_REGION}}` (ex: europe-west9)
- **Projet GCP:** `{{GCP_PROJECT_ID}}`

**Structure Fichiers:**
- **Project Root:** `{{PROJECT_ROOT}}` (ex: `/Users/melkouhen/audit-tools/test-langchain/work`)
- **Output Structure:**
  - `modules/gcs_bucket/` - Module réutilisable
  - `envs/dev/` - Configuration environnement dev
  - `envs/prod/` - Configuration environnement prod
  - `envs/dev/terraform_logs.error` - Logs d'erreurs validation (dev uniquement)

**Environnements:**
- **Dev** et **Prod** (état séparé, configurations isolées)
- Validation UNIQUEMENT sur `envs/dev`
- Production `envs/prod` prêt mais non appliqué

**Livrables Attendus:**
1. ✅ Code Terraform validé (terraform validate → 0 erreurs)
2. ✅ Configuration d'environnement dev et prod
3. ✅ Documentation (README.md, DEPLOYMENT_GUIDE.md)
4. ✅ Rapport de validation complet
5. ✅ Logs d'erreurs en `terraform_logs.error`

**Voir Also:**
- Pour le protocole complet → `prompts/terraform-system.md`
- Pour la review de code → `prompts/terraform-review.md`
- Pour la validation → `prompts/terraform-validate.md`
