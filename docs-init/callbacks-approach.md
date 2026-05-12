# Callbacks LangChain - Approche Native pour Phase Tracking

## Vue d'Ensemble

Au lieu d'un wrapper superficiel qui parse du texte, on utilise le **système de callbacks natif de LangChain** pour tracker les phases d'exécution du workflow Terraform de manière élégante et non intrusive.

## Problème avec l'Approche Pipeline Wrapper

Le `PipelineExecutor` précédent avait plusieurs problèmes :

❌ **Bricolage** : Parsing de texte avec `"✅" in output`  
❌ **Wrapper superficiel** : Code dupliqué qui wraps le Generator  
❌ **Pas de vraies phases** : Simule des phases au lieu de les détecter  
❌ **Maintenance** : Nouveau composant à maintenir  

## Solution : Callbacks LangChain

Les callbacks LangChain sont un pattern standard pour observer l'exécution d'agents.

### Architecture

```python
class TerraformPhaseCallback(BaseCallbackHandler):
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        """Détecte le début d'un outil → identifie la phase."""
        tool_name = serialized.get("name")
        
        if tool_name == "search_knowledge_base":
            self._start_phase("PLANNING")
        elif tool_name == "terraform_validate":
            self._start_phase("VALIDATION")
        elif tool_name == "review_and_fix_code":
            self._start_phase("CODE_REVIEW")
    
    def on_tool_end(self, output, **kwargs):
        """Capture le résultat de l'outil."""
        success = "✅" in output or "successful" in output
        self.tool_results[tool_name] = {"success": success, ...}
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        """Détecte la génération de code."""
        self._start_phase("GENERATION")
```

### Utilisation

```python
from terraform_agent import TerraformGenerator, TerraformPhaseCallback

# Initialiser le generator (inchangé)
generator = TerraformGenerator(config, prompts, knowledge_base)

# Créer le callback
callback = TerraformPhaseCallback(verbose=True)

# Exécuter avec le callback
result = generator.run(
    user_prompt=prompt,
    callbacks=[callback]  # ← Passer le callback
)

# Récupérer le rapport
report = callback.get_report()
```

## Output Exemple

```
================================================================================
📋 PHASE: PLANNING
================================================================================
   → Calling search_knowledge_base
   ✅ search_knowledge_base completed

   Phase completed in 2.34s

================================================================================
🔧 PHASE: GENERATION
================================================================================
   → Calling terraform_init
   ✅ terraform_init completed

   Phase completed in 45.67s

================================================================================
✅ PHASE: VALIDATION
================================================================================
   → Calling terraform_validate
   ✅ terraform_validate completed
   → Calling terraform_plan
   ✅ terraform_plan completed

   Phase completed in 5.12s

================================================================================
🔍 PHASE: CODE_REVIEW
================================================================================
   → Calling review_and_fix_code
   ✅ review_and_fix_code completed

   Phase completed in 12.89s

================================================================================
📊 EXECUTION SUMMARY
================================================================================

Phase                Duration        Status    
--------------------------------------------------
PLANNING             2.34s           ✅        
GENERATION           45.67s          ✅        
VALIDATION           5.12s           ✅        
CODE_REVIEW          12.89s          ✅        

Total                66.02s

🔧 Tool Execution Summary:
   ✅ search_knowledge_base
   ✅ terraform_init
   ✅ terraform_validate
   ✅ terraform_plan
   ✅ review_and_fix_code

================================================================================
```

## Rapport JSON

```json
{
  "execution_log": [
    {
      "phase": "PLANNING",
      "duration_seconds": 2.34,
      "timestamp": "2026-05-12T10:30:15.123456"
    },
    {
      "phase": "GENERATION",
      "duration_seconds": 45.67,
      "timestamp": "2026-05-12T10:30:17.463456"
    },
    {
      "phase": "VALIDATION",
      "duration_seconds": 5.12,
      "timestamp": "2026-05-12T10:31:03.133456"
    },
    {
      "phase": "CODE_REVIEW",
      "duration_seconds": 12.89,
      "timestamp": "2026-05-12T10:31:08.253456"
    }
  ],
  "tool_results": {
    "search_knowledge_base": {
      "output": "...",
      "success": true,
      "timestamp": "2026-05-12T10:30:15.123456"
    },
    "terraform_validate": {
      "output": "✅ terraform validate successful",
      "success": true,
      "timestamp": "2026-05-12T10:31:05.123456"
    }
  },
  "total_duration_seconds": 66.02,
  "timestamp": "2026-05-12T10:31:21.143456"
}
```

