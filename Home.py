import streamlit as st
import json
from news_handler import load_news_article, identify_stakeholders, create_persona_for_stakeholder

st.set_page_config(page_title="Virtual Focus Group", page_icon=":tada:", layout="wide")

def save_personas(personas):
    with open("docs/personas.json", "w") as f:
        json.dump(personas, f, indent=2)

def main():
    st.title("Generate Personas from News Article")

    # Set the default news article path
    news_article_path = "news_article.json"

    # Configure number of personas to create
    num_personas = st.number_input("Number of personas to create:", min_value=1, max_value=10, value=3)

    # Configure number of discussion steps
    num_steps = st.number_input("Number of discussion steps:", min_value=1, max_value=50, value=20)

    if st.button("Generate Personas"):
        article = load_news_article(news_article_path)
        stakeholders = identify_stakeholders(article)
        
        # Limit the number of stakeholders to the specified number of personas
        stakeholders = stakeholders[:num_personas]
        
        personas = {}
        for stakeholder in stakeholders:
            persona = create_persona_for_stakeholder(stakeholder)
            personas[persona['Name']] = persona
        st.session_state.personas = personas
        save_personas(personas)
        # Save the number of steps to session state
        st.session_state.num_steps = num_steps
        st.success(f"{num_personas} personas generated and saved successfully!")

    # Display and allow editing of generated personas
    if 'personas' in st.session_state:
        st.write("Generated Personas:")
        for name, persona in st.session_state.personas.items():
            with st.expander(name):
                st.json(persona)

        if st.button("Edit Personas"):
            st.session_state.editing = True

    if st.session_state.get('editing', False):
        edited_personas = {}
        for name, persona in st.session_state.personas.items():
            with st.expander(f"Edit {name}"):
                edited_persona = {}
                for key, value in persona.items():
                    if isinstance(value, list):
                        edited_persona[key] = st.text_area(f"{key} (comma-separated)", ", ".join(value))
                    else:
                        edited_persona[key] = st.text_area(key, value)
                edited_personas[name] = edited_persona

        if st.button("Save Edited Personas"):
            st.session_state.personas = edited_personas
            save_personas(edited_personas)
            st.success("Edited personas saved successfully!")
            st.session_state.editing = False

    # Button to launch focus group
    if st.button("Launch Focus Group"):
        st.switch_page("pages/1 Run_Virtual_Focus_Group.py")

if __name__ == "__main__":
    main()