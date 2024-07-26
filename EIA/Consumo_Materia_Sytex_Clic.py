import os
import pandas as pd
import sys
import numpy as np
import imaplib
import email
from email.header import decode_header 
import time
import io
from datetime import datetime, timedelta
import traceback
from email.message import EmailMessage
import smtplib
import concurrent.futures

# Importar el módulo
import Sytex

dir_mat = 'materiales.csv'
dir_eq = 'equipos.csv'
noro = 'Noroccidente'
norte = 'Norte'
cen = 'Centro'
Ori = 'Oriente'
mat = 'Mat'
eq = 'Eq'
dicc_cen = {}
dicc_Nor = {}
dicc_Norte = {}
dicc_Oriente = {}

fecha_actual = datetime.now()
fecha_actual_date = fecha_actual.strftime("%Y-%m-%d")
fecha_resta = fecha_actual - timedelta(days=2)
fecha_resta_str = fecha_resta.strftime("%Y-%m-%d")
print(fecha_actual_date)
print(fecha_resta_str)

def FindTask_desde_hasta(fecha_actual,fecha_resta_str):
    #obtenemos las tareas creadas por medio de una API
    Taskurl = os.environ.get("enlace")
    return Sytex.RunApi(Taskurl)

def procesar_correo():
    # Configura la información de la cuenta de correo
    email_address = os.environ.get("correo")
    password = os.environ.get("pass")

    while True:
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(email_address, password)

            # Selecciona la carpeta de correo que deseas revisar (por ejemplo, "INBOX")
            mail.select("INBOX")

            # Busca correos electrónicos de la dirección específica que son no leídos
            result, data = mail.search(None, 'UNSEEN', 'FROM', os.environ.get("correo_lectura"))

            # Obtén los números de los correos electrónicos encontrados
            email_ids = data[0].split()

            # Procesa los correos electrónicos no leídos
            for email_id in email_ids:
                # Descarga el correo electrónico
                _, msg_data = mail.fetch(email_id, "(RFC822)")
                raw_email = msg_data[0][1]

                # Parsea el correo electrónico
                msg = email.message_from_bytes(raw_email)
                email_date = msg['Date']
                
                # Obtiene el asunto del correo
                subject, encoding = decode_header(msg["Subject"])[0]
                subject = subject if encoding is None else subject.decode(encoding)

                # Muestra el asunto del correo
                print("Asunto:", subject)
                file = ''
                dicc={}
                # Procesa los archivos adjuntos
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart" or part.get("Content-Disposition") is None:
                        continue
                    filename = part.get_filename()
                    
                    if filename and filename.endswith(".csv"):
                        file += filename
                        print("Nombre del archivo adjunto:", filename)
                        print(email_date)
                        # Lee el contenido del archivo CSV adjunto con ISO-8859-1
                        csv_data = part.get_payload(decode=True).decode("ISO-8859-1")
                        csv_buffer = io.StringIO(csv_data)
                        dicc[filename]=csv_buffer

                Consumo_clic_correo(dicc)
                # Marca el correo como leído
                mail.store(email_id, '+FLAGS', '\Seen')#mail.store(email_id, '+FLAGS', r'\Seen')
                print("------------------------------")

            # Cierra la conexión con el servidor IMAP
            mail.logout()
        except Exception as e:
            # Obtener la traza de la pila de llamadas
            stack_trace = traceback.extract_tb(e.__traceback__)
            # Obtener la última tupla de la traza de la pila de llamadas
            ultima_llamada = stack_trace[-1]
            # Obtener el número de línea donde ocurrió la excepción
            linea_error = ultima_llamada.lineno
            print("Error:", str(e), "en la línea:", linea_error)

        # Espera 10 minutos antes de revisar nuevamente
        time.sleep(30)

