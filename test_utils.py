import os
from diginomard_toolkit.utils import SaveUtils

saveUtils = SaveUtils('__output/test')

def test_SaveUtils():
    path = saveUtils.saveData('url', 'https://code.visualstudio.com/assets/docs/python/environments/selected-interpreter-status-bar.png')
    assert(os.path.exists(path))