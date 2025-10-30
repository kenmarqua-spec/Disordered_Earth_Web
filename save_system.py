import json, gzip, os, tempfile
from datetime import datetime
SAVE_FILENAME = 'world_save.json.gz'
SAVE_VERSION = '1.0'
class SaveManager:
    def __init__(self, filename=None):
        self.filename = filename or SAVE_FILENAME
    def save(self, data):
        data_out = {'save_version': SAVE_VERSION, 'timestamp': datetime.utcnow().isoformat()+'Z', 'payload': data}
        raw = json.dumps(data_out, separators=(',',':')).encode('utf-8')
        dirpath = os.path.dirname(os.path.abspath(self.filename)) or '.'
        fd, tmp = tempfile.mkstemp(dir=dirpath, prefix='tmp_save_', suffix='.gz'); os.close(fd)
        try:
            with gzip.open(tmp,'wb') as f: f.write(raw)
            os.replace(tmp, self.filename)
        finally:
            if os.path.exists(tmp):
                try: os.remove(tmp)
                except: pass
    def load(self):
        if not os.path.exists(self.filename): return None
        with gzip.open(self.filename,'rb') as f:
            raw = f.read(); return json.loads(raw.decode('utf-8'))
    def exists(self):
        return os.path.exists(self.filename)
