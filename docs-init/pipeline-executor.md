# Pipeline Executor - Workflow avec Phases Explicites

## Vue d'Ensemble

Le `PipelineExecutor` est une classe qui encapsule `TerraformGenerator` et structure l'exécution en **4 phases explicites** avec reporting détaillé.

### Problème Résolu

Le `TerraformGenerator` standard génère du bon code mais le processus est opaque :
```
🚀 Starting agent...
[logs internes...]
✅ Done
```

Le **PipelineExecutor** rend chaque étape visible et auditable :
```
📋 PHASE 1: PLANNING (2.5s)
  ✅ Requirements analyzed
  ✅ Knowledge base: 3 chunks found
  
🔧 PHASE 2: GENERATION (45s)
  ✅ terraform init
  ✅ terraform validate
  
🔍 PHASE 3: CODE REVIEW (12s)
  ✅ UBLA enabled
  ✅ Public access prevention
  ⚠️  Lifecycle policies missing
  Security score: 80%
  
✅ PHASE 4: VALIDATION (8s)
  ✅ terraform plan
  ✅ PIPELINE SUCCEEDED
```

## Architecture

```
PipelineExecutor
├── Phase 1: PLANNING
│   ├── Analyse du prompt utilisateur
│   ├── Détection des requirements (GCS, dev/prod, etc.)
│   └── Recherche knowledge base (k=3 chunks)
│
├── Phase 2: GENERATION
│   ├── Appel du TerraformGenerator
│   ├── terraform init
│   └── terraform validate
│
├── Phase 3: CODE REVIEW
│   ├── Security checks (UBLA, encryption, public access, etc.)
│   ├── Best practices checks (module structure, variables, outputs)
│   └── Scoring (security_score, bp_score)
│
└── Phase 4: VALIDATION
    ├── terraform plan
    ├── Résumé de toutes les phases
    └── Verdict final (SUCCESS/WARNING/FAILED)
```

## Utilisation

### Import et Initialisation

```python
from terraform_agent import Config, PromptManager, KnowledgeBase, PipelineExecutor

# Configuration standard
config = Config(base_dir=Path.cwd())
prompts = PromptManager(config)
knowledge_base = KnowledgeBase(config)

# Créer le pipeline executor
pipeline = PipelineExecutor(
    config=config,
    prompts=prompts,
    knowledge_base=knowledge_base,
)
```

### Exécution

```python
# Charger le prompt utilisateur
user_prompt = Path("user_prompts/1-bucket.md").read_text()

# Exécuter le pipeline (4 phases)
result = pipeline.run(user_prompt=user_prompt)

# Récupérer le rapport d'exécution
report = pipeline.get_execution_report()
```

### Output Structure

Le `PipelineExecutor` produit un output structuré pour chaque phase :

#### Phase 1: PLANNING
```
📋 PHASE 1: PLANNING & ANALYSIS
================================================================================

🔍 Analyzing user requirements...
   Prompt length: 1245 characters

📊 Requirements detected:
✅ GCS Bucket resources
✅ Dev environment
✅ Prod environment

📚 Searching knowledge base for best practices...
   ✓ Found 3 relevant chunks in 0.42s

📝 Execution plan:
   1. Generate Terraform module structure
   2. Initialize with terraform init
   3. Validate syntax with terraform validate
   4. Review code for security & best practices
   5. Generate terraform plan

✅ Planning phase completed in 2.53s
```

#### Phase 2: GENERATION
```
🔧 PHASE 2: CODE GENERATION & VALIDATION
================================================================================

🤖 Invoking Terraform generation agent...
   (Agent will autonomously call tools: init, validate, plan, review)

📊 Generation results:
✅ Terraform init
✅ Terraform validate

✅ Generation phase completed in 45.12s
```

#### Phase 3: CODE REVIEW
```
🔍 PHASE 3: CODE REVIEW & SECURITY ANALYSIS
================================================================================

🔒 Security checks:
✅ Uniform Bucket Level Access (UBLA)
✅ Public access prevention
✅ Encryption at rest
✅ Versioning enabled
❌ Lifecycle policies

📐 Best practices compliance:
✅ Module structure
✅ Variables defined
✅ Outputs defined
✅ Documentation present

🔍 Review findings:
   ✅ No critical or major issues found

✅ Code review passed
   Security score: 80%
   Best practices score: 100%
   Duration: 12.45s
```

