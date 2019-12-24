import re

matcher = {"YES":"yes+|okay+|ok+", 
            "NO":"no+", 
            "GREET":"hello+|hey+|hi+",
            "GOOD_BYE":"bye+"}

def regex_matcher(text):
    found = "UNK"
    text = text.lower()
    for intent, pattern in matcher.items():
        if re.search(pattern, text):
            found = intent
    return found

if __name__ == "__main__":
    print(regex_matcher("yes"))