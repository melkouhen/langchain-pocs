# Harness avec Callbacks - Exemple de Sortie

Le harness d'évaluation intègre maintenant `DetailedTerraformCallback` pour afficher :
- Les **phases d'exécution** en temps réel (PLANNING, GENERATION, VALIDATION, CODE_REVIEW)
- Les **outils appelés** avec leur statut (✅/❌)
- Les **durées par phase**
- Les **checks de sécurité** détectés
- Les **best practices** appliquées

## Exemple de sortie

```
========================================================================
  tc01  —  Simple GCS Bucket
========================================================================
Work dir : /Users/melkouhen/audit-tools/test-langchain/work

================================================================================
📋 PHASE: PLANNING
================================================================================
   → Calling search_knowledge_base
   ✅ search_knowledge_base completed
   → Calling search_knowledge_base
   ✅ search_knowledge_base completed
   → Calling load_module_spec
   ✅ load_module_spec completed

================================================================================
🔧 PHASE: GENERATION
================================================================================
   [LLM generating code...]

================================================================================
✅ PHASE: VALIDATION
================================================================================
   → Calling terraform_init
   ✅ terraform_init completed
   → Calling terraform_validate
   ✅ terraform_validate completed
   → Calling terraform_plan
   ✅ terraform_plan completed

================================================================================
🔍 PHASE: CODE_REVIEW
================================================================================
   → Calling review_and_fix_code
   ✅ review_and_fix_code completed

  Score: 4.50/5  [Excellent]
  TF valid: yes | Files: 8
  ███████░░  3.5/5  [20%]  Correctness
  █████████  5.0/5  [30%]  Security
  ████████░  4.5/5  [25%]  Best Practices
  ████████░  4.0/5  [15%]  Structure
  █████████  5.0/5  [10%]  Documentation

  ──────────────────────────────────────────────────────────────────────
  Execution Report:
  ──────────────────────────────────────────────────────────────────────
  Phases:
    PLANNING: 8.3s
    GENERATION: 15.7s
    VALIDATION: 4.2s
    CODE_REVIEW: 6.1s

  Security Checks:
    ✅ UBLA
    ✅ Public Access Prevention
    ✅ Encryption
    ✅ Versioning
    ⚠️  Lifecycle Policies

  Best Practices:
    ✅ Module Structure
    ✅ Variables Defined
    ✅ Outputs Defined
    ✅ Documentation

Results saved → eval/results/20260512_140530
```

## Avantages

### 1. Visibilité en temps réel
- Voir exactement ce que l'agent fait à chaque étape
- Identifier où le temps est passé
- Détecter les blocages rapidement

### 2. Debug facilité
- Les outils qui échouent sont visibles immédiatement (❌)
- Les erreurs sont loggées avec contexte
- Les phases permettent de localiser les problèmes

### 3. Métriques détaillées
- Durée par phase → identifier les optimisations possibles
- Security checks → voir quelles protections sont appliquées
- Best practices → valider la qualité du code généré

### 4. Traçabilité
- Chaque exécution a un rapport complet
- Les phases sont loggées avec timestamps
- Corrélation possible avec les résultats d'évaluation

## Usage

### Exécution standard
```bash
# Tous les tests avec callbacks
python -m eval.harness

# Un seul test
python -m eval.harness --test-id tc01
```

### Configuration
Le callback est configuré avec `verbose=True` dans le harness pour afficher :
- Les transitions de phase (📋 🔧 ✅ 🔍)
- Les appels d'outils (→ Calling ...)
- Les statuts de complétion (✅/❌)

Pour désactiver l'affichage détaillé, modifier dans `eval/harness.py`:
```python
callback = DetailedTerraformCallback(verbose=False)
```

Le rapport final sera toujours affiché.

## Rapport JSON

Le rapport du callback peut aussi être sérialisé en JSON pour analyse :

```python
report = callback.get_report()
# Structure:
{
    "phases": {
        "PLANNING": {"duration": 8.3, "start": "...", "end": "..."},
        "GENERATION": {"duration": 15.7, ...},
        ...
    },
    "tool_results": {
        "search_knowledge_base": {"output": "...", "success": True},
        "terraform_init": {"output": "...", "success": True},
        ...
    },
    "security_checks": {
        "UBLA": True,
        "Encryption": True,
        ...
    },
    "bp_checks": {
        "Module Structure": True,
        ...
    },
    "total_duration": 34.3
}
```

Ce rapport peut être sauvegardé avec les résultats d'évaluation pour analyse ultérieure.

## Prochaines étapes

- [ ] Ajouter le rapport callback dans `evaluation.json`
- [ ] Dashboard web pour visualiser les phases
- [ ] Comparaison des durées entre runs
- [ ] Alerting si phase > threshold
