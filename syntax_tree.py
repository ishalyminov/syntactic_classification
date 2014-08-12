import itertools
import sys


class DependencyTreeNode(object):
    def __init__(self, in_word_index, in_form, in_lemma, in_grammar):
        self.word_index = in_word_index
        self.form = in_form
        self.lemma = in_lemma
        self.grammar = in_grammar
        self.parent = None
        self.children = []
        self.children_types = []


class DependencyTree(object):
    def __init__(self):
        self.nodes = [DependencyTreeNode(0, 'ROOT', '', '')]

    def add_node(self, in_node):
        self.nodes.append(in_node)

    def add_link(self, in_from_index, in_to_index, in_link_type):
        child_node = self.find_node_by_index(in_to_index)
        parent_node = self.find_node_by_index(in_from_index)
        assert child_node is not None and parent_node is not None
        child_node.parent = parent_node
        parent_node.children.append(child_node)
        parent_node.children_types.append(in_link_type)

    def find_node_by_index(self, in_index):
        for node in self.nodes:
            if node.word_index == in_index:
                return node
        return None

    def get_root(self):
        return self.nodes[0]

    def get_words_number(self):
        return len(self.nodes) - 1


def build_tree(in_lines):
    result_tree = DependencyTree()
    links = []
    for word_index, line in zip(itertools.count(1), in_lines):
        tokens = line.strip().split('\t')
        assert len(tokens) > 3
        form, grammar = tokens[0], tokens[1]
        root = int(tokens[2])
        link_type = tokens[3] if len(tokens) > 3 else 'UNDEF'
        lemma = tokens[4] if len(tokens) > 4 else 'UNDEF'
        node = DependencyTreeNode(word_index, form, lemma, grammar)
        result_tree.add_node(node)
        links.append((root, word_index, link_type))

    for from_index, to_index, link_type in links:
        result_tree.add_link(from_index, to_index, link_type)
    return result_tree


def serialize_tree(in_tree, out_stream):
    for node in sorted(in_tree.nodes, key=lambda cmp_node: cmp_node.word_index)[1:]:
        node_parent = node.parent
        link_type = None
        for child_index in xrange(len(node_parent.children)):
            if node_parent.children[child_index] == node:
                link_type = node_parent.children_types[child_index]
                break
        node_serialized = [node.form, node.grammar, str(node.parent.word_index), link_type]
        print >>out_stream, '\t'.join(node_serialized)


def load_file(in_stream):
    result = []
    lines = in_stream.readlines()
    sentences = ''.join(lines).strip().split('\n\n')
    for sentence_lines in sentences:
        result.append(build_tree(sentence_lines.split('\n')))
    return result


if __name__ == '__main__':
    sentence = build_tree(open('example.txt').readlines())
    serialize_tree(sentence, sys.stdout)

