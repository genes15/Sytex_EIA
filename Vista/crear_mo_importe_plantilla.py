import requests
import json
import os
import concurrent.futures
import pandas as pd


headers = os.environ.get("credenciales")

def RunApi(URL):

    api_url = URL
    try:
    # Realiza una solicitud GET a la API
        response = requests.get(api_url,headers=headers)
        
        if response.status_code in [200,201]:
            return response.json()
        else:
            #print(response.json())
            data = response.json()
            print("Datos de la API:", data)
        
    except requests.exceptions.RequestException as e:
        
        print(f"Error al realizar la solicitud a la API: {str(e)}")
        #print(f"Datos de la API: {str(data)}")
        #mensajes.append(f"Error al realizar la solicitud a la API: {str(e)}")
    except Exception as e:
        #mensajes.append(f"Ocurrió un error: {str(e)}")
        print(f"Ocurrió un error: {str(e)}")

def FindStock(id):
    Taskurl = os.environ.get("API_stock")
    return RunApi(Taskurl)

def MO_active(Mo_Code):
    Mo_Code = str(Mo_Code)
    Taskurl = os.environ.get("API_MO")+Mo_Code
    return RunApi(Taskurl)

def trigger_add_MO(item):
    ChangeStatusurl = os.environ.get("API_import_MO")
    payload = json.dumps(item)

    try:
        response = requests.post(ChangeStatusurl, headers=headers,data=payload)

        if response.status_code in [200,201]:
            #print("añadido corecto de item: "+item['operation'])
            mensaje = 'añadido corecto de item: '
            mensaje += (item['operation'])      
            #data = response.json()
            
            #print("Datos de la API:", data)      
            return True, mensaje
        else:
            data = response.json()
            
            #print("Datos de la API:", data)
            #if 'serial_number' in item:
            #    print(item['serial_number'])
            #print(item['operation'])
            
            mensaje = 'Datos de la API: '
            mensaje += (str(data))
            if 'serial_number' in item:
                mensaje += (', Con Num Serie: ')
                mensaje += (str(item['serial_number']))
            mensaje += (', en la MO: ')
            mensaje += (str(item['operation']))
            
            return False , mensaje
    except Exception as e:
        print(f"Error:  {str(e)}")
        mensaje = 'Error: '
        mensaje += (str(e))
        mensaje += (', en la MO: ')
        mensaje += (str(item['operation']))
        return False, mensaje

def trigger_add_MO_v2(item):
    ChangeStatusurl = os.environ.get("API_import_MO")
    payload = json.dumps(item)

    try:
        response = requests.post(ChangeStatusurl, headers=headers,data=payload)

        if response.status_code in [200,201]:
            print("añadido corecto de item: "+item['operation'])
            mensaje = 'añadido corecto de item: '
            mensaje += (item['operation'])            
            return True, mensaje
        else:
            data = response.json()
            
            print("Datos de la API:", data)
            if 'serial_number' in item:
                print(item['serial_number'])
            print(item['operation'])
            
            mensaje = 'Datos de la API: '
            mensaje += (str(data))
            if 'serial_number' in item:
                mensaje += (', Con Num Serie: ')
                mensaje += (str(item['serial_number']))
            mensaje += (', en la MO: ')
            mensaje += (str(item['operation']))
            
            return False , mensaje, item['operation']
    except Exception as e:
        print(f"Error:  {str(e)}")
        mensaje = 'Error: '
        mensaje += (str(e))
        mensaje += (', en la MO: ')
        mensaje += (str(item['operation']))
        return False, mensaje
    
