import ollama
import json
import re
from .database import get_config_categories
# app/core/parser.py

def parse_expense(text):
    print(f"-> IA analizando: {text}")
    
    mis_categorias = get_config_categories()
    categorias_str = ", ".join(mis_categorias)


    # Instrucciones estrictas para las 3 categorías
    system_prompt = """Eres un extractor de datos financiero. 
    Tu tarea es clasificar el mensaje del usuario en una de estas dos intenciones:
    1. GASTO: Solo puedes usar estas categorías para clasificar el gasto:
    1. Alimentos (Comida, supermercado, restaurantes, snacks)
    2. Gastos personales (Ropa, tecnología, hobbies, deporte, accesorios)
    3. Transporte (Bus, Uber, gasolina, Transmilenio, peajes)
    
    2. AHORRO: El usuario informa cuánto tiene o cuánto guardó. (Requiere: monto, banco, bolsillo)
    
    Responde en JSON. Ejemplo Ahorro:
    {"tipo": "ahorro", "monto": 50000, "banco": "Nequi", "bolsillo": "Viajes"}
    
    Ejemplo Gasto:
    {"tipo": "gasto", "monto": 1500, "categoria": "Alimentos", "descripcion": "pan"}
    """

    try:
        response = ollama.chat(
            model='llama3.2', 
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': f"Gasto: {text}"}
            ],
            options={'temperature': 0} 
        )
        
        content = response['message']['content'].strip()
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if not match: return {"error": "no_json"}
        
        data = json.loads(match.group(0))
        
        # Limpieza de monto (por si la IA pone texto)
        if isinstance(data.get('monto'), str):
            nums = re.findall(r'\d+\.?\d*', data['monto'])
            data['monto'] = float(nums[0]) if nums else 0.0
            
        return data
    except Exception as e:
        print(f"-> Error: {e}")
        return {"error": str(e)}