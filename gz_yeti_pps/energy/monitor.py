from __future__ import annotations

import re
import signal
import sys
from time import sleep
from typing import Iterable, Mapping

from rich.console import Console
from rich.live import Live
from rich.table import Table

from .log_engine import ROOT_LOGGER as PARENT_LOGGER
from .controller import YetiController

MOD_LOGGER = PARENT_LOGGER.get_child('monitor')



