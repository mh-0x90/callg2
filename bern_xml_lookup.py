from __future__ import annotations

import os
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from bern_host_guard import checkit,checkit2, ensure_not_blacklisted


BERN_XML_PATH_ENV = "BERN_XML_PATH"
DEFAULT_BERN_XML_PATH = "bern_data.xml"


def _normalized_host(website: str) -> str:
    parsed = urlparse(website)
    normalized_host = (parsed.hostname or "").lower()
    ensure_not_blacklisted(normalized_host)
    return normalized_host


def lookup_website_value(website: str, xml_path: str | None = None) -> str:
    chosen_path = xml_path or os.getenv(BERN_XML_PATH_ENV, DEFAULT_BERN_XML_PATH)
    tree = ET.parse(chosen_path)
    root = tree.getroot()

    normalized = _normalized_host(website)

    for entry in root.findall(".//entry"):
        website_attr = (entry.get("website") or "").strip().lower()
        if website_attr == normalized:
            value_attr = entry.get("value")
            if value_attr:
                return value_attr.strip()
            if entry.text:
                return entry.text.strip()

        website_node = entry.find("website")
        value_node = entry.find("value")
        if website_node is not None and value_node is not None:
            if (website_node.text or "").strip().lower() == normalized:
                return (value_node.text or "").strip()

    return ""