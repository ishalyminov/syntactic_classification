import nltk
import os
import sys
import zss
import zss_tree


def load_texts(in_texts_root):
    parsed_texts = []
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        for filename in files:
           full_filename = os.path.join(root, filename)
           parsed_texts.append(zss_tree.load_file(full_filename))
    return parsed_texts


texts = load_texts(sys.argv[1])
sentences = []
for text in texts[:3]:
    sentences += text

print 'Texts loaded'

clusterizer = nltk.KMeansClusterer(100, zss.simple_distance)
clusterizer.cluster(sentences)

print 'Texts clustered'