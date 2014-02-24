import collections
import numpy
import os
import itertools
import sys
import kernel

import text_reading
import text_reading.twenty_newsgroups
import text_reading.ruscorpora
from sklearn import feature_extraction, svm, cross_validation

# traversing the text root folder, assigning each filename its category (parent folder name)
def get_text_category_pairs(in_folder):
    text_category_pairs = []
    for root, dirs, files in os.walk(in_folder, followlinks=True):
        category_name = os.path.basename(root)
        for filename in files:
            text_category_pairs.append((os.path.join(root, filename), category_name))
    return text_category_pairs

def process_data(in_folder):
    bags = []
    categories = []
    text_category_pairs = get_text_category_pairs(in_folder)

    for (filename, category) in text_category_pairs:
        text = text_reading.ruscorpora.get_text_raw(filename)
        # creating the simplest bag of words out of text
        text_bag = collections.defaultdict(lambda: 0)
        for word in text:
            text_bag[word] += 1
        bags.append(text_bag)
        categories.append(category)
    print 'Loaded %d documents' % len(categories)

    vectorizer = feature_extraction.DictVectorizer()
    # builds a vocabulary out of all words in the training dataset
    term_document_matrix = vectorizer.fit_transform(bags)
    tfidf_transformer = feature_extraction.text.TfidfTransformer()
    # in this matrix rows are documents, columns - features (terms' tfidf's)
    tfidf_matrix = tfidf_transformer.fit_transform(term_document_matrix)
    print 'Vectorized documents'
    return (tfidf_matrix.todense(), categories)

def train_model(in_tfidf_matrix, in_categories_vector):
    classifier = svm.SVC(kernel=kernel.cosine)
    return classifier.fit(in_tfidf_matrix, in_categories_vector)

def get_submatrix(in_matrix, in_row_indices):
    result_submatrix = numpy.ndarray(shape=(len(in_row_indices), in_matrix.shape[1]))
    for (src_index, dst_index) in zip(in_row_indices, itertools.count()):
        result_submatrix[dst_index] = in_matrix[src_index]
    return result_submatrix

def k_fold_cross_validate(in_term_document_matrix, in_categories_vector, in_k):
    kfold = cross_validation.KFold(len(in_categories_vector), n_folds=in_k, shuffle=True)
    accuracy = 0.0
    for (train_indices, test_indices) in kfold:
        print 'Training a fold'
        train_matrix = get_submatrix(in_term_document_matrix, train_indices)
        train_categories = [in_categories_vector[index] for index in train_indices]
        test_matrix = get_submatrix(in_term_document_matrix, test_indices)
        test_categories = [in_categories_vector[index] for index in test_indices]
        model = train_model(train_matrix, train_categories)
        model_answers = model.predict(test_matrix)
        result_vector = [int(category == gold_category) for (category, gold_category) in zip(model_answers, test_categories)]
        fold_accuracy = sum(result_vector) / float(len(test_categories))
        print 'fold accuracy: %lf' % fold_accuracy
        accuracy += fold_accuracy / in_k
    return accuracy

def just_train(in_term_document_matrix, in_categories_vector, in_k):
    model = train_model(in_term_document_matrix, in_categories_vector)
    model_answers = model.predict(in_term_document_matrix)
    result_vector = [int(category == gold_category) for (category, gold_category) in zip(model_answers, in_categories_vector)]
    fold_accuracy = sum(result_vector) / float(len(in_categories_vector))
    return fold_accuracy

def process_dataset(in_train_data):
    (tfidf_matrix, categories_vector) = process_data(in_train_data)
    accuracy = k_fold_cross_validate(tfidf_matrix, categories_vector, 10)
    print accuracy


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: train_model.py <training data folder>'
        exit(0)
    process_dataset(sys.argv[1])