def create_MO_Devol_retiro(Commit,referencia,tipo,Attribute):##
    
    ChangeStatusMOurl = os.environ.get("API_MO")
    mo = []
    referencia_concatenada = " ".join(referencia)
    if tipo == 2:
        Mo_config={
        "operation_type":tipo,
        "reference_number":referencia_concatenada,
        "description":Commit,
        "project":2004,
        "attributes":[Attribute]
        }
    elif tipo == 1:
        Mo_config={
        "operation_type":tipo,
        "entry_type":1,
        "reference_number":referencia_concatenada,
        "description":Commit,
        "project":2004,
        "attributes":[Attribute]
        }
    
    payload = json.dumps(Mo_config)
    
    try:
        response = requests.post(ChangeStatusMOurl, headers=headers,data=payload)

        if response.status_code in [200,201]:
            print("creacion exitosa de la MO")
            data = response.json()
            print(data['code'])
            #mo.append(data['code'])
            #mo.append(data['id'])
            return data['code']

        else:
            data = response.json()
            print("Datos de la API:", data)
            print(f"Error en la solicitud. Código de estado: {response.status_code}")

    except Exception as e:
        print(f"Error en la solicitud: {str(e)}")
        return (f"Error en la solicitud: {str(e)}")  
    
def import_series_mov(mo,archivo):

    lista_tareas = []
    MO_codigo = mo
    Origen = MO_active(mo)
    Origen = Origen['results'][0]['source_location']['code']
    diccionario_resultados = {}
    contador = 1
    list_values= []

    with open(archivo, 'r') as archivo:
        for linea in archivo:
            lista_tareas.append(str(linea.rstrip()))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        Tasks = executor.map(FindStock, lista_tareas)
    
    for task in zip(Tasks):
        if task[0]['count'] == 1:
            if task[0]['results'][0]['location']['code'] == Origen:
                # Iterar sobre los resultados en task[0]['results']
                for resultado in task[0]['results']:
                    item_data = {
                        "material": resultado['material_code'],
                        "serial_number": resultado['serial_number'],
                        "quantity": 1,
                        "operation": MO_codigo,
                    }
                    # Agregar la lista al diccionario con la clave autoincrementable
                    diccionario_resultados[contador] = item_data
                    
                    # Incrementar el contador
                    contador += 1
            else:
                print('el numero de serie: '+task[0]['results'][0]['serial_number']+' no esta en la ubicacion de origen: '+Origen)

    for value in diccionario_resultados.values():
        list_values.append(value)
        #booleano, mi_lista = trigger_add_MO(value)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        Tasks = executor.map(trigger_add_MO, list_values)

def import_series_entrada(Mo_In,Mo_Mov,xlsx):
    
    """
    metodo para obtener un archivo TXT donde reposan seriales que se les piensa hacer entradas en sytex
    tambien obtenie las MO creadas anteriormente por al almacen en las cuales el bot pone los seriales. 
    
    Args:
        String  Mo_In   Codigo de la MO de entrada
        String  Mo_Mov  Codigo de la MO de movimiento
        XLSX    xlsx    archivo con informacion de las series

    Returns:
        Lista   lista_log_MO    informacion de tipo LOG al momento de cargar los items.
    """
        
    #validar que las Mo sean actas (a confirmar) para añadirles items
    lista_series = []
    lista_codigo = []
    diccionario_resultados = {}
    contador = 1
    list_values= []
    lista_existentes = []
    lista_crear = []

    df = pd.read_excel(xlsx)
    with open(archivo, 'r') as archivo:
        for linea in archivo:
            
            partes = str(linea.rstrip()).split()
            lista_codigo.append(partes[1])
            lista_series.append(partes[0])

    with concurrent.futures.ThreadPoolExecutor() as executor:
        Tasks = executor.map(FindStock, lista_series)

    for task,cod,sn in zip(Tasks,lista_codigo,lista_series):
        if task['count'] == 1:
            for resultado in task['results']:
                item_data = {
                    "material": cod,
                    "serial_number": resultado['serial_number'],
                    "quantity": 1,
                    "operation": Mo_Mov,
                    "source_location_type":task['results'][0]['location']['_class_name'],
                    "source_location":task['results'][0]['location']['code']
                }
                diccionario_resultados[contador] = item_data
                contador += 1
        else:
            item_data = {
                "material": cod,
                "serial_number": sn,
                "quantity": 1,
                "operation": Mo_In,
            }
            diccionario_resultados[contador] = item_data
            contador += 1
            
    for value in diccionario_resultados.values():
        list_values.append(value)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        Tasks = executor.map(trigger_add_MO, list_values)  
    
    for task in zip(Tasks):
        if task[0][0] == True:
            lista_existentes.append(task[0][1])
        else:
            lista_crear.append(task[0][1])
    print(lista_crear)
    return lista_existentes       

