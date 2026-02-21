import ollama
import json

def parse_expense(text):
    prompt = f"""
    Eres un asistente de finanzas. Extrae la información del siguiente texto y responde SOLO en formato JSON.
    Texto: "{text}"
    Formato esperado: {{"monto": float, "categoria": string, "descripcion": string}}
    """
    response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
    try:
        return json.loads(response['message']['content'])
    except:
        return None