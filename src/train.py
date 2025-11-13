import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import json
from preprocessing import preparar_datos

def entrenar_modelo():
    X, y, df = preparar_datos('data/deudas.csv')
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    modelo = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1  # Usa todos los cores disponibles
    )
    
    modelo.fit(X_train, y_train)
    
    y_pred = modelo.predict(X_test)
    
    print(classification_report(y_test, y_pred, 
                                target_names=['Al día', 'Leve', 'Grave', 'Crítica']))
    

    with open('models/modelo_morosidad.pkl', 'wb') as f:
        pickle.dump(modelo, f)
    
    with open('models/feature_names.json', 'w') as f:
        json.dump(list(X.columns), f)
    
    metricas = {
        'accuracy': float(modelo.score(X_test, y_test)),
        'n_estimators': 100,
        'max_depth': 10
    }
    
    with open('models/metricas.json', 'w') as f:
        json.dump(metricas, f, indent=2)
    
    return modelo, metricas

if __name__ == "__main__":
    entrenar_modelo()