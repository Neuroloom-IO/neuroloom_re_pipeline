"""Tests for the Stage 3 mutation engine module."""

import pytest

from mutate.mutation_engine import (
    CHRONOSyncHasher,
    CrossPodDNAFusion,
    FailureDensityFusion,
    MemeticGravityWell,
    MutatedDNA,
    MutationEngine,
    PIDGovernedMutation,
    PIDParameters,
    SafetyGate,
)


class TestPIDParameters:
    def test_compute_returns_float(self) -> None:
        pid = PIDParameters()
        result = pid.compute(0.1)
        assert isinstance(result, float)

    def test_compute_zero_error(self) -> None:
        pid = PIDParameters()
        result = pid.compute(0.0)
        assert result == 0.0


class TestCrossPodDNAFusion:
    def test_fuse_returns_string(self) -> None:
        fusion = CrossPodDNAFusion()
        result = fusion.fuse([0, 1])
        assert isinstance(result, str)
        assert result.startswith("FUSION_")

    def test_fuse_requires_two_pods(self) -> None:
        fusion = CrossPodDNAFusion()
        with pytest.raises(ValueError):
            fusion.fuse([0])

    def test_get_cluster_id(self) -> None:
        fusion = CrossPodDNAFusion()
        cluster = fusion.get_cluster_id([0, 1])
        assert cluster.startswith("cluster_")


class TestPIDGovernedMutation:
    def test_mutate_returns_tuple(self) -> None:
        pid_mut = PIDGovernedMutation()
        sequence = "ATGCATGCATGC"
        mutated, params = pid_mut.mutate(sequence)
        assert isinstance(mutated, str)
        assert isinstance(params, dict)

    def test_mutate_preserves_length(self) -> None:
        pid_mut = PIDGovernedMutation()
        sequence = "ATGCATGCATGC"
        mutated, _ = pid_mut.mutate(sequence)
        assert len(mutated) == len(sequence)

    def test_pid_params_keys(self) -> None:
        pid_mut = PIDGovernedMutation()
        _, params = pid_mut.mutate("AAAA")
        assert "Kp" in params and "Ki" in params and "Kd" in params


class TestCHRONOSyncHasher:
    def test_compute_sync_returns_result(self) -> None:
        import time
        hasher = CHRONOSyncHasher()
        result = hasher.compute_sync(time.time(), "ATGCATGC")
        assert result.sync_verified is True
        assert isinstance(result.epoch_hash, str)

    def test_to_dict(self) -> None:
        import time
        hasher = CHRONOSyncHasher()
        result = hasher.compute_sync(time.time(), "ATGCATGC")
        d = hasher.to_dict(result)
        assert "epoch_hash" in d
        assert "sync_verified" in d


class TestFailureDensityFusion:
    def test_fuse_preserves_length(self) -> None:
        fdf = FailureDensityFusion()
        seq = "ATGCATGCATGCATGC"
        result = fdf.fuse(seq, ["region_0", "region_1"])
        assert len(result) == len(seq)

    def test_analyze_density_returns_dict(self) -> None:
        fdf = FailureDensityFusion()
        d = fdf.analyze_density(["region_0", "region_1"])
        assert "region_0" in d and "region_1" in d


class TestMemeticGravityWell:
    def test_compute_gravity_score_range(self) -> None:
        wells = MemeticGravityWell()
        score = wells.compute_gravity_score([0.0, 0.0, 0.0])
        assert 0.0 <= score <= 1.0

    def test_attract_mutation_preserves_length(self) -> None:
        wells = MemeticGravityWell()
        seq = "ATGCATGCATGCATGC"
        result = wells.attract_mutation(seq, [0.5, 0.5, 0.5])
        assert len(result) == len(seq)


class TestSafetyGate:
    def test_verify_passes_valid_sequence(self) -> None:
        gate = SafetyGate()
        # Use a non-ATGC hex string (as produced by FUSION_ protocol)
        # so entropy=0 and omega meets the threshold
        metrics = gate.verify("FUSION_abcdef012345678", mutation_count=0)
        assert metrics.gates_passed is True
        assert metrics.omega >= SafetyGate.OMEGA_THRESHOLD

    def test_to_dict_has_required_keys(self) -> None:
        gate = SafetyGate()
        metrics = gate.verify("ATGC")
        d = gate.to_dict(metrics)
        for key in ("omega", "beta_1", "omega_verified", "beta_verified", "gates_passed"):
            assert key in d


class TestMutationEngine:
    def test_mutate_returns_list(self) -> None:
        engine = MutationEngine()
        vectors = [
            {"id": "vec_001", "sequence": "ATGCATGC", "source_pods": [0, 1]},
        ]
        results = engine.mutate(vectors)
        assert isinstance(results, list)
        assert len(results) == 1

    def test_mutate_returns_mutated_dna(self) -> None:
        engine = MutationEngine()
        vectors = [{"id": "vec_001", "source_pods": [0, 1]}]
        results = engine.mutate(vectors)
        dna = results[0]
        assert isinstance(dna, MutatedDNA)
        assert dna.dna_id.startswith("DNA_")

    def test_mutate_multiple_vectors(self) -> None:
        engine = MutationEngine()
        vectors = [
            {"id": f"vec_{i:03d}", "source_pods": [0, 1]} for i in range(5)
        ]
        results = engine.mutate(vectors)
        assert len(results) == 5

    def test_all_safety_gates_pass(self) -> None:
        engine = MutationEngine()
        vectors = [{"id": "vec_001", "source_pods": [0, 1]}]
        results = engine.mutate(vectors)
        for dna in results:
            assert dna.safety_metrics.get("gates_passed") is True
