import streamlit as st
import time
from gz_yeti_pps.controller import YetiController
from gz_yeti_pps.helpers.web_app.read_only_frame import ReadOnlyFrame
from gz_yeti_pps.network import build_network_info
import pandas as pd
from datetime import datetime



YETI = YetiController()


def fetch_data():

    return str(str(YETI.state['wattsOut']) + 'W')


net_frame = ReadOnlyFrame(
    controller = YETI,
    info_fn = build_network_info,
    title='Yeti Net Info',
    use_metrics=False,
    refresh_ms=2000,
    key_prefix='net'
)
net_data = net_frame.render()


other_frame = ReadOnlyFrame(
    controller=YETI,
    info_fn=lambda ctrl: ctrl.state,
    title="Device Status",
    use_metrics=True,
    columns=4,
    refresh_ms=2000,
    key_prefix="all"
)
other_data = other_frame.render()


placeholder = st.empty()

while True:
    data = fetch_data()  # Replace with your data-fetching function
    placeholder.text(f"Current data: {data}")
    time.sleep(1)  # Update every second
