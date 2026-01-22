import json
import streamlit as st

def extract_questions_to_list(raw_text, llm):
    prompt = f"""
    You are a document parser. Your goal is to identify distinct compliance requirements from the text.

    Instructions:
    - Group related sub-points into a single requirement if they belong together.
    - Do not invent questions; only extract what is present.
    - Output must be a valid JSON object with a key "requirements" containing a list of strings.

    TEXT TO ANALYZE:
    {raw_text}

    OUTPUT FORMAT:
    {{"requirements": ["Requirement 1", "Requirement 2"]}}
    """
    content = ""
    try:
        response = llm.invoke(prompt)
        content = response.content

        if isinstance(content, list):
            content = "".join([block.get("text", "") if isinstance(block, dict) else str(block) for block in content])

        clean_content = content.replace("```json", "").replace("```", "").strip()

        data = json.loads(clean_content)
        return data.get("requirements", [])

    except Exception as e:
        st.error(f"Error parsing JSON: {e}")
        return [line for line in content.split('\n') if len(line) > 20]
