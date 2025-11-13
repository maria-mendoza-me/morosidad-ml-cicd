import pandas as pd
from datetime import datetime

def preparar_datos(ruta_csv):

    df = pd.read_csv(ruta_csv)
    
    df['en_mora'] = df['meses_mora'].apply(lambda x: 1 if x > 0 else 0)
    
    df['fecha_vencimiento'] = pd.to_datetime(df['fecha_vencimiento'])
    df['dias_desde_vencimiento'] = (datetime.now() - df['fecha_vencimiento']).dt.days
    df['ratio_deuda'] = df['monto_actual'] / df['monto_original']
    
    def categorizar_mora(meses):
        if meses == 0:
            return 0  # Al día
        elif meses == 1:
            return 1  # Leve
        elif meses == 2:
            return 2  # Grave
        else:
            return 3  # Crítica
    
    df['categoria_mora'] = df['meses_mora'].apply(categorizar_mora)
    
    features = ['monto_original', 'monto_actual', 'ratio_deuda', 
                'dias_desde_vencimiento', 'meses_mora']
    
    X = df[features]
    y = df['categoria_mora']
    
    return X, y, df

if __name__ == "__main__":
    X, y, df = preparar_datos('data/deudas.csv')
    print(f"Distribución de categorías:\n{y.value_counts()}")