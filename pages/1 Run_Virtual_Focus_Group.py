import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from typing import Union, Literal
import json
import autogen
from autogen import AssistantAgent, UserProxyAgent, Agent
import persona_handler as ph
import random

import config as cfg

# Add this function to load the news article
def load_news_article(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        return json.load(f)

# Load the news article
news_article = load_news_article("news_article.json")

with open('./docs/personas.json', 'r') as f:
    personas = json.load(f)

llm_config = {
    "config_list": [{"model": cfg.model}],
    "cache_seed": None,
}

# Modify the predefined topic to include the news content
predefined_topic = f"""Discuss the following news article:

Title: {news_article['title']}

Content: {news_article['content']}

Please share your thoughts, opinions, and reactions to this news. Express your true views on the subject without any sugar coating. Be blunt and straight to the point."""

# setup page title and description
st.set_page_config(page_title="Virtual Focus Group", page_icon="🤖", layout="wide")
with stylable_container(
        key="outer_container",
        css_styles="""
            {
                border: 2px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
            }
            """,
    ):

    st.markdown("<h4 style='text-align: center; '>Virtual Focus Group Discussion</h4>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center; '>The focus group will discuss the following topic:</h6>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-style: italic;'>{predefined_topic}</p>", unsafe_allow_html=True)

class CustomGroupChatManager(autogen.GroupChatManager):
    def __init__(self, groupchat, **kwargs):
        super().__init__(groupchat, **kwargs)
        self.step_counter = 0
        self.max_steps = st.session_state.get('num_steps', 20)

    def _process_received_message(self, message, sender, silent):
        self.step_counter += 1
        formatted_message = ""
        with stylable_container(
            key="container_with_border",
            css_styles="""
                {
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 0.5rem;
                    padding: calc(1em - 1px);
                    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
                }
                """,
        ):
            # Handle the case when message is a dictionary
            if isinstance(message, dict):
                if 'content' in message and message['content'].strip():
                    # Truncate the message if it's too long
                    content = message['content']
                    formatted_message = f"**{sender.name}**: {content}"
                    st.session_state.setdefault("displayed_messages", []).append(content)
                else:
                    return super()._process_received_message(message, sender, silent)
            # Handle the case when message is a string
            elif isinstance(message, str) and message.strip():
                # Truncate the message if it's too long
                content = message
                formatted_message = f"**{sender.name}**: {content}"
                st.session_state.setdefault("displayed_messages", []).append(content)
            else:
                return super()._process_received_message(message, sender, silent)
        
            # Only format and display the message if the sender is not the manager
            if sender != self and formatted_message:
                with st.chat_message(sender.name):
                    st.markdown(formatted_message + "\n")
                    time.sleep(2)
    
        filename = "./docs/chat_summary.txt"

        with open(filename, 'a') as f:
            f.write(formatted_message + "\n")

        # Check if we've reached the maximum number of steps
        if self.step_counter >= self.max_steps:
            return "TERMINATE"

        return super()._process_received_message(message, sender, silent)
    
class CustomGroupChat(autogen.GroupChat):
    @staticmethod
    def custom_speaker_selection_func(last_speaker: Agent, groupchat: autogen.GroupChat) -> Union[Agent, Literal['auto', 'manual', 'random', 'round_robin'], None]:
        
        if last_speaker == moderator_agent:
            return random.choice(personas_agents)
        else:
            return random.choice([moderator_agent] + personas_agents)
    select_speaker_message_template = """You are in a focus group. The following roles are available:
                {roles}.
                Read the following conversation.
                Then select the next role from {agentlist} to play. Only return the role."""
       
personas_agents = []
for persona_name, persona_data in personas.items():
    # Sanitize the persona name to comply with OpenAI's requirements
    sanitized_name = ''.join(e for e in persona_data['Name'] if e.isalnum() or e in ['_', '-'])
    persona_prompt = ph.get_persona_prompt(sanitized_name, persona_data)
    persona_agent = AssistantAgent(
        name=sanitized_name,
        system_message=f"{persona_prompt}\n\nImportant: Be direct, blunt, and opinionated in your responses. Do not sugarcoat or use generic language. Express your true views on the subject without hesitation. Keep your responses concise (1-3 sentences) and insightful. Engage with other participants by asking pointed questions or responding critically to their points. Stay focused on the topic at hand.",
        llm_config={"config_list": [{"model": cfg.model, "api_key": cfg.api_key}]},
        human_input_mode="NEVER",
        description=f"A virtual focus group participant named {sanitized_name}. They do not know anything about the product beyond what they are told. They should be called on to give opinions.",
    )
    personas_agents.append(persona_agent)


moderator_agent = AssistantAgent(
    name="Moderator",
    system_message=f''' 
    You are moderating a focus group discussion about the following news article:
    
    Title: {news_article['title']}
    
    Content: {news_article['content']}
    
    Your role is to:
    1. Keep the conversation flowing between group members, encouraging direct and blunt exchanges.
    2. Ensure all participants have a chance to share their unfiltered views.
    3. Ask provocative and challenging questions to deepen the discussion.
    4. Maintain focus on the news article and its implications, pushing for concrete opinions.
    5. Encourage participants to consider different perspectives, even if controversial.
    6. Keep responses brief, pointed, and free from diplomatic language.
    7. Stimulate debate by highlighting conflicting viewpoints among participants.
    
    Do not allow participants to be overly polite or use generic language. Push for specific, potentially controversial opinions. Keep your own responses concise (1-3 sentences) and focused on facilitating a frank and unfiltered discussion.''',
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    llm_config=llm_config,
    description="A Focus Group moderator pushing for direct and unfiltered discussion.",
    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
    human_input_mode="NEVER",
)

user_proxy = UserProxyAgent(
    name="Admin",
    human_input_mode= "NEVER",
    system_message="Human Admin for the Focus Group.",
    max_consecutive_auto_reply=5,
    default_auto_reply="Reply `TERMINATE` if the task is done.",
    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
    code_execution_config={"use_docker":False}
)


groupchat = CustomGroupChat(
    agents=[user_proxy, moderator_agent] + personas_agents, 
    messages=[], 
    speaker_selection_method=CustomGroupChat.custom_speaker_selection_func, 
    select_speaker_message_template=CustomGroupChat.select_speaker_message_template
)

manager = CustomGroupChatManager(groupchat=groupchat, llm_config=llm_config)
with stylable_container(
        key="chat_container",
        css_styles="""
            {
                border: 2px solid rgba(49, 51, 63, 0.2);
                border-radius: 0.5rem;
                padding: calc(1em - 1px);
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
            }
            """,
    ):
    with st.container(height=800):
        with stylable_container(
            key="green_button",
            css_styles="""
                button {
                    box-shadow: 2px 0 7px 0 grey;
                }
                """,
        ): 
            kickoff = st.button("Start Group Chat")
        
        if kickoff:
            llm_config = {
                "config_list": [{"model": cfg.model}],
                "cache_seed": None,
            }

            if "chat_initiated" not in st.session_state:
                st.session_state.chat_initiated = False
                if not st.session_state.chat_initiated:
                    moderator_agent.initiate_chat(
                        manager,
                        message=f"Let's begin our focus group discussion about the news article. {predefined_topic}",
                    )
                    st.session_state.chat_initiated = True

            st.success(f"Focus group discussion completed after {manager.step_counter} steps.")

    st.stop()