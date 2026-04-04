"""Response format helpers — convert dicts to JSON or XML."""

from fastapi.responses import Response
from lxml import etree
from typing import Any


def to_xml(data: Any, root_tag: str = "response") -> Response:
    """Convert a dict or list of dicts to an XML Response.

    Usage:
        return to_xml({"athlete": "Usain Bolt", "medal": "Gold"}, root_tag="athlete")
    """
    root = etree.Element(root_tag)
    _dict_to_xml(root, data)
    xml_bytes = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    return Response(content=xml_bytes, media_type="application/xml")


def _dict_to_xml(parent: etree._Element, data: Any) -> None:
    """Recursively build XML elements from a dict or list."""
    if isinstance(data, dict):
        for key, value in data.items():
            child = etree.SubElement(parent, str(key))
            _dict_to_xml(child, value)
    elif isinstance(data, list):
        for item in data:
            child = etree.SubElement(parent, "item")
            _dict_to_xml(child, item)
    else:
        parent.text = str(data) if data is not None else ""


def pick_format(data: Any, fmt: str = "json", root_tag: str = "response") -> Any:
    """Return JSON (default) or XML based on the `format` query param.

    Usage in a route:
        return pick_format(result, fmt=format, root_tag="athlete")
    """
    if fmt == "xml":
        return to_xml(data, root_tag=root_tag)
    # JSON is FastAPI's default — just return the dict/list
    return data
