HTML_ESCAPE_DICT = {
    '<': '&lt;',
    '>': '&gt;',
    
    '&':'&amp;',
    '"':'&quot;',
    "'":'&#39;',
    
}

def html_escape(text):
    for escape in HTML_ESCAPE_DICT:
        text = text.replace(escape, HTML_ESCAPE_DICT[escape])
    
    return text
