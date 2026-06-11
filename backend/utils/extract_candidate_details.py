from services.llm_initialization import groq_client
import json

def extract_name(res_text):

    prompt = f"""
        Extract the candidate's full name.

        Return ONLY JSON.
        Do not wrap the response in markdown.
        Do not use ```json.

        Format:
        {{"name": "candidate full name"}}

        Resume:
        {res_text[:3000]}
    """

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content  = response.choices[0].message.content


    data = json.loads(content)

    candidate_name = data["name"]

    return candidate_name


