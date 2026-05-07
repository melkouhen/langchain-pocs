# Bonnes Pratiques de Structuration Terraform

## 1. Organisation Générale du Projet

| Contexte | Règle |
|----------|-------|
| **tf-project-layout** | Organiser le projet selon trois catégories : `modules/` (code réutilisable paramétrisé), `envs/` (configurations par environnement avec state files séparés), `global/` (ressources partagées en dehors du cycle de vie des environnements, ex: buckets S3, rôles IAM) |

## 2. Gestion des Modules

| Contexte | Règle |
|----------|-------|
| **tf-module-creation** | Créer un module uniquement si le code est utilisé dans 2+ endroits. Ne pas modulariser une ressource unique. |
| **tf-module-scope** | Garder les modules peu profonds et focalisés (1 groupe de ressources par module). Éviter l'imbrication excessive. |

## 3. Gestion des Environnements

| Contexte | Règle |
|----------|-------|
| **tf-env-separation** | Préférer la séparation par dossiers (`envs/dev/`, `envs/staging/`, `envs/prod/`) plutôt que les workspaces pour les projets d'équipe. |
| **tf-env-isolation** | Isoler complètement les environnements : un backend distinct par environnement, un state file par équipe, jamais de workspace "default" partagé en production. |

## 4. Versionnage et Dépendances

| Contexte | Règle |
|----------|-------|
| **tf-version-pinning** | Épingler les versions Terraform et providers dans les blocs `required_version` et `required_providers` (ex: `~> 1.5.0`, `~> 5.0`). |
| **tf-provider-locking** | Utiliser `~>` pour les contraintes de version. Verrouiller les sources de modules Git sur des commits ou versions spécifiques si utilisation de `source = "git::..."`. |

## 5. État et Verrouillage

| Contexte | Règle |
|----------|-------|
| **tf-remote-state** | Utiliser un backend distant (S3 + DynamoDB ou Terraform Cloud) pour les projets d'équipe. Ne jamais garder le state localement. |
| **tf-state-locking** | Activer le verrouillage du state distant (ex: DynamoDB pour S3) pour éviter les `terraform apply` simultanés par plusieurs personnes. |
| **tf-state-deletion** | Ne jamais supprimer le fichier `.tfstate` directement. Utiliser `terraform destroy` correctement ou gérer le state proprement via CLI/backends. |
| **tf-state-drift** | Exécuter régulièrement `terraform plan` ou `terraform plan -detailed-exitcode` en CI/CD pour détecter les dérives (modifications manuelles via console). |

## 6. Nommage et Convention

| Contexte | Règle |
|----------|-------|
| **tf-resource-naming** | Utiliser une convention de nommage cohérente : `${var.env}-${resource_type}-${index}` (ex: `dev-web-0`, `prod-web-2`). |

## 7. Sécurité et Secrets

| Contexte | Règle |
|----------|-------|
| **tf-no-hardcoded-secrets** | Ne jamais encoder les secrets en dur. Utiliser des variables d'environnement, gestionnaires de secrets (AWS Secrets Manager, Vault) ou `sensitive = true`. |

## 8. Validation et Automatisation

| Contexte | Règle |
|----------|-------|
| **tf-ci-cd-integration** | Intégrer Terraform en CI/CD : exécuter `terraform fmt`, `terraform validate`, `terraform plan` dans le pipeline. |
| **tf-always-plan** | Ne jamais lancer `terraform apply` sans voir `terraform plan` d'abord, particulièrement en CI/CD. |

## 9. Configuration par Environnement

| Contexte | Règle |
|----------|-------|
| **tf-avoid-hardcoding** | Éviter d'encoder les régions, AMI IDs et autres paramètres. Utiliser des variables ou créer un `locals.tf` par environnement. |

## 10. Workspaces : Limitation

| Contexte | Règle |
|----------|-------|
| **tf-workspace-limitation** | Réserver les workspaces aux tests locaux et prototypage (`test`, `dev`, `playground`). Ne pas les utiliser en production en équipe (code partagé, pas de séparation de backend, mauvaise visibilité en CI/CD). |

## Pièges Courants à Éviter

| Contexte | Règle |
|----------|-------|
| **tf-overengineering-modules** | Ne pas wraper une ressource unique (EC2, bucket S3) en module à moins de réutilisation. Garder le design simple et significatif. |
| **tf-workspace-confusion** | Les workspaces peuvent créer de la confusion en équipe (ex: appliquer aveuglément dans le mauvais workspace). Préférer les dossiers d'environnements. |
| **tf-apply-blind** | Ne jamais lancer `terraform apply` sans voir le plan d'abord. C'est comme un dry-run pour l'infrastructure. |
| **tf-hardcoding-params** | Ne pas encoder les régions ou AMI IDs. Utiliser des variables pour région, environnement et autres paramètres. |
