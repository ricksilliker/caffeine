import os
import copy
import re

import yaml

from caffeine import logs, steps


DEFAULT_RECIPES = os.path.join(os.path.dirname(__file__), 'defaultRecipes')
LOG = logs.getLogger(__name__)
VARIABLE_EXPR = re.compile(r'^\${(.*)}')
STAGE_EXPR = re.compile(r'^(stage(\d*).(.*))')
STEP_RESPONSE_EXPR = re.compile(r'^((step)(\d*).(response).(.*))')


def loadRecipeFromPath(path):
    recipe = None

    if not path.endswith('.yaml'):
        err = dict(name='RecipeTypeError', message='recipe not a yaml file', path=path)
        return None, err
    
    with open(path, 'r') as fp:
        recipe = yaml.full_load(fp)

    return recipe, None


def loadRecipesFromPath(path):
    recipes = []

    for f in os.listdir(path):
        recipe, err = loadRecipeFromPath(os.path.join(path, f))
        if err is None:
            recipes.append(recipe)

    return recipes


def loadDefaultRecipes():
    return loadRecipesFromPath(DEFAULT_RECIPES)


class Recipe(object):
    def __init__(self):
        self._data = {}
        self._currentStage = 0
        self._currentStep = 0
        self._responses = []

    @classmethod
    def fromPath(cls, filepath):
        recipeData = loadRecipeFromPath(filepath)
        recipe = cls()
        recipe._data = recipeData[0]

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

    def getStepResponse(self, stageIndex, stepIndex):
        return self._responses[stageIndex][stepIndex]

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

    def resolveStepProps(self, props):
        for k, v in props.items():
            if isinstance(v, (list, tuple)):
                if all(isinstance(x, (str, unicode)) for x in v):
                    props[k] = [self.resolveExpression(x) for x in v]

            if not isinstance(v, (str, unicode)):
                continue

            props[k] = self.resolveExpression(v)

    def resolveExpression(self, v):
        variableMatch = re.match(VARIABLE_EXPR, v)
        varConstant = re.sub(VARIABLE_EXPR, '', v)

        if variableMatch is None:
            return varConstant
        fullVar = variableMatch.group(1)
        stageMatch = re.match(STAGE_EXPR, fullVar)
        if stageMatch:
            stageIndex = int(stageMatch.group(2))
            stage = self.stages[stageIndex]
            if 'name' in stageMatch.group(3):
                return stage['name'] + varConstant
        
        stepMatch = re.match(STEP_RESPONSE_EXPR, fullVar)
        if stepMatch:
            stepIndex = int(stepMatch.group(3))
            stepResponse = self.getStepResponse(self._currentStage, stepIndex)
            responseKey = str(stepMatch.group(5))
            if responseKey not in stepResponse:
                LOG.error('failed to find key in response %s', fullVar)
                return varConstant
            return stepResponse[responseKey] + varConstant

    def replay(self):
        pass

    def revert(self):
        self._responses = []
        self._currentStage = 0
        self._currentStep = 0

    def build(self, stepThrough=True):
        if self._currentStage == (self.numStages - 1):
            if self._currentStep == self.numStepsInStage(self._currentStage):
                LOG.debug('Reached the end of the recipe, nothing else to build.')
                return
        
        stepData = self.getStepFromStage(self._currentStage, self._currentStep)
        stepID = self.getStepID(stepData)
        allSteps = steps.getAvailableStepsByID()
        stepRunner = allSteps[stepID]
        stepProps = self.getStepProps(stepData)
        self.resolveStepProps(stepProps)
        stepRunner.loadData(stepProps)
        stepResponse = stepRunner.run()
        LOG.info(stepResponse.asDict())
        
        LOG.info('Step %s completed with a status %s', self._currentStep, stepResponse['status'])
        if len(self._responses) - 1 < self._currentStage:
            self._responses.append([])
        self._responses[self._currentStage].append(stepResponse)
        


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