import re
import nltk
import pickle
    
def dameraulevenshtein(seq1, seq2):

    oneago = None
    this_row = list(range(1, len(seq2) + 1)) + [0]
    for x in range(len(seq1)):

        twoago, oneago, this_row = (oneago, this_row, [0] * len(seq2) + [x + 1])
        for y in range(len(seq2)):
            delcost = oneago[y] + 1
            addcost = this_row[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            this_row[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y - 1]
                    and seq1[x - 1] == seq2[y] and seq1[x] != seq2[y]):
                this_row[y] = min(this_row[y], twoago[y - 2] + 1)
    return this_row[len(seq2) - 1]


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


#--------------------------------------------------------------------------------------------------------------------


class SymSpell:
    
    def __init__(self, max_edit_distance=3, verbose=0):
        self.max_edit_distance = max_edit_distance
        self.verbose = verbose

        self.dictionary = {}
        self.longest_word_length = 0




    def get_deletes_list(self, w):
        """given a word, derive strings with up to max_edit_distance characters
           deleted exmple: for word = help = ['elp', 'hlp', 'hep', 'hel', 'lp', 'ep', 'el', 'hp', 'hl', 'he']"""

        deletes = []
        queue = [w]
        for d in range(self.max_edit_distance):
            temp_queue = []
            for word in queue:
                if len(word) > 1:
                    for char in range(len(word)):  # character index
                        word_minus_char = word[:char] + word[char + 1:]
                        if word_minus_char not in deletes:
                            deletes.append(word_minus_char)
                        if word_minus_char not in temp_queue:
                            temp_queue.append(word_minus_char)
            queue = temp_queue
            
        return deletes
    
    
    
   
    def create_dictionary_entry(self, w):
        '''add word and its derived deletions to dictionary'''
        # check if word is already in dictionary
        # dictionary entries are in the form: (list of suggested corrections,frequency of word in corpus)
        
        new_real_word_added = False
        if w in self.dictionary:
        
            self.dictionary[w] = (self.dictionary[w][0], self.dictionary[w][1] + 1)
        else:
            self.dictionary[w] = ([], 1)
            self.longest_word_length = max(self.longest_word_length, len(w))

        if self.dictionary[w][1] == 1:
            #if its a new word then add it and its deleted derivatives in dictionary
            new_real_word_added = True
            deletes = self.get_deletes_list(w)
            for item in deletes:
                if item in self.dictionary:
                    self.dictionary[item][0].append(w)
                else:
                    self.dictionary[item] = ([w], 0)

        return new_real_word_added
        
        
        

    def create_dictionary_from_arr(self, arr, token_pattern=r'[a-z]+'):
        total_word_count = 0
        unique_word_count = 0
    
        for line in arr:
            # separate by words by non-alphabetical characters
            words = re.findall(token_pattern, line.lower())
            for word in words:
                total_word_count += 1
                if self.create_dictionary_entry(word):
                    unique_word_count += 1

        print("total words processed: %i" % total_word_count)
        print("total unique words in corpus: %i" % unique_word_count)
        print("total items in dictionary (corpus words and deletions): %i" % len(self.dictionary))
        print("edit distance for deletions: %i" % self.max_edit_distance)
        print("length of longest word in corpus: %i" % self.longest_word_length)
        return self.dictionary
    
    
    

    def get_suggestions(self, string, silent=False):
        """return list of suggested corrections for potentially incorrectly
           spelled word"""
        if (len(string) - self.longest_word_length) > self.max_edit_distance:
            if not silent:
                print("no items in dictionary within maximum edit distance")
            return []

        suggest_dict = {}
        min_suggest_len = float('inf')

        queue = [string]
        q_dictionary = {} 

        while len(queue) > 0:
            q_item = queue[0]
            queue = queue[1:]
            #print(q_item)

            if ((self.verbose < 2) and (len(suggest_dict) > 0) and ((len(string) - len(q_item)) > min_suggest_len)):
                break

            # process queue item
            if (q_item in self.dictionary) and (q_item not in suggest_dict):
                if self.dictionary[q_item][1] > 0:
                    # word is in dictionary, and is a word from the corpus, and not already in suggestion list so add to 
                    # suggestion dictionary, indexed by the word with value (frequency in corpus, edit distance)
                    # q_items that are not the input string are shorter
                    # than input string since only deletes are added (unless manual dictionary corrections are added)
                    assert len(string) >= len(q_item)
                    suggest_dict[q_item] = (self.dictionary[q_item][1], len(string) - len(q_item))
                    
                    # early exit
                    if (self.verbose < 2) and (len(string) == len(q_item)):
                        break
                    elif (len(string) - len(q_item)) < min_suggest_len:
                        min_suggest_len = len(string) - len(q_item)

    
                for sc_item in self.dictionary[q_item][0]:
                    if sc_item not in suggest_dict:

                        assert len(sc_item) > len(q_item)

                        assert len(q_item) <= len(string)

                        if len(q_item) == len(string):
                            assert q_item == string
                            item_dist = len(sc_item) - len(q_item)


                        assert sc_item != string


                        item_dist = dameraulevenshtein(sc_item, string)

                        # do not add words with greater edit distance 
                        if (self.verbose < 2) and (item_dist > min_suggest_len):
                            pass
                        elif item_dist <= self.max_edit_distance:
                            assert sc_item in self.dictionary  # should already be in dictionary if in suggestion list
                            suggest_dict[sc_item] = (self.dictionary[sc_item][1], item_dist)
                            if item_dist < min_suggest_len:
                                min_suggest_len = item_dist


                        if self.verbose < 2:
                            suggest_dict = {k: v for k, v in suggest_dict.items() if v[1] <= min_suggest_len}


            assert len(string) >= len(q_item)

            # do not add words with greater edit distance 
            if (self.verbose < 2) and ((len(string) - len(q_item)) > min_suggest_len):
                pass
            elif (len(string) - len(q_item)) < self.max_edit_distance and len(q_item) > 1:
                for c in range(len(q_item)):  # character index
                    word_minus_c = q_item[:c] + q_item[c + 1:]
                    if word_minus_c not in q_dictionary:
                        queue.append(word_minus_c)
                        q_dictionary[word_minus_c] = None 


        # list for output
        if not silent and self.verbose != 0:
            print("number of possible corrections: %i" % len(suggest_dict))
            print("  edit distance for deletions: %i" % self.max_edit_distance)

   
        as_list = suggest_dict.items()
        # outlist = sorted(as_list, key=lambda (term, (freq, dist)): (dist, -freq))
        outlist = sorted(as_list, key=lambda x: (x[1][1], -x[1][0]))

        if self.verbose == 0:
            return outlist[0]
        else:
            return outlist


    def best_word(self, s, silent=False):
        try:
            return self.get_suggestions(s, silent)[0]
        except:
            return None

