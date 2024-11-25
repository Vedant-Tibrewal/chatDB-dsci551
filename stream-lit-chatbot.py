# import streamlit as st

# def create_chatbot():
#     # Set page configuration
#     st.set_page_config(page_title="Chatbot", page_icon="💬")
#     st.title("Simple Chatbot")
    
#     # Initialize chat history in session state
#     if "messages" not in st.session_state:
#         st.session_state.messages = [
#             {"role": "assistant", "content": "How may I help you today?"}
#         ]
    
#     # Display chat messages
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])
    
#     # Handle user input
#     if prompt := st.chat_input("Enter your message"):
#         # Add user message to chat
#         st.session_state.messages.append({"role": "user", "content": prompt})
        
#         # Display user message
#         with st.chat_message("user"):
#             st.markdown(prompt)
        
#         # Generate and display assistant response
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking..."):
#                 # Replace this with your actual response generation logic
#                 response = f"I received your message: {prompt}"
#                 st.markdown(response)
        
#         # Add assistant response to chat history
#         st.session_state.messages.append({"role": "assistant", "content": response})

# if __name__ == "__main__":
#     create_chatbot()

import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime

def fetch_mysql_data():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Qwertyabcd123",
            database="mysql"
        )
        query = "SELECT * FROM user LIMIT 5;"
        df = pd.read_sql_query(query, connection)
        return df
    except Exception as e:
        return pd.DataFrame({'Error': [str(e)]})
    
def create_chatbot():
    # Set page configuration
    st.set_page_config(page_title="Database Chatbot", page_icon="💬", layout="wide")
    
    # Create sidebar
    with st.sidebar:
        st.title("Database Explorer")
        if st.button("Show Sample Data"):
            df = fetch_mysql_data()
            st.session_state['current_df'] = df
    
    # Main content
    st.title("Database Query Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I can help you query the database. What would you like to know?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display table if message contains DataFrame
            if 'df' in message:
                st.dataframe(message["df"], use_container_width=True)
    
    # Handle user input
    if prompt := st.chat_input("Enter your query"):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Querying database..."):
                try:
                    # Sample data display - replace with actual query logic
                    df = fetch_mysql_data()
                    
                    response = "Here's the data you requested:"
                    st.markdown(response)
                    st.dataframe(df, use_container_width=True)
                    
                    # Store both text and DataFrame in message history
                    message_with_data = {
                        "role": "assistant",
                        "content": response,
                        "df": df
                    }
                    st.session_state.messages.append(message_with_data)
                    
                except Exception as e:
                    error_message = f"Error executing query: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })

# Add data visualization section
def add_visualizations(df):
    st.subheader("Data Visualizations")
    
    # Show basic statistics
    st.write("Basic Statistics:")
    st.dataframe(df.describe())
    
    # Column selection for plotting
    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            selected_col = st.selectbox("Select column for histogram", numeric_cols)
            st.bar_chart(df[selected_col])
        
        with col2:
            st.line_chart(df[selected_col])

if __name__ == "__main__":
    create_chatbot()