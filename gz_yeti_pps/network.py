"""
Utilities for gathering network info from the controller.
"""
from __future__ import annotations
from box import Box


FIELDS = [
    ('wifiStrength', 'wifi_strength'),
    ('ssid', 'ssid'),
    ('ipAddr', 'ip_address')
]
"""
A list of tuples of field names from the controller's state and their corresponding keys in the dictionary to be 
provided by :function:`build_network_info`.
"""


def build_network_info(controller) -> dict:
    """
    Build a dictionary of network info from a controller's state.

    Parameters:
        controller (YetiController):
            The controller to get info from.

    Returns:
        dict:
            A dictionary of network info with the following keys:

                - wifi_strength (int):
                    The WiFi signal strength.
                - ssid (str):
                    The WiFi SSID.
                - ip_address (str):
                    The IP address.
    """
    info = {}
    state = controller.state

    for field, key in FIELDS:
        info[key] = state.get(field)

    return info


def box_network_info(controller) -> Box:
    """
    Build a :class:`Box` of network info from a controller's state.

    Parameters:
        controller (YetiController):
            The controller to get info from.

    Returns:
        Box:
            A :class:`Box` of network info with the following keys:

                - wifi_strength (int):
                    The WiFi signal strength.
                - ssid (str):
                    The WiFi SSID.
                - ip_address (str):
                    The IP address.
    """
    return Box(build_network_info(controller))

