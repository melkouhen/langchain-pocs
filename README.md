<!-- vscode-markdown-toc -->
* 1. [🎯 Objectif](#Objectif)
* 2. [🛠️ Technologies Principales](#TechnologiesPrincipales)
* 3. [📁 Structure du Projet](#StructureduProjet)
* 4. [🏗️ Architecture Globale du notebook](#ArchitectureGlobaledunotebook)
* 5. [🚀 Démarrage Rapide](#DmarrageRapide)
	* 5.1. [Pré-requis](#Pr-requis)
	* 5.2. [Installation des dépendances](#Installationdesdpendances)
	* 5.3. [Configuration](#Configuration)
	* 5.4. [Exécution](#Excution)
* 6. [📊 Résultats](#Rsultats)
* 7. [État du projet](#8.Etatduprojet)

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

| Technologie    | Rôle                                         |
| -------------- | -------------------------------------------- |
| **LangChain**  | Orchestration d'agents et chaînage d'outils  |
| **Claude API** | Modèle LLM pour l'analyse et génération      |
| **ChromaDB**   | Vector store pour la recherche sémantique    |
| **DeepChain**  | Agent autonome avec planification long-terme |
| **LangSmith**  | Tracing et debugging des agents              |

##  3. <a name='StructureduProjet'></a>📁 Structure du Projet

```
.
├── notebooks/
│   └── deepchain-terraform-assistant.ipynb      # Notebook principal (agent orchestration)
├── docs/                                        # Bonnes pratiques Terraform
│   ├── structure.md
│   └── cloud-storage.md
├── prompts/
│   ├── terraform-system.md
│   ├── terraform-user.md
│   ├── terraform-review.md
│   ├── terraform-evaluation.md
│   └── terraform-validate.md
├── .vectorstore2/                               # Base de données ChromaDB
├── work/                                        # Résultats de la génération
├── .env                                         # Configuration (API keys, ...)
└── pyproject.toml                               # Configuration du projet python
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

###  5.1. <a name='Pr-requis'></a>Pré-requis 
- **Plugin VS Code Jupyter** : nécessaire pour exécuter les notebooks interactivement
- **Python 3.14+** : version cible du projet (configurée dans `.python-version`)

###  5.2. <a name='Installationdesdpendances'></a>Installation des dépendances

```bash
uv sync
```

###  5.3. <a name='Configuration'></a>Configuration

Créer un fichier `.env` avec :
```bash
ANTHROPIC_API_KEY=sk-...
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv_...
LANGCHAIN_PROJECT=terraform-agent
```

###  5.4. <a name='Excution'></a>Exécution
1. Ouvrir `notebooks/deepchain-terraform-assistant.ipynb` dans VS Code
2. Exécuter les cellules du notebook
3. Consulter les résultats dans le notebook et dans le répertoire `./work/`

##  6. <a name='Rsultats'></a>📊 Résultats

Après exécution, le notebook génère :
- **Fichiers** : sauvegardés dans `./work/` avec timestamps

##  8. <a name='8.Etatduprojet'></a>État du projet

Le projet est en phase de développement `actif`. 

Le composant de validation basé LLM (judge-as-llm) est actuellement en cours de développement et de stabilisation pour améliorer la qualité de l'agent.