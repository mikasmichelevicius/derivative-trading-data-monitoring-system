import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from utils import CharacterTable, transform
from utils import restore_model, decode_sequences
from utils import read_text, tokenize
import keras
import keras.backend.tensorflow_backend as tb




#modified code from https://github.com/vuptran/deep-spell-checkr
class NeuralNetwork():
    
    def __init__(self):
        self.error_rate = 0.6
        self.reverse = True
        self.model_path = './models/best_97.h5'
        self.hidden_size = 512
        self.sample_mode = 'argmax'
        self.data_path = './data/textData'
        tb._SYMBOLIC_SCOPE.value = True

        #books = ['nietzsche.txt', 'pride_and_prejudice.txt', 'shakespeare.txt', 'war_and_peace.txt','wonderland.txt'] #default model
        self.books = [ 'cwtext.txt','nietzsche.txt', 'pride_and_prejudice.txt', 'shakespeare.txt', 'war_and_peace.txt','wonderland.txt'] #use this for 96_acc

        #error_sentence = 'Daystrom Data Conceptss'
        #test_sentence = 'Daystrom Data Concepts'

        self.text  = read_text(self.data_path, self.books)
        vocab = tokenize(self.text)
        vocab = list(filter(None, set(vocab)))
        # `maxlen` is the length of the longest word in the vocabulary
        # plus two SOS and EOS characters.
        self.maxlen = max([len(token) for token in vocab]) + 2
        self.train_encoder, self.train_decoder, self.train_target = transform(
            vocab, self.maxlen, error_rate=self.error_rate, shuffle=False)
        self.encoder_model, self.decoder_model = restore_model(self.model_path, self.hidden_size)

    #Call this function with a string and it will return a corrected string. (only works for words, does not work for IDs)
    def returnCorrectedString(self,inputString):

        tokens = tokenize(inputString)
        tokens = list(filter(None, tokens))
        nb_tokens = len(tokens)




        misspelled_tokens, _, target_tokens = transform(
            tokens, self.maxlen, error_rate=0, shuffle=False)
        input_chars = set(' '.join(self.train_encoder))
        target_chars = set(' '.join(self.train_decoder))
        input_ctable = CharacterTable(input_chars)
        target_ctable = CharacterTable(target_chars)


        input_tokens, target_tokens, decoded_tokens = decode_sequences(
            misspelled_tokens, target_tokens, input_ctable, target_ctable,
            self.maxlen, self.reverse, self.encoder_model, self.decoder_model, nb_tokens,
            sample_mode=self.sample_mode, random=False)
        newString = ''
        #print('Decoded sentence:', ' '.join([token for token in decoded_tokens]))
        newString = ' '.join([token for token in decoded_tokens])
        return newString
