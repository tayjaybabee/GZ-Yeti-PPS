from __future__ import annotations

import re
import signal
import sys
from time import sleep
from typing import Iterable, Mapping, Optional

from rich.console import Console
from rich.live import Live
from rich.table import Table

from gz_yeti_pps.controller import YetiController
from gz_yeti_pps.log_engine import ROOT_LOGGER as PARENT_LOGGER, Loggable

MOD_LOGGER = PARENT_LOGGER.get_child('energy.table')


class EnergyTable(Loggable):

    DEFAULT_INCLUDE_RE = re.compile(r'(power|watt|volt|amp|current|input|output|charge|load)', re.I)

    def __init__(
            self,
            controller: YetiController,
            include:    Optional[re.Pattern[str]] = None,
            console:    Optional[Console]         = None,
            **kwargs
    ) -> None:
        parent = kwargs.get('parent_logger', MOD_LOGGER)
        self.__controller = None
        self.__console    = None
        self.__include_re = None
        super().__init__(parent)

        self.__init_setup__(controller=controller, include=include, console=console, **kwargs)

    @property
    def controller(self) -> YetiController:
        return self.__controller

    @controller.setter
    def controller(self, new: YetiController) -> None:
        if not isinstance(new, YetiController):
            raise TypeError(f"Controller must be of type 'YetiController' not {type(new)}!")

        self.__controller = new

    @property
    def console(self) -> Console:

        if self.__console is None:
            self.__console = Console()

        return self.__console

    @console.setter
    def console(self, new: Console) -> None:
        if not isinstance(new, (Console, type(None))):
            raise TypeError(f"Console must be of type 'Console' not {type(new)}!")

        if new is None:
            self.__console = Console()

        self.__console = new

    @property
    def include_re(self) -> re.Pattern[str]:
        if self.__include_re is None:
            self.__include_re = self.DEFAULT_INCLUDE_RE

        return self.__include_re

    @include_re.setter
    def include_re(self, new: Optional[re.Pattern[str]]) -> None:

        if not isinstance(new, (re.Pattern, type(None))):
            raise TypeError(f"Include regex must be of type 're.Pattern' not {type(new)}!")

        if new is None:
            new = self.DEFAULT_INCLUDE_RE

        self.__include_re = new

    @property
    def table(self) -> Table:
        return self._build_table(self._filtered_state())

    def __init_setup__(self, **kwargs) -> None:
        if 'controller' in kwargs:
            self.controller = kwargs.get('controller', YetiController())

        if 'include' in kwargs:
            self.include_re = kwargs.get('include', self.DEFAULT_INCLUDE_RE)

        if 'console' in kwargs:
            self.console = kwargs.get('console', Console())

    def _filtered_state(self) -> Mapping[str, object]:
        """Return controller.state entries that match *include_re*."""
        state = self.controller.state  # Box → dict-like
        return {k: state[k] for k in state.keys() if self.include_re.search(k)}

    @staticmethod
    def _build_table(data: Mapping[str, object]) -> Table:
        """Convert a mapping to a Rich :class:`Table`."""
        tbl = Table(title="Yeti Power Telemetry")
        tbl.add_column("Metric", style="bold cyan")
        tbl.add_column("Value", justify="right")

        for k, v in data.items():
            tbl.add_row(k, str(v))
        return tbl

    def render_snapshot(self) -> None:
        """
        Print a single static table to *console*

        Returns:
            None
        """
        log = self.method_logger
        log.debug("Rendering snapshot...")

        self.console.print(self.table)
