# Author: Ningqian Zhang
# Version: 2.0
# Language: Python 2

import argparse
import math
import pickle

# The following lines parse the command line arguments for you. You may ignore this part.
argument_parser = argparse.ArgumentParser("Log probability script. ")
argument_parser.add_argument('-m', '--model', help='The path to the directory containing the necessary files to recreate the language model.', required=True)
argument_parser.add_argument('-i', '--input', help='The path to the input file containing the n-grams to query. ', required=True)
argument_parser.add_argument('-o', '--output', help='The path to the output file containing the log probabilities for the input n-grams. ', required=True)
args = argument_parser.parse_args()

# The following variables are created for your convenience.
# They are the values from the command line input.
model_dir = args.model
ngram_input_path = args.input
log_prob_output_path = args.output

# Prints out what this script does
print("Computing the log-probabilities of the input n-grams in file: " + ngram_input_path)
print("    using the language model recreated from the directory: " + model_dir)
print("Result will be stored in the file: " + log_prob_output_path)
print("")



# START OF YOUR IMPLEMENTATION

# Recreate the LM
with open(model_dir + "/model_type.txt") as f:
    model_type = f.readline().rstrip("\n")
    smooth_or_not = f.readline()

with open(model_dir + "/vocabulary.pkl", "rb") as f:
    vocab_dict = pickle.load(f)

if model_type == "3" or model_type == "3s":
    with open(model_dir + "/trigram_counts.pkl", "rb") as f:
        trigram_dict = pickle.load(f)


queried_ngrams = [tuple(line.rstrip('\n').split(' ')) for line in open(ngram_input_path)]


if model_type == "dummy":
    # The dummy model always assigns 1/V to any unigram
    log_probs = [-math.log(vocab_size) for ngram in queried_ngrams]
    with open(log_prob_output_path, "w") as f:
        f.write("\n".join([str(x) for x in log_probs]))

elif model_type == "1":
    # unsmoothed unigram
    # P(w1w1...wk) = P(w1)P(w2)...P(wk)

    context_size = float(sum(vocab_dict.values()))
    log_probs = []
    with open(log_prob_output_path, "w") as f:
        for index, ngram in enumerate(queried_ngrams):
            print(ngram[0])
            if not vocab_dict.has_key(ngram[0]):
                log_probs.append(math.log(vocab_dict["<unk>"] / context_size))
            else:
                log_probs.append(math.log(vocab_dict[ngram[0]] / context_size))
        f.write("\n".join([str(x) for x in log_probs]))

elif model_type == "3":
    # unsmoothed trigram

    log_probs = []
    with open(log_prob_output_path, "w") as f:
        for index, ngram in enumerate(queried_ngrams):
            # Replace all the unseen word in the testing ngram with <unk> for later use
            if not vocab_dict.has_key(ngram[0]):
                trigram = "<unk>"
                bigram = "<unk>"
            else:
                trigram = ngram[0]
                bigram = ngram[0]
            if not vocab_dict.has_key(ngram[1]):
                trigram = trigram + " " + "<unk>"
                bigram = bigram + " " + "<unk>"
            else:
                trigram = trigram + " " + ngram[1]
                bigram = bigram + " " + ngram[1]
            if not vocab_dict.has_key(ngram[2]):
                trigram = trigram + " " + "<unk>"
            else:
                trigram = trigram + " " + ngram[2]

            # Output "NaN" if either the bigram or trigram is unseen
            if not trigram_dict.has_key(bigram) or not trigram_dict.has_key(trigram):
                log_probs.append("NaN")
            else:
                log_probs.append(math.log(trigram_dict[trigram] / float(trigram_dict[bigram])))
        f.write("\n".join([str(x) for x in log_probs]))

elif model_type == "3s":
    # smoothed trigram
    vocab_size = float(len(vocab_dict.keys()))
    log_probs = []
    with open(log_prob_output_path, "w") as f:
        for index, ngram in enumerate(queried_ngrams):
            if not vocab_dict.has_key(ngram[0]):
                trigram = "<unk>"
                bigram = "<unk>"
            else:
                trigram = ngram[0]
                bigram = ngram[0]
            if not vocab_dict.has_key(ngram[1]):
                trigram = trigram + " " + "<unk>"
                bigram = bigram + " " + "<unk>"
            else:
                trigram = trigram + " " + ngram[1]
                bigram = bigram + " " + ngram[1]
            if not vocab_dict.has_key(ngram[2]):
                trigram = trigram + " " + "<unk>"
            else:
                trigram = trigram + " " + ngram[2]

            if not trigram_dict.has_key(bigram):
                log_probs.append(math.log((1 / vocab_size)))
            elif not trigram_dict.has_key(trigram):
                log_probs.append(math.log((1 / (trigram_dict[bigram] + vocab_size))))
            else:
                log_probs.append(math.log((trigram_dict[trigram] + 1 / (trigram_dict[bigram] + vocab_size))))

        f.write("\n".join([str(x) for x in log_probs]))

else:
    print("Not implemented!! ")
