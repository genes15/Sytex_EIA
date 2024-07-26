import pandas as pd
import re
import os
import Sytex as Sytex
import datetime 
import traceback
import concurrent.futures

#?se puede hacer el proceso mas eficiente haciendo una sola consulta y solo procesar toda la informacion, que haciendo varias consultras

headers = os.environ.get("credenciales")

mensajes = []

mi_diccionario = {
    "Aprovisionamiento": 0,
    "Aprovisionamiento BSC": 0,
    "Aseguramiento": 1,
    "Precableado": 0,
    }

def tarea_programada():
    with open("Logs_excel\\log.txt", "a") as archivo:
            for mensaje in mensajes:
                archivo.write(mensaje + "\n")
    mensajes.clear()

def Consumo_clic_correo(CSV):
    """
    Consumos de archivo tarea clic.
    metodo para obtener archivo .CSV aplicar unos filtros e ir apliando unos 
    condicionales para poder crear tarear, reasignarlas o cancelarla
    
    Args:
        CSV (CSV): CSV que contiene las tareas.

    Returns:
        None
    """
    print("Inicia gestion de tareas")
    try:
        with open('cedulas.txt', 'r') as archivo_cedulas: #se recorre el .txt para saber a que personal cargar las tareas
            cedulas = [line.strip() for line in archivo_cedulas if not line.strip().startswith('#')]
            
        hora_actual = datetime.datetime.now()
        print(hora_actual)
        hora_actual = str(hora_actual)
        mensajes.append(hora_actual)
        df = pd.read_csv(CSV, sep=';', encoding='latin1') #se condiciona la lectura del CSV
        
        filtro_cedulas = df['Task_EngineerID'].astype(str).isin(cedulas) # Filtrar una columna según un criterio
        municipios = ['Medellin', 'Guarne','Bello','Retiro']
        municipio = df['Task_UNEMunicipio'].isin(municipios)
        tas = df['Task_TaskTypeCategory_Name'].isin(['Aprovisionamiento', 'Aprovisionamiento BSC','Aseguramiento','Precableado'])
        Estado_not_in_list = ~df['Task_Status_Name'].isin(['Abierto', 'Finalizada', 'Incompleto','Pendiente','Suspendido']) #filtramos los estados que no interesa tener
        filtro_combinado = filtro_cedulas & tas & Estado_not_in_list & municipio
        resultados_filtrados = df[filtro_combinado] # se unen todos los filtros para empezar a procesar la informacion
        Task_list=[]
        

        #guardamos los valores de la columna de la tareas en una lista
        Task_list = resultados_filtrados['Task_CallID'].tolist()

        #usamos la lista para aplicar hilos a la busqueda de cada tarea
        with concurrent.futures.ThreadPoolExecutor() as executor:
            usuarios = list(executor.map(Sytex.FindUser, cedulas))   
            results = list(executor.map(Sytex.FindTask, Task_list))

        task_callid = {}
        #creamos un diccionario clave=tarea, valor=respuesta de la consulta en sytex
        task_results_dict = dict(zip(Task_list, results))
        #creamos un diccionario clave=cedulas, valor=respuesta de la consulta en sytex
        Cedula_usuarios = dict(zip(cedulas, usuarios))
        
        for index, row in resultados_filtrados.iterrows():
            valor_task_callid = row['Task_CallID']  
            
            for task, value in task_results_dict.items():
                if valor_task_callid == task:
                    task_callid = value
                    break

            if task_callid['count'] == 1 : #si el count == 1 la tarea ya existe en sytex.
                
                if task_callid['results'][0]['code'] == valor_task_callid :
                    if task_callid['results'][0]['assigned_staff']:
                        user_id_sytex = task_callid['results'][0]['assigned_staff']['code']
                    else:
                        print("la tareas no tiene usuario asignado " +valor_task_callid)
                        break
                        
                    user_id_CSV = str(resultados_filtrados.at[resultados_filtrados['Task_CallID'].eq(valor_task_callid).idxmax(), 'Task_EngineerID'])
                    
                    if row['Task_Status_Name'] == "Cancelado" and task_callid['results'][0]['status']['name'] != 'Cancelada':#se verifica que el estado en el documento sea cancelado y el estado de la tarea en sytex diferente de cancelado 
                        Sytex.Change_state(valor_task_callid) # se cambia el estado de la tarea a cancelado
                    elif user_id_sytex != user_id_CSV :# se verifica que la tarea tenga diferentes personas asociadas 
                        Sytex.Change_asignement(valor_task_callid,user_id_CSV)# si es asi se realiza la reasignacion de la tarea.
                    elif row['Task_Status_Name'] == "Asignado" and task_callid['results'][0]['status']['name'] != 'Cancelada': #??
                        Sytex.Change_asignement_hide(valor_task_callid) 
  
            #se podria empaquetar las creaciones de cliente y de tareas para hacerlas juntas a la vez    
            elif row['Task_Status_Name'] in ['Despachado','En Sitio','En Camino']:# si el estado esta en la lista se procede a crear la tarea
                UserCSV = resultados_filtrados.at[resultados_filtrados['Task_CallID'].eq(valor_task_callid).idxmax(), 'Task_EngineerID']
                ClientCSV = resultados_filtrados.at[resultados_filtrados['Task_CallID'].eq(valor_task_callid).idxmax(), 'Task_UNENombreCliente']
                PedidoCSV = resultados_filtrados.at[resultados_filtrados['Task_CallID'].eq(valor_task_callid).idxmax(), 'Task_UNEPedido']
                DireccionCSV = resultados_filtrados.at[resultados_filtrados['Task_CallID'].eq(valor_task_callid).idxmax(), 'Task_UNEDireccion']
                FechaCSV = resultados_filtrados.at[resultados_filtrados['Task_CallID'].eq(valor_task_callid).idxmax(), 'FECHA']
                ActividadCSV = resultados_filtrados.at[resultados_filtrados['Task_CallID'].eq(valor_task_callid).idxmax(), 'Task_TaskTypeCategory_Name']
                #TecnologiaCSV = str(resultados_filtrados.at[resultados_filtrados['Task_CallID'].eq(valor_task_callid).idxmax(), 'Task_UNETecnologias'])
                #TipoinstalacionCSV = str(resultados_filtrados.at[resultados_filtrados['Task_CallID'].eq(valor_task_callid).idxmax(), 'Task_TaskType_Name'])
                DireccionCSV = str(DireccionCSV)
                
                if not  isinstance(ClientCSV, str):
                    ClientCSV = 'clienteNaN'
                
                ClientCSV = ClientCSV[:50]  # Se toma la información necesaria para crear la tarea
                
                if Sytex.ClientExists(ClientCSV)['count'] == 1 : #se verifica que el cliente ya exista en sytex.
                    Client = Sytex.FindClient(ClientCSV) #se trae codigo del cliente
                    UserCSV = str(UserCSV)# se trae el codigo del usuario 
                    for cc, value in Cedula_usuarios.items():
                        if UserCSV == cc:
                            User = str(value)
                            break
                
                    task={ # se contruye la tarea con un diccionario
                        "taskcode": valor_task_callid,
                        "task_description": PedidoCSV,
                        "task_description2": "",
                        "task_description3": DireccionCSV,
                        "category": mi_diccionario[ActividadCSV],
                        "user_staff": { "id": User },
                        "date": FechaCSV,
                        "clientname": {"id":Client}
                    }
                
                    Sytex.CreateTask(task) #se envia la tarea para que se cree
                else:
                    Sytex.CreateClient(ClientCSV)
                    Client = Sytex.FindClient(ClientCSV)
                    UserCSV = str(UserCSV)# se trae el codigo del usuario 
                    for cc, value in Cedula_usuarios.items():
                        if UserCSV == cc:
                            User = str(value)
                            break
                    if Sytex.ClientExists(ClientCSV)['count'] == 1 :
                        task={
                        "taskcode": valor_task_callid,
                        "task_description": PedidoCSV,
                        "task_description2": "",
                        "task_description3": DireccionCSV,
                        "category": mi_diccionario[ActividadCSV],
                        "user_staff": { "id": User },
                        "date": FechaCSV,
                        "clientname": {"id":Client}
                        }
                        Sytex.CreateTask(task)
        
        with open("Logs_excel\\log.txt", "a") as archivo:
            for mensaje in mensajes:
                archivo.write(mensaje + "\n")
    except Exception as e:
        print(e)
        stack_trace = traceback.extract_tb(e.__traceback__)
        ultima_llamada = stack_trace[-1]
        linea_error = ultima_llamada.lineno
        print("Error:", str(e), "en la línea:", linea_error)
        
