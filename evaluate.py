import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from utils import CharacterTable, transform
from utils import restore_model, decode_sequences
from utils import read_text, tokenize

error_rate = 0.6
reverse = True
model_path = './models/best_97.h5'
hidden_size = 512
sample_mode = 'argmax'
data_path = './data/textData'


#books = ['nietzsche.txt', 'pride_and_prejudice.txt', 'shakespeare.txt', 'war_and_peace.txt','wonderland.txt'] #default model
books = [ 'cwtext.txt','nietzsche.txt', 'pride_and_prejudice.txt', 'shakespeare.txt', 'war_and_peace.txt','wonderland.txt'] #use this for 96_acc

#error_sentence = 'Daystrom Data Conceptss'
#test_sentence = 'Daystrom Data Concepts'

text  = read_text(data_path, books)
vocab = tokenize(text)
vocab = list(filter(None, set(vocab)))
# `maxlen` is the length of the longest word in the vocabulary
# plus two SOS and EOS characters.
maxlen = max([len(token) for token in vocab]) + 2
train_encoder, train_decoder, train_target = transform(
    vocab, maxlen, error_rate=error_rate, shuffle=False)
encoder_model, decoder_model = restore_model(model_path, hidden_size)


#modified code from https://github.com/vuptran/deep-spell-checkr

#Call this function with a string and it will return a corrected string. (only works for words, does not work for IDs)
def returnCorrectedString(inputString):
    
    tokens = tokenize(inputString)
    tokens = list(filter(None, tokens))
    nb_tokens = len(tokens)
   



    misspelled_tokens, _, target_tokens = transform(
        tokens, maxlen, error_rate=0, shuffle=False)
    input_chars = set(' '.join(train_encoder))
    target_chars = set(' '.join(train_decoder))
    input_ctable = CharacterTable(input_chars)
    target_ctable = CharacterTable(target_chars)
    
    
    input_tokens, target_tokens, decoded_tokens = decode_sequences(
        misspelled_tokens, target_tokens, input_ctable, target_ctable,
        maxlen, reverse, encoder_model, decoder_model, nb_tokens,
        sample_mode=sample_mode, random=False)
    newString = ''
    #print('Decoded sentence:', ' '.join([token for token in decoded_tokens]))
    newString = ' '.join([token for token in decoded_tokens])
    return newString
    
