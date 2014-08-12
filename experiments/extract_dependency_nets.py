#coding: utf-8
import codecs

import os
import sys

sys.path.append('..')

import syntax_tree


def extract_links_in_subtree(in_subtree_root, in_link_types):
    result_links = []
    for child_index in xrange(len(in_subtree_root.children)):
        link_type = in_subtree_root.children_types[child_index]
        child = in_subtree_root.children[child_index]
        if link_type in in_link_types:
            result_links.append((in_subtree_root.word_index, child.word_index, link_type))
        result_links += extract_links_in_subtree(child, in_link_types)
    return result_links


def build_dependency_net(in_sentence_tree, in_link_list):
    root = in_sentence_tree.get_root()
    dependency_links = extract_links_in_subtree(root, in_link_list)
    links_sorted = sorted(dependency_links)
    result_net = syntax_tree.DependencyTree()
    for from_index, to_index, link_type in links_sorted:
        if not result_net.find_node_by_index(from_index):
            node = in_sentence_tree.find_node_by_index(from_index)
            result_net.add_node(node)
        if not result_net.find_node_by_index(to_index):
            node = in_sentence_tree.find_node_by_index(to_index)
            result_net.add_node(node)
        result_net.add_link(0, from_index, 'primary')
        result_net.add_link(from_index, to_index, link_type)
    return result_net


def load_all_sentences_as_dependency_trees(in_texts_root):
    result = []
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        for filename in files:
            full_filename = os.path.join(root, filename)
            print 'processing file: ', full_filename
            result += syntax_tree.load_file(codecs.getreader('utf-8')(open(full_filename)))
    return result


def process_folder(in_text_root, in_predicates_list):
    trees = load_all_sentences_as_dependency_trees(in_text_root)
    for tree in trees:
        dependency_net = build_dependency_net(tree, in_predicates_list)
        syntax_tree.serialize_tree(dependency_net, codecs.getwriter('utf-8')(sys.stdout))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: extract_dependency_nets.py <SyntagRus plaintext root>'
        exit()
    process_folder(sys.argv[1], [u'предик', u'1-компл', u'2-компл', u'3-компл', u'4-компл', u'5-компл', u'агент'])