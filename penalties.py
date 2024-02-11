# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 15:46:09 2022

Last modification on Sat Feb 10 16:15:32

@author: Agustín Germán Rojas (mail: agustingermanrojas@gmail.com)

La función penalties calcula ciertos parámetros del lanzamiento de un penal en fútbol.
Estos parámetros son:
                        - Velocidad promedio de lanzamiento
                        - Distancia del balón al centro del arco al pasar por la línea de gol

Para esto utiliza un archivo .xlsx exportado por Nacsport en formato 2 y toma ciertos valores
de un archivo Parameter.xlsx, completado anteriormente por el usuario.

Luego, devuelve un .csv con el nombre penalties***.csv en el mismo directorio, donde *** es
el número de archivo procesado.

Además, suma esos registros a penalties.csv, en donde se almacenan todos los registros.

Los archivos exportados por Nacsport deberán contener los datos devenidos de una plantilla con:
    Categoría:  Jugador lanzador del penal
    Descriptores:   - Fecha de la ejecución (asignado automáticamente a cada categoría)
                    - Cuadrante del arco objetivo del penal (1 a 4 empezando de derecha
                      a izquierda en contra de las agujas del reloj desde la perspectiva
                      del lanzador:
                                        - 1 arriba derecha
                                        - 2 arriba izquierda
                                        - 3 abajo izquierda
                                        - 4 abajo derecha
                    - Resultado (arco, palo, fuera)
                    - Gráfico: Par XY indicando destino del balón al llegar a la línea de fondo/gol

"""

import pandas as pd
import numpy as np
from tkinter import Tk, filedialog, PhotoImage, messagebox


# Sección 1: IMPORTACIÓN
# Se carga el archivo de parámetros y se limpian datos


# Cargo los parámetros de la imagen utilizada para marcar el destino del penal
try:
    parameters = pd.read_excel('Parameters.xlsx')
except FileNotFoundError:
    data = {'Parameter': ['fps', 'img_width_px', 'img_height_px','goal_width_px',
                          'goal_height_px','goal_width_cm','goal_height_cm','penalty_distance_cm', 'ErPOS', 'ErDIS'], 
                          'Value': [None, None, None, None, None, None, None, None, None, None]}
    df_parameters = pd.DataFrame(data)
    df_parameters.to_excel('Parameters.xlsx', index=False)

    messagebox.showerror('Error', 'No existe el archivo Parameters.xlsx, así que lo voy a crear. '
      'Lo vas a encontrar en esta misma carpeta, tenés que '
      'completar los valores pedidos (fotogramas por segundo '
      'del video y medidas en pixeles de la imagen del arco '
      'que usaste y las medidas totales de la misma, además de valores de errores). Cuando '
      'termines, volvé a ejecutar el script.')
    
    raise SystemExit

fps = float(parameters.iloc[0, 1])

img_width_px = int(parameters.iloc[1, 1])
img_height_px = int(parameters.iloc[2, 1])

goal_width_px = int(parameters.iloc[3, 1])
goal_height_px = int(parameters.iloc[4, 1])
goal_width_cm = float(parameters.iloc[5, 1])
goal_height_cm = float(parameters.iloc[6, 1])

penalty_distance_cm = float(parameters.iloc[7, 1])

ErPOS = float(parameters.iloc[8, 1])
ErDIS = float(parameters.iloc[9, 1])

# Ventana emergente
root = Tk()
icon = PhotoImage(file='ico.png') # Cambio el ícono de la ventana
root.iconphoto(True, icon)
root.withdraw()

# Cuadro de diálogo para seleccionar un archivo
file_path = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx;*.xls")])
root.destroy()

# Verifico si se seleccionó un archivo
if file_path:
    # Cargo el archivo en un DataFrame
    df = pd.read_excel(file_path)

else:
    messagebox.showerror('Error', 'No se seleccionó ningún archivo')

# Limpieza de datos
df = df.drop(df.columns[9:], axis=1)  # Elimino desde la novena columna en adelante
df = df.drop("Click", axis=1)  # Elimino la columna "Click"


# Sección 2: DISTANCIA
# Se realiza la conversión de las coordenadas XY a unidades de metros y se calculan distancias


# Separo la columna XY en X e Y en pixeles
XY = df['XY'].str.split(pat=';', expand = True)
XY.columns = ['X_px', 'Y_px']
df = pd.concat([df, XY], axis = 1)
df['X_px'] = df['X_px'].astype(int)
df['Y_px'] = df['Y_px'].astype(int)
df = df.drop("XY", axis=1)  # Elimina la columna "XY"

# El (0,0) se encuentra abajo a la izquierda de la imagen, llevo el eje al centro del arco 
a = img_width_px/(-2) #Constante que suma a X
b = goal_height_px/(-2) #Constante que suma a Y

# Transformo las constantes en series para sumarlas a toda la columna
cte = pd.DataFrame()
cte['c'] = pd.Series([a for x in range(len(df.index))]) 
cte['d'] = pd.Series([b for x in range(len(df.index))])

# Defino X,Y sumando las constantes
df['X_px'] = df['X_px'] + cte['c']
df['Y_ground'] = df['Y_px'] # Defino Y_ground para usarlo en el cálculo de la distancia, con el eje en piso
df['Y_px'] = df['Y_px'] + cte['d']

# Transformo las distancias en pixeles en distancias en metros
conversion_px_m_X = (goal_width_cm / goal_width_px) / 100
conversion_px_m_Y = (goal_height_cm / goal_height_px) / 100
df['X_m'] = df['X_px'] * conversion_px_m_X
df['Y_ground'] = df['Y_ground'] * conversion_px_m_Y
df['Y_m'] = df['Y_px'] * conversion_px_m_Y
L_m = penalty_distance_cm / 100 # Distancia del punto a la linea en metros
df['D_m'] = np.sqrt(L_m**2+df['X_m']**2+df['Y_ground']**2)


# Sección 3: TIEMPO
# Se calcula la duración del remate y se realiza la conversión a segundos


# Divido las columnas de inicio y fin en columnas de horas, minutos y segundos
start = df['Inicio'].str.split(pat=':', expand=True)
start.columns = ['start_m', 'start_s', 'start_cs']
final = df['Fin'].str.split(pat=':', expand=True)
final.columns = ['finaR_m', 'final_s', 'final_cs']
df = pd.concat([df, start, final], axis=1)

# Convierto las columnas a números enteros
df[['start_m', 'start_s', 'start_cs', 'finaR_m', 'final_s', 'final_cs']] = \
df[['start_m', 'start_s', 'start_cs', 'finaR_m', 'final_s', 'final_cs']].astype(int)

# Calculo la duración en segundos con la conversión: 1m = 60s | 1s = 100cs
df['duration_m'] = (df['finaR_m'] - df['start_m']) * 6000
df['duration_s'] = (df['final_s'] - df['start_s']) * 100
df['duration_cs'] = df['final_cs'] - df['start_cs']
df['T_s'] = (df['duration_m'] + df['duration_s'] + df['duration_cs'])/100 # Duración en segundos

# Asigno todos los valores de Resultado a la columna Des 2 y los valores de Objetivo a Des 3.
for index, fila in df.iterrows():
    if fila['Des 2'] in ['1', '2', '3', '4']:
        keep = fila['Des 2']
        df.at[index, 'Des 2'] = fila['Des 3']
        df.at[index, 'Des 3'] = keep

# Renombro las columnas
df = df.rename(columns={'N#':'Order', 'Categoría':'Player', 'Des 1':'Date', 'Des 2':'Result', 'Des 3':'Target'})


# Sección 4: KPIs
# Se calculan las KPIs: velocidad del remate, distancia al centro del arco, el acierto lateral y el acierto en altura


df['V_m_s'] = (df['D_m']/df['T_s']) # Velocidad del remate en m/s
df['R_m'] = np.sqrt(df['X_m']**2+df['Y_m']**2) # Distancia al centro del arco en metros

# Acierto según el objetivo previo al remate
df['Target'] = df['Target'].astype(int)

df['Width'] = ((df['Target'].isin([1, 4])) & (df['X_m'] > 0.61)) | \
              ((df['Target'].isin([2, 3])) & (df['X_m'] < -0.61)) # Acierto al objetivo prefijado, izquierda o derecha

df['Height'] = ((df['Target'].isin([1, 2])) & (df['Y_m'] > 0.36)) | \
                ((df['Target'].isin([3, 4])) & (df['Y_m'] < -0.36)) # Acierto al objetivo prefijado, arriba o abajo


# Sección 5: ERRORES
# Se definen las columnas de errores basadas en valores de Parameters.xlsx


ErX_m = ErPOS / 100
ErY_m = ErPOS / 100
ErL_m = ErDIS / 100
ErT_s = 1/fps # Cantidad de segundos por fotograma

df['ErT_s'] = pd.Series([ErT_s for x in range(len(df.index))])

df['ErD_m'] = abs((L_m * ((L_m)**2 + (df['X_m'])**2 + (df['Y_ground'])**2)**(-1/2))) * [ErL_m] + \
                abs((df['X_m'] * ((L_m)**2 + (df['X_m'])**2 + (df['Y_ground'])**2)**(-1/2))) * [ErX_m] + \
                abs((df['Y_ground'] * ((L_m)**2 + (df['X_m'])**2 + (df['Y_ground'])**2)**(-1/2))) * [ErY_m]

df['ErR_m'] = abs((df['X_m'] * ((df['X_m'])**2+(df['Y_m'])**2)**(-1/2))) * [ErX_m] +  \
                abs((df['Y_m'] * ((df['X_m'])**2+(df['Y_m'])**2)**(-1/2))) * [ErY_m]

df['ErV_m_s'] = abs(df['ErD_m']/(df['T_s'])) + abs(df['D_m'] * ErT_s/(df['T_s']**2))

# Rondeo los valores segun apreciacion y errores
df = df.round({'X_px':0,'Y_px':0,
               'D_m': 2, 'ErD_m': 2,
               'T_s': 2, 'ErT_s': 2,
               'V_m_s': 2, 'ErV_m_s': 2, 
               'R_m': 2, 'ErR_m': 2})


# Sección 6: EXPORTACIÓN
# Se exportan los resultados a un nuevo archivo y se actualiza penalties.csv


# Defino una columna que indentifica el archivo procesado en el csv que acumula a todos ellos
try:
    penalties = pd.read_csv('penalties.csv') # Intento cargar el archivo 'penalties.csv'
    df['IDFile'] = penalties['IDFile'].max() + 1 # Si el archivo existe, creo la columna IDFile continuando la numeración

except FileNotFoundError:
    df['IDFile'] = 1 # Si el archivo no existe, creo la columna IDFile con el valor 1
    df = df[['IDFile', 'Date', 'Order', 'Player', 'Target', 'Result', 'D_m', 'ErD_m', 'T_s', 'ErT_s', 'V_m_s', 'ErV_m_s', 'R_m', 'ErR_m', 'Width', 'Height', 'X_m', 'Y_m']].sort_values(by=['Date', 'Order'], ascending=[True, True])
    df.index = range(df.shape[0])
    df.to_csv('penalties.csv', index=False) # Creo penalties.csv

# Reordeno las columnas
df = df[['IDFile', 'Date', 'Order', 'Player', 'Target', 'Result', 'D_m', 'ErD_m', 'T_s', 'ErT_s', 'V_m_s', 'ErV_m_s', 'R_m', 'ErR_m', 'Width', 'Height', 'X_m', 'Y_m']].sort_values(by=['Date', 'Order'], ascending=[True, True])
df.index = range(df.shape[0])

# Exporto el resultado
df.to_csv('penalties' + str(df['IDFile'].iloc[0]).zfill(3) + '.csv', index = False)
print()

# Sumo los nuevos registros al .csv total (penalties)
penalties = pd.read_csv('penalties.csv')
penalties = pd.concat([penalties, df])
penalties.index = range(penalties.shape[0])
penalties.to_csv('penalties.csv', index = False)

# Cuadro de diálogo final
messagebox.showinfo('Ejecución completada', 'Se ha exportado el archivo penalties' + str(df['IDFile'].iloc[0]).zfill(3) + '.csv y se han agregado los nuevos registros a penalties.csv')