"""
NeuroLoom RE Pipeline - Core Constants

This module contains all NeuroLoom system constants used across the RE Pipeline.
All constants are sourced from NEUROLOOM_UNIFIED_ARCHITECTURE_v2.md and must be
used instead of magic numbers throughout the codebase.
"""

# =============================================================================
# CACHE & PERFORMANCE CONSTANTS
# =============================================================================

H_CACHE_HIT_RATE: float = 0.9995
"""99.95% cache hit rate target for zero-energy retrieval."""

R_RECYCLE_RATE: float = 0.87
"""87% thermodynamic recycle rate (locked constant)."""

# =============================================================================
# COHERENCE & SAFETY CONSTANTS
# =============================================================================

OMEGA_FLOOR: float = 0.999999
"""Six nines coherence floor from L0 Constitution."""

OMEGA_RED_LOOM: float = 0.90
"""Red Loom trigger threshold (Omega < 0.90)."""

OMEGA_SNP: float = 0.85
"""SNP (Singularity Negotiation Protocol) trigger threshold (Omega < 0.85)."""

OMEGA_SEVERANCE: float = 0.80
"""Hardware severance trigger threshold (Omega < 0.80)."""

# =============================================================================
# DNA FUSION & MUTATION CONSTANTS
# =============================================================================

S_ISO_FUSION_THRESHOLD: float = 0.87
"""Cross-pod DNA fusion threshold (S_iso > 0.87)."""

S_ISO_ELEVATED_THRESHOLD: float = 0.89
"""Elevated S_iso threshold for RE Pipeline."""

# =============================================================================
# GHOST ENGINE CONSTANTS
# =============================================================================

GHOST_COLLAPSE_THRESHOLD: float = 0.9999
"""Ghost Engine collapse threshold."""

GHOST_LEAKAGE_EXPONENT: int = 5
"""Leakage scaling exponent for Ghost Engine."""

# =============================================================================
# HNSW INDEXING CONSTANTS
# =============================================================================

HNSW_DIM: int = 384
"""Standard embedding dimension for pattern vectors."""

HNSW_M: int = 32
"""HNSW M parameter (number of bi-directional links)."""

HNSW_EF_CONSTRUCTION: int = 200
"""HNSW ef_construction parameter for index building."""

HNSW_EF_SEARCH: int = 100
"""HNSW ef_search parameter for queries."""

HNSW_MAX_ELEMENTS: int = 1_000_000
"""Maximum number of elements in HNSW index."""

HNSW_TARGET_HIT_RATE: float = 0.9995
"""Target hit rate for HNSW index (99.95%)."""

# =============================================================================
# HMV (HOLOGRAPHIC MERKLE VECTOR) ENCODING CONSTANTS
# =============================================================================

HMV_TOTAL_SIZE: int = 1_048_576
"""Total HMV payload size: 1MB (1,048,576 bytes)."""

HMV_HEADER_SIZE: int = 64
"""HMV header size: 64 bytes."""

HMV_HOLOGRAPHIC_SIZE: int = 393_216
"""Holographic layer size: 384KB."""

HMV_MERKLE_SIZE: int = 524_288
"""Merkle tree size: 512KB."""

HMV_BLOOM_SIZE: int = 131_072
"""Bloom filter size: 128KB."""

HMV_SENTINEL_VALUE: int = 0xDEADBEEF
"""Sentinel value for HMV payload validation."""

# =============================================================================
# LATENCY CONSTANTS
# =============================================================================

WARP_LATENCY_US: float = 326.0
"""End-to-end pipeline latency: 326 microseconds."""

ATMOSPHERE_BREATH_US: float = 0.025
"""Atmosphere breath latency: 0.025 microseconds."""

CANVAS_VAULT_LATENCY_MS: int = 100
"""Canvas Vault L4 storage latency: 100ms."""

# =============================================================================
# GOVERNANCE CONSTANTS
# =============================================================================

GOVERNANCE_QUORUM_MAJORITY: float = 0.8
"""Majority quorum threshold (80% required)."""

GOVERNANCE_QUORUM_SUPERMAJORITY: float = 0.9
"""Supermajority quorum threshold (90% required)."""

GOVERNANCE_SNP_VETO_WEIGHT: int = 5
"""Weight of SNP veto in governance decisions."""

GOVERNANCE_SAFETY_OFFICER_VETO_WEIGHT: int = 3
"""Weight of Safety Officer veto in governance decisions."""

