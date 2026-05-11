✅ REVUE COMPLÉTÉE - CORRECTIONS REQUISES

**Statut:** 🔴 Corrections Nécessaires

**Fichiers analysés:** {{num_files}} fichiers  
**Problèmes détectés:** {{num_total}}
- 🔴 **CRITIQUE:** {{num_critical}} (correction obligatoire)
- 🟠 **MAJEUR:** {{num_major}} (correction recommandée)
- 🟡 **MINEUR:** {{num_minor}} (amélioration optionnelle)

---

## Détails de la Revue

{{review_response}}

---

## Instructions de Correction

⚠️ **Les corrections doivent être appliquées à:** `{{root_folder}}`

**Processus:**
1. ✅ Appliquer les corrections CRITIQUE et MAJEUR
2. ✅ Relancer `terraform_init` → `terraform_validate` → `terraform_plan`
3. ✅ Relancer `review_and_fix_code` pour confirmer les corrections
4. ✅ Tous les logs sont dans `{{root_folder}}/terraform_logs.error`

**Critères de Succès:**
- ✅ Tous les problèmes CRITIQUE corrigés
- ✅ terraform validate passe (0 erreurs)
- ✅ review_and_fix_code montre 0 CRITIQUE/MAJEUR
- ✅ Logs complets en terraform_logs.error

L'agent procèdera automatiquement à la correction, validation et revalidation.
