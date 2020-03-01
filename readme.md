# Stateful Chatbot API  
- The chatbot gives answers in the context of the goal-oriented conversation  
- Written in Python – Flask and MongoDB for backend  
- Spacy framework for natural language understanding  
- Regex pattern for simple input such as 'yes', 'no'  
  
# Example   
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
