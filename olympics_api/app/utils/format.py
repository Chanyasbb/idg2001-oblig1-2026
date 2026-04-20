"""Response format helpers — convert dicts/lists to JSON or XML."""

import re
from fastapi.responses import Response
from lxml import etree
from typing import Any


def _safe_tag(tag: str) -> str:
    """Convert any string to a valid XML tag name.

    XML tags can't contain spaces or most special characters.
    e.g. 'Water Polo' → 'Water_Polo', '100m sprint' → '_100m_sprint'
    """
    tag = re.sub(r"[^a-zA-Z0-9_.-]", "_", str(tag))
    if not tag or tag[0].isdigit():
        tag = "_" + tag
    return tag or "item"


def _dict_to_xml(parent: etree._Element, data: Any) -> None:
    """Recursively build XML elements from a dict or list."""
    if isinstance(data, dict):
        for key, value in data.items():
            child = etree.SubElement(parent, _safe_tag(key))
            _dict_to_xml(child, value)
    elif isinstance(data, list):
        for item in data:
            child = etree.SubElement(parent, "item")
            _dict_to_xml(child, item)
    else:
        parent.text = str(data) if data is not None else ""


def to_xml(data: Any, root_tag: str = "response") -> Response:
    """Convert a dict or list of dicts to an XML Response."""
    root = etree.Element(_safe_tag(root_tag))
    _dict_to_xml(root, data)
    xml_bytes = etree.tostring(
        root, pretty_print=True, xml_declaration=True, encoding="UTF-8"
    )
    return Response(content=xml_bytes, media_type="application/xml")


def pick_format(data: Any, fmt: str = "json", root_tag: str = "response") -> Any:
    """Return XML or JSON based on the `format` query parameter.

    JSON is FastAPI's default — just return the dict/list.
    """
    if fmt == "xml":
        return to_xml(data, root_tag=root_tag)
    return data
