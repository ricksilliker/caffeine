import os
import types

import yaml

from caffeine import logs


LOG = logs.getLogger(__name__)
STEP_SUFFIX = '.step'


def loadStepFromPath(path):
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
                builderName = os.path.basename(path).replace('.step', '')
                builder = types.ModuleType(builderName)
                code = fp.read()
                builder.__file__ = builderPath
                exec code in builder.__dict__

    if config is None:
        err = dict(name='MissingConfigError', message='could not find Step config file', path=path)
        return None, err

    if builder is None:
        err = dict(name='MissingBuilderError', message='could not find Step builder file', path=path)
        return None, err

    return StepRunner(builder, config), None


def loadStepsFromDirectory(path):
    steps = []

    names = os.listdir(path)
    for name in names:
        if not name.endswith(STEP_SUFFIX):
            continue
        
        stepPath = os.path.join(path, name)
        step, err = loadStepFromPath(stepPath)
        if err is not None:
            LOG.error('failed to load step', **err)
        steps.append(step)

    return steps


def loadDefaultSteps():
    path = os.path.join(os.path.dirname(__file__), 'defaultSteps')
    
    return loadStepsFromDirectory(path)


def getAvailableStepsByID():
    result = {}
    
    for s in loadDefaultSteps():
        result[s.config['metadata']['id']] = s

    return result


class StepRunner(object):
    def __init__(self, builder, config):
        if not isinstance(builder, types.ModuleType):
            raise ValueError('builder should be a valid python module object')

        if not isinstance(config, dict):
            LOG.info(config)
            raise ValueError('config should be a valid dictionary object')

        # FUTURE: add validation to make sure step has an id

        self._builder = builder
        self._config = config
        self._props = dict()

    @property
    def config(self):
        return self._config

    @property
    def category(self):
        return self._config['metadata']['category']

    @property
    def title(self):
        return self._config['metadata']['title']

    def loadData(self, propData):
        self._props.update(propData)

    def getContext(self):
        result = dict()
        result.update(self._props)
        return result

    def run(self):
        ctx = self.getContext()
        try:
            response = self._builder.build(ctx)
        except Exception as e:
            LOG.exception(e)
            response = StepResponse.fromDict({'status': 400})

        if response is None:
            LOG.error('step missing StepReponse object')
            return StepResponse.fromDict({'status': 500})
        
        if not isinstance(response, StepResponse):
            LOG.error('step did not return a valid StepResponse object')
            return StepResponse.fromDict({'status': 500})

        return response


class StepResponse(object):
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

    def asDict(self):
        result = {}

        for k, v in self._data.items():
            result[k] = v

        return result