## Deux Callbacks Disponibles

### 1. `TerraformPhaseCallback` (Simple)

Track les phases et les durées, sans checks supplémentaires.

```python
callback = TerraformPhaseCallback(verbose=True)
generator.run(prompt, callbacks=[callback])
report = callback.get_report()
```

**Use case** : Développement, debug, comprendre le workflow.

### 2. `DetailedTerraformCallback` (Détaillé)

Ajoute des checks de sécurité et best practices avec scoring.

```python
callback = DetailedTerraformCallback(verbose=True)
generator.run(prompt, callbacks=[callback])
report = callback.get_report()

print(f"Security Score: {report['security_score']}%")
print(f"BP Score: {report['bp_score']}%")
```

**Use case** : CI/CD, audit, validation de compliance.

### Output Détaillé

```
================================================================================
📊 EXECUTION SUMMARY
================================================================================

Phase                Duration        Status    
--------------------------------------------------
PLANNING             2.34s           ✅        
GENERATION           45.67s          ✅        
VALIDATION           5.12s           ✅        
CODE_REVIEW          12.89s          ✅        

Total                66.02s

🔧 Tool Execution Summary:
   ✅ search_knowledge_base
   ✅ terraform_init
   ✅ terraform_validate
   ✅ terraform_plan
   ✅ review_and_fix_code

🔒 Security Checks:
   ✅ UBLA
   ✅ Public Access Prevention
   ✅ Encryption
   ✅ Versioning
   ❌ Lifecycle Policies

   Security Score: 80%

📐 Best Practices Checks:
   ✅ Module Structure
   ✅ Variables Defined
   ✅ Outputs Defined
   ✅ Documentation

   Best Practices Score: 100%

================================================================================
```

### Rapport JSON Détaillé

```json
{
  "execution_log": [...],
  "tool_results": {...},
  "security_checks": {
    "UBLA": true,
    "Public Access Prevention": true,
    "Encryption": true,
    "Versioning": true,
    "Lifecycle Policies": false
  },
  "bp_checks": {
    "Module Structure": true,
    "Variables Defined": true,
    "Outputs Defined": true,
    "Documentation": true
  },
  "security_score": 80.0,
  "bp_score": 100.0,
  "total_duration_seconds": 66.02,
  "timestamp": "2026-05-12T10:31:21.143456"
}
```

## Extensibilité

Créez vos propres callbacks facilement :

```python
from terraform_agent.callbacks import DetailedTerraformCallback

class CostAwareCallback(DetailedTerraformCallback):
    """Callback with cost analysis."""
    
    def on_tool_end(self, output, **kwargs):
        super().on_tool_end(output, **kwargs)
        
        tool_name = kwargs.get("name")
        
        if tool_name == "terraform_plan":
            # Parse plan for cost estimation
            if "storage.googleapis.com" in output:
                print("   💰 GCS bucket detected - estimate: $0.02/GB/month")
```

## Comparaison des Approches

| Aspect | Pipeline Wrapper | Callbacks LangChain |
|--------|------------------|---------------------|
| **Architecture** | Wrapper du Generator | ✅ Composant observateur |
| **Intégration** | Nouveau point d'entrée | ✅ Option sur Generator existant |
| **Détection phases** | Parsing texte (`"✅" in output`) | ✅ Hooks d'outils réels |
| **Données structurées** | Extraction de texte | ✅ Capture directe |
| **Code dupliqué** | Réimplémente le workflow | ✅ Observe le workflow existant |
| **Maintenance** | 2 composants (Generator + Wrapper) | ✅ 1 composant (Callback) |
| **Extensibilité** | Hériter du wrapper | ✅ Hériter du callback |
| **Performance** | Overhead du wrapping | ✅ Overhead minimal |
| **Lisibilité** | 500+ lignes | ✅ ~400 lignes, plus clair |

## Cas d'Usage

### 1. Développement Local

```python
# Voir les phases en temps réel
callback = TerraformPhaseCallback(verbose=True)
generator.run(prompt, callbacks=[callback])
```

### 2. CI/CD Pipeline

```python
# Valider la sécurité
callback = DetailedTerraformCallback(verbose=False)
generator.run(prompt, callbacks=[callback])
report = callback.get_report()

if report["security_score"] < 80:
    raise Exception(f"Security score too low: {report['security_score']}%")
```

### 3. Logging Structuré

