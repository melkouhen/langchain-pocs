# Terraform Environment Module Delegation

<rule id="TF-ENV-MODULE-DELEGATION" severity="CRITICAL" scope="global" category="Architecture">
<title>Environment Modules Must Only Call Shared Modules With Environment Parameters</title>

<description>
Les modules Terraform d'un environnement (dev, staging, prod) ne doivent servir QUE de couche
de paramétrage : ils appellent un module partagé en lui passant les paramètres spécifiques à
l'environnement. Ils ne doivent contenir AUCUNE logique métier, AUCUN bloc resource, et AUCUNE
duplication de code. L'objectif est de garantir que tous les environnements utilisent exactement
la même base de code, seuls les paramètres changent.
</description>

<problem>
Lorsque les modules d'environnement contiennent de la logique ou des ressources directes :
- **Duplication de code** entre dev/staging/prod (maintenance cauchemardesque)
- **Divergence silencieuse** entre environnements (prod != staging != dev)
- **Impossible de corriger un bug** de manière uniforme (chaque env évolue indépendamment)
- **Risque de sécurité** : un correctif appliqué en prod peut être oublié en dev
- **Perte de confiance** : impossible de garantir que ce qui fonctionne en dev fonctionnera en prod
- **Revue de code impossible** : comment valider que 3 copies du même code sont identiques ?
- **Dette technique exponentielle** : chaque modification doit être répliquée N fois
</problem>

<pattern id="correct">
<title>✅ Environment Module as Parameter Layer Only</title>

**Structure attendue :**
```
modules/
  shared_app_stack/        # ← Module partagé contenant toute la logique
    main.tf
    variables.tf
    outputs.tf
envs/
  dev/
    main.tf                # ← Appelle shared_app_stack avec paramètres dev
  staging/
    main.tf                # ← Appelle shared_app_stack avec paramètres staging
  prod/
    main.tf                # ← Appelle shared_app_stack avec paramètres prod
```

**Module partagé (modules/shared_app_stack/main.tf) :**
```hcl
# modules/shared_app_stack/main.tf
# ✅ Toute la logique métier est ici, réutilisable par tous les environnements

resource "google_storage_bucket" "app_data" {
  name          = var.bucket_name
  location      = var.location
  force_destroy = var.allow_destroy

  versioning {
    enabled = var.versioning_enabled
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = var.lifecycle_age_days
    }
  }

  uniform_bucket_level_access = true

  labels = merge(
    {
      environment = var.environment
      managed_by  = "terraform"
    },
    var.additional_labels
  )
}

resource "google_cloud_run_service" "api" {
  name     = var.service_name
  location = var.location

  template {
    spec {
      containers {
        image = var.container_image

        resources {
          limits = {
            cpu    = var.cpu_limit
            memory = var.memory_limit
          }
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "BUCKET_NAME"
          value = google_storage_bucket.app_data.name
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# modules/shared_app_stack/variables.tf
variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod"
  }
}

variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "location" {
  type        = string
  description = "GCP region"
}

variable "bucket_name" {
  type        = string
  description = "Name of the GCS bucket"
}

variable "versioning_enabled" {
  type        = bool
  description = "Enable bucket versioning"
}

variable "lifecycle_age_days" {
  type        = number
  description = "Days before objects are deleted"
}

variable "allow_destroy" {
  type        = bool
  description = "Allow bucket to be destroyed"
  default     = false
}

variable "service_name" {
  type        = string
  description = "Cloud Run service name"
}

variable "container_image" {
  type        = string
  description = "Container image URL"
}

variable "cpu_limit" {
  type        = string
  description = "CPU limit for Cloud Run"
}

variable "memory_limit" {
  type        = string
  description = "Memory limit for Cloud Run"
}

variable "additional_labels" {
  type        = map(string)
  description = "Additional labels for resources"
  default     = {}
}
```