def Consumo_clic_correo(dicc):
    
    for key in dicc:
        if key.startswith(cen):
            dicc_cen[key]= dicc[key]
        elif key.startswith(noro):
            dicc_Nor[key]= dicc[key]
        elif key.startswith(norte):
            dicc_Norte[key]= dicc[key]
        elif key.startswith(Ori):
            dicc_Oriente[key]= dicc[key]
        
    diccionario_combinado = {}
    diccionario_combinado_02 = {}
    
    flag1 = False 
    flag2 = False 
    
    for key in dicc_cen.items():
        print(key[0])
        if eq in key[0]:
            flag1 = True
            equi = dicc_cen[key[0]]
        elif mat in key[0]:
            flag2 = True 
            mt = dicc_cen[key[0]]
        if flag1 and flag2:
            diccionario_combinado = union_equi(diccionario_combinado,equi)
            diccionario_combinado_02 = union_mat(diccionario_combinado,mt)
            diccionario_combinado.update(diccionario_combinado_02)
            #add_items_OM_lista_clic(diccionario_combinado)
            flag1 = False 
            flag2 = False
            
    for key in dicc_Nor.items():
        print(key[0])
        if eq in key[0]:
            flag1 = True
            equi = dicc_Nor[key[0]]
        elif mat in key[0]:
            flag2 = True 
            mt = dicc_Nor[key[0]]
        if flag1 and flag2:
            diccionario_combinado_02 = {}
            diccionario_combinado = {}
            diccionario_combinado = union_equi(diccionario_combinado,equi)
            diccionario_combinado_02 = union_mat(diccionario_combinado,mt)
            diccionario_combinado.update(diccionario_combinado_02)
            mj = add_items_OM_lista_clic(diccionario_combinado)
            flag1 = False 
            flag2 = False
            print(mj)
            
    for key in dicc_Norte.items():
        print(key[0])
        if eq in key[0]:
            flag1 = True
            equi = dicc_Norte[key[0]]
        elif mat in key[0]:
            flag2 = True 
            mt = dicc_Norte[key[0]]
        if flag1 and flag2:
            diccionario_combinado_02 = {}
            diccionario_combinado = {}
            diccionario_combinado = union_equi(diccionario_combinado,equi)
            diccionario_combinado_02 = union_mat(diccionario_combinado,mt)
            diccionario_combinado.update(diccionario_combinado_02)
            #add_items_OM_lista_clic(diccionario_combinado)
            flag1 = False 
            flag2 = False
            
    for key in dicc_Oriente.items():
        print(key[0])
        if eq in key[0]:
            flag1 = True
            equi = dicc_Oriente[key[0]]
        elif mat in key[0]:
            flag2 = True 
            mt = dicc_Oriente[key[0]]
        if flag1 and flag2:
            diccionario_combinado_02 = {}
            diccionario_combinado = {}
            diccionario_combinado = union_equi(diccionario_combinado,equi)
            diccionario_combinado_02 = union_mat(diccionario_combinado,mt)
            diccionario_combinado.update(diccionario_combinado_02)
            #add_items_OM_lista_clic(diccionario_combinado)
            flag1 = False 
            flag2 = False
  
def find_excel_trans(x):

    # Obtén la ruta del script actual
    ruta_script = os.path.dirname(os.path.abspath(__file__))

    # Construye la ruta completa al archivo de Excel dentro de la carpeta 'proyecto/'
    ruta_excel = os.path.join(ruta_script, '.', 'Codigos Sytex Materiales.xlsx')

    # Lee el archivo de Excel
    df = pd.read_excel(ruta_excel)
    df['Clic'] = df['Clic'].astype(str)
    
    if x in df['Clic'].values:
        # Encuentra el índice de la fila que contiene el valor x en la columna 'BMC'
        indice_fila = df.index[df['Clic'] == x].tolist()[0]
        # Obtiene el valor correspondiente en la columna 'Sytex'
        valor_sytex = df.at[indice_fila, 'Sytex']
        if valor_sytex.is_integer():
            # Si es un número entero, convertirlo a una cadena de texto sin el ".0"
            valor_str = str(int(valor_sytex))
        else:
            # Si no es un número entero, convertirlo a una cadena de texto y eliminar los caracteres ".0" si están presentes
            valor_str = str(valor_sytex).rstrip('.0')
        return str(valor_str)
    else:
        return str(x)

