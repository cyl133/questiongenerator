import openai

def generate_personas_from_article(article):
    # You'll need to set up your OpenAI API key
    openai.api_key = 'your-api-key-here'

    prompt = f"""
    Based on the following news article, identify the key stakeholders and generate personas for them. 
    For each persona, provide a name and a brief description of their background, interests, and potential stance on the topic.
    Format the output as a JSON object where the keys are the persona names and the values are their descriptions.

    News Article:
    {article}

    Generate 3-5 personas.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates personas based on news articles."},
            {"role": "user", "content": prompt}
        ]
    )

    personas = response.choices[0].message['content']
    return json.loads(personas)
