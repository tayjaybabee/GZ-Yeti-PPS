from __future__ import annotations
from typing import Optional, Literal, Protocol, Any, List, Dict
from collections import deque
import time


# -- Protocol to help type tools; replace with your real controller type --
class YetiController(Protocol):
    def state(self) -> Dict[str, Any]:
        """
        Returns a snapshot dict including at least 'whOut'.
        Optionally may include 'ampsOut', 'volts', 'wattsOut',
        'whStored', 'socPercent', etc.
        """


class EnergyStorage:
    """
    Combines your initial unit-aware EnergyStorage model with cumulative whOut tracking
    & history. Stores energy internally in Wh, converts to kWh/J, automatically pulls
    newest state from device, handles counter resets, computes power, and maintains a
    timestamped rolling history of readings.

    Features:
      • Pass only the device; no hand-fed metrics required.
      • Call .update() whenever you poll.
      • `.total_out_wh/kwh/joules` track sent energy.
      • `.stored_wh`, `.state_of_charge`, `.capacity`, and unit-switching as before.
      • Calculates watts from `ampsOut × volts` if `wattsOut` isn't present.
      • `.last` snapshot and `.history` list with each timestamped entry.
      • `.average_power_w()` computes mean output from session start.
    """

    # conversion factors: 1 Wh = 3,600 J, 1 kWh = 1,000 Wh
    _CONVERSIONS = {
        'wh': 1.0,
        'kwh': 1000.0,
        'j': 1 / 3600.0  # to convert joules to Wh
    }

    _WH_TO_J: float = 3600.0  # 1 Wh = 3,600 J :contentReference[oaicite:2]{index=2}

    def __init__(
        self,
        device: YetiController,
        capacity: float = 0.0,
        stored: float = 0.0,
        unit: Literal['wh', 'kwh', 'j'] = 'wh',
        max_history: int = 1000,
        clock: callable = time.time,
    ):
        self.__device = device
        self._unit = unit
        self._capacity_wh = 0.0
        self._stored_wh = 0.0
        self.capacity = capacity
        self.stored = stored

        self._initial_wh_out: Optional[float] = None
        self._prev_wh_out: Optional[float] = None
        self._delta_wh: float = 0.0

        self._history: deque = deque(maxlen=max_history)
        self._clock = clock

        self.update()

    @property
    def device(self) -> YetiController:
        return self.__device

    @property
    def capacity(self) -> float:
        return self._wh_to(self._capacity_wh, self._unit)

    @capacity.setter
    def capacity(self, value: float):
        if value < 0:
            raise ValueError(f"capacity in {self._unit} must be >= 0")
        self._capacity_wh = value * self._CONVERSIONS[self._unit]
        if self._stored_wh > self._capacity_wh:
            self._stored_wh = self._capacity_wh

    @property
    def stored(self) -> float:
        return self._wh_to(self._stored_wh, self._unit)

    @stored.setter
    def stored(self, value: float):
        if value < 0:
            raise ValueError(f"stored energy in {self._unit} must be >= 0")
        swh = value * self._CONVERSIONS[self._unit]
        if swh > getattr(self, '_capacity_wh', float('inf')):
            raise ValueError("stored energy can't exceed capacity")
        self._stored_wh = swh

    @property
    def state_of_charge(self) -> float:
        return (self._stored_wh / self._capacity_wh) if self._capacity_wh else 0.0

    @property
    def total_out_wh(self) -> float:
        return self._delta_wh

    @property
    def total_out_kwh(self) -> float:
        return self._delta_wh / 1000.0

    @property
    def total_out_joules(self) -> float:
        return self._delta_wh * self._WH_TO_J

    @property
    def last(self) -> Dict[str, Any]:
        return dict(self._history[-1]) if self._history else {}

    @property
    def history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def average_power_w(self) -> Optional[float]:
        if len(self._history) < 2:
            return None
        first = self._history[0]
        last = self._history[-1]
        dt = last['timestamp'] - first['timestamp']
        if dt <= 0:
            return None
        delta_wh = last['total_wh'] - first['total_wh']
        return (delta_wh / dt) * 3600.0  # Wh/hour = Watts

    def switch_unit(self, new_unit: Literal['wh', 'kwh', 'j']):
        if new_unit not in self._CONVERSIONS:
            raise ValueError(f"Unsupported unit: {new_unit!r}")
        self._unit = new_unit

    def update(self) -> None:
        s = self.__device.state
        t = self._clock()

        raw_wh = s.get('whOut')
        if raw_wh is None:
            raise KeyError("'whOut' missing in device.state()")
        raw_wh = float(raw_wh)

        if self._initial_wh_out is None:
            self._initial_wh_out = self._prev_wh_out = raw_wh
            delta = 0.0
        else:
            delta = raw_wh - self._prev_wh_out
            if delta < 0:
                delta = 0.0  # reset/rollover
            self._delta_wh += delta
        self._prev_wh_out = raw_wh

        amps = s.get('ampsOut')
        volts = s.get('volts')
        watts = s.get('wattsOut')
        if watts is None and amps is not None and volts is not None:
            try:
                watts = float(amps) * float(volts)  # watts = volts × amps :contentReference[oaicite:3]{index=3}
            except Exception:
                watts = None

        wh_stored = s.get('whStored')
        if wh_stored is not None:
            try:
                self._stored_wh = float(wh_stored)
                if self._stored_wh > self._capacity_wh:
                    self._stored_wh = self._capacity_wh
            except Exception:
                pass

        so_c = s.get('socPercent')
        entry = {
            'timestamp': t,
            'whOut': raw_wh,
            'delta_wh': delta,
            'total_wh': self._delta_wh,
            'ampsOut': float(amps) if amps is not None else None,
            'volts': float(volts) if volts is not None else None,
            'wattsOut': float(watts) if watts is not None else None,
            'whStored': float(wh_stored) if wh_stored is not None else None,
            'socPercent': float(so_c) if so_c is not None else None,
        }
        self._history.append(entry)

    @staticmethod
    def _wh_to(wh: float, unit: str) -> float:
        return wh / EnergyStorage._CONVERSIONS[unit]

    def __repr__(self) -> str:
        last = self.last
        w = last.get('wattsOut')
        s = last.get('socPercent')
        st = last.get('whStored')
        power_info = f" lastPower={w:.1f} W" if w is not None else ""
        soc_info = f" Stored={st:.0f} Wh SOC={s:.0f}%" if st is not None and s is not None else ""
        return (
            f"<EnergyStorage total={self.total_out_wh:.1f} Wh "
            f"(~{self.total_out_kwh:.4f} kWh){power_info}{soc_info}>"
        )
