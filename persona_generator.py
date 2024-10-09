import openai
import json

def generate_personas_from_article(article):
    # You'll need to set up your OpenAI API key
    openai.api_key = 'your-api-key-here'

    prompt = f"""
    Based on the following news article, identify 3-5 key stakeholders and generate personas for them.
    For each persona, provide a name and a brief description of their background, interests, and potential stance on the topic.
    Format the output as a valid JSON object where the keys are the persona names and the values are their descriptions.
    Ensure the JSON is properly formatted and can be parsed without errors.

    News Article:
    {article}

    Example of the expected JSON format:
    {{
        "John Doe": "Background: Local business owner. Interests: Economic growth, community development. Stance: Supports the initiative for potential business opportunities.",
        "Jane Smith": "Background: Environmental activist. Interests: Conservation, sustainable living. Stance: Opposes the project due to environmental concerns.",
        "Alex Johnson": "Background: City council member. Interests: Urban planning, public services. Stance: Neutral, seeking more information to make an informed decision."
    }}
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates well-formatted JSON personas based on news articles."},
            {"role": "user", "content": prompt}
        ]
    )

    personas_json = response.choices[0].message['content']
    
    # Ensure the response is valid JSON
    try:
        personas = json.loads(personas_json)
    except json.JSONDecodeError:
        raise ValueError("The API response could not be parsed as JSON. Please try again.")

    return personas
