import streamlit as st
from streamlit_autorefresh import st_autorefresh
from typing import Dict, Union

class ReadOnlyFrame:
    def __init__(
        self,
        controller: object,
        info_fn: callable,
        *,
        title: str = "Status",
        use_metrics: bool = False,
        columns: int = None,
        refresh_ms: int | None = None,
        refresh_limit: int | None = None,
        key_prefix: str = "rof",
    ):
        self.controller = controller
        self.info_fn = info_fn
        self.title = title
        self.use_metrics = use_metrics
        self.columns = columns
        self.key_prefix = key_prefix
        self._c = st.container()
        if refresh_ms is not None:
            self._refresh_count = st_autorefresh(
                interval=refresh_ms,
                limit=refresh_limit,
                key=f"{key_prefix}_autorefresh",
            )

    def render(self):
        """

        """
        data = self.info_fn(self.controller)
        with self._c:
            st.markdown(f"### {self.title}")
            keys = list(data.keys())
            rows = {}
            if self.use_metrics:
                num = len(keys) if not self.columns else self.columns
                cols = st.columns(num, gap="small")
                for col, key in zip(cols, keys):
                    val = data[key]
                    label = key.replace("_", " ").title()
                    if isinstance(val, (int, float)):
                        col.metric(label, value=str(val))
                    else:
                        col.write(f"**{label}:** {val}")
            else:
                for key in keys:
                    val = data[key]
                    label = key.replace("_", " ").title()
                    st.text_input(label, value=str(val), disabled=True, key=f"{self.key_prefix}_{key}")

        # (Optional) you can clear cache or rerun logic here

        return data

