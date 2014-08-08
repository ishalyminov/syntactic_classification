#coding: utf-8
import codecs

import os
import sys

sys.path.append('..')

import syntax_tree


def extract_links_in_subtree(in_subtree_root, in_link_type):
    result_links = []
    for child_index in xrange(len(in_subtree_root.children)):
        link_type = in_subtree_root.children_types[child_index]
        child = in_subtree_root.children[child_index]
        if link_type == in_link_type:
            result_links.append((in_subtree_root.word_index, child.word_index))
        result_links += extract_links_in_subtree(child, in_link_type)
    return result_links


# extracting now only "verb - subject" relations
def extract_frame(in_dependency_tree, in_link_type):
    root = in_dependency_tree.get_root()
    links = extract_links_in_subtree(root, in_link_type)
    return links


def load_all_sentences_as_dependency_trees(in_texts_root):
    result = []
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        for filename in files:
            full_filename = os.path.join(root, filename)
            print 'processing file: ', full_filename
            result += syntax_tree.load_file(codecs.getreader('utf-8')(open(full_filename)))
    return result


def process_folder(in_text_root):
    frames = []
    trees = load_all_sentences_as_dependency_trees(in_text_root)
    for tree in trees:
        links = extract_frame(tree, u'предик')
        for link in links:
            word_a, word_b = tree.find_node_by_index(link[0]).form,\
                             tree.find_node_by_index(link[1]).form
            frames.append((word_a, word_b))
    for frame in frames:
        print ' '.join(frame)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: extract_frames.py <SyntagRus plaintext root>'
        exit()
    process_folder(sys.argv[1])