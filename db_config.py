import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_CHATBOT_HOST = os.getenv("DB_CHATBOT_HOST")
DB_CHATBOT_NAME = os.getenv("DB_CHATBOT_NAME")
DB_CHATBOT_USER = os.getenv("DB_CHATBOT_USER")
DB_CHATBOT_PASS = os.getenv("DB_CHATBOT_PASS")

def get_airline_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        
    )
def get_chatbot_connection():
    return mysql.connector.connect(
        host=DB_CHATBOT_HOST,
        user=DB_CHATBOT_USER,
        password=DB_CHATBOT_PASS,
        database=DB_CHATBOT_NAME,
        
    )

