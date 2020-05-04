from maya import cmds

from caffeine.logs import getActionLogger
from caffeine import steps


LOG = getActionLogger('constrain')


def build(ctx):
    LOG.info('Building task.')
    pc = cmds.parentConstraint(ctx['target'], ctx['followers'], mo=ctx['maintainOffset'])
    sc = cmds.scaleConstraint(ctx['target'], ctx['followers'], mo=ctx['maintainOffset'])

    return steps.StepResponse.fromDict({
        'status': 200,
        'parentConstraint': pc,
        'scaleConstraint': sc
    })


def save(ctx, response):
    pass