#-----------------------------------------------------------------------------------------------------------------


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        


def spell_corrector(word_list, words_d) -> str:
    result_list = []
    for word in word_list:
        if word not in words_d:
            suggestion = ss.best_word(word, silent=True)
            if suggestion is not None:
                result_list.append(suggestion)
        else:
            result_list.append(word)
            
    return " ".join(result_list)



#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


if __name__ == '__main__':

    ss = SymSpell(max_edit_distance=2)
    
    # fetch list of travelling words
    with open('C:/Users/SUMIT TIWARI/Documents/BOOKS/Capston_project/Chatbot/error_detection_and_correction/symspell/travell_words_unique.csv') as travel_f:
        travell_words = travel_f.readlines()
    travell_words = [word.strip() for word in travell_words]    
    
    # fetch english words dictionary
    with open('C:/Users/SUMIT TIWARI/Documents/BOOKS/Capston_project/Chatbot/error_detection_and_correction/symspell/common_english_words_10000.csv') as english_f:
        words = english_f.readlines()
    eng_words = [word.strip() for word in words]
    

    print(eng_words[:5])
    print(travell_words[:5])

    print('Total english words: {}'.format(len(eng_words)))
    print('Total travelling_words: {}'.format(len(travell_words)))
    
    
    
    print('create symspell dict...')
    all_words_list = list(set(travell_words + eng_words))
    ss.create_dictionary_from_arr(all_words_list, token_pattern=r'.+')
    
    #print(ss.dictionary)
    
#-------------------------dictionary-----------------------------------
    words_dict = {k: 0 for k in all_words_list}
    #print(words_dict)
    
#-------------------------store dictionary to file---------------------
    try:
        words_file = open('dictionary', 'wb')
        pickle.dump(ss.dictionary, words_file)
        words_file.close()
  
    except:
        print("Something went wrong")


#------------------------open dictionary to file-----------------------


    file = open("C:/Users/SUMIT TIWARI/Documents/BOOKS/Capston_project/Chatbot/error_detection_and_correction/symspell/word_dictionary", "rb")
    output = pickle.load(file)

#--------------------------------Testing-------------------------------

    sample_text = 'wherr is habibigang?'
    tokens = nltk.word_tokenize(sample_text)
    print()
    print()
    print('original text: ' + sample_text)
    print()
    #correct_text = spell_corrector(tokens, words_dict)
    correct_text = spell_corrector(tokens, output)
    print('corrected text: ' + correct_text)
  

