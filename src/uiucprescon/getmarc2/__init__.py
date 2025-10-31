"""Get MARC XML from ALMA using their API."""
from .records import get_from_bibid, is_validate_xml

__all__ = [
    'get_from_bibid',
    'is_validate_xml'
]
