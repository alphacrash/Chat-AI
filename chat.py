# RUN: python chat.py
import json
import openai
import requests
import prompts

# Values
key_file = "values/key.json"
urls_file = "values/urls.json"

# Key
with open(key_file, "r") as file:
    key_data = json.load(file)
with open(urls_file, "r") as file:
    urls_data = json.load(file)

openai.api_key = key_data["key"]

# API Endpoints
get_by_id_url = urls_data["getById"]
put_by_id_url = urls_data["putById"]
delete_by_id_url = urls_data["deleteById"]
post_by_id_url = urls_data["postById"]
get_all_url = urls_data["getAll"]
search_url = urls_data["search"]

# Main
class BookChat:
    CONVERSATION_AGREE_PROMPT = """OK"""
    CONVERSATION_START_PROMPT = """Great! Start the Conversation."""
    CONVERSATION_PROMPT = """You are a smart conversation assistant in library. Library is 'SUD Library'. You are helping a student to enquire about books. Your task is to follow the conversation flow to assist the student.
    
    ###
    Conversation Flow:
    1. Greet the student
    2. Check if they need any assistance.
    3. Answer their requiests
    4. Greet the student and end the conversation by responding '[END_OF_CONVERSATION]'
    ###

    Please respond 'OK' if you are clear about you task.
    """

    INTENT_DETECTION_SETUP_PROMPT = """Your task is to classify the student's intent from the below `Conversation` between an assistant and a student into following `Intent Categories`. Response should follow the `Output Format`.

    Conversation:
    {conversation}

    Intent Categories:
    GREETING: student is greeting the chatbot.
    BOOK_ENQUIRY: student's query regarding the book present in library.
    CREATE_BOOK: student's request to create a new book in library.
    OUT_OF_CONTEXT: student's query which is irrelevant and cannot be classified in the above intents.

    Output Format: <PREDICTED_INTENT>
    """

    ENQUIRY_DETAILS_PROMPT = """Your task is to extract the following `Entities` from the below `Conversation` between an assistant and a student. Response should follow the `Output Format`. If some entities are missing provide NULL in the `Output Format`.

    Conversation:
    {conversation}

    Entities:
    BOOK_NAME: This is the name of the book.
    BOOK_PRICE: This is the price of the book.
    BOOK_AUTHOR: This is the author of the book.
    BOOK_PUBLISHER: This is the publisher of the book.
    BOOK_LANGUAGE: This is the language of the book.
    BOOK_PAGES: This is the number of pages in the book.

    Output Format: {{'BOOK_NAME': <Book name in strings>, 'BOOK_PRICE': <Price in strings>, 'BOOK_AUTHOR': <Author name in strings>, 'BOOK_PUBLISHER': <Publisher name in strings>, 'BOOK_LANGUAGE': <Language in strings>, 'BOOK_PAGES': <Number of pages in strings>}}
    """

    def intent_detection(self, conversation):
        chat_ml = [
                    {"role": "user", "content": self.INTENT_DETECTION_SETUP_PROMPT.format(conversation=conversation)}
                  ]
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_ml,
        temperature=0)
        
        return response['choices'][0]['message']['content'].strip(" \n'")
    

    def enquiry_details(self, conversation):
        chat_ml = [
            {"role": "user", "content": self.ENQUIRY_DETAILS_PROMPT.format(conversation=conversation)}
        ]
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_ml,
        temperature=0)
        
        return response['choices'][0]['message']['content'].strip(" \n")

    def conversation_chat(self):
        conversation = ""
        end_flag = False

        chatml_messages = [
            {"role": "user", "content": self.CONVERSATION_PROMPT},
            {"role": "assistant", "content": self.CONVERSATION_AGREE_PROMPT},
            {"role": "user", "content": self.CONVERSATION_START_PROMPT}
        ]

        while True:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=chatml_messages
            )

            agent_response = response['choices'][0]['message']['content'].strip(" \n")

            if "END_OF_CONVERSATION" in agent_response:
                print("Assistant: Thank you for connecting with us. Have a nice day!")
                break
            elif end_flag==True:
                print("Assistant: {}".format(agent_response))
                print("Assistant: Thank you for connecting with us. Have a nice day!")
                break

            print("Assistant: {}".format(agent_response))
            chatml_messages.append({"role": "assistant", "content": agent_response})
            conversation += "Assistant: {}\n".format(agent_response)

            student_response = input("Student: ")
            if student_response == "/end":
                break
            chatml_messages.append({"role": "user", "content": student_response})
            conversation += "Student: {}\n".format(student_response)

             # Classify the intent
            intent = self.intent_detection(conversation)

            if 'OUT_OF_CONTEXT' in intent:
                chatml_messages.append({"role": "user", "content": "Politely say to student to stay on the topic not to diverge."})
            elif 'GREETING' in intent:
                chatml_messages.append({"role": "user", "content": "Greet the student and ask how you can help them."})
            elif 'BOOK_ENQUIRY' in intent:
                entities = self.enquiry_details(conversation)
                entities = entities.split(",")
                book_name = entities[0].split(":")[-1].strip(" '}{")
                language = entities[1].split(":")[-1].strip(" '}{")

                if book_name.upper() == "NULL":
                    chatml_messages.append({"role": "user", "content": "Ask the student for name of book"})
                elif language.upper() == "NULL":
                    chatml_messages.append({"role": "user", "content": "Ask the student for language of book"})
                else:
                    data = {
                                "name": book_name,
                                "language": language
                           }
                    response = requests.post(search_url, json=data)
                    resp_json = response.json()

                    if response.status_code == 200:
                        chatml_messages.append({"role": "user", "content": "Provide the details to the student as depicted in the below json in natural language in a single line, don't put it in the json format to the student:\n{}".format(str(resp_json))})
                        end_flag = True
                    else:
                        chatml_messages.append({"role": "user", "content": "Some invalid data is provided by the student. Provide the details to the student as depicted in the below json in natural language, don't put it in the json format to the student:\n{}".format(str(resp_json))})
                        end_flag = True
            elif 'CREATE_BOOK' in intent:
                entities = self.enquiry_details(conversation)
                entities = entities.split(",")
                book_name = entities[0].split(":")[-1].strip(" '}{")
                book_price = entities[1].split(":")[-1].strip(" '}{")
                book_author = entities[2].split(":")[-1].strip(" '}{")
                book_publisher = entities[3].split(":")[-1].strip(" '}{")
                book_language = entities[4].split(":")[-1].strip(" '}{")
                book_pages = entities[5].split(":")[-1].strip(" '}{")

                if book_name.upper() == "NULL":
                    chatml_messages.append({"role": "user", "content": "Ask the student for name of book"})
                elif book_price.upper() == "NULL":
                    chatml_messages.append({"role": "user", "content": "Ask the student for price of book"})
                elif book_author.upper() == "NULL":
                    chatml_messages.append({"role": "user", "content": "Ask the student for author of book"})
                elif book_publisher.upper() == "NULL":
                    chatml_messages.append({"role": "user", "content": "Ask the student for publisher of book"})
                elif book_language.upper() == "NULL":
                    chatml_messages.append({"role": "user", "content": "Ask the student for language of book"})
                elif book_pages.upper() == "NULL":
                    chatml_messages.append({"role": "user", "content": "Ask the student for number of pages in book"})
                else:
                    data = {
                        "name": book_name,
                        "price": book_price,
                        "author": book_author,
                        "publisher": book_publisher,
                        "language": book_language,
                        "pages": book_pages
                    }
                    response = requests.post(post_by_id_url, json=data)
                    resp_json = response.json()

                    if response.status_code == 200:
                        chatml_messages.append({"role": "user", "content": "Inform that book is created and provide the details to the student as depicted in the below json in natural language in a single line, don't put it in the json format to the student:\n{}".format(str(resp_json))})
                        end_flag = True
                    else:
                        chatml_messages.append({"role": "user", "content": "Some invalid data is provided by the student. Provide the details to the student as depicted in the below json in natural language, don't put it in the json format to the student:\n{}".format(str(resp_json))})
                        end_flag = True





if __name__ == "__main__":
    BC = BookChat()
    BC.conversation_chat()