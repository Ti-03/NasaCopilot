import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings  import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from htmlTemplates import bot_template, user_template, css
from streamlit_tags import st_tags
from openpyxl import load_workbook
import time



def get_pdf_text(pdf):
    text=""
    # pdf in pdf_docs:
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
            text += " "+page.extract_text()

    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len

    )
    chunks = text_splitter.split_text(text)
 
    return chunks 
    

def get_vectorsstore(text_chunks):
    embeddings = OpenAIEmbeddings() # using open ai embeddings which is online 
    #embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl") # using hugging face embeddings which is offline and depends on computer hardware
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding = embeddings)
    return vectorstore



    #return response[0][0]
def get_conversation_chain(vectorsstore):
    # model_name='gpt-3.5-turbo', temperature=0.5, top_p=0.5, frequency_penalty=0, presence_penalty=0.4
    llm = ChatOpenAI(model_name='gpt-3.5-turbo')
    memory = ConversationBufferMemory(memory_key='chat_history',return_messages=True,ai_prefix='Sahl')
    conversation_chain=ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorsstore.as_retriever(),
        memory=memory
        )
    return conversation_chain


def handle_userinput(user_question,just_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", just_question), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


    
def get_chat_history(inputs) -> str:
    res = []
    for human, ai in inputs:
        res.append(f"Human:{human}\nAI:{ai}")
    return "\n".join(res)



def main():
    # the page_icon is laptop icon
    load_dotenv()
    st.set_page_config(page_title='Sahl', page_icon=':robot_face:')
    st.write(css, unsafe_allow_html=True)

    st.header('Sahl Copilot :sparkles:')
    def bind_socket():

        pdf_file_paths = [
        r"nasa-std-5018_revalidated.pdf",
        r"nasa-hdbk-4001.pdf",
        #r"nasa-gb-871913.pdf",
        ]
        text_chunks = []
        for pdf_file_path in pdf_file_paths:
            with open(pdf_file_path, 'rb') as f:
                raw_text = get_pdf_text(f)
                text_chunks.extend(get_text_chunks(raw_text))
        #st.write(text_chunks)
        vectorsstore = get_vectorsstore(text_chunks)
        st.session_state.conversation = get_conversation_chain(vectorsstore)
        st.session_state['started'] = True

    # This function will only be run the first time it's called
        #print("Socket bound!")
    if "started" not in st.session_state:
        bind_socket()


    if "conversation" not in st.session_state:   # we have to initialize the conversation if it's not already there
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:   # we have to initialize the chat_history if it's not already there
        st.session_state.chat_history = None


    
                # read the PDF file
    #file_path = r"nasa-std-5018_revalidated.pdf"
    #with open(file_path, 'rb') as f:
    #            #get pdf text
    #                raw_text = get_pdf_text(f)
    #            #get text chumcks
    #                text_chunks = get_text_chunks(raw_text)
    #               
    #                st.write(text_chunks)
#
    #               
    #                vectorsstore = get_vectorsstore(text_chunks )
    #                # ccreate co conversation chain 
    #                st.session_state.conversation = get_conversation_chain(vectorsstore)
    #    

     

    #####################




    











    #############
            
    keywords = st.text_input("Write your message here : ",help="Write your  message here and our powerfull AI will give you the answer !", max_chars=None, placeholder="How to turn off the rocket ?", type="default")
    #Prompt =""
    Prompt ="You are Standards Technical Assistance Resource AI named 'Sahl' and you are a copilot. and your task is to help answer all the questions based on the guides I gave to you on this form :' Section: section number.Issue: issue description   , and My question is  "
   
    if st.button("Send :arrow_forward:"):
        with st.spinner("Processing..."):
            if st.session_state.conversation is None:
               st.write(bot_template.replace("{{MSG}}","Error in our systems, Please try again later.."), unsafe_allow_html=True)
            else:
                if len(keywords) > 0:
                 
                    handle_userinput(Prompt+keywords,keywords)
                else:
                    st.write(bot_template.replace("{{MSG}}","Please enter your question ! "), unsafe_allow_html=True)


#MainMenu {visibility: hidden;}
    hide_st_style = """
            <style>
           
            
            footer {visibility: hidden;}
           
            #my-link{
            text-decoration: blink;
            font-size: 12px;
            position: fixed;
            bottom: 10px;

            }
           
            </style>
            """
    
    st.write("<a href='https://twitter.com/Qutibah_' id='my-link' >Made with ❤️ by Kepler's Crew</a>", unsafe_allow_html=True)
    st.markdown(hide_st_style, unsafe_allow_html=True) 
    #with st.sidebar:
##
    #    st.subheader("JUST AI تفاصيل اكثر عن :sparkles:")
    #    st.write("نظام مبني على الذكاء الاصطناعي للتسهيل والتسريع على الطلبة في عملية بناء الجدول المناسب , وهذه النسخة هي نسخة تجريبية فقط ")
    #    st.write("", unsafe_allow_html=True)
       
    #    pdf_docs =  st.file_uploader("Upload your file",accept_multiple_files=True)
    #    if st.button("Submit"):
    #        #with st.spinner("Loading..."):
    #       



if __name__ == '__main__':
    main()