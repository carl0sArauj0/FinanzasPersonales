import ollama
import json

def parse_expense(text):
    prompt = f"""
    Eres un asistente contable local. Tu tarea es extraer datos de gastos de un texto.
    Responde UNICAMENTE en formato JSON puro.
    Texto: "{text}"
    Formato: {{"monto": float, "categoria": string, "descripcion": string}}
    Si no hay un monto claro, devuelve {{"error": "no_data"}}.
    """
    try:
        response = ollama.chat(model='phi3', messages=[{'role': 'user', 'content': prompt}])
        # Limpiamos la respuesta por si el modelo añade texto extra
        content = response['message']['content']
        return json.loads(content[content.find('{'):content.rfind('}')+1])
    except Exception as e:
        print(f"Error parsing: {e}")
        return None