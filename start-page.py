import streamlit as st
from streamlit_option_menu import option_menu
from menu import menu

st.set_page_config(page_title="Complan AI", page_icon="🧠", layout="centered")
if 'role' not in st.session_state:
    st.session_state.role = None
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


def main():
    st.title("Welcome to the Complan AI!")
    st.subheader("Please choose your role?")
    col1,col2 = st.columns([1,5])
    with col1:
        if st.button("Candidate"):
            st.session_state.role = "candidate"
            st.switch_page("pages/Candidate.py")
    with col2:
        if st.button("Recruiter"):
            st.session_state.role = "hirer"
            st.switch_page("pages/Recruiter.py")
        
menu()

if __name__ == '__main__':
    main()