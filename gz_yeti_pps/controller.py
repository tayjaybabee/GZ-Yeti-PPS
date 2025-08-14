from typing import Union

from box import Box

from gz_yeti_pps.api import API, DEFAULT_STUB, DEFAULT_STATE_URL
from gz_yeti_pps.log_engine import ROOT_LOGGER, Loggable
from gz_yeti_pps.helpers import attempt_connection, parse_truthy_value
from gz_yeti_pps.energy.storage import EnergyStorage


MOD_LOGGER = ROOT_LOGGER.get_child('controller')


class YetiController(Loggable):
    DEFAULT_STUB = DEFAULT_STUB
    DEFAULT_STATE_URL = DEFAULT_STATE_URL

    def __init__(self, api_stub: str = DEFAULT_STUB):
        super().__init__(MOD_LOGGER)
        self.__api  = None
        self.__stub = None
        self.__energy_storage = None

        self.stub = api_stub

    @property
    def ac_port_state(self) -> bool:
        return bool(self.api.state['acPortStatus'])

    @ac_port_state.setter
    def ac_port_state(self, new: Union[bool, int, str]):
        new = parse_truthy_value(new)
        self.api.post('acPortStatus', new)

    @property
    def api(self) -> API:
        if self.__api is None:
            self.__api = API(stub=self.stub, do_not_check_connection=True)

        return self.__api

    @property
    def backlight_state(self) -> bool:
        return bool(self.api.state['backlight'])

    @backlight_state.setter
    def backlight_state(self, new: Union[bool, int, str]):
        log = self.method_logger
        new = parse_truthy_value(new)
        log.debug(f"Setting backlight state to {new}...")

        self.api.post('backlight', new)

    @property
    def device_info(self):
        """
        Returns a Box object containing the device information, as returned by the API. This is a read-only property.

        Returns:
            - Box:
                A Box object containing the device information:

                    - name (str):
                        The name of the device.

                    - model (str):
                        The model of the device.

                    - firmwareVersion (str):
                        The firmware version of the device.

                    - macAddress (str):
                        The MAC address of the device.

                    - platform (str):
                        The platform of the device.
        """
        return Box(self.api.get('sysinfo'))

    @property
    def energy_storage(self) -> 'EnergyStorage':
        if self.__energy_storage is None:
            self.__energy_storage = EnergyStorage(self)
        else:
            self.__energy_storage.update()

        return self.__energy_storage

    @property
    def ip_address(self) -> str:
        """
        Returns the IP address of the device. Read-only.

        Returns:
            str:
                The IP address of the device.
        """
        return self.state.ipAddr

    @property
    def is_charging(self) -> bool:
        """
        Returns whether the device is currently charging from AC power. **Read-only**.
        :return:
        """
        return bool(self.api.state['isCharging'])

    @property
    def model(self) -> str:
        """
        Returns the model of the device. Read-only.

        Returns:
            str:
                The model of the device.
        """
        return self.device_info.model

    @property
    def name(self) -> str:
        """
        Returns the name of the device. Read-only.

        Returns:
            str:
                The name of the device.
        """
        return self.device_info.name

    @property
    def network(self):
        s = self.state


    @property
    def state(self) -> Box:
        """
        Returns the current state of the device. Read-only.

        Returns:
            Box:
                A Box object containing the current state of the device:

        """
        return Box(self.api.get_state())

    @property
    def state_url(self) -> str:
        """
        Returns the URL of the device state. Read-only.

        Returns:
            str:
                The URL of the device state.
        """
        return self.api.state_url

    @property
    def stub(self) -> str:
        """
        Returns the API stub. Read-only.
        """
        return self.__stub or self.DEFAULT_STUB

    @stub.setter
    def stub(self, new):
        if not isinstance(new, str):
            raise TypeError(f"Stub must be a string not {type(new)}!")

        new = new.strip()
        if not new.startswith('http'):
            new = f'http://{new}'

        if not attempt_connection(new):
            try:
                raise ConnectionError(f'Failed to connect to {new}')
            except ConnectionError as e:
                print(f'Unable to connect to {new}: {e}')

        if self.api:
            self.api.will_check_connection = False
            self.api.stub = new

        self.__stub = new

    @property
    def usb_port_state(self) -> bool:
        """
        Returns the state of the USB charge port.

        Returns:
            bool:
                The state of the USB charge port;
                    - True:
                        The port is on (meaning plugged in devices can draw power).

                    - False:
                        The port is off (meaning no devices can draw power).
        """
        return bool(self.api.state['usbPortStatus'])

    @usb_port_state.setter
    def usb_port_state(self, new: Union[bool, int, str]) -> None:
        """
        Sets the USB port state.

        Parameters:
            new (Union[bool, int, str]):
                The new state of the USB charge port; valid values are:
                  - For on:
                    - 1,
                    - '1',
                    - 'on'[1]_,
                    - 'true',
                    - True,
                    - 'yes',
                    - 'y'

                  - For off:
                    - 0,
                    - '0',
                    - 'off',
                    - 'false',
                    - False,
                    - 'no',
                    - 'n'

        .. _[1]: Case-insensitive.

        Returns:
            None:
                No return value.
        """
        log = self.method_logger
        new = parse_truthy_value(new)
        log.debug(f"Setting usb port state to {new}...")
        self.api.post('usbPortStatus', new)
        log.debug(f'Sent POST request to {self.api.stub} with payload {new}')
