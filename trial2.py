from flask import Flask, jsonify, render_template, request #, request
from flask_restful import Api, Resource
from wtforms import Form, StringField, IntegerField, PasswordField, validators, SubmitField, SelectField
from pymongo import MongoClient
import random
# from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

# config_file = open("./config/mongodb", "r+")
# mongodb_address = config_file.read()
mongodb_address = "localhost:27017"
client = MongoClient(mongodb_address)

db = client.slc_db
collection = db.teachers
app = Flask(__name__)
api = Api(app)

# example
# found = collection.find_one({"name":{"$regex": "donna"}})
# print(found) # None or object
# for key, value in found.items():
#     print(key, value)

def mock_nlu(user_input):
    # ("FIND_OFFICE_LOC", {"NAME":"donna"})
    return user_input

def mock_db(intent, entities):
    found = None
    if intent is "FIND_OFFICE_LOC":
        query = {}
        for key, value in entities.items():
            if key is "NAME" or key is "COURSE_CODE":
                query[key.lower()] = {"$regex": value.lower()}
        found = collection.find_one(query)
        if found:
            found = found.get("office", None)
    return found

GREET = ["Hello!","Hi!"]
SELF_INTRO = ["This is bot, How can I help you?"]
ASK_TEACHER_INFO = ["Do you know the teacher's name?"]
RETURN_QUERY = ["Sorry, Can't find", "The office location is {}"]
FOLLOW_UP = ["Do you have more questions?"]
GOOD_BYE = ["Good bye!"]

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
            ("INIT", "FIND_OFFICE_LOC", None):("SPECIFY", (self.rand_message, GREET), (self.rand_message, SELF_INTRO)),
            ("INIT", "FIND_OFFICE_LOC", True):("QUERY", (self.db_message, RETURN_QUERY), (self.rand_message, FOLLOW_UP)),
            ("SPECIFY", "STATE", True):("QUERY", (self.db_message, RETURN_QUERY), (self.rand_message, FOLLOW_UP)),
            ("SPECIFY", "FIND_OFFICE_LOC", True):("QUERY", (self.db_message, RETURN_QUERY), (self.rand_message, FOLLOW_UP)),
            ("QUERY", "FIND_OFFICE_LOC", True):("QUERY", (self.db_message, RETURN_QUERY), (self.rand_message, FOLLOW_UP)),
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
        self.intent, self.entities =  self.nlu_adapter(user_input)
        if self.intent is None:
            respond.append("Sorry, I couldn't get the meaning.")
            return state, respond
        if self.entities is None:
            result = self.transition[(state, self.intent, None)]
        else:
            result = self.transition[(state, self.intent, True)]
        state = result[0]
        
        if len(state)>1:
            for idx in range(1,len(result)):
                func, arg = result[idx]
                if arg:
                    respond.append(func(arg))
                else:
                    respond.append(func())
        return state, respond




if __name__ == "__main__":
    gen = Message_generator(mock_nlu, mock_db)
    state, respond = gen.generate("INIT", ("FIND_OFFICE_LOC", None))
    print(state, respond)
    state, respond = gen.generate(state, ("FIND_OFFICE_LOC", {"NAME":"donna"}))
    print(state, respond)
    state, respond = gen.generate(state, ("FIND_OFFICE_LOC", {"NAME":"konna"}))
    print(state, respond)
    state, respond = gen.generate(state, ("NO", None))
    print(state, respond)