def revisar_seriales(xls):
    """
        metodo que procesa un archivo xlsx con dos columnas seriales y codigos, los busca en sytex 
        e indica cuales sieriales ya existen en sytex y cuales hay que crear.
        Si el serial existe indica en que ubicacion esta. 
        
        Args:
            XLSX (archivo Excel): Seriales a buscar en sytex

        Returns:
            Lista   lista_crear informacion de seriales a crear en sytex.
            Lista   lista_existentes informacion de seriales existente en sytex con ubicaciones.
    """
    #*inicializamos variables
    lista_existentes = []
    lista_crear = []
    i=0
    
    df = pd.read_excel(xls)
    
    sn = df['SN']
    cod = df['COD']

    #* Convierte la columna a una lista
    column_list_sn = [str(value) for value in sn]
    column_list_cod = [str(value) for value in cod]

    #* usamos hilos para hacer varias consultas a la API a la vez. 
    with concurrent.futures.ThreadPoolExecutor() as executor:
        sn = list(executor.map(FindStock, column_list_sn))
        

    for serial in zip(sn):
        
        #* Sí el count > 1 significa que el serial si existe.
        if serial[0]['count'] == 1:
            text = serial[0]['results'][0]['serial_number']+ ", " + serial[0]['results'][0]['material_code'] + " , " + serial[0]['results'][0]['location']['code']
            print(serial[0]['results'][0]['serial_number']+ ", " + serial[0]['results'][0]['material_code'] + " , " + serial[0]['results'][0]['location']['code'])
            lista_existentes.append(text)
        #* de lo contrario no existe en sytex.
        elif serial[0]['count'] == 0:
            text =  column_list_sn[i] + ", " + column_list_cod[i]
            lista_crear.append(text)
        i+=1
        
    return lista_crear,lista_existentes

