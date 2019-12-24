from pymongo import MongoClient
import random
from collections import defaultdict

from regex_matcher import regex_matcher
from nlu import NLU
# from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

# config_file = open("./config/mongodb", "r+")
# mongodb_address = config_file.read()
mongodb_address = "localhost:27017"
client = MongoClient(mongodb_address)

db = client.slc_db
collection = db.teachers


# example
# found = collection.find_one({"name":{"$regex": "donna"}})
# print(found) # None or object
# for key, value in found.items():
#     print(key, value)


nlu = NLU()
def nlu_adapter(user_input):
    #intent, entities = nlu.interpret(user_input)
    #print(intent, entities) # ("FIND_OFFICE_LOC", {"NAME":"donna"})
    return nlu.interpret(user_input)

def db_adapter(intent, entities):
    found = None
    if intent is "FIND_OFFICE_LOC":
        query = {}
        for key, list_values in entities.items():
            if key is "PERSON" or key is "COURSE_CODE":
                if len(list_values) == 1:
                    query = { key.lower(): {"$regex": list_values[0].lower()} }
                elif len(list_values) > 1:
                    query = { "$and": []}
                    for value in list_values:
                        query["$and"].append[{key.lower():{"$regex": value.lower()}}]
                if len(query) > 0:
                    found = collection.find_one(query)
        if found:
            found = found.get("office", None)
    return found

GREET = ["Hello!","Hi!"]
SELF_INTRO = ["I'm your chatbot. How can I help you? (In current version, it can search Teachers' office locations)"]
ASK_TEACHER_INFO = ["Do you know the teacher's name?"]
RETURN_QUERY = ["Sorry, Can't find", "The office location is {}"]
FOLLOW_UP = ["Do you have more questions?"]
SPECIFY_MORE = ["Could you give me the name of the teacher?"]
GOOD_BYE = ["Good bye!"]
SORRY = ["Sorry, coundn't understand fully."]

class Message_generator(object):
    def __init__(self, nlu_adapter, db_adapter):
        self.nlu_adapter = nlu_adapter
        self.db_adapter = db_adapter        
        # self.transition = transition
        # self.user_input = user_input
        self.intent = None
        self.entities = None
        self.query_result = None
        self.transition = {
            ("INIT", "START", None):("INIT", (self.rand_message, GREET), (self.rand_message, SELF_INTRO)),
            ("INIT", "FIND_OFFICE_LOC", None):("SPECIFY", (self.rand_message, SPECIFY_MORE)),
            ("INIT", "FIND_OFFICE_LOC", True):("QUERY", (self.db_message, RETURN_QUERY), (self.rand_message, FOLLOW_UP)),
            ("SPECIFY", "STATE", True):("QUERY", (self.db_message, RETURN_QUERY), (self.rand_message, FOLLOW_UP)),
            ("SPECIFY", "FIND_OFFICE_LOC", True):("QUERY", (self.db_message, RETURN_QUERY), (self.rand_message, FOLLOW_UP)),
            ("SPECIFY", "FIND_OFFICE_LOC", None):("SPECIFY", (self.rand_message, SPECIFY_MORE)),
            ("QUERY", "FIND_OFFICE_LOC", True):("QUERY", (self.db_message, RETURN_QUERY), (self.rand_message, FOLLOW_UP)),
            ("QUERY", "YES", None):("INIT", (self.rand_message, SELF_INTRO)),
            ("QUERY", "NO", None):("EXIT", (self.rand_message, GOOD_BYE))
        }

    def rand_message(self, messages):
        return random.choice(messages)

    def db_message(self, message):
        db_result = self.db_adapter(self.intent, self.entities)
        if db_result:
            return message[1].format(db_result)
        else:
            return message[0]

    def generate(self, state, user_input):
        respond = []

        if user_input != "START":
            self.intent, self.entities =  self.nlu_adapter(user_input)
        else:
            self.intent = "START"
            self.entities = []
        
        # for very short message, use regex-matcher
        if len([user_input.split()]) < 3 and len(self.entities) == 0 and self.intent is "UNK":
            self.intent = regex_matcher(user_input)

        if self.intent is None or self.intent is "UNK":
            respond.append("Sorry, I couldn't get the meaning.")
            return state, respond
        elif self.intent is "GREET":
            respond.append(self.rand_message(GREET))
            return state, respond
        elif self.intent is "GOOD_BYE":
            respond.append(self.rand_message(GOOD_BYE))
            return state, respond

        if len(self.entities) == 0:
            key = (state, self.intent, None)
        else:
            key = (state, self.intent, True)
        result = self.transition.get(key, None)
        if result != None:
            state = result[0]            
            if len(state)>1:
                for idx in range(1,len(result)):
                    func, arg = result[idx]
                    if arg:
                        respond.append(func(arg))
                    else:
                        respond.append(func())
        else: # not in dictionary
            respond.append("Sorry, I couldn't get the meaning.")
        return state, respond




if __name__ == "__main__":
    gen = Message_generator(nlu_adapter, db_adapter)

    questions = ["START", 
                "find me my teacher's office", 
                "I need to know my teacher's office", 
                "I want to find Konna's office",
                "Donna",
                "Donna's place",
                "yes"]

    state = "INIT"
    for question in questions:
        state, response = gen.generate(state, question)
        print("USER:", question)
        print("BOT:", response)
        
        