```python
# Sauvegarder tous les rapports
import json
from datetime import datetime

callback = DetailedTerraformCallback(verbose=False)
generator.run(prompt, callbacks=[callback])

report_file = f"logs/run-{datetime.now():%Y%m%d-%H%M%S}.json"
Path(report_file).write_text(json.dumps(callback.get_report(), indent=2))
```

### 4. Dashboards

```python
# Agréger les métriques
reports = []
for prompt in test_prompts:
    callback = DetailedTerraformCallback(verbose=False)
    generator.run(prompt, callbacks=[callback])
    reports.append(callback.get_report())

# Calculer les moyennes
avg_security = sum(r["security_score"] for r in reports) / len(reports)
avg_duration = sum(r["total_duration_seconds"] for r in reports) / len(reports)

print(f"Average Security Score: {avg_security:.1f}%")
print(f"Average Duration: {avg_duration:.1f}s")
```

### 5. Multiple Callbacks

```python
# Utiliser plusieurs callbacks en parallèle
phase_callback = TerraformPhaseCallback(verbose=True)
metrics_callback = MetricsCallback()  # Custom
alert_callback = AlertCallback()      # Custom

generator.run(
    prompt,
    callbacks=[phase_callback, metrics_callback, alert_callback]
)
```

## Migration

### Depuis TerraformGenerator standard

```python
# Avant
generator = TerraformGenerator(config, prompts, knowledge_base)
result = generator.run(user_prompt)

# Après (ajouter simplement le callback)
generator = TerraformGenerator(config, prompts, knowledge_base)
callback = TerraformPhaseCallback(verbose=True)
result = generator.run(user_prompt, callbacks=[callback])
```

### Depuis PipelineExecutor

```python
# Avant (avec le wrapper)
pipeline = PipelineExecutor(config, prompts, knowledge_base)
result = pipeline.run(user_prompt)

# Après (avec callback)
generator = TerraformGenerator(config, prompts, knowledge_base)
callback = DetailedTerraformCallback(verbose=True)
result = generator.run(user_prompt, callbacks=[callback])
report = callback.get_report()  # Même structure que pipeline.get_execution_report()
```

## Avantages de l'Approche Callbacks

### ✅ Natif LangChain

Utilise le système standard de callbacks - pas de hack ou workaround.

### ✅ Non Intrusif

Le `TerraformGenerator` reste inchangé dans son comportement. Le callback est optionnel.

### ✅ Phases Réelles

Les phases sont détectées via les appels d'outils réels, pas simulées ou extraites de texte.

### ✅ Composant Indépendant

Le callback peut être testé, maintenu et étendu indépendamment du Generator.

### ✅ Pas de Duplication

Observe le workflow existant au lieu de le réimplémenter.

### ✅ Performance

Overhead minimal - juste des hooks sur les événements existants.

### ✅ Standard Pattern

Pattern reconnu dans l'écosystème LangChain - facile à comprendre pour d'autres développeurs.

## Limitations

### Détection Heuristique

Les checks de sécurité/BP dans `DetailedTerraformCallback` restent basés sur la présence de mots-clés dans l'output des outils. Pour une analyse plus robuste, il faudrait :

1. Parser le code Terraform avec un AST
2. Utiliser des outils externes (tfsec, checkov)
3. Intégrer avec terraform show -json

**Mitigation** : C'est une limitation acceptable pour un système de reporting, pas un validateur de sécurité.

### Pas de Modification du Workflow

Les callbacks observent mais ne modifient pas le workflow. Si vous voulez changer l'ordre des opérations ou ajouter des étapes conditionnelles, il faut modifier le Generator lui-même.

**Mitigation** : C'est par design - separation of concerns.

## Fichiers

- **Code source** : `terraform_agent/callbacks.py`
- **Démo notebook** : `notebooks/callbacks_demo.ipynb`
- **Tests** : À créer dans `eval/test_callbacks.py`

## Prochaines Étapes

1. **Tester** avec `notebooks/callbacks_demo.ipynb`
2. **Comparer** avec l'ancien `pipeline_executor_demo.ipynb`
3. **Décider** si on garde ou supprime le `PipelineExecutor`
4. **Étendre** avec vos callbacks personnalisés si nécessaire

## Conclusion

L'approche **callbacks** est plus élégante, maintenable et alignée avec les patterns LangChain que le wrapper `PipelineExecutor`. C'est la solution recommandée pour tracker les phases d'exécution.
