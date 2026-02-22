import ollama
import json
import re

# app/core/parser.py

def parse_expense(text):
    print(f"-> IA analizando: {text}")
    
    # Instrucciones estrictas para las 3 categorías
    system_prompt = """Eres un extractor de datos financiero. 
    Solo puedes usar estas 3 categorías:
    1. Alimentos (Comida, supermercado, restaurantes, snacks)
    2. Gastos personales (Ropa, tecnología, hobbies, deporte, accesorios)
    3. Transporte (Bus, Uber, gasolina, Transmilenio, peajes)
    
    Responde solo en JSON puro.
    Ejemplo: {"monto": 5000.0, "categoria": "Transporte", "descripcion": "Uber al trabajo"}"""

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