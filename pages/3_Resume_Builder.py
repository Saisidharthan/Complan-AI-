import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib import colors
import requests
import tempfile
from menu import menu_with_redirect
st.set_page_config(page_title="Resume Builder", page_icon="🧠")
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

def create_resume_pdf(name, email, phone, address, education, experience, skills, hobbies, languages, leetcode_stats):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf_path = tmpfile.name

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=24, alignment=TA_CENTER
    )

    subtitle_style = ParagraphStyle(
        'SubtitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, spaceAfter=12, alignment=TA_LEFT
    )

    content_style = ParagraphStyle(
        'ContentStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, spaceAfter=10, leading=14
    )

    header_style = ParagraphStyle(
        'HeaderStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, spaceAfter=10, alignment=TA_CENTER
    )

    content = []
    content.append(Paragraph(name, title_style))
    content.append(Spacer(1, 6))
    contact_info = f"{email} &nbsp;&nbsp;|&nbsp;&nbsp; {phone}|&nbsp;&nbsp;{address}"
    contact_info = contact_info.replace("\n", ", ")
    contact_info = Paragraph(contact_info, header_style)
    content.append(contact_info)
    content.append(HRFlowable(width="100%", thickness=1, color="black"))
    content.append(Spacer(1, 12))

    def add_section(title, items, bullet=True):
        section = []
        section.append(Paragraph(title, subtitle_style))
        section.append(HRFlowable(width="40%", thickness=1, color="black", spaceAfter=6))
        for item in items:
            if bullet:
                section.append(Paragraph(f"• {item}", content_style))
            else:
                section.append(Paragraph(item, content_style))
        section.append(Spacer(1, 12))
        return section

    # Left half: Education, Work Experience, Hobbies
    left_column = []
    left_column.extend(add_section("Education", education, False))
    left_column.extend(add_section("Work Experience", experience, False))
    left_column.extend(add_section("Hobbies", hobbies))

    # Right half: Skills, LeetCode Stats, Languages
    right_column = []
    right_column.extend(add_section("Skills", skills))
    
    # LeetCode Stats
    leetcode_stats_section = [
        f"Total Problems Solved: {leetcode_stats.get('totalSolved', 'N/A')}",
        f"Easy Problems Solved: {leetcode_stats.get('easySolved', 'N/A')} / {leetcode_stats.get('totalEasy', 'N/A')}",
        f"Medium Problems Solved: {leetcode_stats.get('mediumSolved', 'N/A')} / {leetcode_stats.get('totalMedium', 'N/A')}",
        f"Hard Problems Solved: {leetcode_stats.get('hardSolved', 'N/A')} / {leetcode_stats.get('totalHard', 'N/A')}",
    ]
    right_column.extend(add_section("LeetCode Stats", leetcode_stats_section, False))
    right_column.extend(add_section("Languages", languages))

    # Combine both columns into a table layout
    data = [[left_column, right_column]]

    table = Table(data, colWidths=[3.5 * inch, 3.5 * inch])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))

    content.append(table)
    doc.build(content)

    return pdf_path

def get_stats(username: str):
    try:
        response = requests.get(f'https://leetcode-stats-api.herokuapp.com/{username}/')
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching stats: {e}")
        return {"status": "error", "message": "Could not reach backend, try again later."}

def main():
    
    st.title("Resume Builder")
    st.write("### Create a professional resume with ease.")

    with st.form(key='resume_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Personal Information")
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            address = st.text_input("Address")

        with col2:
            st.subheader("Resume Details")
            
            education = st.text_area("Education (separate entries with a newline)", value="\n".join(st.session_state.get('education', [])))
            experience = st.text_area("Work Experience (separate entries with a newline)", value="\n".join(st.session_state.get('experience', [])))
            skills = st.text_area("Skills (separate entries with a newline)", value="\n".join(st.session_state.get('skills', [])))
            hobbies = st.text_area("Hobbies (separate entries with a newline)", value="\n".join(st.session_state.get('hobbies', [])))
            languages = st.text_area("Languages (separate entries with a newline)", value="\n".join(st.session_state.get('languages', [])))
            leetcode_username = st.text_input("LeetCode Username")

            submit_button = st.form_submit_button("Generate PDF")
    
    if submit_button:
        if name and email and phone and address and education and experience and skills and hobbies and languages and leetcode_username:
            education_list = education.split('\n')
            experience_list = experience.split('\n')
            skills_list = skills.split('\n')
            hobbies_list = hobbies.split('\n')
            languages_list = languages.split('\n')

            leetcode_stats = get_stats(leetcode_username)
            
            pdf_path = create_resume_pdf(
                name, email, phone, address,
                education_list, experience_list, skills_list,
                hobbies_list, languages_list, leetcode_stats
            )
            
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
                st.download_button(label="Download Resume", data=pdf_bytes, file_name="resume.pdf", mime="application/pdf")
        else:
            st.error("Please fill out all fields before generating the resume.")

if __name__ == "__main__":
    main()
