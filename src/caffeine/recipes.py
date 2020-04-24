import os
import copy

import yaml

from caffeine import logs, steps


LOG = logs.getLogger(__name__)


def loadRecipeFromPath(path):
    recipe = None

    if not path.endswith('.yaml'):
        err = dict(name='RecipeTypeError', message='recipe not a yaml file', path=path)
        return None, err
    
    with open(path, 'r') as fp:
        recipe = yaml.full_load(fp)

    return recipe, None


class Recipe(object):
    def __init__(self):
        self._data = {}
        self._currentStage = 0
        self._currentStep = 0

    @classmethod
    def fromPath(cls, filepath):
        recipeData = loadRecipeFromPath(filepath)
        recipe = cls()
        recipe._data = recipeData

        return recipe

    @property
    def stages(self):
        return self._data.get('stages', [])

    @property
    def numStages(self):
        return len(self.stages)

    def numStepsInStage(self, index):
        return len(self.stages[index].get('steps', []))

    def getStepFromStage(self, stageIndex, stepIndex):
        if stageIndex >= len(self.stages):
            LOG.error('stage index is invalid')
            return

        stage = self.stages[stageIndex]
        stageSteps = stage.get('steps', [])
        if stageSteps:
            return stageSteps[stepIndex]

    def getStepID(self, stepData):
        return stepData.keys()[0]

    def getStepProps(self, stepData):
        return stepData.values()[0]

    def getStepsFromStage(self, index):
        st = self.stages[index]

        declaredSteps = st.get('steps', [])
        allSteps = steps.getAvailableStepsByID()

        err = []
        for s in declaredSteps:
            if s not in allSteps:
                LOG.error('missing step %s', s)
                e = dict(name='StepMissingError', message='step not registered', id=s)
                err.append(e)

        if err != None:
            return None, err

        return declaredSteps, None

    def replay(self):
        pass

    def revert(self):
        pass

    def build(self, stepThrough=True):
        if self._currentStage == (self.numStages - 1):
            if self._currentStep == self.numStepsInStage(self._currentStage):
                LOG.debug('Reached the end of the recipe, nothing else to build.')
                return
        
        stepData = self.getStepFromStage(self._currentStage, self._currentStep)
        stepID = self.getStepID(stepData)
        allSteps = steps.getAvailableStepsByID()
        stepRunner = allSteps[stepID]
        stepRunner.loadData(self.getStepProps(stepData))
        stepRunner.run()

        if self._currentStep >= self.numStepsInStage(self._currentStage):
            if self._currentStage != (self.numStages - 1):
                LOG.debug('Incrementing to next stage.')
                self._currentStep = 0
                self._currentStage += 1
            else:
                LOG.debug('Reached the end of the recipe.')
        else:
            LOG.debug('Incrementing to next step.')
            self._currentStep += 1