def procesar_materiales(mat):
    # Carga el archivo de Excel
    df = pd.read_csv(mat, sep=',', encoding='latin1')
    
    j = FindTask_desde_hasta(fecha_actual_date,fecha_resta_str)
    lista_tareas = [str(Form['code']) for Form in j['results']]
    
    df_filtrado = df[['Id Tarea', 'Codigo Mat', 'Cantidad','Task_EngineerID']]
    df_filtrado = df_filtrado[df_filtrado['Id Tarea'].astype(str).isin(lista_tareas)]
    
    datos_dict_MAT = {}
    for tarea in df_filtrado['Id Tarea'].unique():
        datos_tarea = df_filtrado[df_filtrado['Id Tarea'] == tarea][['Codigo Mat', 'Cantidad']].to_dict(orient='records')
        valores_CC = set(df_filtrado[df_filtrado['Id Tarea'] == tarea]['Task_EngineerID'])
        
        for diccionario in datos_tarea:
            for key, value in diccionario.items():
                if value == diccionario['Codigo Mat']:
                    Cod = find_excel_trans(value)
                    diccionario['Code'] = Cod
                    break
        cc = 0
        for m in valores_CC:
            cc = m
            break
        datos_dict_MAT[str(tarea)] = {'MATERIAL': datos_tarea,
                                     'CC': str(cc)}        
        
    return datos_dict_MAT

def procesar_equipos(eq):
    
    df = pd.read_csv(eq, sep=',', encoding='latin1')
    
    j = FindTask_desde_hasta(fecha_actual_date,fecha_resta_str)
    lista_tareas = [int(Form['code']) for Form in j['results']]
    df_filtrado = df[['Id Tarea','SerialNo','SerialNoReal2','UNEEquipmentUsed_Type','Task_Status_Name','TecnicoID']]
    df_filtrado = df_filtrado[df_filtrado['Id Tarea'].isin(lista_tareas)]
    df_filtrado = df_filtrado[(df_filtrado['UNEEquipmentUsed_Type'] == 'Install')|(df_filtrado['UNEEquipmentUsed_Type'] == 'Repair')|(df_filtrado['UNEEquipmentUsed_Type'] == 'Traslado')]

    datos_dict_EQ = {}
    for tarea in df_filtrado['Id Tarea'].unique():
        datos_tarea = df_filtrado[df_filtrado['Id Tarea'] == tarea][['SerialNo','SerialNoReal2','Task_Status_Name','TecnicoID']].drop_duplicates().to_dict(orient='records')
        
        # Obtener los valores únicos de 'SerialNo' para la tarea actual
        valores_serialNo = set(df_filtrado[df_filtrado['Id Tarea'] == tarea]['SerialNo'])
        valores_serialReal = set(df_filtrado[df_filtrado['Id Tarea'] == tarea]['SerialNoReal2'])
        valores_CC = set(df_filtrado[df_filtrado['Id Tarea'] == tarea]['TecnicoID'])

        code = 'nan' #si al codigo al final siguie siendo nan es porque el serial no esta en la ubicacion de destino
        for diccionario in datos_tarea:
            diccionario['Code'] = code 
        
        todos_nan_Real = all(pd.isna(value) for value in valores_serialNo)
        todos_nan = all(pd.isna(value) for value in valores_serialReal)
        if not todos_nan:
            for m in valores_serialReal:
                if isinstance(m, str):
                    Nseriales = Sytex.Findmaterialstock(m)
                    count = Nseriales['count']

                    if count >= 1:
                        code = Nseriales['results'][0]['material_code']

                        for diccionario in datos_tarea:
                            for key, value in diccionario.items():
                                if value == m:
                                    diccionario['Code'] = code
                                    break    
             
        if not todos_nan_Real:          
            for m in valores_serialNo:
                if isinstance(m, str):
                    Nseriales = Sytex.Findmaterialstock(m)
                    count = Nseriales['count']
                    if count >= 1:
                        code = Nseriales['results'][0]['material_code']
                        for diccionario in datos_tarea:
                            for key, value in diccionario.items():
                                if value == m:
                                    diccionario['Code'] = code
                                    break
        cc = 0
        for m in valores_CC:
            cc = m
            break
        datos_dict_EQ[str(tarea)] = {'EQUIPO': datos_tarea,
                                     'CC': str(cc)}

    return datos_dict_EQ

