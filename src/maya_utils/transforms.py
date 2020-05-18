# built-in imports
import logging

# maya imports
from maya.api import OpenMaya
from maya import cmds


# constants
LOG = logging.getLogger(__name__)


def get_world_matrix(transform):
    """Get the world matrix of a given transform.

    Args:
        transform(str): Node name or node full path.

    Returns:
        OpenMaya.MMatrix
    """
    is_transform = transform.hasFn(OpenMaya.MFn.kTransform)
    if isinstance(transform, OpenMaya.MObject) and is_transform:
        transform = OpenMaya.MFnDependencyNode(transform).name()

    if not isinstance(transform, (str, unicode)):
        LOG.exception('transform must be the node name or full node path.')
        return

    matrix_array = cmds.xform(transform, q=True, worldSpace=True, matrix=True)
    m_matrix = OpenMaya.MMatrix(matrix_array)

    return m_matrix


def get_local_matrix(transform):
    is_transform = transform.hasFn(OpenMaya.MFn.kTransform)
    if isinstance(transform, OpenMaya.MObject) and is_transform:
        transform = OpenMaya.MFnDependencyNode(transform).name()

    if not isinstance(transform, (str, unicode)):
        LOG.exception('transform must be the node name or full node path.')
        return

    matrix_array = cmds.xform(transform, q=True, objectSpace=True, matrix=True)
    m_matrix = OpenMaya.MMatrix(matrix_array)

    return m_matrix


def get_matrix_row(matrix, row_index):
    """Get the row vector of a matrix.

    Args:
        matrix(OpenMaya.MMatrix): A transform's matrix.
        row_index(int): Row index of a matrix.

    Returns:
        list[float]
    """
    result = []
    for column_index in (0, 1, 2):
        result.append(matrix.getElement(row_index, column_index))

    return result