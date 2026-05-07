# Bonne Pratique : Utilisation de Modules Terraform

## Module : Terraform Google Cloud Storage

| Contexte | Règle |
|----------|-------|
| **tf-gcs-module** | Utiliser le module `terraform-google-modules/cloud-storage/google` pour créer et gérer les buckets Google Cloud Storage avec permissions IAM. Ce module automatise la création de un ou plusieurs buckets GCS et l'assignation des permissions de base aux utilisateurs. |

### Caractéristiques Principales

Le module `terraform-google-modules/cloud-storage/google` (version ~> 12.3+) offre :

- Création de un ou plusieurs buckets GCS
- Configuration des liaisons IAM (admins, creators, viewers, storage admins, HMAC key admins)
- Gestion du versioning par bucket
- Configuration des règles de cycle de vie (lifecycle rules)
- Support de la prévention d'accès public
- Gestion du chiffrement, logging, CORS, et bien d'autres configurations
- Sous-module `simple_bucket` pour cas simple (single bucket)

### Exemple d'Usage

```hcl
module "gcs_buckets" {
  source  = "terraform-google-modules/cloud-storage/google"
  version = "~> 12.3"
  
  project_id = "<PROJECT ID>"
  names      = ["first", "second"]
  prefix     = "my-unique-prefix"
  
  set_admin_roles = true
  admins          = ["group:foo-admins@example.com"]
  
  versioning = {
    first = true
  }
  
  bucket_admins = {
    second = "user:spam@example.com,user:eggs@example.com"
  }
}
```

### Avantages

- **DRY (Don't Repeat Yourself)** : Évite la duplication de code pour la création de buckets et permissions
- **Maintenabilité** : Centralisé et versionné via Terraform Registry
- **Conformité** : Les meilleures pratiques de sécurité et configuration GCS sont déjà intégrées
- **Flexibilité** : Support de configurations avancées (lifecycle rules, encryption, custom placement, etc.)

### Compatibilité

- Terraform 0.13+
- Terraform Provider for GCP >= v4.42
- Les versions 1.7.1 et antérieures supportent Terraform 0.12.x

### Permissions Requises

Service account ou utilisateur doit avoir le rôle : `roles/storage.admin`

### APIs Requises

Le projet doit avoir activée : `storage-api.googleapis.com` (Google Cloud Storage JSON API)
