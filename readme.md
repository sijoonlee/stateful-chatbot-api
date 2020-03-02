# Stateful Chatbot API  
- The chatbot gives answers in the context of the goal-oriented conversation  
- Written in Python – Flask and MongoDB for backend  
- Spacy framework for natural language understanding(NLU)  
- Regex pattern for simple input such as 'yes', 'no'  
  
## NLU  
- Spacy framework model is trained to extract semantically useful information such as verbs and objects from sentences  
- By doing so, It will recognize the intent such as 'find teacher's office location' or the entity such as the teacher's name  
  
## API
- only one simple route: '/chat', post method  
- it accepts user's message as JSON object  
    e.g. {"state": "INIT", "message":"Hello:}  
- it responds based upon the state and the intent that is interpreted from the message  
    e.g.{"state":"INIT", "message":"Hi"}  

## State
- INIT : in this state, the api asks users if they want to know the office locaions
- SPECIFY : in this state, the api asks users if they can specify the teacher's name
- QUERY : in this state, the api gives the location information

## Intent
- YES, NO, GREET, GOOD_BYE  
  These are recognized by regex matcher
- FIND_OFFICE_LOC, STATE  
  These are recognized by the trained spacy model

## Example   
USER: START  
BOT: 'Hello!', "I'm your chatbot. How can I help you? (In current version, it can search Teachers' office locations)  
USER: find me my teacher's office  
BOT: 'Could you give me the name of the teacher?'  
USER: I need to know my teacher's office  
BOT: 'Could you give me the name of the teacher?'  
USER: I want to find Konna's office  
BOT: "Sorry, Can't find", 'Do you have more questions?'  
USER: Donna  
BOT: "Sorry, I couldn't get the meaning."  
USER: Donna's place  
BOT: 'The office location is 111', 'Do you have more questions?'  
USER: yes  
BOT: "I'm your chatbot. How can I help you? (In current version, it can search Teachers' office locations)"  
