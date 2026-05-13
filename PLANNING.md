# Plan de Génération Terraform - Phase 2

**Date:** 2026-05-13  
**Projet:** Cloud Run API - Infrastructure GCP  
**Mode:** CREATE  
**Work Dir:** /Users/melkouhen/audit-tools/test-langchain/work-02

---

## 📐 Structure Planifiée

```
work-02/
├── envs/
│   ├── dev/
│   │   ├── main.tf                    # Appel module cloud_run avec vars dev
│   │   ├── variables.tf               # Vars spécifiques dev (override defaults)
│   │   ├── outputs.tf                 # Outputs pour consommation
│   │   ├── terraform.tf               # Backend séparé dev
│   │   └── terraform.tfvars.example   # Exemple de valeurs
│   └── prod/
│       ├── main.tf                    # Appel module cloud_run avec vars prod
│       ├── variables.tf               # Vars spécifiques prod (override defaults)
│       ├── outputs.tf                 # Outputs pour consommation
│       ├── terraform.tf               # Backend séparé prod
│       └── terraform.tfvars.example   # Exemple de valeurs
├── modules/
│   ├── cloud_run_api/
│   │   ├── main.tf                    # Appel module officiel GoogleCloudPlatform/cloud-run/google
│   │   ├── variables.tf               # Abstraction des inputs (env-agnostic)
│   │   ├── outputs.tf                 # Exports du module
│   │   └── versions.tf                # Version pinning du module
│   └── [futurs modules si besoin]
├── providers.tf                       # Provider GCP avec version constraint
├── terraform.tf                       # Config Terraform version + locals partagés
└── README.md                          # Documentation du projet

```

---

## 📋 Fichiers à Générer (Détail)

### 1. Fichier Root

#### `providers.tf` (Root)
- Configuration provider google (région, projet)
- ⚠️ PAS de version provider en generated code (TF-NO-PROVIDER-VERSION)
- Required version Terraform à la root

#### `terraform.tf` (Root)
- Terraform required_version constraint
- Locals partagés (project_id, region, environment list)

---

### 2. Module Partagé: cloud_run_api

**Source:** GoogleCloudPlatform/cloud-run/google (module officiel)

#### `modules/cloud_run_api/variables.tf`
```
Variables:
- service_name (string) - Nom du service
- image (string) - URI de l'image container
- region (string) - Région GCP
- project_id (string) - ID du projet
- port (number, default=8080) - Port d'écoute
- cpu (string, default="1") - CPU limit
- memory (string, default="512Mi") - Memory limit
- max_instances (number, default=10) - Max instances
- min_instances (number, default=0) - Min instances
- concurrency (number, default=80) - Concurrency per instance
- timeout_seconds (number, default=300) - Request timeout
- ingress (string, enum=[all, internal, internal-and-load-balancer])
- allow_unauthenticated (bool) - Public access toggle
```

#### `modules/cloud_run_api/main.tf`
```
- Appel module: source = "GoogleCloudPlatform/cloud-run/google"
- Paramètres mapping depuis vars du module
- Lifecycle ignore: operation-id annotations
```

#### `modules/cloud_run_api/outputs.tf`
```
Outputs:
- service_url
- service_name
- service_id
```

#### `modules/cloud_run_api/versions.tf`
```
- terraform >= 1.0
- provider google >= 5.0 (version pinning)
- module source constraint
```

---

### 3. Environnement DEV

#### `envs/dev/main.tf`
```
- module "cloud_run_dev" { source = "../../modules/cloud_run_api" }
- Variables mapping pour dev:
  * service_name = "my-api-dev"
  * image = "gcr.io/beaming-botany-495511-n6/my-api:latest"
  * ingress = "all"
  * allow_unauthenticated = true
  * Autres: defaults du module
```

#### `envs/dev/variables.tf`
```
- Redéclaration des variables (TF-ENV-ISOLATION)
- Defaults peuvent différer de prod
- Exemple: allow_unauthenticated par défaut true
```

#### `envs/dev/outputs.tf`
```
- Pass-through des outputs du module
- Annotations dev
```

#### `envs/dev/terraform.tf`
```
- Backend "gcs" spécifique DEV:
  bucket = "projet-beaming-botany-495511-n6-terraform-dev"
  prefix = "cloud-run"
  
- Required providers (pas de version du provider en generated)
```

#### `envs/dev/terraform.tfvars.example`
```
Exemple de valeurs pour dev
```

---

### 4. Environnement PROD

#### `envs/prod/main.tf`
```
- Identique structure à dev
- Variables mapping pour prod:
  * service_name = "my-api-prod"
  * image = "gcr.io/beaming-botany-495511-n6/my-api:latest"
  * allow_unauthenticated = false
  * Autres: defaults du module
```

#### `envs/prod/variables.tf`
- Identique structure à dev
- Defaults peuvent différer (allow_unauthenticated false)

#### `envs/prod/outputs.tf`
- Identique structure à dev

#### `envs/prod/terraform.tf`
```
- Backend "gcs" spécifique PROD:
  bucket = "projet-beaming-botany-495511-n6-terraform-prod"
  prefix = "cloud-run"
```

#### `envs/prod/terraform.tfvars.example`
- Exemple de valeurs pour prod

---

## 🔒 Règles Appliquées

| Règle | Implémentation |
|-------|-----------------|
| TF-STRUCTURE | Structure min: main.tf, variables.tf, outputs.tf, terraform.tf ✅ |
| TF-ENV-ISOLATION | État séparé: dev/, prod/ avec terraform.tf distincts ✅ |
| TF-ENV-ISOLATION-BACKEND | Backends GCS séparés par env ✅ |
| TF-ENV-SEPARATION | Dossiers séparés (PAS workspaces) ✅ |
| TF-ENV-COMPOSITION | Env ne déclarent QUE module calls ✅ |
| TF-ENV-MODULE-DELEGATION | Env appellent SEULEMENT modules partagés ✅ |
| CLOUDRUN-MODULE-USAGE | Utilise GoogleCloudPlatform/cloud-run/google ✅ |
| TF-NO-HARDCODED-SECRETS | Pas de secrets en clair ✅ |
| TF-STATE-DELETION | Backends en GCS (pas d'accès direct local) ✅ |
| TF-VERSION-PINNING | Provider version >= 5.0 en versions.tf ✅ |
| TF-NO-PROVIDER-VERSION | Pas de provider version en generated code ✅ |

---

## ⚙️ Variables Mapping

### Dev
```hcl
service_name           = "my-api-dev"
allow_unauthenticated  = true
ingress                = "all"
```

### Prod
```hcl
service_name           = "my-api-prod"
allow_unauthenticated  = false
ingress                = "all"  # À confirmer en prod
```

### Partagé
```hcl
image                  = "gcr.io/beaming-botany-495511-n6/my-api:latest"
region                 = "europe-west9"
project_id             = "beaming-botany-495511-n6"
port                   = 8080
cpu                    = "1"
memory                 = "512Mi"
max_instances          = 10
min_instances          = 0
concurrency            = 80
timeout_seconds        = 300
```

---

## 🎯 Prochaines Étapes

- Phase 3: Générer tous les fichiers
- Phase 4: Validation séquentielle (init → validate → plan → review)
- Phase 5: Logging des corrections
- Phase 6: Capitalisation des règles manquantes

