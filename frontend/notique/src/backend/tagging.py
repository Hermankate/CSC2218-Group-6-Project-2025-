import re

def extract_tags(note_content):
    tags = re.findall(r"@\w+|#\w+", note_content)
    return tags
