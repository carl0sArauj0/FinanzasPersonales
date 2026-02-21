import ollama
import json
import re

def parse_expense(text):
    print(f"-> IA analizando: {text}")
    
    # El prompt ahora es una instrucción de sistema muy estricta
    prompt = f"Extrae monto, categoria y descripcion del texto: '{text}'. Responde solo JSON puro."
    
    try:
        # Añadimos 'options': {'temperature': 0} para que no alucine
        response = ollama.chat(
            model='phi3', 
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0} 
        )
        
        content = response['message']['content']
        
        # Buscamos TODOS los bloques que parezcan JSON
        # El patrón [^{}]* significa: busca algo que empiece con { y termine con } 
        # pero que no sea "codicioso" (que se detenga en el primer cierre)
        objs = re.findall(r'\{[^{}]*\}', content)
        
        if objs:
            # Tomamos SOLO el primero, ignoramos los ejercicios de "Saborlandia"
            clean_json = objs[0]
            print(f"-> JSON extraído: {clean_json}")
            
            data = json.loads(clean_json)
            
            # Validación extra: si el monto no es número, intentamos limpiarlo
            if isinstance(data.get('monto'), str):
                # Extrae solo números por si la IA puso "500 pesos"
                nums = re.findall(r'\d+\.?\d*', data['monto'])
                data['monto'] = float(nums[0]) if nums else 0.0
                
            return data
        else:
            print("-> No se encontró ningún JSON válido")
            return {"error": "no_json"}

    except Exception as e:
        print(f"-> Error: {e}")
        return {"error": str(e)}