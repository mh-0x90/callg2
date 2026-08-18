

from flask import redirect,url_for
receipt_templates = {
    "compact": "receipt_compact.html",
    "standard": "receipt_compact.html",
}
def validate_style(style_name:str):
    return style_name in receipt_templates.keys()

def compact_mode_check(md="") -> None:
        return redirect(f"/audit/{md}")


