import numpy


def cosine(in_lhs, in_rhs):
    # (lhs_norm, rhs_norm) = (numpy.linalg.norm(in_lhs), numpy.linalg.norm(in_rhs))
    # result = numpy.dot(in_lhs / lhs_norm, (in_rhs / rhs_norm).T)
    result = numpy.dot(in_lhs, in_rhs.T)
    return result


def jaccard_distance(in_lhs, in_rhs):
    (set_lhs, set_rhs) = (set(in_lhs), set(in_rhs))
    jaccard_index = len(set_lhs.intersection(set_rhs)) / float(len(set_lhs.union(set_rhs)))
    return 1.0 - jaccard_index


def tree_edit_distance(in_lhs, in_rhs):
    pass