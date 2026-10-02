# SPDX-FileCopyrightText: 2026 Carnegie Mellon University
#
# SPDX-License-Identifier: GPL-2.0-only

"""Compatibility wrapper around streamlit-label-kit.

streamlit-label-kit (<= 0.1.3) calls Streamlit's internal image_to_url()
helper with an integer image width. Newer Streamlit releases expect a
LayoutConfig object in that position, which breaks the bounding box viewer
and editor. Until label-kit is updated we adapt the call here.

The label-kit frontend also builds the image URL by appending the media path
to the URL of the current page, which only works for an app served from the
root. With multipage navigation the page is e.g. /labeling, so we make the
media path relative to the parent of the page.
"""

from __future__ import annotations

import importlib
import inspect
from typing import Any

from streamlit.elements.lib import image_utils
from streamlit_label_kit import detection

__all__ = ["detection"]

_image_to_url = image_utils.image_to_url


def _compat_image_to_url(image: Any, width: Any, *args: Any, **kwargs: Any) -> str:
    if isinstance(width, int):
        from streamlit.elements.lib.layout_utils import LayoutConfig

        width = LayoutConfig(width=width)
    url = _image_to_url(image, width, *args, **kwargs)

    # label-kit strips the leading '/' and the frontend prepends the page URL
    # ("http://host/labeling" + "/../media/x.png" resolves to "/media/x.png")
    if url.startswith("/"):
        url = "//.." + url
    return url


_labelkit_detection = importlib.import_module(
    "streamlit_label_kit.LabelToolKit.detection",
)
if "layout_config" in inspect.signature(_image_to_url).parameters:
    setattr(_labelkit_detection, "image_to_url", _compat_image_to_url)  # noqa: B010
