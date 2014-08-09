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


def extract_frame(in_dependency_tree, in_link_list):
    root = in_dependency_tree.get_root()
    links = extract_links_in_subtree(root, in_link_list)
    return links


def load_all_sentences_as_dependency_trees(in_texts_root):
    result = []
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        for filename in files:
            full_filename = os.path.join(root, filename)
            print 'processing file: ', full_filename
            result += syntax_tree.load_file(codecs.getreader('utf-8')(open(full_filename)))
    return result


def process_folder(in_text_root, in_predicates_list):
    frames = []
    trees = load_all_sentences_as_dependency_trees(in_text_root)
    for tree in trees:
        links = extract_frame(tree, in_predicates_list)
        for word_a_index, word_b_index, link_type in links:
            word_a, word_b = tree.find_node_by_index(word_a_index).lemma,\
                             tree.find_node_by_index(word_b_index).lemma
            frames.append((word_a, link_type, word_b))
    for frame in frames:
        print ' -> '.join(frame)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: extract_frames.py <SyntagRus plaintext root>'
        exit()
    process_folder(sys.argv[1], [u'предик', u'1-компл', u'2-компл', u'3-компл', u'4-компл', u'5-компл', u'агент'])