#### Phase 4: VALIDATION
```
✅ PHASE 4: VALIDATION & SUMMARY
================================================================================

🎯 Pipeline execution summary:

Phase                     Status          Duration  
--------------------------------------------------
PLANNING                  ✅ SUCCESS       2.53s     
GENERATION                ✅ SUCCESS       45.12s    
CODE_REVIEW               ✅ SUCCESS       12.45s    
VALIDATION                ✅ SUCCESS       3.21s     

📊 Overall metrics:
   Total execution time: 68.92s
✅ Terraform plan generated
   Generated files: 6 .tf files

🏁 Final verdict:
   ✅ PIPELINE SUCCEEDED
   All phases completed successfully
   Code is production-ready

================================================================================
Pipeline execution completed in 68.92s
================================================================================
```

## Rapport d'Exécution

Le pipeline génère un rapport JSON détaillé :

```python
report = pipeline.get_execution_report()
```

### Structure du Rapport

```json
{
  "execution_log": [
    {
      "phase": "PLANNING",
      "status": "SUCCESS",
      "details": "Requirements analyzed, 3 KB chunks retrieved",
      "timestamp": "2026-05-12T10:30:15.123456",
      "duration_seconds": 2.53
    },
    {
      "phase": "GENERATION",
      "status": "SUCCESS",
      "details": "Code generated in 45.12s",
      "timestamp": "2026-05-12T10:30:17.654321",
      "duration_seconds": 45.12
    },
    {
      "phase": "CODE_REVIEW",
      "status": "SUCCESS",
      "details": "Security: 80%, BP: 100%",
      "timestamp": "2026-05-12T10:31:02.789012",
      "duration_seconds": 12.45
    },
    {
      "phase": "VALIDATION",
      "status": "SUCCESS",
      "details": "✅ PIPELINE SUCCEEDED",
      "timestamp": "2026-05-12T10:31:15.234567",
      "duration_seconds": 3.21
    }
  ],
  "total_duration_seconds": 68.92,
  "timestamp": "2026-05-12T10:31:24.123456",
  "work_directory": "/Users/user/project/work"
}
```

## Checks Effectués

### Security Checks (Phase 3)
- **Uniform Bucket Level Access (UBLA)**: `uniform_bucket_level_access = true`
- **Public access prevention**: `public_access_prevention = "enforced"`
- **Encryption at rest**: `encryption` ou `kms_key_name` configuré
- **Versioning enabled**: `versioning { enabled = true }`
- **Lifecycle policies**: Règles de transition/expiration

### Best Practices Checks (Phase 3)
- **Module structure**: Code organisé en modules réutilisables
- **Variables defined**: Fichier `variables.tf` présent
- **Outputs defined**: Fichier `outputs.tf` présent
- **Documentation present**: Descriptions et README

### Validation Checks (Phase 4)
- **Terraform plan**: Génération du plan sans erreur
- **Files generated**: Nombre de fichiers `.tf` créés
- **All phases OK**: Toutes les phases ont réussi

## Scoring

Le pipeline calcule deux scores :

### Security Score
```
security_score = (nombre de checks sécurité passés / total checks) * 100
```

- **≥ 80%**: ✅ Code sécurisé
- **60-79%**: ⚠️ Améliorations recommandées
- **< 60%**: ❌ Problèmes critiques

### Best Practices Score
```
bp_score = (nombre de checks BP passés / total checks) * 100
```

- **≥ 75%**: ✅ Bonnes pratiques respectées
- **50-74%**: ⚠️ Améliorations recommandées
- **< 50%**: ❌ Refactoring nécessaire

## Verdict Final

Le pipeline produit un verdict basé sur tous les résultats :

```python
if all_phases_ok and security_score >= 80 and plan_success:
    verdict = "✅ PIPELINE SUCCEEDED"
elif all_phases_ok:
    verdict = "⚠️ PIPELINE COMPLETED WITH WARNINGS"
else:
    verdict = "❌ PIPELINE FAILED"
```

