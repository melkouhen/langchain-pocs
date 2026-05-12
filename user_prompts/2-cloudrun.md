# Spécifications Utilisateur - Projet Terraform

**Rôle:** Senior Cloud Engineer & Terraform Architect.

**Tâche:** Générer une structure de projet Terraform production-ready pour déployer des resources GCP.

**Vue d'Ensemble du Projet:**
- **Objectif:** Créer une infrastructure résiliente et maintainable avec isolation dev/prod
- **Bénéficiaires:** Équipe DevOps, développeurs, infrastructures

**Spécifications Techniques:**

**Ressources:**
- Cloud Run services (environnements dev et prod)
  - Service dev: `my-api-dev`
  - Service prod: `my-api-prod`
  - Image container: `gcr.io/beaming-botany-495511-n6/my-api:latest`
  - Port: `8080` (configurable)
  - Configuration:
    - CPU: 1 vCPU
    - Memory: 512Mi
    - Max instances: 10
    - Min instances: 0 (scale to zero)
    - Concurrency: 80 requêtes par instance
    - Timeout: 300s
    - Ingress: `all` (accepte le trafic de toutes les sources)
    - Allow unauthenticated: `true` pour dev, `false` pour prod

**Infrastructure Cloud:**
- **Provider:** GCP (Google Cloud Platform)
- **Région:** `europe-west9`
- **Projet GCP:** `beaming-botany-495511-n6`

**Environnements:**
- **Dev** et **Prod** (état séparé, configurations isolées)

**Répertoire de Génération:**
- **work_dir:** `/Users/melkouhen/audit-tools/test-langchain/work`

**Voir Also:**
- Pour le protocole complet → `prompts/terraform-system.md`
