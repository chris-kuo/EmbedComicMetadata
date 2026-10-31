from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__docformat__ = 'restructuredtext en'

'''
Helpers for reading reading-direction information from an epub.
Deliberately free of calibre imports so it can be tested standalone.
'''

import zipfile
import xml.etree.ElementTree as ET

CONTAINER_PATH = 'META-INF/container.xml'


def _local(tag):
    '''Strip the XML namespace from a tag name.'''
    return tag.rsplit('}', 1)[-1]


def _find_opf_path(zf):
    root = ET.fromstring(zf.read(CONTAINER_PATH))
    for el in root.iter():
        if _local(el.tag) == 'rootfile' and el.get('full-path'):
            return el.get('full-path')
    return None


def epub_page_progression_direction(path_or_file):
    '''
    Returns the lower-cased value of the page-progression-direction attribute
    on the OPF <spine> ('rtl', 'ltr', 'default') or None if absent/unreadable.
    '''
    try:
        zf = zipfile.ZipFile(path_or_file)
    except Exception:
        return None
    try:
        opf_path = _find_opf_path(zf)
        if opf_path is None:
            return None
        opf = ET.fromstring(zf.read(opf_path))
        for el in opf.iter():
            if _local(el.tag) == 'spine':
                value = el.get('page-progression-direction')
                return value.strip().lower() if value else None
    except Exception:
        return None
    finally:
        zf.close()
    return None


def epub_is_rtl(path_or_file):
    '''True if the epub's spine declares page-progression-direction="rtl".'''
    return epub_page_progression_direction(path_or_file) == 'rtl'