## Comparaison avec TerraformGenerator

| Aspect | TerraformGenerator | PipelineExecutor |
|--------|-------------------|------------------|
| **Phases visibles** | Non | ✅ 4 phases explicites |
| **Security checks** | Implicite | ✅ Checks détaillés avec scoring |
| **BP compliance** | Implicite | ✅ Checks détaillés avec scoring |
| **Reporting** | Agent output | ✅ Rapport JSON structuré |
| **Durée par phase** | Non | ✅ Durée de chaque phase |
| **Verdict final** | Non | ✅ SUCCESS/WARNING/FAILED |
| **Rétrocompatible** | - | ✅ Wrapping du Generator |

## Cas d'Usage

### 1. Développement Interactif
Utilisez le **PipelineExecutor** pour voir chaque étape et comprendre ce que fait l'agent.

### 2. CI/CD Pipeline
Intégrez le rapport JSON dans vos pipelines pour vérifier les scores de sécurité et BP.

```python
report = pipeline.get_execution_report()
failed_phases = [
    entry for entry in report["execution_log"] 
    if entry["status"] == "FAILED"
]

if failed_phases:
    raise Exception(f"Pipeline failed: {failed_phases}")
```

### 3. Audit et Compliance
Sauvegardez les rapports d'exécution pour tracer les générations de code.

```python
import json
from datetime import datetime

report = pipeline.get_execution_report()
report_file = f"audit/terraform-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
Path(report_file).write_text(json.dumps(report, indent=2))
```

### 4. Dashboards et Métriques
Agrégez les rapports pour créer des dashboards :
- Durée moyenne par phase
- Taux de succès
- Scores de sécurité moyens

## Extensibilité

Le `PipelineExecutor` peut être étendu facilement :

### Ajouter des Checks Personnalisés

```python
class CustomPipelineExecutor(PipelineExecutor):
    def _phase_3_code_review(self, generation_results):
        results = super()._phase_3_code_review(generation_results)
        
        # Ajouter vos checks personnalisés
        custom_checks = {
            "Cost optimization": self._check_cost_optimization(),
            "Compliance tags": self._check_compliance_tags(),
        }
        
        results["custom_checks"] = custom_checks
        return results
```

### Ajouter une Phase

```python
def run(self, user_prompt):
    # Phases existantes
    planning = self._phase_1_planning(user_prompt)
    generation = self._phase_2_generation(user_prompt)
    review = self._phase_3_code_review(generation)
    
    # Nouvelle phase
    cost_analysis = self._phase_5_cost_analysis(review)
    
    validation = self._phase_4_validation(planning, generation, review)
    return generation["agent_output"]
```

## Limitations

- **Performance**: Ajoute ~2-3s de overhead pour le parsing et reporting
- **Heuristiques**: Les checks sont basés sur la présence de mots-clés dans l'output
- **Pas de modification du code**: Le pipeline ne modifie pas le comportement du Generator

## Migration

### Depuis TerraformGenerator

```python
# Ancien code
from terraform_agent import TerraformGenerator
generator = TerraformGenerator(config, prompts, knowledge_base)
result = generator.run(user_prompt)

# Nouveau code (drop-in replacement)
from terraform_agent import PipelineExecutor
pipeline = PipelineExecutor(config, prompts, knowledge_base)
result = pipeline.run(user_prompt)
```

Le `PipelineExecutor` est un **wrapper** autour de `TerraformGenerator`, donc le résultat est identique, seul l'output structuré change.

## Prochaines Étapes

1. **Tester** avec `notebooks/pipeline_executor_demo.ipynb`
2. **Comparer** les outputs avec `terraform_generator.ipynb`
3. **Intégrer** dans vos workflows CI/CD si applicable
4. **Étendre** avec vos checks personnalisés

## Ressources

- Code source: `terraform_agent/pipeline_executor.py`
- Notebook démo: `notebooks/pipeline_executor_demo.ipynb`
- Tests: `eval/test_cases.py` (à adapter pour le pipeline)
