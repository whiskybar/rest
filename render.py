from docutils.core import publish_string
from urllib import unquote_plus

def render(event, context):
    return publish_string(
        source=unquote_plus(event.get('content', '')),
        settings_overrides={'file_insertion_enabled': 0, 'raw_enabled': 0},
        writer_name='html',
    )

