import codecs
import sys
import distance_util

sys.path.append('..')

import distance

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: pairwise_distances_listwise.py <input texts root> <result file>')
        exit()
    sentences = distance_util.load_all_sentences_as_plaintext(sys.argv[1])
    print('Loaded', len(sentences), 'sentences')
    distances_top = distance_util.compute_distances_generic(sentences,
                                                            distance.edit_distance_listwise,
                                                            sample_size=20000)
    output_stream = codecs.getwriter('utf-8')(open(sys.argv[2], 'w'))
    distance_util.output_result(distances_top, output_stream)