def revision_tareas(CSV):
    """
    Revision de tareas.
    metodo usado para quitar las tareas gestionadas 
    por un tecnico diferente al tecnico que trasacciona por sytex
    
    Args:
        CSV (CSV): CSV que contiene las tareas.

    Returns:
        None
    """
    print('--------------------------')
    print("Inicia revision de tareas")
    lista_tareas_sytex=[]
    
    try:
        # *Obtenemos las cedulas a filtrar desde un archivo .txt
        with open('cedulas.txt', 'r') as archivo_cedulas:
            cedulas = [line.strip() for line in archivo_cedulas if not line.strip().startswith('#')]

        hora_actual = datetime.datetime.now()
        fecha_actual = hora_actual.date()
        print(hora_actual)
        df = pd.read_csv(CSV, sep=';', encoding='latin1') 
        
        #*filtramos las cedulas en la columna para luego quedarnos con las que no coincidan.
        filtro_cedulas = df['Task_EngineerID'].astype(str).isin(cedulas)
        filtro_no_cedulas = ~filtro_cedulas
        df_no_cedulas = df[filtro_no_cedulas]
        
        #*convertimos la columna de la tareas en una lista 
        Task_list_csv = df_no_cedulas['Task_CallID'].tolist()
        Task_list_csv_str = [str(item) for item in Task_list_csv]
        
        fecha_actual_date = fecha_actual.strftime("%Y-%m-%d")
        actuales_sytex = findTask_actuales(fecha_actual_date)
        
        for task in actuales_sytex['results']:
            lista_tareas_sytex.append(task['code'])
        
        lista_tareas_reasignar = []
        for t in lista_tareas_sytex:
            if t in Task_list_csv_str:
                lista_tareas_reasignar.append(t)

        #print(lista_tareas_sytex)
        for t in lista_tareas_reasignar:
            Sytex.Change_asignement_hide(t)

    except Exception as e:
        print(e)
        # # Obtener la traza de la pila de llamadas
        stack_trace = traceback.extract_tb(e.__traceback__)
        # # Obtener la última tupla de la traza de la pila de llamadas
        ultima_llamada = stack_trace[-1]
        # # Obtener el número de línea donde ocurrió la excepción
        linea_error = ultima_llamada.lineno
        print("Error:", str(e), "en la línea:", linea_error)
