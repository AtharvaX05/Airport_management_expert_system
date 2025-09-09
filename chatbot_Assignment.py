from db_config import get_airline_connection, get_chatbot_connection

# Get DB connections
chatbot_conn = get_chatbot_connection()
chatbot_cursor = chatbot_conn.cursor(dictionary=True)

airline_conn = get_airline_connection()
airline_cursor = airline_conn.cursor(dictionary=True)

def get_chatbot_response(user_query):
    query = user_query.lower()

    # Search for matching Q&A
    chatbot_cursor.execute("SELECT * FROM ChatbotQA")
    qa_list = chatbot_cursor.fetchall()

    for qa in qa_list:
        if qa["QuestionPattern"] in query:
            if not qa["IsDynamic"]:
                return qa["Answer"]
            else:
                # Dynamic query case
                dynamic_sql = qa["DynamicQuery"]

                # crude parameter extraction (last word as parameter)
                param = query.split()[-1]  
                airline_cursor.execute(dynamic_sql, (param,))
                result = airline_cursor.fetchone()
                if result:
                    return f"{qa['Answer']} Result: {result}"
                else:
                    return "Sorry, I couldn't find relevant data."

    return "Sorry, I don’t have an answer for that yet."

# --- Simple Chat Loop ---
if __name__ == "__main__":
    print("Airport Chatbot 🤖 (type 'exit' to quit)")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print("Bot:", get_chatbot_response(user_input))
