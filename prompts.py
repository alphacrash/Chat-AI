# Prompts
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

Output Format: {'book_name': <Book name in strings>, 'book_price': <Price in strings>, 'book_author': <Author name in strings>, 'book_publisher': <Publisher name in strings>, 'book_language': <Language in strings>, 'book_pages': <Number of pages in strings>}
"""