def process_retor_devolu(file_path):
    """
    procesamiento de diccionario.
    Metodo usado para procesar un diccionario y poder crear MO, Configurar MO e añadir items en sytex
    con el fin de facilitar el trabajo de las devoluciones y retornos.
    
    Args:
        dicc (Diccionario): Dicc que contiene informacion de seriales a mover en sytex

    Returns:
        Lista (List)
    """
    # Leer el archivo Excel usando pandas
    df = pd.read_excel(file_path)

    #table = df.to_html()

    # Crea un diccionario para almacenar las filas separadas
    dict_by_cc = {}

    # Selecciona la columna 'CC'
    columnsn = df['SN']
    #columntask = df['Tarea']

    # Convierte la columna a una lista
    column_list_sn = [str(value) for value in columnsn]
    #column_list_task = [str(value) for value in columntask]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        sn = list(executor.map(FindStock, column_list_sn))
    i=0
    
    list_results_dict_sn = dict(zip(column_list_sn, sn))
    # Itera sobre cada fila del DataFrame
    for _, row in df.iterrows():
        cc_value = row['CC']
        
        if sn[i]['count']==1:
            estado = 'Existe'
        else:
            estado = 'No_Existe'
            
        if cc_value not in dict_by_cc:
            dict_by_cc[cc_value] = {}
        
        if 'Existe' not in dict_by_cc[cc_value]:
            dict_by_cc[cc_value]['Existe']={}
            
        if 'No_Existe' not in dict_by_cc[cc_value]:
            dict_by_cc[cc_value]['No_Existe']={}
            
        if 'Retiro' not in dict_by_cc[cc_value][estado]:
            dict_by_cc[cc_value][estado]['Retiro']=[]
        if 'Devolucion' not in dict_by_cc[cc_value][estado]:
            dict_by_cc[cc_value][estado]['Devolucion']=[]
        
        dict_by_cc[cc_value][estado][row['Tipo Movimiento']].append(row.to_dict())
        
        i+=1
        
    i=0
    MO_re_devo=[]
    mo = ''
    for cc in dict_by_cc:
        #rotamos por cedulas column_list_task
        print(cc)
        for estado in dict_by_cc[cc]:
            print(estado)
            
            for tipo in dict_by_cc[cc][estado]:
                Commit = ""
                referencia = []
                print(tipo)
                #mensaje1=""
                for m in dict_by_cc[cc][estado][tipo]:
                    print(m['Tarea'])
                    if pd.isna(m['Tarea']) and pd.isna(m['Pedido']):
                        mensaje1=""
                    else:
                        int_number = str(int(m['Tarea']))
                        mensaje1 = str(int_number+" - "+m['Pedido'])
    
                    Commit = str(m['Tipo Movimiento']+" entregado por "+str(m['CC'])+" Recibido por "+m['Quien Recibe'])
                    referencia.append(mensaje1)

                #crear la MO
                if estado == "Existe":
                    if tipo == "Retiro":
                        print('creamos la MO movimiento retiro')
                        mo = create_MO_Devol_retiro(Commit,referencia,2,501) #movimiento retiro
                    elif tipo == "Devolucion":
                        print('creamos la MO movimiento devolucion')
                        mo = create_MO_Devol_retiro(Commit,referencia,2,1540) #movimiento devolucion
                elif estado == "No_Existe":
                    if tipo == "Retiro":
                        print('creamos la MO entrada retiro')
                        mo = create_MO_Devol_retiro(Commit,referencia,1,501) #entrada retiro
                    elif tipo == "Devolucion":
                        print('creamos la MO entrada devoluciono')
                        mo = create_MO_Devol_retiro(Commit,referencia,1,1540) #entrada devolucion
                MO_re_devo.append(mo) 
                       
                for item in dict_by_cc[cc][estado][tipo]:
                    #añadir los item
                    print('añadimos item')
                    #print(item)
                    
                    if item['Tipo Movimiento'] == 'Retiro':
                        almacen = 'VW-0211'
                    elif item['Estado'] == 'Inactivo':
                        almacen = 'VW-0211'
                    elif item['Estado'] == 'Activo':
                        almacen = '1337'
                        
                    if pd.isna(m['Tarea']) and pd.isna(m['Pedido']):
                        referencia_str = ''
                    else:
                        int_number = str(int(m['Tarea']))
                        referencia_str = str(int_number+" - "+item['Pedido']+" obs:"+item['Comentarios'])
                        
                    if estado == "Existe":
                        count = list_results_dict_sn[item['SN']]
                        if count['count'] == 1:
                            cod_eq = count['results'][0]['material_code']
                            print('0')
                            
                        item_data = {
                        "material": cod_eq,
                        "serial_number": item['SN'],
                        "quantity": 1,
                        "source_location_type":count['results'][0]['location']['_class_name'],
                        "source_location":count['results'][0]['location']['code'],
                        "destination_location_type":'depósito virtual',
                        "destination_location":almacen,
                        "operation": mo,
                        "comments":referencia_str
                        }
                    elif estado == "No_Existe":
                        cod_eq = 'Pruebas 01'
                        
                        item_data = {
                        "material": cod_eq,
                        "serial_number": item['SN'],
                        "quantity": 1,
                        # "source_location_type":count['results'][0]['location']['_class_name'],
                        # "source_location":count['results'][0]['location']['code'],
                        "destination_location_type":'depósito virtual',
                        "destination_location":almacen,
                        "operation": mo,
                        "comments":referencia_str
                        }

                    trigger_add_MO_v2(item_data)
                   #serial,codigo serial,segun el estado(tipo destino,destino),estado,# de referencia,comentarios en el items
    print(MO_re_devo)

    return MO_re_devo
