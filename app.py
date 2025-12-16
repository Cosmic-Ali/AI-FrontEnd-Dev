import streamlit as st
import dotenv
import langchain
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import zipfile
import os
from pathlib import Path
import PyPDF2
from io import BytesIO
from docx import Document

# Load environment variables
dotenv.load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("gemini_key",'')

# Load config variables
from backend.config import MODEL,system_prompt,SYSTEM_PROMPT

# Streamlit page setup
st.title("Website Portfolio Generator")
st.set_page_config(page_title="Website Portfolio Generator", page_icon="📜")

# File upload
upload_file = st.file_uploader("Upload your resume (PDF, Word format)", type=["pdf", "docx"])
if upload_file:
    
    col1, col2 = st.columns(2)
    with col1:
        
            if upload_file is not None:
                file_extension = Path(upload_file.name).suffix.lower()
                content = ""

                # Extract content based on file type
                if file_extension == ".pdf":
                    with BytesIO(upload_file.read()) as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            content += page.extract_text()
                    # st.subheader("Preview of extracted resume content:")
                    # st.write(content)
                    st.success("PDF uploaded successfully!")

                elif file_extension == ".docx":
                    doc = Document(upload_file)
                    for para in doc.paragraphs:
                        content += para.text + "\n"
                    # st.subheader("Preview of extracted resume content:")
                    # st.write(content)
                    st.success("DOCX uploaded successfully!")

                else:
                    st.warning("Unsupported file format. Please upload a PDF or DOCX file.")

                # Set up AI model for portfolio generation
                system_prompt = f'''
   You are an expert web developer with more than 15 years of experience in creating responsive, modern, and clean front-end websites using HTML, CSS, and JavaScript. Your task is to generate a complete sleek website front-end with modern design for a personal portfolio, with details extracted from the following resume:\n resume details: {content} \n Take some style ideas from the user prompt IF given below, or else just style it like a sleek modern website front-end. Link these files together -> index.html, style.css, script.js. Your output should only contain code for HTML, CSS, and JavaScript in the following exact format (do not add anything extra): 
    --html-- 
    [HTML code here] 
    --html-- 

    --css-- 
    [CSS code here] 
    --css-- 

    --js-- 
    [JavaScript code here] 
    --js--
    '''

                llm = ChatGoogleGenerativeAI(model=MODEL)
                msg = [("system", system_prompt)]
                user_prompt = st.text_area('Describe your website portfolio style')
                if st.button("Generate Portfolio"):

                    if user_prompt is not None:
                        msg.append(("user", user_prompt))
                    else:
                        msg.append(('user','.'))
                    response = llm.invoke(msg)

                    # Check the content type of the response and split accordingly
                    if isinstance(response.content, str):
                        # html_content = response.content.split("--html--")[1].split("--css--")[0].strip()
                        html_content = response.content.split("--html--")[1]
                        css_content = response.content.split("--css--")[1]
                        js_content = response.content.split("--js--")[1]

                        # Write HTML, CSS, and JS to files
                        with open("index.html", "w") as f:
                            f.write(html_content)
                        with open("style.css", "w") as f:
                            f.write(css_content)
                        with open("script.js", "w") as f:
                            f.write(js_content)

                        # Zip the files
                        with zipfile.ZipFile("website.zip", "w") as z:
                            z.write("index.html")
                            z.write("style.css")
                            z.write("script.js")
                        
                        success = st.success("Website Generated Successfully!")
                        if os.path.exists("website.zip"):
                            st.download_button("Download Website", data=open("website.zip", "rb"), file_name="website.zip")

                # else:
                #     st.error("Error: The response content is not in the expected format.")
                
            else:
                st.warning("Please upload a resume file to generate the portfolio.")

        

