# Terraform Rules Repository

Ce répertoire contient les **règles apprises** et les **best practices** pour la génération Terraform autonome.

## 📁 Structure

| Fichier | Contenu |
|---------|---------|
| **RULES_FORMAT.md** | 📖 Documentation complète du format XML des règles |
| **RULES_TEMPLATE.md** | 📋 Template vide à dupliquer pour créer une nouvelle règle |
| **rules-*.md** | ✅ Règles existantes (exemple: `rules-gcs-providers.md`) |

## 🎯 Qu'est-ce qu'une Règle?

Une **règle** est un pattern documenté qui:

1. ✅ Identifie un problème ou une bonne pratique
2. ✅ Fournit des exemples correct et incorrect
3. ✅ Explique la racine cause et les conséquences
4. ✅ Inclut des étapes de validation
5. ✅ Est réutilisable par l'agent dans les générations futures

**Exemple:** Règle sur les version constraints
```
Problème: terraform-google-modules/cloud-storage/google v12.3 
          nécessite Google provider >= 6.37.0
Exemple correct: version = "~> 6.0"
Exemple incorrect: version = "~> 5.0"
Conséquence: Erreur terraform validate
```

## 🚀 Utilisation

### Pour ajouter une nouvelle règle:

1. **Consultez** `RULES_FORMAT.md` pour comprendre la structure
2. **Dupliquez** `RULES_TEMPLATE.md`
3. **Complétez** chaque section:
   - `<title>` — Titre court
   - `<description>` — Explication détaillée
   - `<pattern id="correct">` — Exemple valide
   - `<antipattern id="incorrect">` — Exemple invalide
   - `<when-to-apply>` — Conditions d'application
4. **Renommez** le fichier: `rules-{PREFIX}-{DOMAIN}.md`
   - Exemple: `rules-gcs-logging.md`, `rules-tf-backend.md`
