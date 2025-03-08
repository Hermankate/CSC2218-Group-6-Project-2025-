import webbrowser

def share_on_x(note_title, note_content):
    url = f"https://twitter.com/intent/tweet?text={note_title}: {note_content}"
    webbrowser.open(url)

def share_on_facebook(note_title, note_content):
    url = f"https://www.facebook.com/sharer/sharer.php?u={note_content}"
    webbrowser.open(url)
