import pytest
import sys
import os
import pickle
import json

# Agregar src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

def test_modelo_existe():
    assert os.path.exists('models/modelo_morosidad.pkl'), "Modelo no encontrado"

def test_modelo_carga():
    with open('models/modelo_morosidad.pkl', 'rb') as f:
        modelo = pickle.load(f)
    assert modelo is not None

def test_metricas_existen():
    assert os.path.exists('models/metricas.json')
    
    with open('models/metricas.json', 'r') as f:
        metricas = json.load(f)
    
    assert 'accuracy' in metricas
    assert metricas['accuracy'] > 0.5, "Accuracy muy bajo"

def test_prediccion_formato():
    with open('models/modelo_morosidad.pkl', 'rb') as f:
        modelo = pickle.load(f)
    
    import pandas as pd
    
    X_test = pd.DataFrame([{
        'monto_original': 5000,
        'monto_actual': 3000,
        'ratio_deuda': 0.6,
        'dias_desde_vencimiento': 45,
        'meses_mora': 1
    }])
    
    prediccion = modelo.predict(X_test)
    assert prediccion[0] in [0, 1, 2, 3], "Predicción fuera de rango"

if __name__ == "__main__":
    pytest.main([__file__, '-v'])