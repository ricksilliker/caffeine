class PropData(object):
    def __init__(self, name, config):
        self._name = name
        self._dataType = config.get('type', 'null')
        self._description = config.get('description', '')
        self._hidden = config.get('hidden', False)
        self._currentValue = None

    @property
    def description(self):
        return self._description

    @property
    def dataType(self):
        return self._dataType

    @property
    def name(self):
        return self._name

    @property
    def hidden(self):
        return self._hidden

    @property
    def value(self):
        return self._currentValue

    @value.setter
    def value(self, data):
        self._currentValue = data