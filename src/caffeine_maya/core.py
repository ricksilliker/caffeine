from maya.api import OpenMaya


def addRigComponentAttr(mobject):
    modifier = OpenMaya.MDagModifier()
    attr = OpenMaya.MFnGenericAttribute().create('rigComponent', 'rigComponent')
    modifier.addAttribute(mobject, attr)
    modifier.doIt()


def createNewBone():
    modifier = OpenMaya.MDagModifier()
    mobject = modifier.createNode('joint')
    modifier.doIt()
    dependNode = OpenMaya.MFnDependencyNode(mobject)
    dependNode.setName('NewBone#')
    addRigComponentAttr(mobject)


def getRigComponents():
    result = []

    iterator = OpenMaya.MItDag()
    while not iterator.isDone():
        dagNode = OpenMaya.MFnDagNode(iterator.getPath())
        if not dagNode.hasAttribute('rigComponent'):
            iterator.next()
            continue
        parent = dagNode.parent(0)
        if parent.hasFn(OpenMaya.MFn.kWorld):
            parent = None
        result.append({
            'name': dagNode.name(),
            'node': iterator.currentItem(),
            'parent': parent
        })
        iterator.next()

    for nodeData in result:
        if nodeData['parent'] is None:
            continue
        for i, x in enumerate(result):
            if isinstance(nodeData['parent'], OpenMaya.MObject):
                if nodeData['parent'] == x['node']:
                    nodeData['parent'] = i
                    continue
    return result


class ComponentData(object):
    def __init__(self):
        self._mobject = None
        self._nodeType = ''
        self._fields = []

    def initialize(self):
        if self._mobject is None:
            return

        if self._mobject.hasFn(OpenMaya.MFn.kJoint):
            self._nodeType = 'Bone'
            self._fields.append(ComponentField('name', 'str'))
            self._fields.append(ComponentField('initialTransform', 'transform'))


    @property
    def fields(self):
        return self._fields

    @classmethod
    def getComponentData(cls, mobject):
        result = cls()
        result._mobject = mobject
        result.initialize()
        return result


class ComponentField(object):
    def __init__(self, name, dataType, group=None):
        self._dataType = dataType
        self._name = name
        self._group = group

    @property
    def dataType(self):
        return self._dataType

    @property
    def group(self):
        return self._group

    @property
    def name(self):
        return self._name
