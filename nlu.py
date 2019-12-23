from collections import defaultdict
import spacy

# "en_core_web_md"
# text = "let me know brian elliot's office"
# text = "How are you?"
# doc = nlp(text)
# print([token.head.i for token in doc])
# print([token.dep_ for token in doc])
# # print([token.pos_ for token in doc])
# print([token.text for token in doc])

class NLU(object):
    def __init__(self, model_dir="./model"):
        self.nlp = spacy.load(model_dir)

    def extract_entities(self, doc):
        entities = defaultdict(list)
        for ent in doc.ents:
            # print(ent.label_, ent.text)
            entities[ent.label_].append(ent.text)
        return entities

    def interpret(self, text):
        doc = self.nlp(text)
        deps = [token.dep_ for token in doc]
        root = [i for i, dep in enumerate(deps) if dep == 'ROOT']
        xcomp = [i for i, dep in enumerate(deps) if dep == 'XCOMP']
        poss = [i for i, dep in enumerate(deps) if dep == 'POSS']
        place = [i for i, dep in enumerate(deps) if dep == 'PLACE']
        
        extracts = defaultdict(list)
        extracts_to_have = ["POSS", "PLACE"]
        intent_find_words = ["find", "search", "know", "wanna", "want", "is"]
        extract_office_words = ["office", "room", "place"]

        intent = "UNK"
        if len(root) > 1 or len(xcomp) > 1 or len(poss) > 2 or len(place) > 1:
            intent = "COMPLEX"
        elif str(doc[root[0]]).lower() in extract_office_words and len(place) == 1:
            intent = "COMPLEX"
        elif len(poss) == 2 and (poss[0] - poss[1])**2 > 1:
            intent = "COMPLEX"
        else:
            temp = []
            for i, t in enumerate(doc):
                if len(xcomp) == 1:
                    if t.dep_ in extracts_to_have and (t.head.i == root[0] or t.head.i == xcomp[0]):
                        extracts[t.dep_].append(str(t))
                        temp.append(i)
                else:
                    if t.dep_ in extracts_to_have and (t.head.i == root[0]):
                        extracts[t.dep_].append(str(t))
                        temp.append(i)

            while(len(temp)):
                temp_copy = temp.copy()
                temp = []
                for i, t in enumerate(doc):
                    if t.dep_ in extracts_to_have and t.head.i in temp_copy:
                        extracts[t.dep_].append(str(t))
                        temp.append(i)

            root_string = str(doc[root[0]]).lower()
            if len(xcomp) == 1:
                xcomp_string = str(doc[xcomp[0]]).lower()
            else:
                xcomp_string = None

            if root_string in extract_office_words:
                intent = "FIND_OFFICE_LOC"
            elif root_string in intent_find_words or xcomp_string in intent_find_words:
                found = False
                for ent_A in extract_office_words:
                    for ent_B in extracts.get("PLACE",[]):
                        if ent_A == ent_B.lower():
                            found = True
                            break
                if found:
                    intent = "FIND_OFFICE_LOC"
        
        entities = self.extract_entities(doc)
        
        to_del = []
        for entity in entities.get("PERSON", []):
            for extract in extracts.get("POSS", []):
                if entity.lower().find(extract.lower()) == -1:
                    to_del.append(entity)
        
        for item in to_del:
            entities["PERSON"].remove(item)

        #print("intent", intent)
        #print("entities", entities)

        return (intent, entities)

if __name__ == "__main__":

    nlu = NLU()

    print(nlu.interpret("Where is Donna Graves's Office?"))
