# Model Routing - Phase 1 Optimization

## 🎯 Objectif

Réduire les coûts d'API Claude en déléguant certaines tâches à des modèles Ollama locaux, tout en conservant la flexibilité de revenir à Claude si nécessaire.

## 📊 Gains Estimés

| Configuration | Tokens Claude | Coût par run | Réduction |
|---------------|---------------|--------------|-----------|
| **Tout Claude** (baseline) | ~7,850 | $0.018 | 0% |
| **Ollama: summarization** | ~6,650 | $0.014 | 22% |
| **Ollama: summarization + parsing** | ~5,850 | $0.012 | 33% |
| **Ollama: all 3 tasks** | ~5,350 | $0.011 | 39% |

## 🔧 Configuration

### Via .env (Recommandé)

```bash
# .env
USE_OLLAMA_FOR=summarization,parsing,review

# Modèles Ollama (optionnel, valeurs par défaut)
OLLAMA_SUMMARY_MODEL=qwen3.5:9b
OLLAMA_PARSE_MODEL=qwen2.5-coder:7b-instruct
OLLAMA_REVIEW_MODEL=qwen2.5-coder:14b
```

### Via Code

```python
from terraform_agent import Config, PromptManager, KnowledgeBase, ModelRouter, TerraformAgent

config = Config()
config.USE_OLLAMA_FOR = {"summarization", "parsing"}  # Sélectif
# ou
config.USE_OLLAMA_FOR = set()  # Désactiver Ollama complètement

# Le reste est automatique
prompts = PromptManager(config)
kb = KnowledgeBase(config)
agent = TerraformAgent(config, prompts, kb)
```

## 📋 Tâches Délégables

### 1. **summarization** (Résumé knowledge base)

**Avant (Claude):**
```
Knowledge base query → 3 chunks × ~400 chars = ~1,200 chars → Claude
```

**Après (Ollama):**
```
Knowledge base query → 3 chunks × ~400 chars → Ollama summarize → ~400 chars → Claude
```

**Gain:** ~800 chars / ~200 tokens / ~$0.001 par requête

**Qualité:** ✅ Excellente avec qwen3.5:9b (capacité suffisante pour résumés)

### 2. **parsing** (Analyse erreurs Terraform)

**Avant (Claude):**
```
terraform validate error (500-2000 chars brut) → Claude parse
```

**Après (Ollama):**
```
terraform validate error → Ollama parse → structured summary (200-400 chars) → Claude
```

**Gain:** ~300-800 chars / ~75-200 tokens / ~$0.0004 par erreur

**Qualité:** ✅ Bonne avec qwen2.5-coder:7b-instruct (spécialisé code)

### 3. **review** (Revue de code)

**Déjà fait!** Utilise Ollama depuis le début via `review_and_fix_code`.

**Gain:** ~$0.008 par review (déjà économisé)

## 🔄 Fallback Automatique

Si Ollama n'est pas disponible (service down, modèle manquant), le système bascule automatiquement sur Claude:

```python
# model_router.py - Gère automatiquement
def get_model(self, task_type: ModelType, fallback: bool = True):
    if should_use_ollama:
        if self._check_ollama_available():
            return ChatOllama(...)  # Ollama OK
        if fallback:
            logger.warning("Ollama unavailable, falling back to Claude")
            return ChatAnthropic(...)  # Fallback Claude
```

**Logs:**
```
⚠️  Ollama unavailable for summarization, falling back to Claude
✓ Using Claude model 'claude-haiku-4-5-20251001' for summarization
```

## 🧪 Testing

### Tester Ollama disponible

```bash
curl http://localhost:11434/api/tags
# Should return JSON with model list
```

### Tester avec Ollama

```bash
# .env
USE_OLLAMA_FOR=summarization,parsing,review

python notebooks/deepchain_terraform_assistant.ipynb
```

**Vérifier dans logs:**
```
✓ Using Ollama model 'qwen3.5:9b' for summarization
✓ Using Ollama model 'qwen2.5-coder:7b-instruct' for parsing
```

### Tester avec Claude uniquement

```bash
# .env
USE_OLLAMA_FOR=

python notebooks/deepchain_terraform_assistant.ipynb
```

**Vérifier dans logs:**
```
✓ Using Claude model 'claude-haiku-4-5-20251001' for summarization
✓ Using Claude model 'claude-haiku-4-5-20251001' for parsing
```

### Tester fallback automatique

```bash
# Arrêter Ollama
pkill ollama

# .env
USE_OLLAMA_FOR=summarization

python notebooks/deepchain_terraform_assistant.ipynb
```

**Vérifier dans logs:**
```
⚠️  Ollama unavailable for summarization, falling back to Claude
✓ Using Claude model 'claude-haiku-4-5-20251001' for summarization
```

## 📈 Monitoring avec Phoenix

Si Phoenix est activé, vous verrez les appels modèles dans l'UI:

```
http://localhost:6006

Traces:
├── search_knowledge_base
│   └── Ollama qwen3.5:9b (summarization) ← NEW
├── terraform_validate
│   └── Ollama qwen2.5-coder:7b (parsing) ← NEW
└── review_and_fix_code
    └── Ollama qwen2.5-coder:14b (review)
```

## ⚙️ Modèles Ollama Recommandés

### Installation

```bash
# Minimum (Phase 1)
ollama pull qwen2.5-coder:7b-instruct  # Parsing rapide
ollama pull qwen3.5:9b                 # Summarization qualité

# Optionnel (meilleure qualité review)
ollama pull qwen2.5-coder:14b          # Review code avancé
```

### Comparaison Modèles

| Modèle | Taille | Usage Recommandé | Qualité | Vitesse |
|--------|--------|------------------|---------|---------|
| qwen2.5-coder:7b-instruct | 4.7 GB | Parsing erreurs | ⭐⭐⭐ | ⚡⚡⚡ |
| qwen3.5:9b | 6.6 GB | Summarization | ⭐⭐⭐⭐ | ⚡⚡ |
| qwen2.5-coder:14b | 9.0 GB | Code review | ⭐⭐⭐⭐⭐ | ⚡ |

## 🚨 Troubleshooting

### Erreur: "Ollama not available"

**Cause:** Service Ollama non démarré

**Solution:**
```bash
ollama serve
# Dans un terminal séparé
```

### Erreur: "Model 'qwen3.5:9b' not found"

**Cause:** Modèle non téléchargé

**Solution:**
```bash
ollama pull qwen3.5:9b
```

### Performance dégradée

**Cause:** Ollama utilise CPU au lieu de GPU

**Solution:**
```bash
# Vérifier GPU disponible
ollama list
# Si GPU non détecté, installer drivers appropriés
```

### Résultats de mauvaise qualité

**Cause:** Modèle trop petit pour la tâche

**Solution:**
```bash
# .env - Utiliser modèles plus gros
OLLAMA_SUMMARY_MODEL=qwen2.5-coder:14b
OLLAMA_PARSE_MODEL=qwen2.5-coder:14b
```

Ou revenir à Claude:
```bash
# .env
USE_OLLAMA_FOR=  # Désactiver Ollama
```

## 🔮 Roadmap Phase 2

- [ ] Base template generation avec Ollama
- [ ] Retry logic avec backoff exponentiel
- [ ] Caching intelligent résultats Ollama
- [ ] Fine-tuning qwen2.5-coder sur règles custom
- [ ] Batch processing requêtes similaires
