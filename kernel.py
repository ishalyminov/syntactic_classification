import numpy


def cosine(in_lhs, in_rhs):
    # (lhs_norm, rhs_norm) = (numpy.linalg.norm(in_lhs), numpy.linalg.norm(in_rhs))
    # result = numpy.dot(in_lhs / lhs_norm, (in_rhs / rhs_norm).T)
    result = numpy.dot(in_lhs, in_rhs.T)
    return result

def graph_kernel(in_lhs, in_rhs):
    return 1.0