def union_equi(diccionario_combinado,eq):
    materiales_dict = procesar_equipos(eq)
    for clave, valores in materiales_dict.items():
        if clave in diccionario_combinado:
            diccionario_combinado[clave].update(valores)
        else:
            diccionario_combinado[clave] = valores
    return diccionario_combinado

def union_mat(diccionario_combinado,mat):
    equipos_dict = procesar_materiales(mat)
    for clave, valores in equipos_dict.items():
        if clave in diccionario_combinado:
            diccionario_combinado[clave].update(valores)
        else:
            diccionario_combinado[clave] = valores
    return diccionario_combinado

def Union_Mate_Equipo():
    
    diccionario_combinado = {}
    diccionario_combinado_02 = {}

    diccionario_combinado = union_equi(diccionario_combinado)
    diccionario_combinado_02 = union_mat(diccionario_combinado)
    diccionario_combinado.update(diccionario_combinado_02)

    return diccionario_combinado

def Correo():
    # Configura los detalles del servidor SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # El puerto puede variar, por ejemplo, para Gmail es 587

    # Configura tus credenciales de correo electrónico
    sender_email = os.environ.get("correo")
    password = os.environ.get("pass")

    # Configura los destinatarios
    receiver_email = os.environ.get("correo_entrega")

    # Crea el objeto EmailMessage
    msg = EmailMessage()

    # Configura los detalles del correo
    msg['Subject'] = 'Log consumos Materiales-Equipos'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content('Hola, Molano Consumos de materiales')

    # Adjunta el archivo
    filename = 'Log Consumos.txt'
    with open(filename, 'rb') as attachment:
        msg.add_attachment(attachment.read(), maintype='application', subtype='octet-stream', filename=filename)

    # Establece conexión con el servidor SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, password)

    # Envía el correo
    server.send_message(msg)

    # Cierra la conexión con el servidor SMTP
    server.quit()

    print('Correo enviado exitosamente')
    
