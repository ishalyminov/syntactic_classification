import itertools
import sys

'''
    Sentence as a syntactic tree.
    Contains nodes - tuples ('word form', 'grammar tags'),
    dependency link lists - links[src_node_index] = [(dst_node_index, 'dependency type')].
    Tree's 0th node is always the ROOT, all the 'word' nodes start from 1.
'''


class Sentence(object):
    def __init__(self):
        self.nodes = [('ROOT', '')]
        self.parents = [None]
        self.links = [[]]

    def add_link(self, in_word_tuple, in_parent_index, in_link_type):
        word_index = len(self.nodes)
        self.nodes.append(in_word_tuple)
        self.parents.append(in_parent_index)
        self.__create_link_lists(in_parent_index)
        if word_index not in self.links[in_parent_index]:
            self.links[in_parent_index].append((word_index, in_link_type))

    def get_link(self, in_src_index, in_dst_index):
        for link in self.links[in_src_index]:
            if link[0] == in_dst_index:
                return link
        return None

    def __create_link_lists(self, in_index):
        while len(self.links) < in_index + 1:
            self.links.append([])

    def __iter__(self):
        for word in self.nodes[1:]:
            yield word


def deserialize_sentence(in_lines):
    result_sentence = Sentence()
    for line in in_lines:
        tokens = line.strip().split('\t')
        assert len(tokens) > 2
        # form, grammar
        node = (tokens[0], tokens[1])
        root = int(tokens[2])
        link_type = tokens[3] if len(tokens) > 3 else 'UNDEF'
        result_sentence.add_link(node, root, link_type)
    return result_sentence


def serialize_sentence(in_sentence, out_stream):
    for (word, word_index, parent_index) in zip(in_sentence.nodes[1:],
                                                itertools.count(1),
                                                in_sentence.parents[1:]):
        link_from_parent = in_sentence.get_link(parent_index, word_index)
        print >>out_stream, '\t'.join(word + (str(parent_index), link_from_parent[1]))


def load_file(in_stream):
    result = []
    lines = open(in_stream).readlines()
    sentences = ''.join(lines).strip().split('\n\n')
    for sentence_lines in sentences:
        result.append(deserialize_sentence(sentence_lines.split('\n')))
    return result


if __name__ == '__main__':
    sentence = deserialize_sentence(open('example.txt').readlines())
    serialize_sentence(sentence, sys.stdout)

