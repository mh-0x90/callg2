from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET


def store_piece(piece: str, other_text: str, xml_path: str = "rasht_output.xml") -> Path:
    root = ET.Element("entries")

    path = Path(xml_path)
    if path.exists():
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            root = ET.Element("entries")

    entry = ET.SubElement(root, "entry")
    value = ET.SubElement(entry, "value")
    value.text = piece
    other = ET.SubElement(entry, "other")
    other.text = other_text

    tree = ET.ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return path
