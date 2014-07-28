import codecs
import heapq
import multiprocessing
import os
import random

# sentence contents constants
SENTENCE_LEN_MIN = 4
SENTENCE_LEN_MAX = 15

# means that 100 x 100 distances will be calculated inside a single job
JOB_SIZE_PER_DIMENSION = 100
JOBS_NUMBER = 16
JOBS_CHUNK_SIZE = 50

SENTENCES_SAMPLE = []
SENTENCES = []
DISTANCE_FUNCTION_HANDLER = None

DISTANCES_MIN = []
MAX_RESULT_SIZE = 1000


def split_sentences(in_file):
    result = []
    lines = codecs.getreader('utf-8')(open(in_file)).readlines()
    sentences = ''.join(lines).strip().split('\n\n')
    for sentence in sentences:
        lines = [line.split('\t')[:1] for line in sentence.split('\n')]
        result.append(lines)
    return result


def load_all_sentences_as_plaintext(in_texts_root):
    result = []
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        for filename in files:
            full_filename = os.path.join(root, filename)
            print('processing file: ', full_filename)
            for sentence in split_sentences(full_filename):
                if len(sentence) < SENTENCE_LEN_MIN or SENTENCE_LEN_MAX < len(sentence):
                    continue
                result.append(sentence)
    return result


def compute_distances_in_subregion(in_coordinates):
    start_i, end_i, start_j, end_j = in_coordinates

    min_distances = []
    min_distances_number = 10
    for index_i in range(start_i, end_i):
        for index_j in range(start_j, end_j):
            if not index_i < index_j:
                continue
            dist = DISTANCE_FUNCTION_HANDLER(SENTENCES[SENTENCES_SAMPLE[index_i]],
                                             SENTENCES[SENTENCES_SAMPLE[index_j]])
            if dist < 0.0 or dist > 1.0:
                print('!')
                raise RuntimeError()
            if len(min_distances) == min_distances_number:
                heapq.heappushpop(min_distances, (dist, index_i, index_j))
            else:
                heapq.heappush(min_distances, (dist, index_i, index_j))
    print('Processed subregion: [%d, %d] X [%d, %d]' % (start_i, end_i, start_j, end_j))
    return min_distances


def update_result(in_distances):
    global DISTANCES_MIN
    for dist in in_distances:
        if len(DISTANCES_MIN) == MAX_RESULT_SIZE:
            heapq.heappushpop(DISTANCES_MIN, dist)
        else:
            heapq.heappush(DISTANCES_MIN, dist)


def compute_distances_generic(in_sentences,
                              in_distance_function,
                              sample_size=None):
    global DISTANCE_FUNCTION_HANDLER, SENTENCES
    DISTANCE_FUNCTION_HANDLER = in_distance_function
    SENTENCES = in_sentences

    random_sample_size = sample_size if sample_size else len(SENTENCES)
    random_sample = range(len(SENTENCES))
    random.shuffle(random_sample)

    global SENTENCES_SAMPLE
    SENTENCES_SAMPLE = random_sample[:random_sample_size]
    job_pool = multiprocessing.Pool(JOBS_NUMBER)
    jobs_chunk = []
    print('Computing pairwise distances for %d X %d elements' % (random_sample_size,
                                                                 random_sample_size))
    for start_index_i in range(0, random_sample_size, JOB_SIZE_PER_DIMENSION):
        for start_index_j in range(start_index_i, random_sample_size, JOB_SIZE_PER_DIMENSION):
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


def print_sentence(in_sentence, in_output_stream):
    for line in in_sentence:
        print >>in_output_stream, '\t'.join(line)


def output_result(in_distances_top, in_result_stream):
    dists = []
    while len(in_distances_top):
        dists.append(heapq.heappop(in_distances_top))
    for dist in reversed(dists):
        print >>in_result_stream, '%d to %d: %f' % (dist[1], dist[2], dist[0])
        print_sentence(SENTENCES[SENTENCES_SAMPLE[dist[1]]], in_result_stream)
        print >>in_result_stream, '\n'
        print_sentence(SENTENCES[SENTENCES_SAMPLE[dist[2]]], in_result_stream)
        print >>in_result_stream, '\n\n\n'