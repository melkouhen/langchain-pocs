# Synthèse : Structurer des projets Terraform comme un Pro

Cette synthèse reprend les points clés de l'article de Hamza Bouachir sur les meilleures pratiques de structuration Terraform pour garantir l'évolutivité, la sécurité et la maintenabilité de l'infrastructure.

## 1. Structure de Dossiers Recommandée
Une organisation claire permet d'éviter les fichiers monolithiques et de réduire le "rayon d'exposition" (blast radius) en cas d'erreur.

*   **`/modules`** : Contient les composants réutilisables (ex: `vpc`, `database`, `eks`).
*   **`/environments`** : Dossiers distincts (`dev`, `staging`, `prod`) avec leur propre configuration de backend.
*   **`/global`** : Pour les ressources transverses (IAM, DNS, S3 pour les logs).

## 2. Utilisation Stratégique des Modules
Les modules sont les briques de base de votre infrastructure.
*   **DRY (Don't Repeat Yourself)** : Encapsulez la logique complexe pour la réutiliser.
*   **Maintenance facilitée** : Une modification dans le module se répercute sur tous les environnements qui l'appellent.
*   **Attention** : Évitez la sur-ingénierie. Si une ressource est unique et simple, un module n'est pas forcément nécessaire.

## 3. Isolation : Dossiers vs Workspaces
Le débat sur la gestion des environnements est tranché en faveur de la clarté :
-   **Workspaces** : Pratiques pour des tests éphémères, mais risqués car ils partagent la même configuration de code.
-   **Structure par Dossiers (Recommandé)** : Offre une isolation physique des fichiers d'état (`state`), permettant des configurations de backend différentes et une meilleure intégration avec les pipelines CI/CD.

## 4. Meilleures Pratiques (Battle-Tested)
| Pratique | Description |
| :--- | :--- |
| **Backend & Locking** | Utiliser un backend distant (S3, GCS) avec verrouillage (DynamoDB) pour éviter les corruptions de state. |
| **Pinning de Version** | Verrouiller les versions des providers et de Terraform pour éviter les régressions lors d'un `init`. |
| **Hygiène du Code** | Exécuter systématiquement `terraform fmt` et `terraform validate`. |
| **Gestion des Secrets** | Ne jamais stocker de mots de passe en clair. Utiliser des variables d'environnement ou des coffres-forts (Vault, AWS Secrets Manager). |

## 5. Flux de Travail (Workflow)
L'auteur insiste sur la rigueur du cycle de vie Terraform :
1.  **`terraform plan`** : Étape cruciale à examiner attentivement avant toute action.
2.  **Automatisation** : Intégration dans une CI/CD pour que l'application de l'infrastructure soit prévisible et auditée.
3.  **Surveillance du Drift** : Vérifier régulièrement que l'infrastructure réelle ne s'est pas éloignée de la configuration définie dans le code.

---
*Résumé basé sur l'article : "Structuring Terraform Projects Like a Pro" par Hamza Bouachir.*