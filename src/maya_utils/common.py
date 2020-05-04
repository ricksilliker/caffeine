# built-in imports
import logging

# maya imports
from maya.api import OpenMaya
from maya import cmds


# constants
LOG = logging.getLogger(__name__)


def get_mobject(nodePath):
    if not isinstance(nodePath, (str, unicode)):
        return

    sel = OpenMaya.MSelectionList()
    sel.add(nodePath)

    return sel.getDependNode(0)


def get_mobjects(nodePaths):
    if not isinstance(nodePaths, (list, tuple)):
        return []

    result = []
    for nodepath in nodePaths:
        n = get_mobject(nodepath)
        result.append(n)

    return result


def get_dagPath(nodePath):
    sel = OpenMaya.MSelectionList()
    sel.add(nodePath)

    return sel.getDagPath(0)


def iter_selection():
    sel = OpenMaya.MGlobal.getActiveSelectionList()
    for i in range(sel.length()):
        yield sel.getDependNode(i)


def get_plug(node, plug_name, use_index=-1, use_next_index=False):
    """Get a valid MPlug from an MObject and attribute name.

    Args:
        node(OpenMaya.MObject): An existing node.
        plug_name(str): An existing attribute name.
        use_index(int): If an array attribute, use this index.
        use_next_index(bool): If an array plug, use the next available element.

    Returns:
        OpenMaya.MPlug
    """
    node_fn = OpenMaya.MFnDependencyNode(node)
    attr = node_fn.attribute(plug_name)

    LOG.debug('Getting attribute %s for node %s', plug_name, node_fn.name())

    try:
        plug = OpenMaya.MPlug(node, attr)
    except RuntimeError:
        LOG.exception(
            'could not find attribute %s on node %s',
            plug_name, node_fn.name())

    if use_index > -1:
        try:
            plug = plug.elementByLogicalIndex(use_index)
        except RuntimeError:
            LOG.exception(
                'attribute was not an array plug %s.%s',
                node_fn.name(), plug_name)
            return

    if use_next_index:
        try:
            num_elements = plug.evaluateNumElements()
            plug = plug.elementByLogicalIndex(num_elements)
        except RuntimeError:
            LOG.exception(
                'attribute was not an array plug %s.%s',
                node_fn.name(), plug_name)
            return

    return plug


def connect_plugs(out_plug, in_plug):
    """Connect a source MPlug to a destination MPlug.

    Args:
        out_plug(OpenMaya.MPlug): source.
        in_plug(OpenMaya.MPlug): destination.

    Returns:
        None
    """

    if not isinstance(out_plug, OpenMaya.MPlug) or out_plug.node().isNull():
        LOG.error('source must be of type OpenMaya.MPlug')
        return

    if not isinstance(in_plug, OpenMaya.MPlug) or in_plug.node().isNull():
        LOG.error('destination must be of type OpenMaya.MPlug')
        return

    LOG.debug('%s >> %s', out_plug.name(), in_plug.name())

    dgModifier = OpenMaya.MDGModifier()
    dgModifier.connect(out_plug, in_plug)
    dgModifier.doIt()


def copy_mesh(mesh, keep_parent=False):
    if keep_parent:
        parent_node = OpenMaya.MFnDagNode(mesh).parent(0)
    else:
        parent_node = OpenMaya.MFnDependencyNode().create('transform')

    out_mesh = OpenMaya.MFnMesh().copy(mesh, parent_node)
    return out_mesh, parent_node


def get_name(mobject):
    return OpenMaya.MFnDependencyNode(mobject).name()


def get_fullpath(mobject):
    return OpenMaya.MFnDagNode(mobject).fullPathName()