import codecs
import cPickle
from spacy.en import English
import spacy

tokenizer = English(parser=False)
en_nlp = spacy.load('en')
name = "semeval_mixed_test"  # Input file name.
label = 1  # 1 is for METONYMY/NON-LITERAL, 0 is for LITERAL
inp = codecs.open("data/" + name + ".txt", mode="r", encoding="utf-8")
# PLEASE FORMAT THE INPUT FILE AS ONE SENTENCE PER LINE. SEE BELOW:
# ENTITY<SEP>sentence<ENT>ENTITY<ENT>rest of sentence.
# Germany<SEP>Their privileges as permanent Security Council members, especially the right of veto, 
# had been increasingly questioned by <ENT>Germany<ENT> and Japan which, as major economic powers.
out = []
seq_length = 50  # There are THREE baselines in the paper (5, 10, 50) so use this integer to set it.


def locate_entity(document, ent, left_w, right_w):
    left_w = '' if len(left_w) == 0 else left_w[-1].text
    right_w = '' if len(right_w) == 0 else right_w[0].text
    for doc in document:
        if doc.text == ent[0]:
            index = doc.i
            if left_w == '' or document[index - 1].text == left_w:
                if right_w == '' or document[index + len(ent)].text == right_w:
                    return index + len(ent) - 1
    raise Exception()  # If this is ever triggered, there are problems parsing the text. Check SpaCy output!


def pad(coll, from_left):
    while len(coll) < seq_length:
        if from_left:
            coll = [u"0.0"] + coll
        else:
            coll += [u"0.0"]
    return coll


for line in inp:
    line = line.split(u"<SEP>")
    sentence = line[1].split(u"<ENT>")
    entity = [t.text for t in tokenizer(sentence[1])]
    en_doc = en_nlp(u"".join(sentence).strip())
    words = []
    index = locate_entity(en_doc, entity, tokenizer(sentence[0].strip()), tokenizer(sentence[2].strip()))
    start = en_doc[index]
    right = pad([t.text for t in en_doc[start.i + 1:][:seq_length]], False)
    dep_right = pad([t.dep_ for t in en_doc[start.i + 1:]][:seq_length], False)
    left = pad([t.text for t in en_doc[:index - len(entity) + 1][-seq_length:]], True)
    dep_left = pad([t.dep_ for t in en_doc[:index - len(entity) + 1]][-seq_length:], True)
    out.append((left, dep_left, right, dep_right, label))
    print(left, right)
    print(dep_left, dep_right)
    print(line[1])
print("Processed:", len(out), " lines/sentences.")
cPickle.dump(out, open("pickle/" + name + "_base.pkl", "w"))
