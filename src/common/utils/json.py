import json


class JsonFile:

    def __init__(self,
                 filename: str,
                 ensure_ascii: bool = False,
                 sort_keys: bool = False,
                 indent: int = 2):
        self.filename = filename
        self.ensure_ascii = ensure_ascii
        self.sort_keys = sort_keys
        self.indent = indent

    def write(self, data):
        with open(self.filename, mode="w", encoding='utf-8') as file:
            json.dump(
                data,
                file,
                ensure_ascii=self.ensure_ascii,
                sort_keys=self.sort_keys,
                indent=self.indent
            )
