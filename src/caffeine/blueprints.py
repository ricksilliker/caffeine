import os
import types

import yaml

from caffeine import logs, props

LOG = logs.getLogger(__name__)
BLUEPRINT_SUFFIX = '.blueprint'


def loadFromPath(path):
    config = None
    builder = None

    names = os.listdir(path)
    for name in names:
        if builder is not None and config is not None:
            break

        if name == 'config.yaml':
            configPath = os.path.join(path, name)
            with open(configPath, 'r') as fp:
                config = yaml.full_load(fp)

        if name == 'builder.py':
            builderPath = os.path.join(path, name)

            with open(builderPath, 'r') as fp:
                builderName = os.path.basename(path).replace(BLUEPRINT_SUFFIX, '')
                builder = types.ModuleType(builderName)
                code = fp.read()
                builder.__file__ = builderPath
                exec code in builder.__dict__

    if config is None:
        err = dict(name='MissingConfigError', message='could not find Blueprint config file', path=path)
        return None, err

    if builder is None:
        err = dict(name='MissingBuilderError', message='could not find Blueprint builder file', path=path)
        return None, err

    return BlueprintData(builder, config), None


def loadFromDirectory(path):
    blueprints = []
    names = os.listdir(path)
    for name in names:
        if not name.endswith(BLUEPRINT_SUFFIX):
            continue
        blueprintPath = os.path.join(path, name)
        bp, err = loadFromPath(blueprintPath)
        if err is not None:
            LOG.error('failed to load blueprint', **err)
        blueprints.append(bp)
    return blueprints


def loadAvailableByTitle(path):
    result = {}
    for b in loadFromDirectory(path):
        result[b.config['metadata']['title']] = b
    return result


class BlueprintHierarchy(object):
    def __init__(self):
        self.blueprints = []

    def addBlueprint(self, bp):
        res = dict(blueprint=bp, children=[])
        if bp in self.blueprints:
            return self.blueprints.index(bp)
        self.blueprints.append(res)
        return len(self.blueprints) - 1

    def addChild(self, parentIndex, bp):
        childIndex = self.addBlueprint(bp)
        self.blueprints[parentIndex]['children'].append(childIndex)
        return childIndex

    def clear(self):
        self.blueprints = []


class BlueprintData(object):
    def __init__(self, builder, config):
        if not isinstance(builder, types.ModuleType):
            raise ValueError('builder should be a valid python module object')

        if not isinstance(config, dict):
            LOG.info(config)
            raise ValueError('config should be a valid dictionary object')

        self._builder = builder
        self._config = config
        self._props = []
        for name, conf in config['properties'].items():
            self._props.append(props.PropData(name, conf))

    @property
    def props(self):
        return self._props

    @property
    def config(self):
        return self._config

    @property
    def builder(self):
        return self._builder

    @property
    def name(self):
        for prop in self._props:
            if prop.name == 'name':
                return prop.value
        return ''

    @property
    def componentType(self):
        return self._config['metadata']['title']

    def create(self):
        try:
            return self._builder.create()
        except Exception as err:
            LOG.exception('failed to create Blueprint')
            e = dict(name='BlueprintCreateError', status=500, message='failed to create Blueprint')
            return BlueprintResponse.fromDict(e)

    def updateFromContext(self, **kwargs):
        data = self._builder.initCallback(**kwargs)
        for k, v in data.items():
            for prop in self._props:
                if prop.name == k:
                    prop.value = v


class BlueprintResponse(object):
    def __init__(self):
        self._data = {}

    @classmethod
    def fromDict(cls, d):
        resp = cls()
        for k, v in d.items():
            resp._data[k] = v

        return resp

    def __getitem__(self, key):
        return self._data.get(key, None)

    def __contains__(self, key):
        if key in self._data:
            return True

        return False

    def asDict(self):
        result = {}

        for k, v in self._data.items():
            result[k] = v

        return result
