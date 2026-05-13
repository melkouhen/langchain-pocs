# Règles Terraform Chargées - Phase 1

**Date:** 2026-05-13 (updated)
**Scopes couverts:** google_cloud_run_service, global  
**Total règles identifiées:** 27 (18 CRITICAL, 8 MAJOR, 1 MINOR)

## ⚠️ Règle Critique Absolue

**TF-NO-PROVIDER-VERSION** - EXCEPTION CRITIQUE
- Scope: global
- Sévérité: CRITICAL
- Énoncé: Ne JAMAIS générer de constraints de version dans required_providers
- Raison: Le fichier de lock gère les versions, pas le code Terraform
- Application: Toujours laisser source sans version (ex: `source = "hashicorp/google"` SANS `version = "..."`)

---

## 🔴 Règles CRITIQUES

### Architecture (7 règles CRITICAL)

1. **CLOUDRUN-MODULE-USAGE** (CRITICAL)
   - Use Official GoogleCloudPlatform/cloud-run/google Module
   - Scope: google_cloud_run_service
   - Obligation: Utiliser le module officiel au lieu de déclarer google_cloud_run_service directement
   - Raison: Abstractions éprouvées, validation d'entrée, best practices forcées

2. **GCS-MODULE-USAGE** (CRITICAL)
   - Use Official terraform-google-modules/cloud-storage/google Module
   - Scope: google_storage_bucket
   - Obligation: Utiliser le module officiel pour Cloud Storage

3. **TF-ENV-COMPOSITION** (CRITICAL)
   - Environment Configurations Must Not Declare Cloud Resources Directly
   - Scope: global
   - Obligation: Les fichiers env ne doivent PAS déclarer de ressources cloud directement

4. **TF-ENV-ISOLATION** (CRITICAL)
   - Environment Isolation: Separate Directories and State Files
   - Scope: global
   - Obligation: État séparé pour dev et prod

5. **TF-ENV-MODULE-DELEGATION** (CRITICAL)
   - Environment Modules Must Only Call Shared Modules With Environment Parameters
   - Scope: global
   - Obligation: Les modules env doivent seulement appeler des modules partagés

6. **TF-ENV-SEPARATION** (CRITICAL)
   - Environment Separation: Folders vs Workspaces
   - Scope: global
   - Obligation: Utiliser des dossiers séparés plutôt que des workspaces

7. **TF-STRUCTURE** (CRITICAL)
   - Project Layout Organization
   - Scope: global
   - Obligation: Structure minimale requise (main.tf, variables.tf, outputs.tf, providers.tf)

---

### Security (3 règles CRITICAL)

8. **TF-ENV-ISOLATION-BACKEND** (CRITICAL)
   - Environment Isolation: Separate Backends & State
   - Scope: global
   - Obligation: Backends séparés pour dev et prod

9. **TF-NO-HARDCODED-SECRETS** (CRITICAL)
   - No Hardcoded Secrets
   - Scope: global
   - Obligation: Aucun secret en clair dans le code

10. **TF-STATE-DELETION** (CRITICAL)
    - Never Delete State Files Directly
    - Scope: global
    - Obligation: Interdiction d'accès direct aux fichiers state

---

### State Management (3 règles)

11. **TF-VERSION-PINNING** (CRITICAL)
    - Version Pinning: Providers & Terraform
    - Scope: global
    - Obligation: Verrouiller les versions des providers

12. **TF-BACKEND-STATE** (CRITICAL)
    - Remote State Management via GCS Backend
    - Scope: global
    - Obligation: Utiliser GCS pour le backend state

13. **TF-STATE-DRIFT** (MINOR)
    - State Drift Detection: Regular Plan Runs
    - Scope: global
    - Obligation: Exécuter terraform plan régulièrement pour détecter les dérives

---

### Code Quality (2 règles)

14. **TF-NO-PROVIDER-VERSION** (MAJOR)
    - Do Not Generate Provider Versions in Generated Code
    - Scope: global
    - Obligation: Ne pas générer de versions de provider

15. **TF-ALWAYS-PLAN** (MAJOR)
    - Always Review Plan Before Apply
    - Scope: global
    - Obligation: Toujours vérifier le plan avant l'apply

---

## 📋 Résumé des Obligations

### Structure du Projet
- ✅ Dossiers séparés pour dev et prod (PAS de workspaces)
- ✅ État Terraform séparé par environnement
- ✅ Backends séparés pour chaque environnement
- ✅ Fichiers minimums: main.tf, variables.tf, outputs.tf, providers.tf

### Architecture
- ✅ Utiliser le module GoogleCloudPlatform/cloud-run/google pour Cloud Run
- ✅ Les configs d'environnement ne déclarent PAS les ressources cloud directement
- ✅ Les modules d'env appellent seulement des modules partagés avec paramètres

### Sécurité
- ✅ Aucun secret en clair
- ✅ Backends isolés par environnement
- ✅ Pas d'accès direct au state Terraform

### Validation
- ✅ Version pinning pour tous les providers
- ✅ GCS backend pour le state distant
- ✅ terraform plan obligatoire avant apply

---

## 🎯 Implication pour le Projet

**Mode:** CREATE (nouveau projet)

**Configuration requise:**
```
structure/
├── envs/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── backend.tf
├── modules/
│   ├── cloud_run_api/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── ...
├── providers.tf
└── terraform.tf
```

**Points clés d'implémentation:**
1. Modules partagés pour Cloud Run (source: GoogleCloudPlatform/cloud-run/google)
2. Configurations dev/prod via variables (pas de déclaration de ressources)
3. Backend séparé pour chaque environnement (terraform.tf au niveau env)
4. Version pinning déclaré dans root providers.tf

