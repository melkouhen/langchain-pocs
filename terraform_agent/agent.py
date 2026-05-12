"""Backward compatibility module.

This module provides backward compatibility for code using the old TerraformAgent name.
The class has been renamed to TerraformGenerator for better semantic clarity.

Deprecated:
    TerraformAgent: Use TerraformGenerator instead
"""

import warnings
from .generator import TerraformGenerator


class TerraformAgent(TerraformGenerator):
    """Deprecated: Use TerraformGenerator instead.

    This is a compatibility alias that will be removed in a future version.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "TerraformAgent is deprecated and will be removed in a future version. "
            "Use TerraformGenerator instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)


__all__ = ["TerraformAgent"]