# =============================================================================
# MUTATION CONSTANTS
# =============================================================================

MUTATION_RATE_MAX_PER_HOUR: int = 100
"""Maximum mutations per hour."""

MUTATION_RATE_MAX_PER_DAY: int = 1000
"""Maximum mutations per day."""

MUTATION_BETA_1_MAX_NORMAL: int = 100
"""Maximum Betti number beta_1 for normal operations."""

MUTATION_BETA_1_MAX_RE: int = 150
"""Maximum Betti number beta_1 for RE Pipeline operations."""

FUSION_MAX_PER_HOUR: int = 20
"""Maximum DNA fusions per hour."""

# =============================================================================
# PID CONTROLLER CONSTANTS
# =============================================================================

PID_KP_DEFAULT: float = 1.0
"""Default proportional gain for PID controller."""

PID_KI_DEFAULT: float = 0.1
"""Default integral gain for PID controller."""

PID_KD_DEFAULT: float = 0.05
"""Default derivative gain for PID controller."""

PID_MUTATION_RATE_MIN: float = 0.0
"""Minimum mutation rate output from PID controller."""

PID_MUTATION_RATE_MAX: float = 1.0
"""Maximum mutation rate output from PID controller."""

# =============================================================================
# LYAPUNOV SAFETY CONSTANTS
# =============================================================================

LYAPUNOV_CRITICAL: float = 0.05
"""Critical Lyapunov exponent threshold."""

LYAPUNOV_KILL: float = 0.5
"""Kill switch Lyapunov threshold."""

# =============================================================================
# GDO META-FITNESS WEIGHTS
# =============================================================================

GDO_WEIGHT_OMEGA: float = 0.4
"""Weight of Omega coherence in V_GDO calculation."""

GDO_WEIGHT_DNA: float = 0.3
"""Weight of DNA fitness in V_GDO calculation."""

GDO_WEIGHT_S_ISO: float = 0.2
"""Weight of semantic isomorphism in V_GDO calculation."""

GDO_WEIGHT_DELTA_C: float = 0.1
"""Weight of coherence delta in V_GDO calculation."""

# =============================================================================
# FED_SYNC_V1 CONSTANTS
# =============================================================================

FED_SYNC_VERSION: str = "V1"
"""FED_SYNC protocol version."""

FED_SYNC_VECTOR_DIM: int = 384
"""FED_SYNC vector dimension (matches HNSW_DIM)."""

FED_SYNC_ZKP_ANNIHILATION_ROUNDS: int = 3
"""Number of ZKP annihilation rounds for vector distillation."""

FED_SYNC_POU_MIN_GAIN_DELTA: float = 0.01
"""Minimum gain delta for PoU attestation (1% improvement required)."""

# =============================================================================
# CANVAS VAULT CONSTANTS
# =============================================================================

CANVAS_VAULT_MAX_CRYSTALS: int = 10000
"""Maximum number of immortal crystals in Canvas Vault."""

CANVAS_VAULT_HIT_RATE: float = 0.9997
"""Canvas Vault immortal storage hit rate (99.97%)."""

# =============================================================================
# ADVERSARIAL PREDICTION MARKETS CONSTANTS
# =============================================================================

MARKET_VIRTUAL_ANALYSTS: int = 1000
"""Number of virtual analysts in prediction markets."""

MARKET_DECISION_ACCURACY_TARGET: float = 0.99999
"""Target decision accuracy (99.999%) for prediction markets."""

# =============================================================================
# SYSTEM METRICS
# =============================================================================

MAX_CONCURRENT_AGENTS: int = 500_000
"""Maximum concurrent agents supported."""

THROUGHPUT_OPS_PER_SEC: int = 28_400_000
"""System throughput: 28.4M operations per second."""

AVAILABILITY: float = 0.999999
"""Six nines availability."""

COORDINATION_EFFICIENCY: float = 0.99999999
"""Eight nines coordination efficiency."""

FAULT_TOLERANCE_F_MAX: float = 0.333
"""Byzantine fault tolerance: f < n/3."""

# =============================================================================
# VERSION & METADATA
# =============================================================================

__version__: str = "1.0.0"
"""NeuroLoom RE Pipeline version."""

ARCHITECTURE_VERSION: str = "v2.0"
"""NeuroLoom Unified Architecture version."""

DOMAIN_ID: int = 9
"""RE Pipeline is Domain 9."""
