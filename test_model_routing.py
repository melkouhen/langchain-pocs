#!/usr/bin/env python3
"""Test script for model routing functionality.

Tests:
1. ModelRouter initialization
2. Ollama availability check
3. Model selection (Ollama vs Claude)
4. Fallback behavior
5. Knowledge base summarization
6. Terraform error parsing
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from terraform_agent.config import Config
from terraform_agent.model_router import ModelRouter


def test_model_router_init():
    """Test ModelRouter initialization."""
    print("\n🧪 Test 1: ModelRouter Initialization")
    print("=" * 60)

    config = Config()
    router = ModelRouter(
        use_ollama_for=config.USE_OLLAMA_FOR,
        ollama_models=config.OLLAMA_MODELS,
        claude_model=config.AGENT_MODEL,
    )

    print(f"✓ Router initialized")
    print(f"  - Use Ollama for: {config.USE_OLLAMA_FOR}")
    print(f"  - Ollama models: {config.OLLAMA_MODELS}")
    print(f"  - Claude fallback: {config.AGENT_MODEL}")


def test_ollama_availability():
    """Test Ollama availability check."""
    print("\n🧪 Test 2: Ollama Availability Check")
    print("=" * 60)

    config = Config()
    router = ModelRouter(
        use_ollama_for={"summarization"},
        ollama_models=config.OLLAMA_MODELS,
        claude_model=config.AGENT_MODEL,
    )

    available = router._check_ollama_available()
    if available:
        print("✓ Ollama is available at http://localhost:11434")
    else:
        print("⚠️  Ollama is NOT available")
        print("   Start with: ollama serve")


def test_model_selection():
    """Test model selection for different task types."""
    print("\n🧪 Test 3: Model Selection")
    print("=" * 60)

    config = Config()

    # Test with Ollama enabled
    print("\n📌 Scenario A: Ollama enabled for all tasks")
    config.USE_OLLAMA_FOR = {"summarization", "parsing", "review"}
    router = ModelRouter(
        use_ollama_for=config.USE_OLLAMA_FOR,
        ollama_models=config.OLLAMA_MODELS,
        claude_model=config.AGENT_MODEL,
    )

    for task in ["summarization", "parsing", "review"]:
        model = router.get_model(task)
        print(f"  - {task}: {type(model).__name__} ({getattr(model, 'model', config.AGENT_MODEL)})")

    # Test with Ollama disabled
    print("\n📌 Scenario B: Ollama disabled (all Claude)")
    config.USE_OLLAMA_FOR = set()
    router = ModelRouter(
        use_ollama_for=config.USE_OLLAMA_FOR,
        ollama_models=config.OLLAMA_MODELS,
        claude_model=config.AGENT_MODEL,
    )

    for task in ["summarization", "parsing", "review"]:
        model = router.get_model(task)
        print(f"  - {task}: {type(model).__name__} ({getattr(model, 'model', config.AGENT_MODEL)})")


def test_summarization():
    """Test knowledge base summarization."""
    print("\n🧪 Test 4: Knowledge Base Summarization")
    print("=" * 60)

    config = Config()
    router = ModelRouter(
        use_ollama_for={"summarization"},
        ollama_models=config.OLLAMA_MODELS,
        claude_model=config.AGENT_MODEL,
    )

    sample_text = """
    Terraform best practice 1: Use version constraints for providers.
    Terraform best practice 2: Enable versioning on state backends.
    Terraform best practice 3: Use remote state for team collaboration.
    Terraform best practice 4: Never hardcode secrets in .tf files.
    Terraform best practice 5: Use workspaces or separate folders for environments.
    """

    prompt = f"""Summarize these Terraform best practices in 2-3 sentences:

{sample_text}

Summary:"""

    try:
        print("  - Invoking summarization model...")
        summary = router.invoke("summarization", prompt)
        print(f"  ✓ Original: {len(sample_text)} chars")
        print(f"  ✓ Summary: {len(summary)} chars")
        print(f"\n  📝 Result:\n{summary[:200]}...")
    except Exception as e:
        print(f"  ❌ Summarization failed: {e}")


def test_error_parsing():
    """Test terraform error parsing."""
    print("\n🧪 Test 5: Terraform Error Parsing")
    print("=" * 60)

    config = Config()
    router = ModelRouter(
        use_ollama_for={"parsing"},
        ollama_models=config.OLLAMA_MODELS,
        claude_model=config.AGENT_MODEL,
    )

    sample_error = """
Error: Invalid resource name

  on main.tf line 12, in resource "google_storage_bucket" "example":
  12:   name = "My_Invalid_Bucket_Name"

Bucket names must contain only lowercase letters, numbers, and hyphens.
    """

    prompt = f"""Parse this Terraform error and provide:
1. Error type
2. Root cause
3. Suggested fix

Error:
{sample_error}

Parsed error:"""

    try:
        print("  - Invoking parsing model...")
        parsed = router.invoke("parsing", prompt)
        print(f"  ✓ Original: {len(sample_error)} chars")
        print(f"  ✓ Parsed: {len(parsed)} chars")
        print(f"\n  📝 Result:\n{parsed[:300]}...")
    except Exception as e:
        print(f"  ❌ Parsing failed: {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  MODEL ROUTING TEST SUITE")
    print("=" * 60)

    # Check environment
    print("\n📋 Environment:")
    print(f"  - USE_OLLAMA_FOR: {os.getenv('USE_OLLAMA_FOR', 'summarization,parsing,review')}")
    print(f"  - OLLAMA_SUMMARY_MODEL: {os.getenv('OLLAMA_SUMMARY_MODEL', 'qwen3.5:9b')}")
    print(f"  - OLLAMA_PARSE_MODEL: {os.getenv('OLLAMA_PARSE_MODEL', 'qwen2.5-coder:7b-instruct')}")

    test_model_router_init()
    test_ollama_availability()
    test_model_selection()
    test_summarization()
    test_error_parsing()

    print("\n" + "=" * 60)
    print("  ✅ ALL TESTS COMPLETED")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("  1. Check logs above for any warnings")
    print("  2. Adjust .env configuration if needed")
    print("  3. Run full agent with: notebooks/deepchain_terraform_assistant.ipynb")
    print()


if __name__ == "__main__":
    main()
