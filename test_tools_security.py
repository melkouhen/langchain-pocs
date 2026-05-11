"""Tests de sécurité pour les correctifs tools.py

Valide que :
1. Les paths sont correctement validés (pas de traversal)
2. Les dépendances d'outils sont respectées
3. Les environnements sont vérifiés
"""

import tempfile
from pathlib import Path
import pytest

from terraform_agent.config import Config
from terraform_agent.prompts import PromptManager
from terraform_agent.knowledge_base import KnowledgeBase
from terraform_agent.tools import (
    init_tools,
    _validate_terraform_path,
    _check_dev_environment,
    _check_terraform_initialized,
    terraform_init,
    terraform_validate,
)


class TestPathValidation:
    """Tests de validation des paths."""

    def setup_method(self):
        """Setup pour chaque test."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config(base_dir=Path(self.temp_dir))
        self.config.WORK_DIR = Path(self.temp_dir) / "work"
        self.config.WORK_DIR.mkdir(parents=True, exist_ok=True)

        # Mock minimal pour init_tools
        self.prompts = PromptManager(self.config)

        # Ne pas initialiser vraiment ChromaDB (trop lourd pour tests)
        # On teste juste la logique de validation

    def test_validate_path_inside_work_dir(self):
        """✅ Path valide dans work_dir doit être accepté."""
        from terraform_agent.tools import init_tools, _config

        # Mini init sans KnowledgeBase
        import terraform_agent.tools as tools_module
        tools_module._config = self.config

        valid_path = self.config.WORK_DIR / "envs" / "dev"
        valid_path.mkdir(parents=True, exist_ok=True)

        result = _validate_terraform_path(str(valid_path))
        assert result.is_relative_to(self.config.WORK_DIR)

    def test_validate_path_outside_work_dir_fails(self):
        """❌ Path en dehors de work_dir doit être rejeté."""
        import terraform_agent.tools as tools_module
        tools_module._config = self.config

        # Tenter d'accéder au répertoire parent
        malicious_path = self.config.WORK_DIR / ".." / ".." / "etc"

        with pytest.raises(ValueError, match="Path outside work directory"):
            _validate_terraform_path(str(malicious_path))

    def test_validate_path_absolute_outside_fails(self):
        """❌ Path absolu en dehors doit être rejeté."""
        import terraform_agent.tools as tools_module
        tools_module._config = self.config

        with pytest.raises(ValueError, match="Path outside work directory"):
            _validate_terraform_path("/etc/passwd")


class TestEnvironmentChecks:
    """Tests de vérification d'environnement."""

    def test_dev_environment_allowed(self):
        """✅ Environnement dev doit être autorisé."""
        assert _check_dev_environment("/path/to/envs/dev") is None
        assert _check_dev_environment("/path/to/dev/main.tf") is None

    def test_prod_environment_blocked(self):
        """❌ Environnement prod doit être bloqué."""
        error = _check_dev_environment("/path/to/envs/prod")
        assert error is not None
        assert "only allowed in dev" in error.lower()

    def test_unknown_environment_blocked(self):
        """❌ Environnement inconnu doit être bloqué."""
        error = _check_dev_environment("/path/to/random")
        assert error is not None


class TestTerraformInitDependency:
    """Tests de dépendance terraform init."""

    def test_initialized_directory_passes(self):
        """✅ Répertoire initialisé doit passer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            terraform_dir = Path(tmpdir) / ".terraform"
            terraform_dir.mkdir()

            assert _check_terraform_initialized(tmpdir) is None

    def test_uninitialized_directory_fails(self):
        """❌ Répertoire non initialisé doit échouer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            error = _check_terraform_initialized(tmpdir)
            assert error is not None
            assert "terraform_init first" in error


class TestToolsIntegration:
    """Tests d'intégration des correctifs dans les tools."""

    def setup_method(self):
        """Setup pour tests d'intégration."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = Config(base_dir=Path(self.temp_dir))
        self.config.WORK_DIR = Path(self.temp_dir) / "work"
        self.config.WORK_DIR.mkdir(parents=True, exist_ok=True)

        import terraform_agent.tools as tools_module
        tools_module._config = self.config

    def test_terraform_init_validates_path(self):
        """terraform_init doit valider le path."""
        # Path en dehors de work_dir
        result = terraform_init("/etc/passwd")
        assert "ERROR" in result
        assert "Path outside" in result or "Invalid path" in result

    def test_terraform_init_checks_environment(self):
        """terraform_init doit vérifier l'environnement."""
        # Créer un path prod valide
        prod_path = self.config.WORK_DIR / "envs" / "prod"
        prod_path.mkdir(parents=True, exist_ok=True)

        result = terraform_init(str(prod_path))
        assert "ERROR" in result
        assert "dev environment" in result

    def test_terraform_validate_checks_init(self):
        """terraform_validate doit vérifier que init a été exécuté."""
        # Créer un path dev valide mais non initialisé
        dev_path = self.config.WORK_DIR / "envs" / "dev"
        dev_path.mkdir(parents=True, exist_ok=True)

        result = terraform_validate(str(dev_path))
        assert "ERROR" in result
        assert "terraform_init first" in result


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