5. **Validez** la structure XML (pas d'erreurs de balise)
6. **Committez** dans le répertoire `rules/`

### Pour l'agent (générations futures):

L'agent indexera automatiquement les règles dans ChromaDB et:
- 🔍 Cherchera les règles applicables via `search_knowledge_base()`
- ✅ Validera le code généré contre les règles
- 🔧 Corrigera les violations selon leur sévérité

## 📊 Règles Existantes

### Par Domaine

#### GCS (Google Cloud Storage)
- [rules-gcs-providers.md](rules-gcs-providers.md) — Provider version constraints
- [rules-gcs-input-types.md](rules-gcs-input-types.md) — Input variable types

#### Terraform Structure
- [rules-tf-project-structure.md](rules-tf-project-structure.md) — File organization
- [rules-tf-naming-state.md](rules-tf-naming-state.md) — Naming conventions
- [rules-tf-environments.md](rules-tf-environments.md) — Environment isolation
- [rules-tf-state-versioning.md](rules-tf-state-versioning.md) — State management
- [rules-tf-security-cicd.md](rules-tf-security-cicd.md) — Security & CI/CD

### Par Sévérité

**🔴 CRITICAL** — Bloque la génération/déploiement:
- GCS-PROVIDER-001: Module provider version
- TF-SECURITY-*: Violations de sécurité
- TF-STATE-*: State management issues

**🟠 MAJOR** — À corriger avant déploiement:
- TF-NAMING-*: Conventions de naming
- TF-STRUCTURE-*: Problèmes de structure
- TF-ENVIRONMENT-*: Isolation d'environnement

**🟡 MINOR** — Améliorations recommandées:
- Style et documentation
- Optimisations de performance
- Best practices optionnelles

## 🔍 Rechercher une Règle

**Par sujet:**
```bash
grep -l "security\|encryption" rules-*.md
grep -l "provider\|version" rules-*.md
grep -l "naming\|convention" rules-*.md
```

**Par sévérité:**
```bash
grep 'severity="CRITICAL"' rules-*.md
grep 'severity="MAJOR"' rules-*.md
```

**Par domaine:**
```bash
ls rules-gcs-*.md      # Google Cloud Storage
ls rules-tf-*.md       # General Terraform
```

## 📝 Format de Fichier

Toutes les règles utilisent le format XML structuré:

```xml
<rule id="PREFIX-TYPE-NNN" severity="CRITICAL" category="Compatibility">
  <title>...</title>
  <description>...</description>
  <context>...</context>
  <problem>...</problem>
  <pattern id="correct">...</pattern>
  <antipattern id="incorrect">...</antipattern>
  <why>...</why>
  <validation>...</validation>
  <when-to-apply>...</when-to-apply>
  <implementation-checklist>...</implementation-checklist>
  <related-rules>...</related-rules>
  <references>...</references>
</rule>
```

👉 **Voir [RULES_FORMAT.md](RULES_FORMAT.md) pour la documentation complète**

## 🤖 Intégration Agent

Pour que l'agent utilise les règles:

1. **Génération:** L'agent identifie des patterns et règles
2. **Documentation:** Formate les règles apprises en XML
3. **Stockage:** Les sauvegarde dans `rules/`
4. **Indexation:** ChromaDB les indexe automatiquement
5. **Réutilisation:** Générations futures les consultent

👉 **Voir [prompts/terraform-system.md](../prompts/terraform-system.md) — Phase 5 : Capture de Connaissance & Génération de Règles** pour les détails techniques

## ✅ Checklist: Créer une Nouvelle Règle

- [ ] Lire [RULES_FORMAT.md](RULES_FORMAT.md)
- [ ] Dupliquer [RULES_TEMPLATE.md](RULES_TEMPLATE.md)
- [ ] Compléter toutes les sections obligatoires
- [ ] Valider la structure XML (pas d'erreurs de balises)
- [ ] Tester les exemples de code (doivent être exécutables)
- [ ] Choisir ID, severity, category corrects
- [ ] Renommer le fichier: `rules-{PREFIX}-{DOMAIN}.md`
- [ ] Commit dans le repo

## 🔗 Références

| Document | Objectif |
|----------|----------|
| [RULES_FORMAT.md](RULES_FORMAT.md) | Guide complet du format des règles |
| [RULES_TEMPLATE.md](RULES_TEMPLATE.md) | Template pour créer une règle |
| [terraform-system.md](../prompts/terraform-system.md) | Système prompt — Phase 5 pour génération et documentation |
| [Terraform Docs](https://www.terraform.io/language) | Référence Terraform officielle |
| [Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest) | Provider Google officiel |

## 💡 Bonnes Pratiques

✅ **À faire:**
- Soyez concis mais complet
- Utilisez des exemples réels et testables
- Expliquez le "pourquoi", pas juste le "quoi"
- Référencez la documentation officielle
- Datez vos règles (creation date)
- Marquez le statut: "Validated in production", "Proposed", etc.

❌ **À éviter:**
- Texte trop long ou verbeux
- Exemples fictifs ou irréalistes
- Jargon sans explication
- Règles trop vagues ou générales
- Sections vides ou incomplètes

## 🎓 Exemples

Consultez les fichiers `rules-*.md` existants pour voir:
- Comment structurer une règle complexe
- Comment formater les exemples de code
- Comment écrire une bonne description
- Comment couvrir les cas d'erreur courants

## 🐛 Troubleshooting

**Q: Je ne suis pas sûr du format?**  
A: Consultez [RULES_FORMAT.md](RULES_FORMAT.md) ou dupliquez une règle existante.

**Q: Comment valider ma règle?**  
A: Vérifiez la structure XML et testez les exemples de code.

**Q: Comment ajouter une règle au projet?**  
A: Commitez-la dans le répertoire `rules/`. L'agent l'indexera automatiquement.

**Q: Comment l'agent utilise les règles?**  
A: Consultez [prompts/terraform-system.md](../prompts/terraform-system.md) — Phase 5 : Capture de Connaissance & Génération de Règles.

## 📞 Support

- 📖 Documenté dans [CLAUDE.md](../CLAUDE.md)
- 🔍 Exemples existants dans `rules-*.md`
- 🤖 Intégration agent dans [prompts/terraform-system.md](../prompts/terraform-system.md) — Phase 5

---

**Dernière mise à jour:** 2026-05-11  
**Statut:** ✅ Production-ready  
**Nombre de règles:** 7 domaines couverts
