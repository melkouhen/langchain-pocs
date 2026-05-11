
# Terraform Code Review & Generation Agent

Agent autonome de génération et validation de code Terraform respectant les meilleures pratiques.

## 🎯 Objectif

L'agent génère du code Terraform, le valide et corrige automatiquement les erreurs détectées en s'appuyant sur les bonnes pratiques définies dans le répertoire `docs/`.

## 💡 Pourquoi cet agent?

- **Gain de temps:** Génération automatique de modules Terraform production-ready en 2-5 minutes
- **Qualité garantie:** Validation syntaxique + revue de code automatique (sécurité, performance, coûts)
- **Best practices intégrées:** Recherche sémantique dans la knowledge base avant génération
- **Multi-environnements:** Génère dev/prod avec configurations adaptées

**Cas d'usage:**
- Bootstrapping rapide d'infrastructure GCP
- Standardisation de modules Terraform dans l'équipe
- Audit automatique de code Terraform existant

## 🛠️ Technologies

| Technologie    | Rôle                                       |
| -------------- | ------------------------------------------ |
| **LangChain**  | Orchestration des agents                   |
| **Claude API** | Génération de code (Haiku 4.5)             |
| **ChromaDB**   | Recherche sémantique des bonnes pratiques  |
| **DeepAgents** | Planification autonome                     |
| **Ollama**     | Validation locale (qwen2.5-coder:7b)       |

## 📁 Structure

```
notebooks/
├── deepchain_terraform_assistant.ipynb    # Point d'entrée principal
├── token_analysis.ipynb                   # Analyse consommation tokens
└── chromadb_explorer.ipynb                # Exploration knowledge base

terraform_agent/                           # Agent Python (624 lignes)
├── agent.py                               # Orchestration
├── tools.py                               # 3 outils: search, validate, review
├── knowledge_base.py                      # ChromaDB
├── prompts.py                             # Templates
└── config.py                              # Configuration

docs/                                      # Bonnes pratiques
├── structure.md
└── cloud-storage.md

prompts/                                   # Templates LLM
├── terraform-system.md                    # Comportement agent
├── terraform-user.md
├── terraform-review.md
├── terraform-validate.md
└── terraform-evaluation.md

work/                                      # Sortie générée
├── modules/gcs_bucket/                    # Module réutilisable
├── envs/{dev,prod}/                       # Environnements
├── README.md
├── DEPLOYMENT.md
├── VALIDATION_REPORT.md
└── PROJECT_SUMMARY.md
```

## 🏗️ Architecture

```
1. INITIALIZATION
   → Charge prompts + crée ChromaDB + index docs/

2. SETUP
   → Initialise Claude + enregistre outils

3. EXECUTION
   → Agent autonome appelle:
      - search_knowledge_base → bonnes pratiques
      - validate_and_fix_code → validation syntaxe
      - review_and_fix_code   → revue qualité

4. OUTPUT
   → Génère Terraform + documentation dans work/
```

## 🚀 Démarrage

### Pré-requis

**Obligatoires:**
```bash
# Python 3.14+
python --version

# uv (gestionnaire packages)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ollama + modèle qwen2.5-coder:7b
ollama pull qwen2.5-coder:7b
curl http://localhost:11434/api/tags  # Vérifier
```

**Optionnels (déploiement GCP):**
```bash
gcloud auth application-default login
terraform version  # >= 1.5
```

### Installation

```bash
uv sync
```

### Configuration

```bash
# Créer .env depuis le template
cp .env.example .env

# Éditer .env et ajouter:
# ANTHROPIC_API_KEY=sk-ant-...

# Obtenir clé: https://console.anthropic.com/account/keys
```

### Exécution

```bash
# 1. Vérifier setup
python --version                          # 3.14+
curl http://localhost:11434/api/tags      # Ollama OK

# 2. Ouvrir notebook
code notebooks/deepchain_terraform_assistant.ipynb

# 3. Exécuter les cellules (durée: 2-5 min)

# 4. Résultats dans work/
#    → work/PROJECT_SUMMARY.md (vue d'ensemble)
#    → work/DEPLOYMENT.md (guide déploiement)
```

