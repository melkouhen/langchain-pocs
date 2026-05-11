# Spécifications Utilisateur - Projet Terraform

**Rôle:** Senior Cloud Engineer & Terraform Architect.

**Tâche:** Générer une structure de projet Terraform production-ready pour déployer des resources GCP.

**Vue d'Ensemble du Projet:**
- **Objectif:** Créer une infrastructure résiliente et maintainable avec isolation dev/prod
- **Bénéficiaires:** Équipe DevOps, développeurs, infrastructures

**Spécifications Techniques:**

**Ressources:**
- GCS buckets (environnements dev et prod)
  - Bucket dev: `{{BUCKET_PREFIX}}-dev` (ex: `my-bucket-elkouhen-dev`)
  - Bucket prod: `{{BUCKET_PREFIX}}-prod` (ex: `my-bucket-elkouhen-prod`)

**Infrastructure Cloud:**
- **Provider:** GCP (Google Cloud Platform)
- **Région:** ` europe-west9`
- **Projet GCP:** `beaming-botany-495511-n6`

**Environnements:**
- **Dev** et **Prod** (état séparé, configurations isolées)

**Répertoire de Génération:**
- **Chemin:** `/Users/melkouhen/audit-tools/test-langchain/work`

**Voir Also:**
- Pour le protocole complet → `prompts/terraform-system.md`
