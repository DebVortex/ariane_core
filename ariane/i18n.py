import gettext as gt
import os

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__), 'locale'))
translate = gt.translation('ariane', localedir, fallback=True)

_ = translate.gettext
