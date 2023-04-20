from html import escape

def res_header(name, text):
    return f'<b>{name}:</b> <code>{escape(text)}</code>\n'