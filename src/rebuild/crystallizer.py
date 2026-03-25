"""
NeuroLoom RE Pipeline - Stage 4: DNA Crystallizer

Validates and crystallizes mutated DNA sequences from Stage 3 into stable
immutable crystal form for deployment across the NeuroLoom federation.
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

# Thresholds sourced from config.constants (inlined to avoid cross-package import complexity)
_OMEGA_FLOOR: float = 0.999999  # Six nines coherence floor (config.OMEGA_FLOOR)
_BETA_1_MAX_RE: float = 150.0   # Max Betti beta_1 for RE Pipeline (config.MUTATION_BETA_1_MAX_RE)


class CrystalStatus(Enum):
    """Status of a crystallized DNA sequence."""

    PENDING = "pending"
    VALID = "valid"
    REJECTED = "rejected"
    CRYSTALLIZED = "crystallized"


@dataclass
class ValidationResult:
    """Result of DNA sequence validation."""

    dna_id: str
    omega_ok: bool
    beta_ok: bool
    chrono_sync_ok: bool
    passed: bool
    reason: str


@dataclass
class CrystalizedDNA:
    """An immutable crystallized DNA record."""

    crystal_id: str
    dna_id: str
    cluster_id: str
    original_vector_ids: list[str]
    crystallized_sequence_hash: str
    omega: float
    beta_1: float
    pid_rate: float
    chrono_epoch: int
    status: CrystalStatus
    crystallized_at: float = field(default_factory=time.time)
    version: str = "4.0.0"


class DNACrystallizer:
    """
    Stage 4 DNA Crystallizer.

    Validates mutated DNA sequences from Stage 3 and crystallizes
    passing sequences into stable, immutable records.
    """

    OMEGA_THRESHOLD: float = _OMEGA_FLOOR
    BETA_THRESHOLD: float = _BETA_1_MAX_RE

    def __init__(self) -> None:
        self._crystals: list[CrystalizedDNA] = []
        self._validation_log: list[ValidationResult] = []

    def validate(self, dna_record: dict[str, Any]) -> ValidationResult:
        """Validate a single DNA record against safety thresholds."""
        dna_id = dna_record.get("dna_id", "unknown")
        safety = dna_record.get("safety_metrics", {})
        chrono = dna_record.get("chrono_sync", {})

        omega = float(safety.get("omega", 0.0))
        beta_1 = float(safety.get("beta_1", float("inf")))
        sync_verified = bool(chrono.get("sync_verified", False))

        omega_ok = omega >= self.OMEGA_THRESHOLD
        beta_ok = beta_1 <= self.BETA_THRESHOLD
        chrono_ok = sync_verified

        passed = omega_ok and beta_ok and chrono_ok

        if passed:
            reason = "All gates passed"
        else:
            reasons = []
            if not omega_ok:
                reasons.append(f"Omega {omega:.6f} < {self.OMEGA_THRESHOLD:.6f}")
            if not beta_ok:
                reasons.append(f"Beta_1 {beta_1:.2f} > {self.BETA_THRESHOLD:.2f}")
            if not chrono_ok:
                reasons.append("CHRONO_SYNC not verified")
            reason = "; ".join(reasons)

        result = ValidationResult(
            dna_id=dna_id,
            omega_ok=omega_ok,
            beta_ok=beta_ok,
            chrono_sync_ok=chrono_ok,
            passed=passed,
            reason=reason,
        )
        self._validation_log.append(result)
        return result

    def crystallize(self, dna_record: dict[str, Any]) -> tuple[CrystalizedDNA | None, ValidationResult]:
        """Validate and crystallize a single DNA record."""
        validation = self.validate(dna_record)
        if not validation.passed:
            return None, validation

        dna_id = dna_record.get("dna_id", "unknown")
        cluster_id = dna_record.get("cluster_id", "unknown")
        original_vector_ids: list[str] = dna_record.get("original_vector_ids", [])
        safety = dna_record.get("safety_metrics", {})
        chrono = dna_record.get("chrono_sync", {})
        pid_params = dna_record.get("pid_params", {})

        omega = float(safety.get("omega", 0.0))
        beta_1 = float(safety.get("beta_1", 0.0))
        pid_rate = float(pid_params.get("applied_rate", 0.5))
        chrono_epoch = int(chrono.get("current_epoch", 0))

        sequence_hash = self._compute_crystal_hash(dna_record)
        crystal_id = f"CRYSTAL_{dna_id}_{sequence_hash[:8]}"

        crystal = CrystalizedDNA(
            crystal_id=crystal_id,
            dna_id=dna_id,
            cluster_id=cluster_id,
            original_vector_ids=original_vector_ids,
            crystallized_sequence_hash=sequence_hash,
            omega=omega,
            beta_1=beta_1,
            pid_rate=pid_rate,
            chrono_epoch=chrono_epoch,
            status=CrystalStatus.CRYSTALLIZED,
        )
        self._crystals.append(crystal)
        return crystal, validation

    def crystallize_batch(
        self, dna_records: list[dict[str, Any]]
    ) -> tuple[list[CrystalizedDNA], list[ValidationResult]]:
        """Validate and crystallize a batch of DNA records."""
        crystals: list[CrystalizedDNA] = []
        validations: list[ValidationResult] = []
        for record in dna_records:
            crystal, validation = self.crystallize(record)
            validations.append(validation)
            if crystal is not None:
                crystals.append(crystal)
        return crystals, validations

    def load_and_crystallize(self, mutated_dna_path: str) -> dict[str, Any]:
        """Load mutated DNA JSON from Stage 3 and crystallize all sequences."""
        with open(mutated_dna_path, encoding="utf-8") as f:
            stage3_data: dict[str, Any] = json.load(f)

        dna_records: list[dict[str, Any]] = stage3_data.get("mutated_dnas", [])
        crystals, validations = self.crystallize_batch(dna_records)

        passed = [v for v in validations if v.passed]
        failed = [v for v in validations if not v.passed]

        return {
            "stage": 4,
            "pipeline_version": "4.0.0",
            "source_execution_id": stage3_data.get("execution_id", "unknown"),
            "crystallization_timestamp": time.time(),
            "input_dna_count": len(dna_records),
            "crystallized_count": len(crystals),
            "rejected_count": len(failed),
            "pass_rate": len(passed) / max(len(validations), 1),
            "crystals": [self._crystal_to_dict(c) for c in crystals],
            "validation_log": [
                {
                    "dna_id": v.dna_id,
                    "passed": v.passed,
                    "reason": v.reason,
                }
                for v in validations
            ],
        }

    def get_crystals(self) -> list[CrystalizedDNA]:
        """Return all crystallized DNA records."""
        return list(self._crystals)

    def get_validation_log(self) -> list[ValidationResult]:
        """Return all validation results."""
        return list(self._validation_log)

    def get_stats(self) -> dict[str, Any]:
        """Return crystallization statistics."""
        total = len(self._validation_log)
        passed = sum(1 for v in self._validation_log if v.passed)
        return {
            "total_validated": total,
            "passed": passed,
            "rejected": total - passed,
            "pass_rate": passed / max(total, 1),
            "crystals": len(self._crystals),
        }

    @staticmethod
    def _compute_crystal_hash(dna_record: dict[str, Any]) -> str:
        """Compute a deterministic hash for the crystal record."""
        payload = json.dumps(dna_record, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    def _crystal_to_dict(crystal: CrystalizedDNA) -> dict[str, Any]:
        """Serialize a CrystalizedDNA to a plain dict."""
        d = asdict(crystal)
        d["status"] = crystal.status.value
        return d
