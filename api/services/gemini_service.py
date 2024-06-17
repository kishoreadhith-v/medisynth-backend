import google.generativeai as genai
import os
import json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_patient_info_and_anomalies(text):
    prompt = (
        "Extract patient information and anomalies from the following lab report text. "
        "The output should be a JSON object with the following structure:\n"
        "{\n"
        "  \"patient_info\": {\n"
        "    \"name\": \"<name>\",\n"
        "    \"age\": <age>,\n"
        "    \"gender\": \"<gender>\",\n"
        "    \"patient_id\": \"<patient_id>\",\n"
        "    \"contact_info\": {\n"
        "      \"phone\": \"<phone>\",\n"
        "      \"email\": \"<email>\"\n"
        "    }\n"
        "  },\n"
        "  \"anomalies\": [\n"
        "    {\n"
        "      \"test_name\": \"<test_name>\",\n"
        "      \"value\": <value>,\n"
        "      \"normal_range\": \"<normal_range>\",\n"
        "      \"comments\": \"<comments>\"\n"
        "    },\n"
        "    ...\n"
        "  ]\n"
        "}\n\n"
        "Here is the lab report text:\n"
        f"{text}"
    )
    
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    response = model.generate_content([prompt])
    
    response_text = response.candidates[0].content.parts[0].text.strip()
    
    if response_text.startswith("```json") and response_text.endswith("```"):
        response_text = response_text[7:-3].strip()
    
    return json.loads(response_text)
