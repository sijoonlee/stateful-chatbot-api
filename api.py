from flask import Flask, jsonify, render_template, request
from flask_restful import Api, Resource
from wtforms import Form, StringField, IntegerField, PasswordField, validators, SubmitField, SelectField
from message_generator import Message_generator, nlu_adapter, db_adapter

app = Flask(__name__)
api = Api(app)
bot_message = Message_generator(nlu_adapter, db_adapter)

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.get_json()
    if user_input.get("state", None) and user_input.get("message"):
        state, respond = bot_message.generate(user_input["state"], user_input["message"])
    else:
        state = user_input.get("state", None)
        respond = False
    return jsonify({"state":state, "message":respond})

if __name__=="__main__":
    app.run(host='0.0.0.0')