## 📊 Résultats

**Infrastructure générée dans `work/`:**

- **Module réutilisable** (`modules/gcs_bucket/`)
  - `main.tf`: 1 ressource google_storage_bucket avec 11 variables
  - `variables.tf`: versioning, encryption, IAM, lifecycle, logging...
  - `outputs.tf`: bucket URL, nom, self_link, etc.
  
- **Environnements**
  - `envs/dev/`: Bucket simple pour tests
  - `envs/prod/`: Bucket avec lifecycle rules (transition vers COLDLINE après 90j)

**Documentation auto-générée:**
- `README.md` (400+ lignes): Guide complet d'utilisation


**Exemple de résultat:**
```hcl
# work/modules/gcs_bucket/main.tf
resource "google_storage_bucket" "this" {
  name          = var.bucket_name
  location      = var.location
  storage_class = var.storage_class
  
  uniform_bucket_level_access = true  # Sécurité
  public_access_prevention    = "enforced"
  
  versioning {
    enabled = var.versioning_enabled
  }
}
```

## 🔧 Troubleshooting

| Problème | Cause | Solution |
|----------|-------|----------|
| `ModuleNotFoundError: chromadb` | Environnement virtuel non initialisé | `rm -rf .venv && uv sync` |
| `Ollama connection error` | Service Ollama non démarré | `ollama serve` (terminal séparé) |
| `ANTHROPIC_API_KEY invalid` | Clé manquante ou erronée | Vérifier sur [console.anthropic.com](https://console.anthropic.com/account/keys) |
| `ChromaDB initialization hangs` | Base vectorielle corrompue | `rm -rf .vectorstore .vectorstore2` |
| `Permission denied: ./work/` | Droits fichiers | `chmod 755 work/ && rm -rf work/*` |

**Logs utiles:**
```bash
# Vérifier Ollama
curl http://localhost:11434/api/tags

# Tester clé Anthropic
python -c "from anthropic import Anthropic; Anthropic(api_key='sk-ant-...')"

# Explorer ChromaDB
jupyter notebook notebooks/chromadb_explorer.ipynb
```

## 📚 Documentation complémentaire

Pour plus de détails, consulter **[CLAUDE.md](CLAUDE.md)** (documentation complète du projet).

## État du projet

**Statut:** ✅ Production-ready (mise à jour: 11 mai 2026)

### Limitations connues

- **Cloud providers:** Actuellement GCP uniquement (AWS/Azure à venir)
- **Modules:** Focus sur Google Cloud Storage (autres services en développement)
- **Langues:** Prompts et documentation en français/anglais mélangés

### Roadmap

**Court terme (1-2 semaines):**
- [ ] Support AWS S3 et Azure Blob Storage
- [ ] Backend Terraform remote state (GCS)
- [ ] Exemple CI/CD (GitHub Actions)

**Moyen terme (1-2 mois):**
- [ ] Catalogue de modules personnalisables
- [ ] Estimation de coûts (Infracost)
- [ ] Intégration Terraform Cloud

### Support & Contribution

**Besoin d'aide?**
1. Consulter section [Troubleshooting](#-troubleshooting)
2. Vérifier [CLAUDE.md](CLAUDE.md) pour détails techniques
3. Consulter l'historique: `git log --oneline -15`

**Contribuer:**
- Lire [CLAUDE.md](CLAUDE.md) avant modification
- Un commit = une fonctionnalité/fix
- Format commit: `<type>: <description>` (types: `feat`, `fix`, `docs`, `refactor`, `chore`)

**Liens utiles:**
- [Terraform Documentation](https://www.terraform.io/language)
- [Google Cloud Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Anthropic Claude API](https://docs.anthropic.com)
- [LangChain Docs](https://python.langchain.com)
