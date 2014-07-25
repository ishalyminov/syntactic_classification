import codecs
import heapq
import multiprocessing
import os
import random
import sys

sys.path.append('..')

import distance
import zss_tree

SENTENCES = []
SENTENCES_SAMPLE = []

# means that 100 x 100 distances will be calculated inside a single job
JOB_SIZE_PER_DIMENSION = 100
JOBS_NUMBER = 16
JOBS_CHUNK_SIZE = 50

# sentence contents constants
SENTENCE_LEN_MIN = 4
SENTENCE_LEN_MAX = 15

DISTANCES_MIN = []
MAX_RESULT_SIZE = 100


def load_all_sentences(in_texts_root):
    global SENTENCES
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        for filename in files:
            full_filename = os.path.join(root, filename)
            print 'processing file: ', full_filename
            for sentence in zss_tree.load_file(full_filename):
                if len(sentence) < SENTENCE_LEN_MIN or SENTENCE_LEN_MAX < len(sentence):
                    continue
                SENTENCES.append(sentence)


def update_result(in_distances):
    global DISTANCES_MIN
    for dist in in_distances:
        if len(DISTANCES_MIN) == MAX_RESULT_SIZE:
            heapq.heappushpop(DISTANCES_MIN, dist)
        else:
            heapq.heappush(DISTANCES_MIN, dist)


def compute_distances_in_subregion(in_coordinates):
    start_i, end_i, start_j, end_j = in_coordinates

    min_distances = []
    min_distances_number = 10
    for index_i in xrange(start_i, end_i):
        for index_j in xrange(start_j, end_j):
            if not index_i < index_j:
                continue
            dist = distance.distance_syntactic(SENTENCES[SENTENCES_SAMPLE[index_i]],
                                               SENTENCES[SENTENCES_SAMPLE[index_j]])
            if dist < 0.0 or dist > 1.0:
                print '!'
                raise RuntimeError()
            if len(min_distances) == min_distances_number:
                heapq.heappushpop(min_distances, (-dist, index_i, index_j))
            else:
                heapq.heappush(min_distances, (-dist, index_i, index_j))
    print 'Processed subregion: [%d, %d] X [%d, %d]' % (start_i, end_i, start_j, end_j)
    return min_distances


def compute_distances(sample_size=None):
    random_sample_size = sample_size if sample_size else len(SENTENCES)
    random_sample = range(len(SENTENCES))
    random.shuffle(random_sample)

    global SENTENCES_SAMPLE
    SENTENCES_SAMPLE = random_sample[:random_sample_size]
    job_pool = multiprocessing.Pool(JOBS_NUMBER)
    jobs_chunk = []
    print 'Computing pairwise distances for %d X %d elements' % (random_sample_size,
                                                                 random_sample_size)
    for start_index_i in xrange(0, random_sample_size, JOB_SIZE_PER_DIMENSION):
        for start_index_j in xrange(start_index_i, random_sample_size, JOB_SIZE_PER_DIMENSION):
            jobs_chunk.append((start_index_i,
                               start_index_i + JOB_SIZE_PER_DIMENSION,
                               start_index_j,
                               start_index_j + JOB_SIZE_PER_DIMENSION))
            if len(jobs_chunk) == JOBS_CHUNK_SIZE:
                chunk_results = job_pool.map(compute_distances_in_subregion, jobs_chunk)
                for result in chunk_results:
                    update_result(result)
                jobs_chunk = []
    if len(jobs_chunk):
        chunk_results = job_pool.map(compute_distances_in_subregion, jobs_chunk)
        for result in chunk_results:
            update_result(result)
        jobs_chunk = []
    return DISTANCES_MIN


def output_result(in_distances_top, in_result_stream):
    while len(in_distances_top):
        dist = heapq.heappop(in_distances_top)
        print >>in_result_stream, '%d to %d: %f' % (dist[1], dist[2], -dist[0])
        zss_tree.print_sentence(SENTENCES[SENTENCES_SAMPLE[dist[1]]], in_result_stream)
        zss_tree.print_sentence(SENTENCES[SENTENCES_SAMPLE[dist[2]]], in_result_stream)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: compute_pairwise_distances.py <input texts root> <result file>'
        exit()
    load_all_sentences(sys.argv[1])
    print 'Loaded', len(SENTENCES), 'sentences'
    distances_top = compute_distances(sample_size=1000)
    output_stream = codecs.getwriter('utf-8')(open(sys.argv[2], 'w'))
    output_result(distances_top, output_stream)
