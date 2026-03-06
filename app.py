def procesar_df_csv(df):
    """
    Transforma el DataFrame de forma dinámica. 
    Detecta automáticamente todas las columnas de opciones antes de la columna de respuesta.
    """
    new_df = pd.DataFrame()
    new_df['Poll'] = ['Poll'] * len(df)
    new_df['Multiple choice'] = ['Multiple choice'] * len(df)
    new_df['Pregunta'] = [f'Pregunta {i+1}' for i in range(len(df))]
    
    # Supuestos de estructura:
    # Col 0: Pregunta
    # Col 1: Vacía (o descartable)
    # Col 2 en adelante: Opciones
    # Última Col: Respuesta correcta
    
    num_cols = df.shape[1]
    # Detectamos todas las columnas que son opciones (de la 2 hasta la penúltima)
    option_cols = list(range(2, num_cols - 1))
    answer_col_idx = num_cols - 1
    
    for i, row in df.iterrows():
        # Obtenemos la letra de la respuesta correcta (ej: 'E')
        correct_answer = str(row.iloc[answer_col_idx]).strip().upper()
        
        # Iteramos dinámicamente por todas las columnas de opciones detectadas
        for col_idx in option_cols:
            val = str(row.iloc[col_idx])
            
            # Calculamos la letra que corresponde a esta columna (2=A, 3=B, 4=C, etc.)
            # chr(65) es 'A', chr(66) es 'B'...
            letra_columna = chr(65 + (col_idx - 2))
            
            # Si la letra de esta columna coincide con la respuesta, marcamos
            if letra_columna == correct_answer:
                val = f"***{val}"
                
            # Asignamos al nuevo DataFrame
            new_df.loc[i, f'Option_{col_idx}'] = val
            
    return new_df