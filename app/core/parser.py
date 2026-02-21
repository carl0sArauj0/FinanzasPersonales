import ollama
import json

def parse_expense(text):
    print(f"-> IA pensando en: {text}...") # <-- Esto nos dirá que empezó
    prompt = f"""
    Eres un asistente contable. Extrae: monto, categoria y descripcion.
    Responde SOLO JSON puro.
    Texto: "{text}"
    Formato: {{"monto": float, "categoria": string, "descripcion": string}}
    """
    try:
        # Verifica que aquí diga 'phi3' o el modelo que descargaste
        response = ollama.chat(model='phi3', messages=[{'role': 'user', 'content': prompt}])
        
        content = response['message']['content']
        print(f"-> IA respondió: {content}") # <-- Veremos qué inventó la IA
        
        # Limpieza básica por si la IA agrega texto extra
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        return json.loads(content[json_start:json_end])
    except Exception as e:
        print(f"-> Error en la IA: {e}")
        return {"error": str(e)}