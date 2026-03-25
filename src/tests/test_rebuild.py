"""Tests for the Stage 4 DNA Crystallizer module."""

import json
import os
import tempfile
from typing import Any

import pytest

from rebuild.crystallizer import (
    CrystalizedDNA,
    CrystalStatus,
    DNACrystallizer,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_dna_record(
    dna_id: str = "DNA_000001_abc12345",
    cluster_id: str = "cluster_1_2",
    omega: float = 0.999999,
    beta_1: float = 0.0,
    sync_verified: bool = True,
    applied_rate: float = 0.5,
    current_epoch: int = 492882,
) -> dict[str, Any]:
    return {
        "dna_id": dna_id,
        "cluster_id": cluster_id,
        "original_vector_ids": [f"parent_{dna_id}"],
        "pid_params": {
            "Kp": 1.0,
            "Ki": 0.1,
            "Kd": 0.05,
            "applied_rate": applied_rate,
        },
        "chrono_sync": {
            "epoch_hash": "a" * 64,
            "alignment_score": 1.0,
            "current_epoch": current_epoch,
            "epoch_offset": 0,
            "sync_verified": sync_verified,
        },
        "safety_metrics": {
            "omega": omega,
            "beta_1": beta_1,
            "gates_passed": omega >= 0.999999 and beta_1 <= 150.0,
        },
    }


@pytest.fixture()
def crystallizer() -> DNACrystallizer:
    return DNACrystallizer()


@pytest.fixture()
def valid_record() -> dict[str, Any]:
    return _make_dna_record()


@pytest.fixture()
def stage3_json_file() -> str:
    """Write a minimal Stage 3 mutated_dna.json to a temp file."""
    data = {
        "pipeline_version": "3.0.0",
        "execution_id": "exec_1774381500",
        "mutated_dnas": [
            _make_dna_record("DNA_000001_2e7a9f3c", "cluster_1_2", applied_rate=0.99),
            _make_dna_record("DNA_000002_6a3f1e8b", "cluster_0_3", applied_rate=0.01),
            _make_dna_record("DNA_000003_8f4b2d6a", "cluster_1_2", applied_rate=0.5255),
        ],
    }
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(data, f)
        return f.name


# ---------------------------------------------------------------------------
# Validation tests
# ---------------------------------------------------------------------------


class TestValidation:
    def test_valid_record_passes(self, crystallizer: DNACrystallizer, valid_record: dict[str, Any]) -> None:
        result = crystallizer.validate(valid_record)
        assert result.passed is True
        assert result.omega_ok is True
        assert result.beta_ok is True
        assert result.chrono_sync_ok is True

    def test_low_omega_fails(self, crystallizer: DNACrystallizer) -> None:
        record = _make_dna_record(omega=0.5)
        result = crystallizer.validate(record)
        assert result.passed is False
        assert result.omega_ok is False

    def test_high_beta_fails(self, crystallizer: DNACrystallizer) -> None:
        record = _make_dna_record(beta_1=200.0)
        result = crystallizer.validate(record)
        assert result.passed is False
        assert result.beta_ok is False

    def test_chrono_sync_unverified_fails(self, crystallizer: DNACrystallizer) -> None:
        record = _make_dna_record(sync_verified=False)
        result = crystallizer.validate(record)
        assert result.passed is False
        assert result.chrono_sync_ok is False

    def test_validation_result_has_dna_id(self, crystallizer: DNACrystallizer, valid_record: dict[str, Any]) -> None:
        result = crystallizer.validate(valid_record)
        assert result.dna_id == valid_record["dna_id"]

    def test_failed_reason_not_empty(self, crystallizer: DNACrystallizer) -> None:
        record = _make_dna_record(omega=0.1, beta_1=999.0, sync_verified=False)
        result = crystallizer.validate(record)
        assert result.passed is False
        assert len(result.reason) > 0


# ---------------------------------------------------------------------------
# Crystallization tests
# ---------------------------------------------------------------------------


class TestCrystallization:
    def test_crystallize_valid_returns_crystal(
        self, crystallizer: DNACrystallizer, valid_record: dict[str, Any]
    ) -> None:
        crystal, validation = crystallizer.crystallize(valid_record)
        assert crystal is not None
        assert isinstance(crystal, CrystalizedDNA)
        assert crystal.status == CrystalStatus.CRYSTALLIZED

    def test_crystallize_invalid_returns_none(self, crystallizer: DNACrystallizer) -> None:
        record = _make_dna_record(omega=0.5)
        crystal, validation = crystallizer.crystallize(record)
        assert crystal is None
        assert validation.passed is False

    def test_crystal_id_contains_dna_id(
        self, crystallizer: DNACrystallizer, valid_record: dict[str, Any]
    ) -> None:
        crystal, _ = crystallizer.crystallize(valid_record)
        assert crystal is not None
        assert valid_record["dna_id"] in crystal.crystal_id

    def test_crystal_fields_match_record(
        self, crystallizer: DNACrystallizer, valid_record: dict[str, Any]
    ) -> None:
        crystal, _ = crystallizer.crystallize(valid_record)
        assert crystal is not None
        assert crystal.dna_id == valid_record["dna_id"]
        assert crystal.cluster_id == valid_record["cluster_id"]
        assert crystal.omega == valid_record["safety_metrics"]["omega"]
        assert crystal.beta_1 == valid_record["safety_metrics"]["beta_1"]

    def test_crystallize_batch(self, crystallizer: DNACrystallizer) -> None:
        records = [
            _make_dna_record("DNA_001_aabbccdd"),
            _make_dna_record("DNA_002_eeff0011", omega=0.1),  # should fail
            _make_dna_record("DNA_003_22334455"),
        ]
        crystals, validations = crystallizer.crystallize_batch(records)
        assert len(crystals) == 2
        assert len(validations) == 3
        assert sum(1 for v in validations if v.passed) == 2

    def test_get_crystals_accumulates(self, crystallizer: DNACrystallizer) -> None:
        crystallizer.crystallize(_make_dna_record("DNA_A_11223344"))
        crystallizer.crystallize(_make_dna_record("DNA_B_55667788"))
        assert len(crystallizer.get_crystals()) == 2

    def test_get_validation_log_accumulates(self, crystallizer: DNACrystallizer) -> None:
        crystallizer.validate(_make_dna_record("DNA_X_aabbccdd"))
        crystallizer.validate(_make_dna_record("DNA_Y_eeff0011"))
        assert len(crystallizer.get_validation_log()) == 2


# ---------------------------------------------------------------------------
# Stats tests
# ---------------------------------------------------------------------------


class TestStats:
    def test_stats_initial_empty(self, crystallizer: DNACrystallizer) -> None:
        stats = crystallizer.get_stats()
        assert stats["total_validated"] == 0
        assert stats["crystals"] == 0
        assert stats["pass_rate"] == 0.0  # no validations yet

    def test_stats_after_batch(self, crystallizer: DNACrystallizer) -> None:
        records = [_make_dna_record(f"DNA_{i:03d}_{'a'*8}") for i in range(5)]
        crystallizer.crystallize_batch(records)
        stats = crystallizer.get_stats()
        assert stats["total_validated"] == 5
        assert stats["passed"] == 5
        assert stats["rejected"] == 0
        assert stats["pass_rate"] == 1.0
        assert stats["crystals"] == 5


# ---------------------------------------------------------------------------
# load_and_crystallize tests
# ---------------------------------------------------------------------------


class TestLoadAndCrystallize:
    def test_load_crystallizes_all_valid(self, crystallizer: DNACrystallizer, stage3_json_file: str) -> None:
        try:
            result = crystallizer.load_and_crystallize(stage3_json_file)
            assert result["crystallized_count"] == 3
            assert result["rejected_count"] == 0
            assert result["pass_rate"] == 1.0
            assert result["stage"] == 4
            assert result["source_execution_id"] == "exec_1774381500"
        finally:
            os.unlink(stage3_json_file)

    def test_load_result_has_crystals(self, crystallizer: DNACrystallizer, stage3_json_file: str) -> None:
        try:
            result = crystallizer.load_and_crystallize(stage3_json_file)
            assert len(result["crystals"]) == 3
            for c in result["crystals"]:
                assert c["status"] == CrystalStatus.CRYSTALLIZED.value
        finally:
            os.unlink(stage3_json_file)

    def test_load_result_has_validation_log(
        self, crystallizer: DNACrystallizer, stage3_json_file: str
    ) -> None:
        try:
            result = crystallizer.load_and_crystallize(stage3_json_file)
            assert len(result["validation_log"]) == 3
            for entry in result["validation_log"]:
                assert entry["passed"] is True
        finally:
            os.unlink(stage3_json_file)
