import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timedelta
import os
import time
from menu import menu_with_redirect
st.set_page_config(page_title="Job Interview Simulator", page_icon="📈")
menu_with_redirect()
Page_style="""
<style>
    [data-testid="stAppViewContainer"]{
        background-image:url("https://img.freepik.com/free-vector/futuristic-background-design_23-2148503793.jpg");
        background-size:cover;
    }
    [data-testid="stHeader"] {
    background-color:rgba(0,0,0,0);
    }
    [data-testid="stSidebarContent"]{
        background-image:url("https://img.freepik.com/free-vector/futuristic-background-design_23-2148503793.jpg");
        background-size:cover;
    }
        [data-testid="baseButton-header"]{
        color:transparent;
    }
</style>
"""
st.markdown(Page_style,unsafe_allow_html=True)

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
model = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)


def generate_questions(job_role, work_experience):
    system_template = (
        "You are an intelligent competency diagnostic system. Ask a series of questions to the job seeker "
        "to test their competence, and based on their scores, recommend jobs to them."
    )
    human_prompt = f"Assume the given job seeker is a {job_role} with {work_experience} years of experience. Generate a set of 5 questions to test their competence."
    prompt_template = ChatPromptTemplate.from_messages([("system", system_template), ("user", human_prompt)])
    parser = StrOutputParser()
    chain = prompt_template | model | parser

    try:
        response = chain.invoke({"job_role": job_role, "work_experience": work_experience})
        return response
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return ""

def get_questions(context):
    class Questions(BaseModel):
        set_of_questions: List[str] = Field(description="List of questions to test the competence of the job seeker")

    parser = PydanticOutputParser(pydantic_object=Questions)
    format_instructions = parser.get_format_instructions()
    human_prompt = f"Here is the context: {context}. Extract the set of questions from the given context to test the competence of the job seeker. Generate the questions in the following format: {format_instructions}"
    prompt = PromptTemplate(
        template="You are an intelligent information extractor. Extract the set of questions from the given context to test the competence of the job seeker in a List format.\n{format_instructions}\n{human_prompt}\n",
        input_variables=["human_prompt"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | model | parser

    try:
        response = chain.invoke({"human_prompt": human_prompt})
        return response
    except Exception as e:
        st.error(f"Error extracting questions: {e}")
        return ""

def calculate_score(answers, job_role, work_experience):
    human_prompt = f"Assume the given job seeker is a {job_role} with {work_experience} years of experience. Calculate the score of the job seeker based on their answers to the questions. Here is the set of answers provided by the job seeker for each question: {answers}. Each question can be scored out of 5 points, leading to a maximum possible score of 25 points as only a set of 5 questions and answers are provided."
    prompt = PromptTemplate(
        template="You are an intelligent competency diagnostic system. You are required to calculate the score of the job seeker based on their answers to the questions based on their job role and work experience.\n{human_prompt}",
        input_variables=["human_prompt"],
    )
    parser = StrOutputParser()
    chain = prompt | model | parser

    try:
        response = chain.invoke({"human_prompt": human_prompt})
        return response
    except Exception as e:
        st.error(f"Error generating scores: {e}")
        return ""

def format_remaining_time(remaining_time):
    minutes, seconds = divmod(remaining_time.seconds, 60)
    return f"{minutes:02}:{seconds:02}"

def main():
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'final_answers' not in st.session_state:
        st.session_state.final_answers = {}
    if 'job_role' not in st.session_state:
        st.session_state.job_role = ""
    if 'work' not in st.session_state:
        st.session_state.work = ""
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'time_limit' not in st.session_state:
        st.session_state.time_limit = timedelta(minutes=1)
    if 'end_time' not in st.session_state:
        st.session_state.end_time = None
    if 'response' not in st.session_state:
        st.session_state.response = ""

    st.title("Job Interview Simulator")
    st.markdown("Enter your job role and work experience to generate a set of questions. You will have a limited time to answer them.")
    
    with st.sidebar:
        st.session_state.job_role = st.text_input("Enter your job role")
        st.session_state.work = st.text_input("Enter your work experience")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Generate Questions"):
            response = generate_questions(st.session_state.job_role, st.session_state.work)
            res = get_questions(response)
            if len(res.set_of_questions) == 5:
                st.session_state.questions = res.set_of_questions
                st.session_state.start_time = datetime.now()
                st.session_state.end_time = st.session_state.start_time + st.session_state.time_limit
                st.success("Questions generated! You have 5 minutes to complete the test.")
    
    with col2:
        if st.button("Reset Test"):
            st.session_state.clear()
            st.rerun()

    if st.session_state.response:
        st.write(st.session_state.response)
    
    if st.session_state.questions:
        remaining_time = st.session_state.end_time - datetime.now()
        timer_placeholder = st.empty()
        progress_placeholder = st.empty()
        for question in st.session_state.questions:
            st.write(question)
            answer = st.text_input("Enter your answer", key=question)
            st.session_state.final_answers[question] = answer

        if st.button("Submit Answers"):
            response = calculate_score(st.session_state.final_answers, st.session_state.job_role, st.session_state.work)
            st.session_state.questions.clear()
            st.session_state.response = response
            st.rerun()

        while remaining_time > timedelta(seconds=0):
            remaining_time = st.session_state.end_time - datetime.now()
            if remaining_time <= timedelta(seconds=0):
                st.write("⏳ Time's up! Submitting your answers automatically...")
                st.session_state.final_answers = {q: st.session_state.final_answers.get(q, '') for q in st.session_state.questions}
                
                response = calculate_score(st.session_state.final_answers, st.session_state.job_role, st.session_state.work)
                st.session_state.questions.clear()
                st.session_state.response = response
                st.rerun()
                break

            timer_placeholder.markdown(f"⏳ Time remaining: {format_remaining_time(remaining_time)}")
            time_percentage = (st.session_state.time_limit - remaining_time) / st.session_state.time_limit
            progress_placeholder.progress(time_percentage, text=f"Time remaining: {format_remaining_time(remaining_time)}")

            time.sleep(1)
    else:
        st.info("Generate questions to start the test.")

if __name__ == "__main__":
    main()
