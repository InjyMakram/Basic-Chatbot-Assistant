# -*- coding: utf-8 -*-

import spacy
from spacy.matcher import Matcher
import webbrowser
import random
from datetime import datetime
import threading
import time
import dateparser

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# Define patterns and responses
patterns_responses = [
    ("MY_NAME_IS", [{"LOWER": "my"}, {"LOWER": "name"}, {"LOWER": "is"}, {"ENT_TYPE": "PERSON"}], "Hello {name}, how can I help you today?"),
    ("GREETINGS", [{"LOWER": {"IN": ["hi", "hey", "hello"]}}], "Hello, how can I assist you?"),
    ("ASK_NAME", [{"LOWER": "what"}, {"LOWER": "is"}, {"LOWER": "your"}, {"LOWER": "name"}], "I am a chatbot created to assist you, but you can call me Alexa."),
    ("FEELINGS", [{"LOWER": "how"}, {"LOWER": "are"}, {"LOWER": "you"}], "I'm a chatbot, so I don't have feelings, but I'm here to help!"),
    ("SORRY", [{"LOWER": "sorry"}], "It's okay, no worries. Everyone makes mistakes, even chatbots sometimes!"),
    ("GOODBYE", [{"LOWER": "goodbye"}], "Goodbye! It was nice talking to you."),
    ("OPEN_YOUTUBE", [{"LOWER": "open"}, {"LOWER": "youtube"}], "Opening YouTube... Don't forget to like and subscribe!"),
    ("OPEN_GOOGLE", [{"LOWER": "open"}, {"LOWER": "google"}], "Opening Google... Ready to search the internet?"),
    ("TELL_JOKE", [{"LOWER": "tell"}, {"LOWER": "me"}, {"LOWER": "a"}, {"LOWER": "joke"}], "Here's a joke for you: {joke}"),
    ("TIME", [{"LOWER": "what"}, {"LOWER": "time"}, {"LOWER": "is"}, {"LOWER": "it"}], "The current time is {time}."),
    ("SET_REMINDER", [{"LOWER": "remind"}, {"LOWER": "me"}, {"LOWER": "to"}, {"IS_ALPHA": True, "OP": "+"}], "Reminder set for {time}."),
    ("COMPLIMENT", [{"LOWER": {"IN": ["great", "awesome", "fantastic", "good", "nice"]}}], "Thank you! I appreciate the compliment!"),
    ("BAD_WORD", [{"LOWER": {"IN": ["bitch", "fuck you", "shit"]}}], "Please refrain from using bad language.")
]

jokes = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "Why don't skeletons fight each other? They don't have the guts!",
    "What do you call fake spaghetti? An impasta!",
    "Why did the bicycle fall over? Because it was two-tired!",
]

for pattern_id, pattern, _ in patterns_responses:
    matcher.add(pattern_id, [pattern])

def set_reminder(reminder_text, reminder_time):
    def reminder_action():
        delay = (reminder_time - datetime.now()).total_seconds()
        if delay > 0:
            time.sleep(delay)
            print(f"Reminder: {reminder_text}")  # This will print the reminder text when the time comes
    threading.Thread(target=reminder_action).start()

def respond(doc):
    matches = matcher(doc)
    if matches:
        match_id, start, end = matches[0]
        match_span = doc[start:end]
        for pattern_id, pattern, response in patterns_responses:
            if match_id == nlp.vocab.strings[pattern_id]:
                if pattern_id == "MY_NAME_IS":
                    name = match_span[-1].text
                    return response.format(name=name)
                elif pattern_id == "OPEN_YOUTUBE":
                    webbrowser.open("https://www.youtube.com")
                    return response
                elif pattern_id == "OPEN_GOOGLE":
                    webbrowser.open("https://www.google.com")
                    return response
                elif pattern_id == "TELL_JOKE":
                    joke = random.choice(jokes)
                    return response.format(joke=joke)
                elif pattern_id == "TIME":
                    current_time = datetime.now().strftime("%H:%M:%S")
                    return response.format(time=current_time)
                elif pattern_id == "SET_REMINDER":
                    full_input = doc.text.strip()
                    remind_index = full_input.lower().find("remind me to") + len("remind me")
                    on_index = full_input.lower().find("on")
                    
                    if on_index != -1 and remind_index != -1:
                        reminder_text = full_input[remind_index:on_index].strip()  # Extract text between "remind me" and "on"
                        reminder_details = full_input[on_index:]  # Remaining text for date and time
                        print(f"Parsing reminder details: {reminder_details}")  # Debug statement
                        reminder_datetime = dateparser.parse(reminder_details.strip())
                        
                        print(f"Parsed reminder datetime: {reminder_datetime}")  # Debug statement
                        if reminder_datetime:
                            set_reminder(reminder_text, reminder_datetime)
                            return response.format(time=reminder_datetime.strftime("%Y-%m-%d %H:%M:%S"))
                        else:
                            return "I couldn't understand the time for the reminder. Please specify a clear date and time like 'Remind me to call John on July 17th at 3 PM'."
                elif pattern_id == "COMPLIMENT":
                    return response  # Response for compliments
                elif pattern_id == "BAD_WORD":
                    return response  # Response for bad words
                else:
                    return response
    return "I'm sorry, I didn't understand that. Maybe try asking me to tell a joke?"

def chatbot():
    print("Hi, I'm your enhanced chatbot! Type 'goodbye' to exit.")
    while True:
        user_input = input("> ")
        if user_input.lower() == "goodbye":
            print("Goodbye! It was nice talking to you.")
            break
        doc = nlp(user_input)
        print(respond(doc))

if __name__ == "__main__":
    chatbot()
