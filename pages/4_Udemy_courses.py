import base64
import requests
import streamlit as st
from dotenv import load_dotenv
import os
from menu import menu_with_redirect
st.set_page_config(page_title="Candidate AI", page_icon="🧠")
menu_with_redirect()
load_dotenv()
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
def get_auth_header(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    auth_bytes = auth_str.encode("ascii")
    auth_base64 = base64.b64encode(auth_bytes).decode("ascii")
    return {"Authorization": f"Basic {auth_base64}"}

def fetch_udemy_courses(auth_header, query="", fields=""):
    base_url = "https://www.udemy.com/api-2.0/courses/"
    params = {
        "search": query,
        "page": 1,
        "page_size": 5,
        "fields[course]": fields
    }
    response = requests.get(base_url, headers=auth_header, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch courses: {response.status_code}")
        return None

def main():
    st.title("Udemy Courses Recommender")
    client_id = os.getenv("UDEMY_CLIENT_ID")
    client_secret = os.getenv("UDEMY_CLIENT_SECRET")
    query = st.text_input("Search for courses")

    fields = "title,headline,url,num_subscribers,avg_rating,price"

    if st.button("Search") and client_id and client_secret:
        auth_header = get_auth_header(client_id, client_secret)
        courses = fetch_udemy_courses(auth_header, query, fields)
        
        if courses:
            for course in courses.get('results', []):
                st.subheader(f"Title: {course['title']}")
                st.write(f"**Headline:** {course['headline']}")
                st.write(f"**Number of Subscribers:** {course['num_subscribers']}")
                st.write(f"**Average Rating:** {course['avg_rating']}")
                st.write(f"**Price:** {course['price']}")
                st.write(f"[View Course](https://www.udemy.com{course['url']})")

if __name__ == "__main__":
    main()
