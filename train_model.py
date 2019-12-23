from __future__ import unicode_literals, print_function

import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding



first_names = ["Donna", "donna", "Mandy", "mandy", "Colin", "colin", "Janis", "janis", "Brian", "brian"]
full_names = ["Donna Graves", "donna graves", "Mandy Green", "mandy green", "Colin Banger", "colin banger", 
              "Janis Michael", "janis michael", "Brian Elliot", "brian elliot"]

TRAIN_DATA = []

for name in first_names:
    TRAIN_DATA.append(("Find me {}'s office".format(name), 
              { "heads": [0, 0, 4, 2, 0],  # index of token head
                "deps": ["ROOT", "-", "POSS", "-", "PLACE"]}))
    TRAIN_DATA.append(("Could you find me {}'s office".format(name), 
              { "heads": [2, 2, 2, 2, 6, 4, 2],  # index of token head
                "deps": ["-", "-", "ROOT", "-", "POSS", "-", "PLACE"]}))
    TRAIN_DATA.append(("I want to find {}'s office".format(name), 
              { "heads": [1, 1, 3, 1, 6, 4, 3],  # index of token head
                "deps": ['-', 'ROOT', '-', '-', 'POSS', '-', 'PLACE']}))
    TRAIN_DATA.append(("Where is {}'s office?".format(name), 
              { "heads": [1, 1, 4, 2, 1, 1],  # index of token head
                "deps": ["-", "ROOT", "POSS", "-", "PLACE", "-"]}))
    TRAIN_DATA.append(("Where can I find {}'s office?".format(name), 
              { "heads": [3, 3, 3, 3, 6, 4, 3, 3],  # index of token head
                "deps": ["-", "-", "-", "ROOT", "POSS", "-", "PLACE", "-"]}))
    TRAIN_DATA.append(("Let me know {}'s office".format(name), 
              { "heads": [2, 2, 2, 5, 3, 2],  # index of token head
                "deps": ["-", "-", "ROOT", "POSS", "-", "PLACE"]}))

for name in full_names:
    TRAIN_DATA.append(("Find me {}'s office".format(name), 
              { "heads": [0, 0, 3, 5, 3, 0],  # index of token head
                "deps": ["ROOT", "-", "POSS", "POSS", "-", "PLACE"]}))
    TRAIN_DATA.append(("Could you find me {}'s office".format(name), 
              { "heads": [2, 2, 2, 2, 6, 7, 6, 2],  # index of token head
                "deps": ["-", "-", "ROOT", "-", "POSS", "POSS", "-", "PLACE"]}))
    TRAIN_DATA.append(("I want to find {}'s office".format(name), 
              { "heads": [1, 1, 3, 1, 5, 7, 5, 3],  # index of token head
                "deps": ['-', 'ROOT', '-', '-', 'POSS', 'POSS', '-', 'PLACE']}))
    TRAIN_DATA.append(("Where is {}'s office?".format(name), 
              { "heads": [1, 1, 3, 5, 3, 1, 1],  # index of token head
                "deps": ["-", "ROOT", "POSS", "POSS", "-", "PLACE", "-"]}))
    TRAIN_DATA.append(("Where can I find {}'s office?".format(name), 
              { "heads": [3, 3, 3, 3, 5, 7, 5, 3, 3],  # index of token head
                "deps": ["-", "-", "-", "ROOT", "POSS", "POSS", "-", "PLACE", "-"]}))
    TRAIN_DATA.append(("Let me know {}'s office".format(name), 
              { "heads": [2, 2, 2, 4, 6, 4, 2],  # index of token head
                "deps": ["-", "-", "ROOT", "POSS", "POSS", "-", "PLACE"]}))    

def main(model=None, output_dir=None, n_iter=15):
    """Load the model, set up the pipeline and train the parser."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    # We'll use the built-in dependency parser class, but we want to create a
    # fresh instance – just in case.
    if "parser" in nlp.pipe_names:
        nlp.remove_pipe("parser")
    parser = nlp.create_pipe("parser")
    nlp.add_pipe(parser, first=True)

    for text, annotations in TRAIN_DATA:
        for dep in annotations.get("deps", []):
            parser.add_label(dep)

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "parser"]
    with nlp.disable_pipes(*other_pipes):  # only train parser
        optimizer = nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, losses=losses)
            print("Losses", losses)

    # test the trained model
    test_model(nlp)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        test_model(nlp2)


def test_model(nlp):
    texts = [
        "find office",
        "find Donna's office",
        "find me Mandy Green's office",
        "how can I find Donna's office",
        "I'd like to find Donna's office"
    ]
    docs = nlp.pipe(texts)
    for doc in docs:
        print(doc.text)
        print([(t.text, t.dep_, t.head.text) for t in doc if t.dep_ != "-"])


if __name__ == "__main__":
    main("en_core_web_md", output_dir="./model")
    
    nlp = spacy.load("./model")
    # "en_core_web_md"
    print(nlp.pipe_names)

    text = "let me know brian elliot's office"
    #text = "How are you?"
    doc = nlp(text)
    print([token.head.i for token in doc])
    print([token.dep_ for token in doc])
    # print([token.pos_ for token in doc])
    print([token.text for token in doc])