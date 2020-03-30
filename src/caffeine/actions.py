import os
import logs
import toml
import imp
import types

LOG = logs.getLogger(__name__)
ACTION_SUFFIX = '.action'


def loadActionFromPath(path):
    config = None
    builder = None
    
    names = os.listdir(path)
    for name in names:
        if builder is not None and config is not None:
            break

        if name == 'config.toml':
            configPath = os.path.join(path, name)
            config = toml.load(configPath)

        if name == 'builder.py':
            builderPath = os.path.join(path, name)

            with open(builderPath, 'r') as fp:
                builderName = os.path.basename(path).replace('.action', '')
                builder = types.ModuleType(builderName)
                code = fp.read()
                builder.__file__ = builderPath
                exec code in builder.__dict__

    if config is None:
        err = dict(name='MissingConfigError', message='could not find Action config file', path=path)
        return None, err

    if builder is None:
        err = dict(name='MissingBuilderError', message='could not find Action builder file', path=path)
        return None, err

    return ActionData(builder, config), None


def loadActionsFromDirectory(path):
    actions = []

    names = os.listdir(path)
    for name in names:
        if not name.endswith(ACTION_SUFFIX):
            continue
        
        actionPath = os.path.join(path, name)
        action, err = loadActionFromPath(actionPath)
        if err is not None:
            LOG.error('failed to load action', **err)
        actions.append(action)

    return actions


def loadDefaultActions():
    path = os.path.join(os.path.dirname(__file__), 'defaultActions')
    
    return loadActionsFromDirectory(path)


class ActionData(object):
    def __init__(self, builder, config):
        if not isinstance(builder, types.ModuleType):
            raise ValueError('builder should be a valid python module object')

        if not isinstance(config, dict):
            raise ValueError('config should be a valid dictionary object')

        self._builder = builder
        self._config = config

    @property
    def config(self):
        return self._config

    @property
    def category(self):
        return self._config['metadata']['category']

    @property
    def title(self):
        return self._config['metadata']['title']

    def run(self):
        ctx = self.getContext()
        response = self._builder.build(ctx)

        return response


class ActionResponse(object):
    def __init__(self):
        self._status = None
        self._data = {}

    def asDict(self):
        result = {}

        for k, v in self._data.items():
            result[k] = v

        result['status'] = self._status

        return result
