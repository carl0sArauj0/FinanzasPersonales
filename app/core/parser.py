import ollama
import json
import re

def parse_expense(text):
    print(f"-> IA analizando: {text}")
    
    # Le damos ejemplos claros para que no tenga que "inventar" nada
    system_prompt = """Eres un extractor de datos financiero. 
    Solo respondes en JSON puro. Sin texto extra. 
    Ejemplo:
    Entrada: "Gasté 500 en pizza"
    Respuesta: {"monto": 500.0, "categoria": "Comida", "descripcion": "pizza"}"""

    try:
        # Cambiamos a llama3.2 que es mejor siguiendo formatos
        response = ollama.chat(
            model='llama3.2', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Extrae: {text}"}
            ],
            options={'temperature': 0} 
        )
        
        content = response['message']['content'].strip()
        
        # Limpiador avanzado: busca el primer '{' y el último '}'
        # Esto elimina textos como "Aquí tienes el JSON:" o "Saborlandia"
        content = re.search(r'\{.*\}', content, re.DOTALL).group(0)
        
        # Eliminar posibles comentarios o fallos de la IA (como el "or" que te dio)
        # Si la IA puso "categoria": "comida" or "ocio", lo forzamos a algo válido
        if " or " in content:
            content = content.split(" or ")[0] + '" }' # Intento de rescate

        data = json.loads(content)
        
        # Validamos que el monto sea un número real
        if isinstance(data.get('monto'), str):
            # Extraer solo los números de un string tipo "500 pesos"
            data['monto'] = float(re.findall(r'\d+\.?\d*', data['monto'])[0])
            
        return data

    except Exception as e:
        print(f"-> Error crítico: {e}. Contenido crudo: {content if 'content' in locals() else 'Nada'}")
        return {"error": "IA confundida, intenta de nuevo"}