# Terraform Environment Module Composition Rules

<rule id="TF-ENV-COMPOSITION" severity="CRITICAL" category="Structure">
<title>Environment Configurations Must Not Declare Cloud Resources Directly</title>

<description>
Les configurations d'environnement (dans `envs/`) ne doivent contenir aucun bloc `resource`
déclarant des ressources cloud. Elles servent uniquement à paramétrer et composer des modules
définis dans le répertoire `modules/`. Cette séparation garantit que toute la logique
d'infrastructure réutilisable est centralisée dans les modules.
</description>

<context>
Scope: envs/**/*.tf
Applies to: All Terraform environment configurations
Directory: envs/dev/, envs/staging/, envs/prod/
</context>

<problem>
Déclarer des ressources cloud directement dans `envs/` conduit à :
- Duplication de code entre les environnements (dev/staging/prod)
- Logique d'infrastructure éclatée entre `envs/` et `modules/`
- Impossible de réutiliser la configuration dans un autre contexte
- Divergence silencieuse entre environnements (chaque env évolue indépendamment)
- Difficulté à appliquer un correctif ou une mise à jour de manière uniforme
</problem>

<pattern id="correct">
<title>✅ Correct Pattern — Environment as Composition Layer</title>
<explanation>envs/prod/main.tf référence uniquement des modules, aucun bloc resource</explanation>

```hcl
# envs/prod/main.tf — CORRECT

module "app_bucket" {
  source = "../../modules/gcs_bucket"

  project_id          = var.project_id
  bucket_name         = "${var.project_id}-app-prod"
  location            = var.region
  environment         = "prod"
  versioning_enabled  = true
  lifecycle_rule_age  = 365
}

module "logs_bucket" {
  source = "../../modules/gcs_bucket"

  project_id         = var.project_id
  bucket_name        = "${var.project_id}-logs-prod"
  location           = var.region
  environment        = "prod"
  versioning_enabled = false
  lifecycle_rule_age = 90
}
```

```hcl
# envs/dev/main.tf — CORRECT

module "app_bucket" {
  source = "../../modules/gcs_bucket"

  project_id         = var.project_id
  bucket_name        = "${var.project_id}-app-dev"
  location           = var.region
  environment        = "dev"
  versioning_enabled = false
  lifecycle_rule_age = 30
}
```
</pattern>

<antipattern id="incorrect">
<title>❌ Common Mistake — Resource Declared Directly in envs/</title>
<explanation>envs/prod/main.tf contient un bloc resource au lieu d'appeler un module</explanation>

```hcl
# envs/prod/main.tf — INCORRECT ❌

resource "google_storage_bucket" "app" {
  name          = "${var.project_id}-app-prod"  # ❌ Logique dupliquée en dev et staging
  location      = var.region
  force_destroy = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action { type = "Delete" }
    condition { age = 365 }
  }
}
```

<result>
La même configuration `google_storage_bucket` est copiée dans envs/dev/ et envs/staging/
avec de légères différences. Tout correctif doit être appliqué manuellement dans les 3 envs.
La divergence silencieuse devient inévitable.
</result>
</antipattern>

<why>
**Root Cause of Violations:** Les équipes ajoutent une ressource rapide directement dans
l'environnement sans créer de module, pensant gagner du temps. La dette s'accumule en silence.

**Consequence:**
- La duplication entre envs/ crée des divergences non détectées jusqu'en production
- Un bug dans la ressource doit être corrigé dans chaque env séparément
- Impossible de garantir que dev et prod ont la même configuration de base
- La revue de code ne peut pas valider l'uniformité entre environnements

**Prevention:**
- Toute ressource cloud doit exister dans `modules/` avant d'être utilisée dans `envs/`
- Si une ressource n'existe que dans un seul env, elle doit quand même passer par un module
  (cf. TF-MODULES-002 : la règle DRY s'applique dès 2 environments qui pourraient diverger)
</why>

<validation>
  <step number="1">Vérifier l'absence de blocs `resource` dans envs/ :</step>
  <step number="2">`grep -r "^resource " envs/` → doit retourner vide</step>
  <step number="3">`grep -r "^module " envs/` → doit lister uniquement des appels de modules</step>
  <result-expected>✓ Aucune ressource cloud déclarée dans envs/, uniquement des blocs module</result-expected>
  <result-failure>✗ Présence de blocs resource dans envs/ — déplacer la logique dans modules/</result-failure>
</validation>

<when-to-apply>
**Appliquer cette règle TOUJOURS :**
- Lors de la création ou modification d'un fichier dans `envs/`
- Lors d'une revue de code sur un PR touchant `envs/**/*.tf`
- Lors du refactoring d'un projet existant

**Ne pas confondre avec :**
- Les blocs `terraform {}` et `provider {}` dans envs/ — autorisés (configuration backend/provider)
- Les blocs `data {}` dans envs/ — acceptables si la donnée est spécifique à l'environnement
- Les blocs `module {}` dans envs/ — c'est exactement ce qui est attendu ✓
</when-to-apply>

<implementation-checklist>
- [ ] Identifier tous les blocs `resource` dans `envs/**/*.tf`
- [ ] Pour chaque ressource trouvée, créer ou identifier le module correspondant dans `modules/`
- [ ] Extraire la logique de la ressource dans le module (variables pour les valeurs différentes par env)
- [ ] Remplacer le bloc `resource` dans envs/ par un appel `module`
- [ ] Passer les valeurs spécifiques à l'env via les variables du module
- [ ] Vérifier : `terraform plan` produit le même résultat avant/après refactoring
- [ ] Exécuter `grep -r "^resource " envs/` → aucun résultat attendu
</implementation-checklist>

<related-rules>
- TF-STRUCTURE-001: Organisation générale du projet (trois niveaux : modules, envs, global)
- TF-MODULES-002: Critères de création d'un module (DRY)
- TF-MODULES-003: Périmètre des modules (shallow et focused)
</related-rules>

<examples>
<example number="1">
<title>Refactoring : ressource inline → appel de module</title>
<code>
# AVANT (incorrect) — envs/dev/main.tf
resource "google_storage_bucket" "data" {
  name     = "my-project-data-dev"
  location = "EU"
}

# APRÈS (correct) — modules/gcs_bucket/main.tf
resource "google_storage_bucket" "this" {
  name     = var.bucket_name
  location = var.location
}

# APRÈS (correct) — envs/dev/main.tf
module "data_bucket" {
  source      = "../../modules/gcs_bucket"
  bucket_name = "my-project-data-dev"
  location    = "EU"
}
</code>
</example>

<example number="2">
<title>Paramétrage différent par environnement via le même module</title>
<code>
# modules/gcs_bucket/variables.tf
variable "versioning_enabled" {
  type    = bool
  default = false
}

variable "lifecycle_rule_age" {
  type    = number
  default = 30
}

# envs/dev/main.tf — paramètres dev
module "bucket" {
  source              = "../../modules/gcs_bucket"
  bucket_name         = "my-project-dev"
  versioning_enabled  = false
  lifecycle_rule_age  = 7
}

# envs/prod/main.tf — paramètres prod
module "bucket" {
  source              = "../../modules/gcs_bucket"
  bucket_name         = "my-project-prod"
  versioning_enabled  = true
  lifecycle_rule_age  = 365
}
</code>
</example>
</examples>

<references>
- Terraform Documentation: Module Composition — https://developer.hashicorp.com/terraform/language/modules/develop/composition
- Best Practice: Infrastructure as Code — separation between reusable logic and environment config
- Date Discovered: 2026-05-11
- Status: Validated — enforced in this project
</references>

</rule>
