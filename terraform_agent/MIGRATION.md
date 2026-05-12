# Migration Guide: TerraformAgent → TerraformGenerator

## Changement de Nomenclature

Pour une meilleure cohérence sémantique, la classe `TerraformAgent` a été renommée en `TerraformGenerator`.

### Nouvelle Architecture

```
terraform_agent/
├── generator.py      # TerraformGenerator (génération de code)
├── reviewer.py       # TerraformReviewer (revue de code)
├── agent.py         # TerraformAgent (alias deprecated)
└── ...
```

## Migration

### Avant (deprecated)

```python
from terraform_agent import TerraformAgent

agent = TerraformAgent(config, prompts, knowledge_base)
result = agent.run(user_prompt)
```

⚠️ **Warning:** Affiche un DeprecationWarning

### Après (recommandé)

```python
from terraform_agent import TerraformGenerator

generator = TerraformGenerator(config, prompts, knowledge_base)
result = generator.run(user_prompt)
```

## Rétrocompatibilité

L'ancien nom `TerraformAgent` reste disponible pour la rétrocompatibilité :

```python
# Fonctionne toujours mais affiche un warning
from terraform_agent import TerraformAgent  
agent = TerraformAgent(...)  # ⚠️ DeprecationWarning
```

**Recommandation:** Migrer vers `TerraformGenerator` dès que possible.

## Nomenclature Cohérente

| Classe | Rôle | Fichier |
|--------|------|---------|
| `TerraformGenerator` | Génération de code Terraform | `generator.py` |
| `TerraformReviewer` | Revue de code Terraform | `reviewer.py` |
| `TerraformAgent` | ⚠️ Deprecated alias | `agent.py` |

## Notebooks Mis à Jour

- ✅ `terraform_generator.ipynb` → Utilise `TerraformGenerator`
- ✅ `terraform_code_review_v2.ipynb` → Utilise `TerraformReviewer`

## Timeline

- **v1.0**: Introduction de `TerraformGenerator` et `TerraformReviewer`
- **v1.x**: `TerraformAgent` disponible avec DeprecationWarning
- **v2.0**: Suppression de `TerraformAgent` (prévu)

## Questions

**Q: Pourquoi ce changement ?**
A: Pour une nomenclature plus claire et explicite :
- `TerraformGenerator` → Génère du code
- `TerraformReviewer` → Revue du code

**Q: Mon code existant va-t-il casser ?**
A: Non, `TerraformAgent` fonctionne toujours mais affiche un warning.

**Q: Quand dois-je migrer ?**
A: Dès que possible pour éviter les breaking changes en v2.0.

## Checklist de Migration

- [ ] Remplacer les imports `TerraformAgent` par `TerraformGenerator`
- [ ] Renommer les variables `agent` en `generator` (optionnel)
- [ ] Mettre à jour la documentation/commentaires
- [ ] Tester le code
- [ ] Vérifier qu'il n'y a plus de DeprecationWarning