**Environment modules (envs/*/main.tf) :**
```hcl
# envs/dev/main.tf
# ✅ Aucune logique métier, uniquement des paramètres

module "app_stack" {
  source = "../../modules/shared_app_stack"

  environment          = "dev"
  project_id           = var.project_id
  location             = "europe-west1"
  bucket_name          = "${var.project_id}-app-dev"
  versioning_enabled   = false           # ← Pas de versioning en dev
  lifecycle_age_days   = 7               # ← Nettoyage rapide en dev
  allow_destroy        = true            # ← Autorisé en dev
  service_name         = "api-dev"
  container_image      = var.dev_image
  cpu_limit            = "1000m"         # ← Resources limitées en dev
  memory_limit         = "512Mi"
  additional_labels    = {
    cost_center = "development"
  }
}

output "bucket_name" {
  value = module.app_stack.bucket_name
}

output "service_url" {
  value = module.app_stack.service_url
}
```

```hcl
# envs/staging/main.tf
# ✅ Même structure, paramètres staging

module "app_stack" {
  source = "../../modules/shared_app_stack"

  environment          = "staging"
  project_id           = var.project_id
  location             = "europe-west1"
  bucket_name          = "${var.project_id}-app-staging"
  versioning_enabled   = true            # ← Versioning activé
  lifecycle_age_days   = 30              # ← Rétention intermédiaire
  allow_destroy        = true            # ← Autorisé en staging
  service_name         = "api-staging"
  container_image      = var.staging_image
  cpu_limit            = "2000m"         # ← Resources intermédiaires
  memory_limit         = "1Gi"
  additional_labels    = {
    cost_center = "staging"
  }
}
```

```hcl
# envs/prod/main.tf
# ✅ Même structure, paramètres production

module "app_stack" {
  source = "../../modules/shared_app_stack"

  environment          = "prod"
  project_id           = var.project_id
  location             = "europe-west1"
  bucket_name          = "${var.project_id}-app-prod"
  versioning_enabled   = true            # ← Versioning obligatoire en prod
  lifecycle_age_days   = 365             # ← Rétention longue
  allow_destroy        = false           # ← Protection en prod
  service_name         = "api-prod"
  container_image      = var.prod_image
  cpu_limit            = "4000m"         # ← Resources maximales
  memory_limit         = "2Gi"
  additional_labels    = {
    cost_center = "production"
    compliance  = "required"
  }
}
```

**Bénéfices :**
- ✅ **Une seule source de vérité** : toute la logique dans `modules/shared_app_stack/`
- ✅ **Zéro duplication** : aucun code copié-collé entre environnements
- ✅ **Correctif uniforme** : un bug corrigé dans le module partagé = corrigé partout
- ✅ **Garantie de cohérence** : tous les envs utilisent exactement la même logique
- ✅ **Revue de code simple** : valider le module partagé, puis valider les paramètres
- ✅ **Test de la logique** : tester le module partagé = tester tous les envs
- ✅ **Évolution maîtrisée** : nouvelle feature = ajout d'une variable dans le module partagé
</pattern>

<antipattern id="incorrect">
<title>❌ Duplicated Logic Across Environment Modules</title>

```hcl
# envs/dev/main.tf
# ❌ WRONG: Logique métier dupliquée dans chaque environnement

resource "google_storage_bucket" "app_data" {
  name          = "${var.project_id}-app-dev"
  location      = "europe-west1"
  force_destroy = true

  versioning {
    enabled = false
  }

  lifecycle_rule {
    action { type = "Delete" }
    condition { age = 7 }
  }

  uniform_bucket_level_access = true
  labels = { environment = "dev" }
}

resource "google_cloud_run_service" "api" {
  name     = "api-dev"
  location = "europe-west1"

  template {
    spec {
      containers {
        image = var.dev_image
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }
  }
}
```

```hcl
# envs/staging/main.tf
# ❌ WRONG: Même logique copiée-collée avec de légères différences

resource "google_storage_bucket" "app_data" {
  name          = "${var.project_id}-app-staging"
  location      = "europe-west1"
  force_destroy = true

  versioning {
    enabled = true   # ❌ Différence subtile, difficile à détecter en revue
  }

  lifecycle_rule {
    action { type = "Delete" }
    condition { age = 30 }
  }

  uniform_bucket_level_access = true
  labels = { environment = "staging" }
}

resource "google_cloud_run_service" "api" {
  name     = "api-staging"
  location = "europe-west1"

  template {
    spec {
      containers {
        image = var.staging_image
        resources {
          limits = {
            cpu    = "2000m"
            memory = "1Gi"
          }
        }
      }
    }
  }
}
```

```hcl
# envs/prod/main.tf
# ❌ WRONG: Encore la même logique, avec d'autres paramètres

resource "google_storage_bucket" "app_data" {
  name          = "${var.project_id}-app-prod"
  location      = "europe-west1"
  force_destroy = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action { type = "Delete" }
    condition { age = 365 }
  }

  uniform_bucket_level_access = true
  labels = { 
    environment = "prod"
    # ❌ BUG: label "compliance" ajouté en prod mais pas en staging/dev
    compliance  = "required"
  }
}

resource "google_cloud_run_service" "api" {
  name     = "api-prod"
  location = "europe-west1"

  template {
    spec {
      containers {
        image = var.prod_image
        resources {
          limits = {
            cpu    = "4000m"
            memory = "2Gi"
          }
        }
        # ❌ BUG: variable d'environnement manquante en prod
        # Présente en dev/staging mais oubliée ici lors d'une copie
      }
    }
  }
}
```

**Problèmes concrets :**
- ❌ **150 lignes dupliquées** au lieu de 30 lignes + appel de module
- ❌ **Divergence silencieuse** : label `compliance` uniquement en prod
- ❌ **Bug introduit par copie incomplète** : variable d'environnement manquante en prod
- ❌ **Maintenance impossible** : corriger un bug = modifier 3 fichiers + risque d'oubli
- ❌ **Revue de code cauchemardesque** : comparer 3 blocs de 50 lignes pour détecter les différences
- ❌ **Impossible de tester** : chaque env a sa propre logique, impossible de tester de manière centralisée
</antipattern>

<why>
**Principe fondamental : DRY (Don't Repeat Yourself) au niveau des environnements**

Cette règle est **CRITIQUE** car :

1. **Sécurité** : Un correctif de sécurité doit s'appliquer à TOUS les environnements.
   Si la logique est dupliquée, il y a un risque d'oublier un environnement.

2. **Fiabilité** : Si dev/staging/prod utilisent des logiques différentes, un test validé
   en staging ne garantit RIEN pour la production.

3. **Maintenance** : Chaque ligne de code dupliquée = dette technique exponentielle.
   N environnements = N fois plus de code à maintenir.

4. **Qualité** : Impossible de faire une revue de code rigoureuse sur du code dupliqué.
   Les différences subtiles passent inaperçues.

5. **Confiance** : Sans garantie que tous les envs utilisent la même base, impossible
   d'avoir confiance dans le pipeline dev → staging → prod.

**Racine du problème :**
Les développeurs ajoutent "rapidement" une ressource dans un env pour tester, puis
copient-collent vers les autres envs. La divergence commence dès la première copie.

**Solution :**
**TOUTE** logique métier doit vivre dans `modules/shared_*/`. Les fichiers `envs/*/main.tf`
ne doivent contenir QUE des appels de modules avec des paramètres différents.
</why>

<when-to-apply>
**Cette règle s'applique TOUJOURS pour :**
- Tous les fichiers dans `envs/**/*.tf`
- Tous les environnements (dev, staging, prod, test, demo, etc.)
- Tous les types de ressources (GCS, Cloud Run, GCE, GKE, BigQuery, etc.)
- Tous les modules d'infrastructure (réseau, sécurité, monitoring, etc.)

**Exceptions (très rares) :**
- Bloc `terraform {}` pour la configuration du backend (peut varier par env)
- Bloc `provider {}` si les credentials sont différentes par env
- Bloc `data {}` pour récupérer une donnée spécifique à l'env (ex: projet GCP actuel)
- Variables `variable {}` pour exposer les paramètres de l'environnement

**Règle de validation stricte :**
```bash
# Vérifier qu'aucun bloc resource n'existe dans envs/
grep -r "^resource " envs/ 
# ✅ Résultat attendu : aucune ligne trouvée

# Vérifier que seuls des modules sont appelés
grep -r "^module " envs/
# ✅ Résultat attendu : liste des appels de modules
```
</when-to-apply>

<validation>
<step number="1">Lister tous les blocs resource dans envs/ :</step>
<command>`find envs/ -name "*.tf" -exec grep -l "^resource " {} \;`</command>

<step number="2">Pour chaque fichier trouvé, identifier les ressources dupliquées :</step>
<command>`grep "^resource " envs/dev/main.tf envs/staging/main.tf envs/prod/main.tf | sort`</command>

<step number="3">Créer un module partagé pour chaque type de ressource dupliquée</step>

<step number="4">Remplacer les blocs resource par des appels module dans chaque env</step>

<step number="5">Valider que le plan Terraform reste identique :</step>
<command>`terraform plan -out=before.plan` (avant refactoring)</command>
<command>`terraform plan -out=after.plan` (après refactoring)</command>
<command>`terraform show -json before.plan > before.json`</command>
<command>`terraform show -json after.plan > after.json`</command>
<command>`diff before.json after.json` (doit être vide ou montrer uniquement des changements cosmétiques)</command>

<result-expected>
✅ Aucun bloc `resource` dans `envs/**/*.tf`
✅ Tous les appels sont des `module` pointant vers `modules/shared_*/`
✅ `terraform plan` montre "No changes" après refactoring
</result-expected>

<result-failure>
❌ Présence de blocs `resource` dans `envs/` → refactoring incomplet
❌ `terraform plan` montre des changements → régression introduite
</result-failure>
</validation>

<implementation-checklist>
- [ ] Auditer tous les fichiers `envs/**/*.tf` pour identifier les blocs `resource`
- [ ] Identifier les ressources dupliquées entre dev/staging/prod
- [ ] Créer un module partagé `modules/shared_app_stack/` (ou nom approprié)
- [ ] Déplacer toute la logique métier dans le module partagé
- [ ] Identifier les paramètres variables (nom, région, taille, etc.) → variables du module
- [ ] Remplacer chaque bloc `resource` dans `envs/` par un appel `module`
- [ ] Passer les paramètres spécifiques à chaque environnement
- [ ] Exécuter `terraform plan` dans chaque env → vérifier "No changes"
- [ ] Ajouter des validations sur les variables du module (validation blocks)
- [ ] Documenter les paramètres du module dans `modules/shared_app_stack/README.md`
- [ ] Valider en revue de code que les paramètres reflètent bien les besoins de chaque env
- [ ] Établir une politique : INTERDICTION de créer des `resource` dans `envs/`
- [ ] Configurer un pre-commit hook pour bloquer les commits contenant `resource` dans `envs/`
</implementation-checklist>

<related-rules>
- TF-ENV-COMPOSITION: Environment configurations must not declare resources directly
- TF-MODULES-DRY: When to create modules (DRY principle)
- TF-MODULES-SCOPE: Module scope and boundaries
- TF-STRUCTURE: Project structure (modules vs envs)
- GCS-MODULE-USAGE: Use official modules for GCS
- CLOUDRUN-MODULE-USAGE: Use official modules for Cloud Run
</related-rules>

<references>
- Terraform Best Practices: Module Composition - https://developer.hashicorp.com/terraform/language/modules/develop/composition
- DRY Principle in Infrastructure as Code - https://www.terraform.io/docs/language/modules/develop/composition.html
- Environment Separation Patterns - https://cloud.google.com/architecture/managing-infrastructure-as-code
- Preventing Configuration Drift - https://www.hashicorp.com/resources/preventing-configuration-drift
</references>

</rule>
