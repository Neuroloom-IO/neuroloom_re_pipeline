"""
NeuroLoom RE Pipeline - SNP Monitor Module

Implements Singularity Negotiation Protocol (SNP) monitoring and triggers.

Trigger Cascade:
- Omega < 0.90: Red Loom Protocol (Fiber Shield)
- Omega < 0.85: SNP Trigger (Governance Board)
- Omega < 0.80: Hardware Severance (Kill Switch)
"""

import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from ..config import (
    OMEGA_FLOOR,
    OMEGA_RED_LOOM,
    OMEGA_SNP,
    OMEGA_SEVERANCE,
)


class SNPState(Enum):
    """SNP monitor states."""
    NORMAL = "normal"
    RED_LOOM = "red_loom"
    SNP_TRIGGERED = "snp_triggered"
    SEVERANCE = "severance"


@dataclass
class SNPAlert:
    """SNP alert event."""
    timestamp: float
    state: SNPState
    omega: float
    trigger_value: float
    message: str


class SNPMonitor:
    """
    Singularity Negotiation Protocol Monitor.
    
    Monitors Omega coherence and triggers appropriate responses
    based on threshold cascade.
    """
    
    def __init__(
        self,
        omega_floor: float = OMEGA_FLOOR,
        red_loom: float = OMEGA_RED_LOOM,
        snp_trigger: float = OMEGA_SNP,
        severance: float = OMEGA_SEVERANCE,
    ):
        self.omega_floor = omega_floor
        self.red_loom = red_loom
        self.snp_trigger = snp_trigger
        self.severance = severance
        
        self._current_state = SNPState.NORMAL
        self._current_omega = omega_floor
        self._alert_history: List[SNPAlert] = []
        
        self._on_red_loom: Optional[Callable[[], None]] = None
        self._on_snp: Optional[Callable[[], None]] = None
        self._on_severance: Optional[Callable[[], None]] = None
        self._on_recovery: Optional[Callable[[], None]] = None
    
    def check_omega(self, omega: float) -> SNPState:
        """Check Omega coherence and update state."""
        self._current_omega = omega
        previous_state = self._current_state
        
        if omega < self.severance:
            new_state = SNPState.SEVERANCE
        elif omega < self.snp_trigger:
            new_state = SNPState.SNP_TRIGGERED
        elif omega < self.red_loom:
            new_state = SNPState.RED_LOOM
        else:
            new_state = SNPState.NORMAL
        
        if new_state != previous_state:
            self._handle_state_transition(previous_state, new_state, omega)
        
        self._current_state = new_state
        return new_state
    
    def trigger_red_loom(self) -> None:
        """Trigger Red Loom Protocol."""
        alert = SNPAlert(
            timestamp=time.time(),
            state=SNPState.RED_LOOM,
            omega=self._current_omega,
            trigger_value=self.red_loom,
            message="Red Loom Protocol engaged - Fiber Shield activated",
        )
        self._alert_history.append(alert)
        if self._on_red_loom:
            self._on_red_loom()
    
    def trigger_snp(self) -> None:
        """Trigger SNP Protocol."""
        alert = SNPAlert(
            timestamp=time.time(),
            state=SNPState.SNP_TRIGGERED,
            omega=self._current_omega,
            trigger_value=self.snp_trigger,
            message="SNP Triggered - Governance Board convened",
        )
        self._alert_history.append(alert)
        if self._on_snp:
            self._on_snp()
    
    def trigger_severance(self) -> None:
        """Trigger Hardware Severance."""
        alert = SNPAlert(
            timestamp=time.time(),
            state=SNPState.SEVERANCE,
            omega=self._current_omega,
            trigger_value=self.severance,
            message="Hardware Severance triggered - Kill switch activated",
        )
        self._alert_history.append(alert)
        if self._on_severance:
            self._on_severance()
    
    def set_callbacks(
        self,
        on_red_loom: Optional[Callable[[], None]] = None,
        on_snp: Optional[Callable[[], None]] = None,
        on_severance: Optional[Callable[[], None]] = None,
        on_recovery: Optional[Callable[[], None]] = None,
    ) -> None:
        """Set callbacks for state transitions."""
        self._on_red_loom = on_red_loom
        self._on_snp = on_snp
        self._on_severance = on_severance
        self._on_recovery = on_recovery
    
    def get_state(self) -> SNPState:
        """Get current SNP state."""
        return self._current_state
    
    def get_omega(self) -> float:
        """Get current Omega value."""
        return self._current_omega
    
    def get_alerts(self, n: int = 10) -> List[SNPAlert]:
        """Get recent alerts."""
        return self._alert_history[-n:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get SNP monitor statistics."""
        return {
            "current_state": self._current_state.value,
            "current_omega": self._current_omega,
            "omega_floor": self.omega_floor,
            "red_loom": self.red_loom,
            "snp_trigger": self.snp_trigger,
            "severance": self.severance,
            "total_alerts": len(self._alert_history),
            "red_loom_count": sum(1 for a in self._alert_history if a.state == SNPState.RED_LOOM),
            "snp_count": sum(1 for a in self._alert_history if a.state == SNPState.SNP_TRIGGERED),
            "severance_count": sum(1 for a in self._alert_history if a.state == SNPState.SEVERANCE),
        }
    
    def _handle_state_transition(
        self,
        old_state: SNPState,
        new_state: SNPState,
        omega: float
    ) -> None:
        """Handle state transition."""
        if new_state == SNPState.RED_LOOM and old_state != SNPState.RED_LOOM:
            self.trigger_red_loom()
        elif new_state == SNPState.SNP_TRIGGERED:
            self.trigger_snp()
        elif new_state == SNPState.SEVERANCE:
            self.trigger_severance()
        elif new_state == SNPState.NORMAL and old_state != SNPState.NORMAL:
            if self._on_recovery:
                self._on_recovery()
