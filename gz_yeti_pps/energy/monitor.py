from __future__ import annotations

import re
import signal
import sys
from time import sleep
from typing import Iterable, Mapping, Optional

from rich.console import Console
from rich.live import Live
from rich.table import Table

from ..log_engine import ROOT_LOGGER as PARENT_LOGGER
from ..controller import YetiController
from .table import EnergyTable

MOD_LOGGER = PARENT_LOGGER.get_child('monitor')


class Monitor(EnergyTable):
    """
    Live monitor table for the Yeti controller that refreshes every *refresh_interval* seconds.

    Parameters:
    -----------
        controller (YetiController):
            The connected Yeti controller.

        refresh_interval (float):
            The number of seconds to wait between each refresh.

        include (re.Pattern):
            A regex pattern to match against the column names. Passed to :class:`EnergyTable`.

        console (rich.console.Console):
            The console to use for output.
    """
    def __init__(
            self,
            controller:       YetiController,
            refresh_interval: float                     = 1.0,
            include:          Optional[re.Pattern[str]] = None,
            console:          Optional[Console]         = None
    ) -> None:
        super().__init__(controller, include=include, console=console)
        self.__refresh_interval = None

        self.refresh_interval = refresh_interval

    @property
    def refresh_interval(self) -> float:
        return self.__refresh_interval

    @refresh_interval.setter
    def refresh_interval(self, new: float) -> None:
        if not isinstance(new, float):
            raise TypeError(f"Refresh interval must be a float not {type(new)}!")

        if new < 0:
            raise ValueError(f"Refresh interval must be greater than 0 not {new}!")

        self.__refresh_interval = new

    def __exit_handler(self, signum, frame) -> None:
        """
        Exit handler for the monitor.
        """
        log = self.method_logger
        log.debug("Exiting monitor...")
        log.debug("Exiting monitor... done")
        sys.exit(0)

    def run(self) -> None:
        """
        Start the monitor.
        """
        signal.signal(signal.SIGINT, self.__exit_handler)

        with Live(self.table, console=self.console,) as live:
            while True:
                sleep(self.refresh_interval)
                live.update(self.table)
