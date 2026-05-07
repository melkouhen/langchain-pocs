<!-- vscode-markdown-toc -->
* 1. [🎯 Objectif](#Objectif)
* 2. [🛠️ Technologies Principales](#TechnologiesPrincipales)
* 3. [📁 Structure du Projet](#StructureduProjet)
* 4. [🏗️ Architecture Globale du notebook](#ArchitectureGlobaledunotebook)
* 5. [🚀 Démarrage Rapide](#DmarrageRapide)
	* 5.1. [Pré-requis Système](#Pr-requisSystme)
	* 5.2. [Installation des dépendances](#Installationdesdpendances)
	* 5.3. [Configuration](#Configuration)
	* 5.4. [Exécution](#Excution)
* 6. [📊 Résultats & Sortie](#RsultatsSortie)
* 7. [État du projet](#tatduprojet)

<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

# Terraform Code Review & Generation Agent

Agent de génération et validation de code Terraform.

##  1. <a name='Objectif'></a>🎯 Objectif

Cet agent:
1. **Génère** du code Terraform
2. **Valide** le code généré
3. **Corrige** les erreurs détectées

Cet agent doit respecter les bonnes pratiques trouvées dans le répertoire docs.


##  2. <a name='TechnologiesPrincipales'></a>🛠️ Technologies Principales

| Technologie    | Rôle                                            | Version     |
| -------------- | ----------------------------------------------- | ----------- |
| **LangChain**  | Orchestration d'agents et chaînage d'outils     | >= 1.2.15   |
| **Claude API** | Modèle LLM pour l'analyse et génération         | Haiku 4.5   |
| **ChromaDB**   | Vector store pour la recherche sémantique       | >= 1.5.8    |
| **DeepAgents** | Agent autonome avec planification long-terme    | >= 0.5.4    |
| **Ollama**     | Modèle local pour validation Terraform          | qwen2.5-7b  |
| **LangSmith**  | Tracing et debugging des agents (optionnel)     | >= 0.7.38   |

##  3. <a name='StructureduProjet'></a>📁 Structure du Projet

```
.
├── notebooks/
│   ├── deepchain_terraform_assistant.ipynb      # Notebook principal (agent orchestration)
│   ├── token_analysis.ipynb                     # Analyse consommation tokens Claude
│   └── chromadb_explorer.ipynb                  # Exploration de la knowledge base
├── terraform_agent/                             # Code agent Python (624 lignes)
│   ├── agent.py                                 # Orchestration DeepAgent
│   ├── tools.py                                 # Outils: validation, review, search
│   ├── knowledge_base.py                        # Integration ChromaDB
│   ├── prompts.py                               # Gestion des prompts
│   └── config.py                                # Configuration centralisée
├── docs/                                        # Bonnes pratiques Terraform
│   ├── structure.md
│   └── cloud-storage.md
├── prompts/                                     # Templates LLM
│   ├── terraform-system.md                      # System prompt (agent behavior)
│   ├── terraform-user.md
│   ├── terraform-review.md
│   ├── terraform-validate.md
│   └── terraform-evaluation.md
├── work/                                        # Résultats de la génération
│   ├── modules/gcs_bucket/                      # Module Terraform réutilisable
│   ├── envs/{dev,prod}/                         # Environnements Terraform (dev & prod)
│   ├── README.md                                # Documentation complète
│   ├── DEPLOYMENT.md                            # Guide déploiement pas-à-pas
│   ├── VALIDATION_REPORT.md                     # Rapport d'assurance qualité
│   └── PROJECT_SUMMARY.md                       # Résumé du projet généré
├── .vectorstore2/                               # Base de données ChromaDB (cache)
├── .env                                         # Configuration (API keys)
├── .env.example                                 # Template .env
├── pyproject.toml                               # Dépendances Python (uv)
└── .python-version                              # Python 3.14
```

##  4. <a name='ArchitectureGlobaledunotebook'></a>🏗️ Architecture Globale du notebook

L'agent est implémenté comme un notebook python avec les phases suivantes :

```

1️⃣ INITIALIZATION
   ├─ Charge les prompts (system, user, templates)
   ├─ Crée une base vectorielle (ChromaDB) 
   └─ Index les documents (docs/*.md) dans ChromaDB

2️⃣ AGENT SETUP
   ├─ Initialise le modèle Claude
   └─ Configure les outils disponibles

3️⃣ AGENT EXECUTION
   ├─ Lance l'agent autonome
   ├─ L'agent appelle les outils selon les besoins :
   │  ├─ search_knowledge_base    → Récupère les best practices
   │  ├─ validate_and_fix_code    → Valide la syntaxe
   │  └─ review_and_fix_code      → Effectue la revue de code
   └─ Génère le code Terraform final

4️⃣ OUTPUT
   └─ Résultats dans ./work/ avec rapport de validation/révision
```

##  5. <a name='DmarrageRapide'></a>🚀 Démarrage Rapide

###  5.1. <a name='Pr-requisSystme'></a>Pré-requis Système

**Logiciels obligatoires:**
- **Python 3.14+** : version cible (voir `.python-version`)
- **uv** : gestionnaire de packages Python rapide
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Ollama** : pour modèle local Terraform validation
  ```bash
  # macOS: https://ollama.ai/download
  # Télécharger et installer, puis:
  ollama pull qwen2.5-coder:7b
  ```
  - Le service Ollama doit écouter sur `http://localhost:11434`
  - Vérifier: `curl http://localhost:11434/api/tags`

**Pour déploiement Terraform (optionnel si test uniquement):**
- **gcloud CLI** : authentification GCP
  ```bash
  gcloud auth application-default login
  ```
- **Terraform >= 1.5** : pour déployer l'infrastructure générée

**IDE (recommandé):**
- **VS Code** avec extensions:
  - Jupyter plugin (pour exécuter les notebooks)
  - Terraform extension (pour synthaxe HCL)

###  5.2. <a name='Installationdesdpendances'></a>Installation des dépendances

```bash
uv sync
```

###  5.3. <a name='Configuration'></a>Configuration

**Copier le template et remplir les clés:**
```bash
cp .env.example .env
```

**Variables requises dans `.env`:**
```bash
# Anthropic API (obligatoire)
ANTHROPIC_API_KEY=sk-ant-...

# LangSmith (optionnel - pour tracing/debugging)
LANGSMITH_API_KEY=lsv_pt_...
LANGSMITH_PROJECT=terraform-agent
```

**Obtenir les clés:**
- `ANTHROPIC_API_KEY` : https://console.anthropic.com/account/keys
- `LANGSMITH_API_KEY` : https://smith.langchain.com (optionnel)

###  5.4. <a name='Excution'></a>Exécution

**Étape 1: Vérifier les pré-requis**
```bash
# Python
python --version  # Should be 3.14+

# Ollama (doit être en running)
curl http://localhost:11434/api/tags  # Doit répondre
```

**Étape 2: Installer les dépendances**
```bash
uv sync
```

**Étape 3: Lancer le notebook**
1. Ouvrir VS Code
2. Ouvrir `notebooks/deepchain_terraform_assistant.ipynb`
3. Sélectionner kernel Python (uv env)
4. Exécuter les cellules dans l'ordre

**Étape 4: Consulter les résultats**
- Résultats générés dans `./work/`
- Lire `work/PROJECT_SUMMARY.md` pour vue d'ensemble
- Consulter `work/DEPLOYMENT.md` pour déployer l'infrastructure

##  6. <a name='RsultatsSortie'></a>📊 Résultats & Sortie

Après exécution, le notebook génère dans `./work/`:

**Infrastructure Terraform (production-ready):**
- `modules/gcs_bucket/` — Module réutilisable Google Cloud Storage
  - `main.tf` — Ressource GCS avec variables
  - `variables.tf` — 11 variables d'entrée
  - `outputs.tf` — 6 outputs pour consommation aval
- `envs/dev/` — Environnement de développement
  - Configuration pour bucket de test
  - État Terraform isolé
- `envs/prod/` — Environnement de production
  - Configuration avec lifecycle rules (économie)
  - État Terraform isolé
  

##  7. <a name='tatduprojet'></a>État du projet

**Statut:** ✅ **En cours de développement** (dernière mise à jour 7 mai 2026)
