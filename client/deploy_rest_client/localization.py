import os
import locale
import gettext

import constant
# localdir
rootdir = os.path.dirname(constant.__file__)

def get_to_text(_text):
    transLoc = rootdir +"/i18n"
    if locale.getdefaultlocale() == ('ru_RU', 'UTF-8'):
        _lang = 'ru'
    else:
        _lang = 'en'
    t = gettext.translation('client', transLoc, languages=[_lang])
    _ = t.ugettext
    t.install()
    return _(_text)
