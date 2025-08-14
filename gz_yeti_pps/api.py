from .helpers import attempt_connection
from cachetools import cached, TTLCache
import requests

from gz_yeti_pps.log_engine import ROOT_LOGGER, Loggable
from gz_yeti_pps.common.constants import DEFAULT_API_STUB as DEFAULT_STUB, DEFAULT_TIMEOUT, DEFAULT_STATE_URL
from gz_yeti_pps.common.errors import GZYetiPPSConnectionError as GZYetiPPSConnectionError

ConnectionError = GZYetiPPSConnectionError

MOD_LOGGER = ROOT_LOGGER.get_child('api')

STATE_CACHE = TTLCache(maxsize=1, ttl=5)
CONN_CHECK_CACHE = TTLCache(maxsize=20, ttl=5)
GET_CACHE = TTLCache(maxsize=20, ttl=5)


class API(Loggable):
    def __init__(
            self,
            stub=DEFAULT_STUB,
            do_not_check_connection=False,
            timeout=DEFAULT_TIMEOUT
    ):
        super().__init__(MOD_LOGGER)
        self.__stub                  = None
        self.__timeout               = None
        self.__will_check_connection = None

        self.will_check_connection = not do_not_check_connection
        self.timeout = timeout
        self.stub                  = stub

    @property
    def state(self):
        return self.get_state()

    @property
    def state_url(self):
        return f'{self.stub or DEFAULT_STUB}/state'

    @property
    def stub(self):
        return self.__stub

    @stub.setter
    def stub(self, new):
        if not isinstance(new, str):
            raise TypeError(f"Stub must be a string not {type(new)}!")

        new = new.strip()

        if not new.startswith('http://') and not new.startswith('https://'):
            new = f'http://{new}'

        if self.will_check_connection:
            self.check_connection(new)

        self.__stub = new

    @property
    def timeout(self):
        return self.__timeout or DEFAULT_TIMEOUT

    @timeout.setter
    def timeout(self, new):
        log = self.method_logger
        log.debug(f"Setting timeout to {new}...")
        if not isinstance(new, (float, int)):
            log.warning(f"Timeout must be a number not {type(new)}! Seeing if conversion is possible...")

            if isinstance(new, str):

                new = new.strip()
                log.debug(f"Stripped value: {new}")

                if not new.strip().isnumeric():
                    log.warning(f"Value is not numeric! Raising TypeError!")
                    raise TypeError(f"Timeout must be a number not {type(new)}!")
                else:
                    log.debug(f"Value is numeric!")

        log.debug(f'Converting {new} to float and returning...')

        self.__timeout = float(new)

    @property
    def will_check_connection(self):
        return self.__will_check_connection

    @will_check_connection.setter
    def will_check_connection(self, new):
        if not isinstance(new, bool):
            raise TypeError(f"Will check connection must be a bool not {type(new)}!")

        self.__will_check_connection = new

    @cached(cache=CONN_CHECK_CACHE)
    def check_connection(self, url: str = DEFAULT_STUB) -> bool:
        print(url)

        log = self.method_logger
        log.debug(f"Checking connection to {url}...")

        try:
            log.debug(f"Attempting to connect to {url} with timeout: {self.timeout}...")
            attempt_connection(url, raise_on_fail=True, timeout=self.timeout)
        except ConnectionError as e:
            log.error(f"Failed to connect to {url}: {e}")
            raise ConnectionError(f"Stub {url} is not accessible!") from e

        log.debug(f"Successfully connected to {url}!")
        return True

    @cached(cache=GET_CACHE)
    def get(self, endpoint=str):
        log = self.method_logger
        log.debug(f"Getting {endpoint}...")
        res = requests.get(f'{self.stub}/{endpoint}')
        log.debug(f'GET {self.stub}/{endpoint} returned {res.status_code}')

        return res.json()


    @cached(cache=STATE_CACHE)
    def get_state(self):
        log = self.method_logger

        try:
            res = requests.get(f'{self.state_url}')
            log.debug(f'GET {self.state_url} returned {res.status_code}')
            return res.json()
        except requests.exceptions.RequestException as e:
            raise GZYetiPPSConnectionError(self.state_url, f"API call failed: {e}") from e

    def post(self, key, value):
        log = self.method_logger
        log.debug(f"Posting {value} to {key}...")

        res = requests.post(f'{self.state_url}', json={key: value})

        log.debug(f"POST {self.state_url} returned {res.status_code}")
        if not res.status_code == 200:
            try:
                res.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise ConnectionError(f"Failed to post to {self.state_url}: {e}") from e
