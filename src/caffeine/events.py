import logging


LOG = logging.getLogger(__name__)


class Event(object):
    def __init__(self, name):
        self._name = name
        self._blocking = False
        self._callbacks = []

    @property
    def name(self):
        return self._name

    def block(self, value):
        self._blocking = value

    def connect(self, cb):
        self._callbacks.append(cb)

    def disconnect(self, cb):
        self._callbacks.remove(cb)

    def clear(self):
        self._callbacks = []

    def emit(self, *args, **kwargs):
        if self._blocking:
            return

        for cb in self._callbacks:
            try:
                cb(*args, **kwargs)
            except Exception as err:
                LOG.error('callback for %s errored', self._name, exc_info=True)