def add_items_OM_lista_clic(lista):
        lista_error = []
        lista_text = []
        lista_exito = []
        mensajes = []
        list_instances = []
        attributes_list = []
        Mo_creadas =[]
        
        for key, value in lista.items():
            flag = True
            flag1 = True
            verify = False
            task = Sytex.FindTask(key)
            list_atribu = []
                
            if task['count'] > 0:
                if task['results'][0]['assigned_staff']:
                    #comparar las cedulas para ver si la tarea si es la persona quien lo hizo. 
                    if value['CC'] != task['results'][0]['assigned_staff']['code']:
                        flag1 = False
                else :
                    flag1 = False
                task01=Sytex.Get_task_atribute(task['results'][0]['id'])
                attributes_list = task01['attributes']
                for m in attributes_list:
                    list_atribu.append(m['id'])
                    if 'Consumo' in m['name']:
                        flag = False
            
            if task['count']!= 0 and flag and flag1:#buscar el atributo para intentar saltarla
                taskcode=task['results'][0]['code']
                idtask=task['results'][0]['id']
                iddestino=task['results'][0]['client']['id']
                code_staffmo=task['results'][0]['assigned_staff']['id']
                #hacer una lista con la MO creadas entregado un diccionario
                simpleoperation_id_EQ = Sytex.create_MO_stock(code_staffmo,iddestino,idtask,2,875)# crear la mo pero con atributo de consumo equipos
                simpleoperation_id_Mat = Sytex.create_MO_stock(code_staffmo,iddestino,idtask,2,876)# crear la mo pero con atributo de consumo materiales
                
                Mo_creadas.append(simpleoperation_id_EQ)
                MOi_EQ = Sytex.MO_active(simpleoperation_id_EQ)
                Mo_creadas.append(simpleoperation_id_Mat)
                MOi_Mat = Sytex.MO_active(simpleoperation_id_Mat)
                for key_type, items in value.items():
                    for item in items:
                        flag_seriales = True
                        if key_type == 'EQUIPO':
                            #print(item['SerialNo'])
                            if not isinstance(item['SerialNo'], str) and not isinstance(item['SerialNoReal2'], str) or item['Code'] == 'nan' :
                                print('SERIAL NO ENCONTRADO')
                                m = str(item['SerialNo'])+" en tarea: "+str(taskcode)
                                list_instances.append(m)
                                flag_seriales = False
                            if flag_seriales:
                                if not isinstance(item['SerialNo'], str):
                                    serial = item['SerialNoReal2']
                                elif not isinstance(item['SerialNoReal2'], str):
                                    serial = item['SerialNo']
                                    
                                verify=Sytex.verify_MO_eq(MOi_EQ['results'][0]['id'],item['Code'],serial)
                                if verify:
                                    item_data = {
                                        "material": item['Code'],
                                        "serial_number": serial,
                                        "quantity": 1,
                                        "operation": simpleoperation_id_EQ,
                                    }
                                    booleano, mi_lista = Sytex.trigger_add_MO(item_data)
                                    if booleano:
                                        lista_text.append('1')
                                    else:
                                        lista_text.append('2')
                                        lista_error.append(mi_lista)
                            
                        elif key_type == 'MATERIAL':
                            verify=Sytex.verify_MO_mat(MOi_Mat['results'][0]['id'],item['Code'],item['Cantidad'])
                            if verify:
                                item_data = {
                                    "material": item['Code'],
                                    "quantity": item['Cantidad'],
                                    "operation": simpleoperation_id_Mat,
                                }
                                booleano, mi_lista = Sytex.trigger_add_MO(item_data)
                                if booleano:
                                    lista_text.append('1')
                                else:
                                    lista_text.append('2')
                                    lista_error.append(mi_lista)
                    print('---------------------')
                        
                todos_son_uno = all(elemento == '1' for elemento in lista_text) if lista_text else False
                if todos_son_uno:
                    lista_exito.append(simpleoperation_id_EQ)
                    lista_exito.append(simpleoperation_id_Mat)
                    
                list_atribu.append(500)
                Sytex.task_atribute(idtask,list_atribu)
                if verify:
                    lista_text.clear()
    
        confirm_ok = []
        confirm_wrong  = [] 
        
        if lista_error:
            mensaje = 'Revisar las items de las MO: '
            mensaje += '\n'.join(lista_error)
            mensajes.append(mensaje + '\n')
        else:
            mensajes.append('no hay MO que revisar')
        
        #if lista_exito:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(Sytex.confirm_MO, Mo_creadas)
            
        for task, mo in zip(results,Mo_creadas):
            if task is True:
                confirm_ok.append(mo)
            else:
                mensaje = task
                mensaje += ' MO: '
                mensaje +=  mo
                confirm_wrong.append(mensaje)
            
        if confirm_wrong:
            mensaje = 'no se pudo confirmas las siguientes MO: '
            mensaje += ', '.join(confirm_wrong)
            mensajes.append(mensaje + '\n')          
            
        if list_instances:
            mensaje = 'los seriales no existen en sytex: '
            mensaje += ', '.join(list_instances)
            mensajes.append(mensaje + '\n')
            
        with open("Log Consumos.txt", "a") as archivo:
        # Escribe cada mensaje en una nueva línea del archivo
            for mensaje in mensajes:
                archivo.write(mensaje + "\n")       
        return(mensajes)
