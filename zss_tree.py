"""
    Tree operations and structures for integration with Zhang-Shasha distance
"""
import codecs

import itertools
import zss


class DependencyTree(object):
    def __init__(self, in_lines):
        self.nodes = []
        self.parents = []
        self.links = []
        self.load_tree(in_lines)

    def load_tree(self, in_lines):
        nodes = [zss.Node('root')]
        links = []
        parents = [0]
        for (line_index, line) in zip(itertools.count(1), in_lines):
            tokens = line.strip().split('\t')
            # probably punctuation
            if len(tokens) < 2:
                continue
            # form, grammar
            node = (tokens[0], tokens[1])
            root = int(tokens[2])
            link_type = tokens[3] if len(tokens) > 3 else 'UNDEF'
            nodes.append(zss.Node('|'.join(node)))
            parents.append(root)
            links.append((root, line_index))
        for (from_index, to_index) in links:
            nodes[from_index].addkid(nodes[to_index])
        assert len(nodes) == len(parents)
        self.nodes = nodes
        self.links = links
        self.parents = parents

    def get_root(self):
        return self.nodes[0]

    def to_string(self):
        return ' '.join([node.label for node in self.nodes])

    def __len__(self):
        return len(self.nodes)


def load_file(in_file):
    result = []
    lines = codecs.getreader('utf-8')(open(in_file)).readlines()
    sentences = ''.join(lines).strip().split('\n\n')
    for sentence in sentences:
        result.append(DependencyTree(sentence.split('\n')))
    return result


def print_sentence(in_sentence, in_result_stream):
    for node, parent in zip(in_sentence.nodes, in_sentence.parents):
        print >>in_result_stream, '%s\t%d' % (node.label, parent)
