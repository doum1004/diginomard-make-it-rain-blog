from utils import SaveUtils

saveUtils = SaveUtils('__output', localSetting=True)
saveUtils.saveData('url', 'https://code.visualstudio.com/assets/docs/python/environments/selected-interpreter-status-bar.png')
saveUtils.saveImageFromURL('url', 'https://code.visualstudio.com/assets/docs/python/environments/selected-interpreter-status-bar.png')