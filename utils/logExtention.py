import logging
from collections import defaultdict


# from https://qiita.com/podhmo/items/efb65ed90871ba2ac544
FORMAT="%(asctime)s %(levelname)s %(name)s %(message)s[%(call_count)d]"

class Extension:
    def __init__(self):
        self.c = defaultdict(int)


class LogRecordExtension(logging.LogRecord):
    extension = Extension()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extension.c[self.msg] += 1
        self.call_count = self.extension.c[self.msg]
