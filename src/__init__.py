"""
NeuroLoom RE Pipeline - Domain 9

The Reverse Engineering Pipeline is Domain 9 of the NeuroLoom ecosystem.
It enables technology hydration by analyzing external systems and extracting
patterns that can be applied across all 8 existing domains.

Stages:
1. DECONSTRUCT - Analyze codebases, binaries, firmware, APIs
2. PATTERN_DISTILL - Extract and index optimization vectors
3. MUTATE - Cross-pod DNA fusion and optimization
4. REBUILD - Validate and deploy improved patterns

Architecture follows the 7-layer command hierarchy:
- L0: Constitution (immutable law)
- L1-L3: Orchestration (Queen, Managers, Swarms)
- L4: Specialist Agents
- L5: Microswarms (immune system)
- L6: Atomic Layer (stateless functions)
"""

__version__ = "1.0.0"
__domain_id__ = 9
__domain_name__ = "RE Pipeline"

from . import atomic_layer
from . import config
from . import decon
from . import distill
from . import mutate
from . import rebuild
from . import governance
from . import hmv

__all__ = [
    "atomic_layer",
    "config",
    "decon",
    "distill",
    "mutate",
    "rebuild",
    "governance",
    "hmv",
]
