import re
from aqt import gui_hooks
from aqt.qt import QMimeData

def on_paste_mime(mime, editor, internal, extended, drop_event):
    """
    Hooks into Anki's clipboard processing.
    """
    # 1. Safety checks
    if not mime.hasText():
        return mime

    text = mime.text()

    # Quick exit if no dollar signs
    if '$' not in text:
        return mime

    # 2. Perform Replacements
    new_text = text

    # Pattern A: Display Math $$...$$ -> \[...\]
    # flags=re.DOTALL allows matches to span across newlines
    new_text = re.sub(r'\$\$(.*?)\$\$', lambda m: r'\[' + m.group(1) + r'\]', new_text, flags=re.DOTALL)

    # Pattern B: Inline Math $...$ -> \(...\)
    # We do NOT use DOTALL here to avoid accidentally matching text between
    # two completely separate currency symbols in a paragraph.
    new_text = re.sub(r'(?<!\\)\$(.*?)(?<!\\)\$', lambda m: r'\(' + m.group(1) + r'\)', new_text)

    # If nothing changed, return original mime data
    if new_text == text:
        return mime

    # 3. Create a fresh MimeData object
    # We cannot just modify the existing 'mime' object because Anki might
    # still prioritize the 'text/html' part of the clipboard.
    # By creating a new object with ONLY text, we force Anki to use our cleaned version.
    new_mime = QMimeData()
    new_mime.setText(new_text)

    return new_mime

# Register the hook
gui_hooks.editor_will_process_mime.append(on_paste_mime)
