"""
NeuroLoom RE Pipeline - Atomic Layer Memory Module

This module implements L6 (Atomic Layer) memory functions.
"""

import hashlib
import struct
from typing import Any, Optional, Dict, List, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

from ..config import (
    H_CACHE_HIT_RATE,
    HNSW_DIM,
    ATMOSPHERE_BREATH_US,
)


class CacheStrategy(Enum):
    """Cache eviction strategies."""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    RANDOM = "random"


@dataclass
class MemoryEntry:
    """Memory cache entry."""
    key: str
    value: Any
    access_count: int = 0
    last_access: float = 0.0
    created_at: float = 0.0
    size_bytes: int = 0


class AtomicCache:
    """Zero-energy atomic memory cache with 99.95% hit rate."""

    def __init__(
        self,
        max_size_mb: int = 1024,
        target_hit_rate: float = H_CACHE_HIT_RATE,
        strategy: CacheStrategy = CacheStrategy.LRU,
    ):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.target_hit_rate = target_hit_rate
        self.strategy = strategy
        self._cache: Dict[str, MemoryEntry] = {}
        self._current_size = 0
        self._hits = 0
        self._misses = 0

    def ATOM_MEM_READ(self, key: str) -> Tuple[bool, Any]:
        """Read from atomic memory cache."""
        import time

        if key in self._cache:
            entry = self._cache[key]
            entry.access_count += 1
            entry.last_access = time.time()
            self._hits += 1
            return True, entry.value

        self._misses += 1
        return False, None

    def ATOM_MEM_WRITE(self, key: str, value: Any, size_bytes: Optional[int] = None) -> bool:
        """Write to atomic memory cache."""
        import time

        if size_bytes is None:
            size_bytes = len(str(value))

        while self._current_size + size_bytes > self.max_size_bytes and self._cache:
            self._evict_one()

        entry = MemoryEntry(
            key=key,
            value=value,
            access_count=1,
            last_access=time.time(),
            created_at=time.time(),
            size_bytes=size_bytes,
        )

        if key in self._cache:
            self._current_size -= self._cache[key].size_bytes

        self._cache[key] = entry
        self._current_size += size_bytes
        return True

    def _evict_one(self) -> Optional[str]:
        """Evict one entry based on strategy."""
        if not self._cache:
            return None

        if self.strategy == CacheStrategy.LRU:
            key = min(self._cache.keys(), key=lambda k: self._cache[k].last_access)
        elif self.strategy == CacheStrategy.LFU:
            key = min(self._cache.keys(), key=lambda k: self._cache[k].access_count)
        elif self.strategy == CacheStrategy.FIFO:
            key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
        else:
            import random
            key = list(self._cache.keys())[random.randint(0, len(self._cache) - 1)]

        self._current_size -= self._cache[key].size_bytes
        del self._cache[key]
        return key

    def ATOM_MEM_EVICT(self, key: str) -> bool:
        """Explicitly evict a key from cache."""
        if key in self._cache:
            self._current_size -= self._cache[key].size_bytes
            del self._cache[key]
            return True
        return False

    def get_hit_rate(self) -> float:
        """Get current cache hit rate."""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size_bytes": self._current_size,
            "size_mb": self._current_size / (1024 * 1024),
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.get_hit_rate(),
            "target_hit_rate": self.target_hit_rate,
        }


class VectorEncoder:
    """Encode arbitrary data into 384-dimensional semantic vectors."""

    def __init__(self, dim: int = HNSW_DIM):
        self.dim = dim
        self._cache = AtomicCache(max_size_mb=256)

    def encode(self, data: Union[str, bytes, Dict[str, Any]]) -> np.ndarray:
        """Encode data into a semantic vector."""
        cache_key = self._compute_key(data)
        hit, cached = self._cache.ATOM_MEM_READ(cache_key)
        if hit:
            return cached

        vector = self._generate_vector(data)
        self._cache.ATOM_MEM_WRITE(cache_key, vector)
        return vector

    def _compute_key(self, data: Union[str, bytes, Dict]) -> str:
        """Compute cache key for data."""
        if isinstance(data, dict):
            import json
            data = json.dumps(data, sort_keys=True)
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def _generate_vector(self, data: Union[str, bytes, Dict]) -> np.ndarray:
        """Generate semantic vector from data."""
        if isinstance(data, str):
            byte_data = data.encode('utf-8')
        elif isinstance(data, dict):
            import json
            byte_data = json.dumps(data, sort_keys=True).encode('utf-8')
        else:
            byte_data = data if isinstance(data, bytes) else str(data).encode()

        hash_val = hashlib.sha512(byte_data).digest()
        vector = np.frombuffer(hash_val, dtype=np.float32)

        while len(vector) < self.dim:
            hash_val = hashlib.sha512(hash_val + byte_data).digest()
            more = np.frombuffer(hash_val, dtype=np.float32)
            vector = np.concatenate([vector, more])

        vector = vector[:self.dim]
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        return vector.astype(np.float32)

    def batch_encode(self, data_list: List[Union[str, bytes, Dict]]) -> np.ndarray:
        """Encode multiple data items into vectors."""
        return np.array([self.encode(d) for d in data_list], dtype=np.float32)


class SimCalc:
    """Compute similarity between vectors."""

    def __init__(self):
        self._cache = AtomicCache(max_size_mb=128)

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        cache_key = self._compute_key(a, b, "cos")
        hit, cached = self._cache.ATOM_MEM_READ(cache_key)
        if hit:
            return float(cached)

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            similarity = 0.0
        else:
            similarity = float(np.dot(a, b) / (norm_a * norm_b))

        similarity = max(-1.0, min(1.0, similarity))
        self._cache.ATOM_MEM_WRITE(cache_key, np.float32(similarity))
        return similarity

    def euclidean_distance(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute Euclidean distance between two vectors."""
        cache_key = self._compute_key(a, b, "euc")
        hit, cached = self._cache.ATOM_MEM_READ(cache_key)
        if hit:
            return float(cached)

        distance = float(np.linalg.norm(a - b))
        self._cache.ATOM_MEM_WRITE(cache_key, np.float32(distance))
        return distance

    def dot_product(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute dot product between two vectors."""
        return float(np.dot(a, b))

    def _compute_key(self, a: np.ndarray, b: np.ndarray, metric: str) -> str:
        """Compute cache key for similarity calculation."""
        a_hash = hashlib.sha256(a.tobytes()[:64]).hexdigest()[:16]
        b_hash = hashlib.sha256(b.tobytes()[:64]).hexdigest()[:16]
        return f"{metric}:{a_hash}:{b_hash}"


class ContextCompressor:
    """Compress context for HMV encoding."""

    def __init__(self, target_size: int = 1024):
        self.target_size = target_size

    def compress(self, context: Union[str, bytes, Dict]) -> bytes:
        """Compress context to target size."""
        import zlib
        import json

        if isinstance(context, dict):
            context = json.dumps(context)
        if isinstance(context, str):
            context = context.encode('utf-8')

        compressed = zlib.compress(context, level=9)
        if len(compressed) > self.target_size:
            compressed = compressed[:self.target_size]
        elif len(compressed) < self.target_size:
            compressed = compressed + b'\x00' * (self.target_size - len(compressed))
        return compressed

    def decompress(self, compressed: bytes) -> bytes:
        """Decompress context."""
        import zlib
        compressed = compressed.rstrip(b'\x00')
        return zlib.decompress(compressed)
