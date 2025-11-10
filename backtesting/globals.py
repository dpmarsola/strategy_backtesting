class Globals():
    
    _instance = None
    _store = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def save(self, key, value):
        self._store[key] = value

    def get(self, key, default=None):
        return self._store.get(key, default)

    def clear(self):
        self._store.clear()

    def list_all_globals(self):
        return self._store