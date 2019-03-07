class Dictionary:
    def __init__(self, config):
        self.config = config
        self.content = []

        for t in self.config['tokens']:
            self.content.append(t)
        if self.config['bytes']:
            for b in range(256):
                self.content.append(bytes([b]))
        # suppose `config` is {'tokens' : ['wasfd', 'asdf'], 'bytes' : True}.
        # then now
        # self.content would be ['wasfd', 'asdf', b'\x00', b'\x01', b'\x02',  ...  ,b'\xff']

    def size(self):
        return len(self.content) + 1

    def eof(self):
        return len(self.content)

    def bytes(self, i):
        if i >= len(self.content):
            return b""
        else:
            return self.content[i]
