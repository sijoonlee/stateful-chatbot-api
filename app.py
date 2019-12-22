from collections import defaultdict
import random


# event -> action
# action -> transition
# tanssition -> state
contexts = {
    "user-input":[],
    "nlu":{"intent":["question-office-hour"], "entities":[]},
    "query":[],
    "current":None,
    "retry":False,
    "quit":False
}
def get_user_input():
    contexts["user-input"].append("USER INPUT")

def nlu(contexts):
    contexts["nlu"]["intent"].append("question-office-location")
    contexts["nlu"]["entities"].append({"name":"Donna"})

def query(contexts):
    contexts.query.append({"office-location":"1001", "office-hour":"11:11"})    

transitions = {
    "greet":[{"on":None, "target":"get-questions"}],
    "get-questions":[   {"on":{"question-office-hour":contexts["nlu"]["intent"][:-1]=="question-office-hour"}, "target":"answer-office-hour"},
                        {"on":{"question-office-location":contexts["nlu"]["intent"][:-1]=="question-office-location"}, "target":"answer-office-location"}],
    "answer-office-hour":[{"on":{contexts["retry"]:True}, "target":"get-questions"},
                            {"on":{contexts["retry"]:False}, "target":"good-bye"}],
    "answer-office-hour":[{"on":{contexts["retry"]:True}, "target":"get-questions"},
                            {"on":{contexts["retry"]:False}, "target":"good-bye"}]
}

class Transition(object):
    def __init__(self, id):
        self.id = id
        self.on_and_target = []
    def setCondition(self, on, target):
        self.on_and_target.append({"on":on, "target":target})


states = {
    "greet":{"type":"start", 
            "slot":[{"type":"initiatives", "sentence":["Hi!", "Hello!"]}]},
    "get-questions": {"slot":[{"type":"initiatives", "sentence":["How can I help you? Office Hour? Office Location?"]}, 
                            {"type":"requests", "function":nlu, "get":contexts["user-input"], "set":contexts["nlu"]}]},
    "answer-office-hour": {"slot":[ {"type":"responses", "function":query, "param":contexts["nlu"], "return":contexts["query"], "sentence":["The office is located at {}"]},
                                    {"type":"follow-ups", "contexts":contexts["retry"], "sentence":["Do you have more questions?"]}]},
    "answer-office-location": { "slot":[{"type":"responses", "function":query, "param":contexts["nlu"], "return":contexts["query"], "sentence":["The office hour is {}"]},
                                        {"type":"follow-ups", "contexts":contexts["retry"], "sentence":["Do you have more questions?"]}]},
    "good-bye":{"type":"end", "slots":[{"type":"initiative", "sentence":["Good bye!"]}]}
}


if __name__ == "__main__":
    start_id = None
    start_attr = None
    
    #find start
    for id, attr in states.items():
        attr_type = attr.get("type", False)
        if attr_type is "start":
            start_id = id
            start_attr = attr
            break

    for slot in start_attr["slot"]:
        if slot["type"] is "initiatives":
            print(random.choice(slot["sentence"]))
        elif slot["type"] is "requests":
            slot["return"] = slot["nlu"](slot["context"])
            print(contexts)
        elif slot["type"] is "responses":
            slot["return"] = slot["query"](slot["context"])
            print(contexts)

    contexts["nlu"]["intent"].append("question-office-hour")
    print(contexts["nlu"]["intent"][:-1])
    print(transitions["get-questions"][0]["on"]["question-office-hour"])

    

    


            

