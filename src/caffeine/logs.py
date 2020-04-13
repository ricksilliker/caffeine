import logging


def getLogger(name=None, level=logging.DEBUG, propagate=False):
    if name is None:
        return logging.root

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = propagate

    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())

    adapter = StructuredLogAdapter(logger, dict())

    return adapter


class StructuredLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        record = '{0} \n'.format(msg)
        for k, v in kwargs.items():
            record += '\t{0}: {1}\n'.format(k, v)

        return record, dict()


def getActionLogger(taskName):
    return getLogger('caffeine.{0}'.format(taskName), level=logging.INFO)