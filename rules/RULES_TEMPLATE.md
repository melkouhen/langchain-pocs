# Template Règle Terraform

Dupliquez ce fichier et remplissez chaque section. Consultez `RULES_FORMAT.md` pour la documentation complète du format.

```xml
# Renommez ce fichier en: rules-{PREFIX}-{DOMAIN}.md
# Exemple: rules-gcs-logging.md, rules-tf-backend-config.md

<rule id="XXX-TYPE-001" severity="CRITICAL" category="Architecture|Security|State Management|Code Quality|Operations">
<title>Titre court et explicite (< 80 caractères)</title>

<description>
Description détaillée du problème. 
Expliquez pourquoi c'est important et quel impact cela a.
3-4 phrases maximum.
</description>

<context>
Module: terraform-module-name
Version: ~> X.Y
Provider Required: >= X.Y.Z
Other Context: relevant details
</context>

<problem>
Statement of the specific problem.
What goes wrong if this rule is violated?
Why is this a blocker?
</problem>

<pattern id="correct">
<title>✅ Correct Pattern</title>
<explanation>Explanation of what makes this correct</explanation>

```hcl
# Example of correct code
resource "type" "name" {
  correct_setting = "value"
}
```
</pattern>

<pattern id="correct-alternative">
<title>✅ Alternative Correct Pattern</title>
<explanation>If multiple valid approaches exist, document each</explanation>

```hcl
# Example of alternative correct code
resource "type" "name" {
  alternative_setting = "value"
}
```
</pattern>

<antipattern id="incorrect">
<title>❌ Common Mistake</title>
<explanation>What makes this incorrect</explanation>

```hcl
# Example of incorrect code
resource "type" "name" {
  wrong_setting = "bad_value"  # ❌ WRONG: explanation
}
```

<result>What happens when this mistake occurs: Error message or behavior</result>
</antipattern>

<antipattern id="incorrect-2">
<title>❌ Another Common Mistake</title>
<explanation>If multiple common mistakes exist, document each</explanation>

```hcl
# Another example of incorrect code
```

<result>Resulting error or failure</result>
</antipattern>

<why>
Explanation of root cause and consequences.

**Root Cause:** 
Why does this problem exist? Technical explanation.

**Consequence:** 
What fails when this rule is violated?
- First failure mode
- Second failure mode
- Third failure mode

**Prevention:** 
How to prevent this issue going forward?
Best practice or pattern to follow.
</why>

<validation>
<step number="1">Step to validate (e.g., terraform init)</step>
<step number="2">Another validation step (e.g., terraform validate)</step>
<step number="3">Additional checks if needed (e.g., terraform plan)</step>
<result-expected>✓ What successful validation looks like</result-expected>
<result-failure>✗ What failure looks like</result-failure>
</validation>

<when-to-apply>
**Apply this rule WHENEVER:**
- Condition 1
- Condition 2
- Condition 3

**DO NOT apply if:**
- Exclusion condition 1
- Exclusion condition 2
- Exception or special case

**Context-Dependent:**
If there are nuances, explain them here.
</when-to-apply>

<implementation-checklist>
- [ ] Understand the problem (read this rule completely)
- [ ] Identify violations in your code
- [ ] Review the correct pattern
- [ ] Apply the fix
- [ ] Run validation step 1
- [ ] Run validation step 2
- [ ] Verify expected result
- [ ] Document any non-obvious choices
- [ ] Add comments referencing rule ID (OPTIONAL: Rule-XXX-YYY-NNN)
</implementation-checklist>

<related-rules>
- XXX-TYPE-002: Related rule title
- YYY-TYPE-001: Another related rule
- ZZZ-TYPE-003: Third related rule (if applicable)
</related-rules>

<references>
- Documentation Link: https://example.com/docs
- Terraform Registry: https://registry.terraform.io/...
- GitHub Issue: https://github.com/...
- RFC/Design Doc: link if applicable
- Date Discovered: YYYY-MM-DD
- Status: Validated in production / Proposed / Experimental
- Last Updated: YYYY-MM-DD
</references>

</rule>
```

---

## Instructions de Remplissage

### 1. Nommage et Métadonnées
- Remplacez `XXX-TYPE-001` par un ID unique suivant la convention
- Choisissez la sévérité: `CRITICAL`, `MAJOR`, ou `MINOR`
- Sélectionnez une catégorie: `Compatibility`, `Security`, `Performance`, etc.
- Renommez le fichier: `rules-PREFIX-DOMAIN.md`

### 2. Contenu Minimal
Au minimum, complétez:
- `<title>` — Une phrase claire
- `<description>` — 3-4 lignes expliquant le problème
- `<problem>` — Énoncé concis du problème
- `<pattern id="correct">` — Au moins un bon exemple
- `<antipattern id="incorrect">` — Au moins un mauvais exemple
- `<when-to-apply>` — Quand utiliser cette règle

### 3. Contenu Recommandé
Ajoutez pour plus de clarté:
- `<context>` — Versions, modules, configurations applicables
- `<why>` — Racine cause et conséquences
- `<validation>` — Étapes pour vérifier la conformité
- `<implementation-checklist>` — Étapes concrètes de correction

### 4. Contenu Optionnel
Selon la complexité:
- Multiples `<pattern>` pour variantes correctes
- Multiples `<antipattern>` pour erreurs courantes
- `<related-rules>` — Connexions à d'autres règles
- `<references>` — Documentation externe, dates, statut

---

## Conseils de Rédaction

✅ **À faire:**
- Soyez concis mais complet
- Utilisez des exemples réels
- Expliquez le "pourquoi", pas juste le "quoi"
- Testez vos exemples de code (ils doivent être exécutables)
- Rendez chaque section utile et non-vide

❌ **À éviter:**
- Texte trop long ou redondant
- Exemples fictifs ou irréalistes
- Jargon sans explication
- Règles trop vagues ou générales
- Sections vides ou "TODO"

---

## Exemple: Règle Complétée

Voir les fichiers `rules-*.md` existants pour des exemples complets:
- `rules-gcs-providers.md` — Exemple de sévérité CRITICAL
- `rules-tf-naming-state.md` — Exemple de sévérité MAJOR avec multiples patterns
- `rules-tf-security-cicd.md` — Exemple de domaine complexe

---

## Intégration dans le Projet

1. Complétez ce template
2. Renommez: `rules-{PREFIX}-{DOMAIN}.md`
3. Vérifiez la structure XML (pas d'erreurs de balise)
4. Testez les exemples de code
5. Committez dans `rules/`
6. L'agent indexera automatiquement à la prochaine exécution

---

**Prêt?** Dupliquez ce fichier et commencez à documenter vos règles!
