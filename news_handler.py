import json
from typing import List, Dict
import config as cfg

def load_news_article(file_path: str) -> Dict:
    with open(file_path, 'r') as f:
        return json.load(f)

def identify_stakeholders(article: Dict) -> List[str]:
    prompt = f"""
    Identify the key stakeholders mentioned or implied in the following news article:
    Title: {article['title']}
    Content: {article['content']}
    
    List the stakeholders, one per line.
    """
    response = cfg.client.chat.completions.create(
        model=cfg.model,
        messages=[{"role": "user", "content": prompt}]
    )
    stakeholders = response.choices[0].message.content.strip().split('\n')
    return [s.strip() for s in stakeholders if s.strip()]

def create_persona_for_stakeholder(stakeholder: str) -> Dict:
    prompt = f"""
    Create a detailed persona for the following stakeholder: {stakeholder}
    Include the following information:
    - Name
    - Background
    - Interests
    - Personality traits
    - Stance on the news topic
    
    Return the information as a JSON object, without any additional text or formatting.
    Ensure that the top-level keys are exactly: "Name", "Background", "Interests", "PersonalityTraits", and "StanceOnNewsTopic".
    """
    response = cfg.client.chat.completions.create(
        model=cfg.model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw_content = response.choices[0].message.content
    print(f"Raw API response for {stakeholder}:")
    print(raw_content)
    
    try:
        # Try to parse the JSON directly
        persona_data = json.loads(raw_content)
    except json.JSONDecodeError:
        print(f"Error decoding JSON for {stakeholder}. Attempting to clean and parse the response...")
        
        # Clean the response
        cleaned_content = raw_content.strip()
        # Remove any markdown code block indicators
        cleaned_content = cleaned_content.replace("```json", "").replace("```", "")
        
        try:
            # Try to parse the cleaned content
            persona_data = json.loads(cleaned_content)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON for {stakeholder} even after cleaning.")
            # If parsing fails, create a basic structure with available information
            persona_data = {}

    # Ensure the required keys are present
    required_keys = ["Name", "Background", "Interests", "PersonalityTraits", "StanceOnNewsTopic"]
    for key in required_keys:
        if key not in persona_data:
            persona_data[key] = "Information not available"

    # Ensure the Name is set to the stakeholder if it's not present or empty
    if not persona_data["Name"]:
        persona_data["Name"] = stakeholder

    return persona_data