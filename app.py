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
from gtts import gTTS
import base64
import speech_recognition as sr
import pyaudio
import time

language = "en"


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true" hidden="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )



def get_audio():
    text = ""
    recorder = sr.Recognizer()
    with sr.Microphone() as mic:
        recorder.adjust_for_ambient_noise(mic, duration=0.9)
        audio = recorder.listen(mic)

        print("You can start talking now")
        textt = st.write("listening... (you can start talking now)")
        print("Time is over")
        textt = st.write("Processing your speech")     
    try:
        text = recorder.recognize_google(audio)
    except:
         pass
    print(f"You said: {text}")
    return text



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
    llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.5, top_p=0.5, frequency_penalty=1, presence_penalty=0.4)
    memory = ConversationBufferMemory(memory_key='chat_history',return_messages=True,ai_prefix='SAHL')
    conversation_chain=ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorsstore.as_retriever(),
        memory=memory
        )
    return conversation_chain


def handle_userinput(user_question,test):
    response = st.session_state.conversation({'question':user_question})

    st.session_state.chat_history = response['chat_history']

    text = response['chat_history'][-1].content

    speech = gTTS(text=text, lang=language, slow=False, tld="com")
    speech.save("text2speech.mp3")
    autoplay_audio("text2speech.mp3")

    #for i, message in enumerate(st.session_state.chat_history):
    for i, message in enumerate( response['chat_history']):
        if i%2 ==0:
            #pass
            st.write(user_template.replace("{{MSG}}",message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace("{{MSG}}",message.content), unsafe_allow_html=True)


    
def get_chat_history(inputs) -> str:
    res = []
    for human, ai in inputs:
        res.append(f"Human:{human}\nAI:{ai}")
    return "\n".join(res)


pdf_file_paths = [
        r"2021-11-18-NASA-STD-5006A-w-Chg-2-Reval-Final.pdf",
        r"Subject.pdf",
        #r"nasa-std-5018_revalidated (1).pdf",
        #r"NASA-STD-87398-Revision-B_1.pdf",
        #r"NASA-STD-871928-WTMS-Baseline.pdf",
        #r"NASA-STD-871927-Baseline.pdf",
        #r"nasa-std-871926baseline.pdf",
        #r"nasa-std-5018_revalidated.pdf",
        #r"nasa-hdbk-4001.pdf",
        #r"nasa-gb-871913.pdf",
        ]
def main():
    # the page_icon is laptop icon
    load_dotenv()
    st.set_page_config(page_title='SAHL', page_icon=':robot_face:')
    st.write(css, unsafe_allow_html=True)
    st.header('SAHL Copilot :rocket:')
    def bind_socket():

       
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
    with st.sidebar:
#
        st.subheader("Upload your files here :sparkles:")
        st.write("Image or pdf files are accepted ! ")
        st.write("", unsafe_allow_html=True)
      
        pdf_docs =  st.file_uploader("Upload your file",type=["pdf", "png", "jpg"])
        if st.button("Submit"):
            if pdf_docs is not None:
                 with st.spinner("Uploading"):     
                      if(pdf_docs.type == "application/pdf"):
                            st.write("PDF file uploaded !")
                      elif(pdf_docs.type == "image/png" or pdf_docs.type == "image/jpeg"):
                            st.write("Image file uploaded !")
                            if(pdf_docs.name=="filletWeld.jpeg"):
                                st.write(bot_template.replace("{{MSG}}","For equal-leg fillet welds, the fillet size is equal to the leg length of the largest inscribed right isosceles triangle."), unsafe_allow_html=True)

            else:
                 st.write("Please upload a file of type: " + ", ".join(["pdf", "png", "jpg"]))
    keywords = st.text_input("Write your message here : ",help="Write your  message here and our powerfull AI will give you the answer !", max_chars=None, placeholder="How does heat effects welding ?", type="default")
    Prompt =""

    #Prompt ="You are Standards Technical Assistance Resource AI named 'SAHL' and you are a copilot. and your task is to help answer all the questions based on the guides I gave to you on this form :' Section: section number.Issue: issue description   , and My question is  "
    st.button("Microphone :microphone:")
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
    
    st.write("<a href='https://www.spaceappschallenge.org/2023/find-a-team/keplers-crew/' id='my-link' >Made with ❤️ by Kepler's Crew</a>", unsafe_allow_html=True)
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
