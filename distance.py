import zss


def distance_jaccard(in_sentence_a, in_sentence_b):
    a_set, b_set = set(in_sentence_a), set(in_sentence_b)
    return len(a_set.intersection(b_set)) / float(a_set.union(b_set))


def distance_syntactic(in_sentence_a, in_sentence_b):
    edit_distance = zss.simple_distance(in_sentence_a.get_root(),
                                        in_sentence_b.get_root(),
                                        label_dist=lambda x, y: x != y)
    return edit_distance / float(len(in_sentence_a) + len(in_sentence_b))


def distance_syntactic_advanced(in_sentence_a, in_sentence_b):
    edit_distance = zss.simple_distance(in_sentence_a.get_root(),
                                        in_sentence_b.get_root(),
                                        label_dist=lambda x, y: x != y)
    return edit_distance / float(len(in_sentence_a) + len(in_sentence_b))
