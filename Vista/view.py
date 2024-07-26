from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QDateEdit, QDialog, QVBoxLayout,QTextEdit,QFileDialog
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QLabel, QTabWidget

import crear_mo_importe_plantilla 
    

class Archivo_Seriales(QDialog):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seleccionar archivo")
        boton_seleccionar = QPushButton("Seleccionar archivo", self)
        boton_seleccionar.clicked.connect(self.abrir_dialogo_archivo)
        
    def abrir_dialogo_archivo(self):
        """
        metodo para obtener un archivo .xlsx con dos columnas y procesa informacion consultandola en sytex
        la informacion retornada se publica en cuadro de tipo area de texto en la interfaz grafica.
        
        Args:
            XLSX (archivo Excel): Seriales a buscar en sytex

        Returns:
            Lista   lista_crear informacion de seriales a crear en sytex.
            Lista   lista_existentes informacion de seriales existente en sytex con ubicaciones.
        """
        
        # Mostrar el diálogo de selección de archivos
        opciones = QFileDialog.Options()
        opciones |= QFileDialog.ReadOnly  # Establecer el diálogo como solo lectura (opcional)

        archivos, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos", "", "Archivos de Excel (*.xlsx);;Todos los archivos (*)", options=opciones)

        # Ahora, 'archivos' es una lista que contiene los nombres de los archivos seleccionados
        for archivo in archivos:
            print("Archivo seleccionado:", archivo)
            for archi in archivos:
                print(archi)
        
        lista_crear, lista_existentes = crear_mo_importe_plantilla.revisar_seriales(archivo)
        
        cuadro_seriales_crear.setText("\n".join(lista_crear))
        cuadro_seriales_existente.setText("\n".join(lista_existentes))
        self.accept()
     
class Archivo_Seriales_Entrada(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seleccionar archivo")
        boton_seleccionar = QPushButton("Seleccionar archivo", self)
        boton_seleccionar.clicked.connect(self.abrir_dialogo_archivo)
        
    def abrir_dialogo_archivo(self):
        """
        metodo para obtener un archivo TXT donde reposan seriales que se les piensa hacer entradas en sytex
        tambien obtenie las MO creadas anteriormente por al almacen en las cuales el bot pone los seriales. 
        
        Args:
            None

        Returns:
            Lista   lista_log_MO informacion de tipo LOG al momento de cargar los items.
        """
        
        # Mostrar el diálogo de selección de archivos
        opciones = QFileDialog.Options()
        opciones |= QFileDialog.ReadOnly  # Establecer el diálogo como solo lectura (opcional)
        
        archivos, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos", "", "Archivos de Texto (*.txt);;Todos los archivos (*)", options=opciones)

        # Ahora, 'archivos' es una lista que contiene los nombres de los archivos seleccionados
        for archivo in archivos:
            print("Archivo seleccionado:", archivo)
            for archi in archivos:
                print(archi)
                
        In = cuadro_MO_in.toPlainText()
        Mov = cuadro_MO_Mov.toPlainText()
        print("Texto obtenido In:", In)
        print("Texto obtenido Mov:", Mov)
        lista_log_MO = crear_mo_importe_plantilla.import_series_entrada(In,Mov,archivo)
        
        cuadro_lectura.setText("\n".join(lista_log_MO))
        #cuadro_seriales_existente.setText("\n".join(lista_existentes))
        
        self.accept()   

class Archivo_Seriales_Ret_Devo(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seleccionar archivo")
        boton_seleccionar = QPushButton("Seleccionar archivo", self)
        boton_seleccionar.clicked.connect(self.abrir_dialogo_archivo)
        
    def abrir_dialogo_archivo(self):
        # Mostrar el diálogo de selección de archivos
        opciones = QFileDialog.Options()
        opciones |= QFileDialog.ReadOnly  # Establecer el diálogo como solo lectura (opcional)
        
        archivos, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos", "", "Archivos de Excel (*.xlsx);;Todos los archivos (*)", options=opciones)

        # Ahora, 'archivos' es una lista que contiene los nombres de los archivos seleccionados
        for archivo in archivos:
            print("Archivo seleccionado:", archivo)
            for archi in archivos:
                print(archi)
        lista_mo_confirm = []
        lista_mo_confirm = crear_mo_importe_plantilla.process_retor_devolu(archivo)
        
        cuadro_Mo_Confirmar_Ret_Devo.setText("\n".join(lista_mo_confirm))
        
        self.accept()  

def borrar_contenido():
    cuadro_lectura.clear()
    cuadro_MO.clear()
    cuadro_seriales_existente.clear()
    cuadro_seriales_crear.clear()

app = QApplication([])

ventana = QMainWindow()
ventana.setWindowTitle("Importardor items MO")
ventana.setGeometry(250, 50, 700, 700)

widget_central = QWidget()
ventana.setCentralWidget(widget_central)

layout = QGridLayout()

# Crear el widget de pestañas
pestañas = QTabWidget(ventana)

# Crear las páginas de las pestañas
pagina1 = QWidget()
#boton_pagina1 = QPushButton("Botón en la página 1")
pagina1.layout = QVBoxLayout()
#pagina1.layout.addWidget(boton_pagina1)
pagina1.setLayout(pagina1.layout)

pagina2 = QWidget()
#boton_pagina2 = QPushButton("Botón en la página 2")
pagina2.layout = QVBoxLayout()
#pagina2.layout.addWidget(boton_pagina2)
pagina2.setLayout(pagina2.layout)

pagina3 = QWidget()
#boton_pagina2 = QPushButton("Botón en la página 2")
pagina3.layout = QVBoxLayout()
#pagina2.layout.addWidget(boton_pagina2)
pagina3.setLayout(pagina3.layout)

pagina4 = QWidget()
#boton_pagina2 = QPushButton("Botón en la página 2")
pagina4.layout = QVBoxLayout()
#pagina2.layout.addWidget(boton_pagina2)
pagina4.setLayout(pagina4.layout)

# Agregar las páginas al widget de pestañas
pestañas.addTab(pagina1, "Entrada de equipos")
pestañas.addTab(pagina2, "Página 2")
pestañas.addTab(pagina3, "Busqueda de seriales")
pestañas.addTab(pagina4, "Devoluciones - Retornos")

pestañas.setGeometry(10, 10, 651, 650)
#pestañas.setWindowTitle('Ejemplo de Pestaña con PyQt5')

label = QLabel('Mo Entrada:', pagina1)
label.move(15, 50)  # Establecer la posición en la ventana sin afectar al layout
label.setFixedSize(70, 25)  # Establecer el tamaño

label = QLabel('Mo Movimiento;', pagina1)
label.move(300, 50)  # Establecer la posición en la ventana sin afectar al layout
label.setFixedSize(70, 25)  # Establecer el tamaño

label = QLabel('Mo:', pagina2)
label.move(15, 50)  # Establecer la posición en la ventana sin afectar al layout
label.setFixedSize(70, 25)  # Establecer el tamaño

label = QLabel('Seriales Existentes:', pagina3)
label.move(10, 40)  # Establecer la posición en la ventana sin afectar al layout
label.setFixedSize(90, 25)  # Establecer el tamaño

label = QLabel('Seriales a Crear:', pagina3)
label.move(350, 40)  # Establecer la posición en la ventana sin afectar al layout
label.setFixedSize(90, 25)  # Establecer el tamaño

boton_Entrada = QPushButton("Ingreso Seriales", pagina1)
boton_Entrada.move(10, 10)  # Establecer la posición en la ventana sin afectar al layout
boton_Entrada.setFixedSize(100, 25)  # Establecer el tamaño

boton_Mov = QPushButton("Movimiento", pagina2)
boton_Mov.move(10, 10)  # Establecer la posición en la ventana sin afectar al layout
boton_Mov.setFixedSize(70, 25)  # Establecer el tamaño

boton_Seriales = QPushButton("Busqueda Seriales", pagina3)
boton_Seriales.move(10, 10)  # Establecer la posición en la ventana sin afectar al layout
boton_Seriales.setFixedSize(110, 25)  # Establecer el tamaño

# Crear un botón para borrar el contenido
boton_Ret_Devo = QPushButton("Redolucion - Retorno", pagina4)
boton_Ret_Devo.move(10, 10)  # Establecer la posición en la ventana sin afectar al layout
boton_Ret_Devo.setFixedSize(200, 25)  # Largo, ancho

# Crear un botón para borrar el contenido
boton_plantilla = QPushButton("Descargar plantilla", pagina4)
boton_plantilla.move(350, 10)  # Establecer la posición en la ventana sin afectar al layout
boton_plantilla.setFixedSize(175, 25)  # Largo, ancho

# Crear un botón para borrar el contenido
boton_borrar = QPushButton("Borrar Contenido", pagina1)
boton_borrar.clicked.connect(borrar_contenido)
boton_borrar.move(10, 110)  # Establecer la posición en la ventana sin afectar al layout
boton_borrar.setFixedSize(100, 25)  # Largo, ancho

# Crear un botón para borrar el contenido
boton_borrar = QPushButton("Borrar Contenido", pagina2)
boton_borrar.clicked.connect(borrar_contenido)
boton_borrar.move(10, 110)  # Establecer la posición en la ventana sin afectar al layout
boton_borrar.setFixedSize(100, 25)  # Largo, ancho

# Crear un botón para borrar el contenido
boton_borrar = QPushButton("Borrar Contenido", pagina3)
boton_borrar.clicked.connect(borrar_contenido)
boton_borrar.move(350, 10)  # Establecer la posición en la ventana sin afectar al layout
boton_borrar.setFixedSize(100, 25)  # Largo, ancho


# Crear un QLineEdit en modo solo lectura
cuadro_lectura = QTextEdit(pagina1)
cuadro_lectura.move(10, 200)  # Establecer la posición en la ventana sin afectar al layout
cuadro_lectura.setFixedSize(600, 400) # Largo, ancho


# Crear un QLineEdit en modo solo lectura
cuadro_MO_in = QTextEdit(pagina1)
cuadro_MO_in.move(75, 50)  # Establecer la posición en la ventana sin afectar al layout
cuadro_MO_in.setFixedSize(110, 25) # Largo, ancho

# Crear un QLineEdit en modo solo lectura
cuadro_MO_Mov = QTextEdit(pagina1)
cuadro_MO_Mov.move(375, 50)  # Establecer la posición en la ventana sin afectar al layout
cuadro_MO_Mov.setFixedSize(110, 25) # Largo, ancho

# Crear un QLineEdit en modo solo lectura
cuadro_MO = QTextEdit(pagina2)
cuadro_MO.move(40, 50)  # Establecer la posición en la ventana sin afectar al layout
cuadro_MO.setFixedSize(100, 25) # Largo, ancho

# Crear un QLineEdit en modo solo lectura
cuadro_seriales_existente = QTextEdit(pagina3)
cuadro_seriales_existente.move(10, 60)  # Establecer la posición en la ventana sin afectar al layout
cuadro_seriales_existente.setFixedSize(320, 500) # Largo, ancho

# # Crear un QLineEdit en modo solo lectura
cuadro_seriales_crear = QTextEdit(pagina3)
cuadro_seriales_crear.move(350, 60)  # Establecer la posición en la ventana sin afectar al layout
cuadro_seriales_crear.setFixedSize(280, 500) # Largo, ancho

# # Crear un QLineEdit en modo solo lectura
cuadro_Mo_Confirmar_Ret_Devo = QTextEdit(pagina4)
cuadro_Mo_Confirmar_Ret_Devo.move(10, 60)  # Establecer la posición en la ventana sin afectar al layout
cuadro_Mo_Confirmar_Ret_Devo.setFixedSize(320, 500) # Largo, ancho

#layout.addWidget(cuadro_lectura)

#layout.addWidget(cuadro_MO)
widget_central.setLayout(layout)

Selecionar_archivo_seriales = Archivo_Seriales()
Selecionar_archivo_seriales_entrada = Archivo_Seriales_Entrada()
Selecionar_archivo_xls_Ret_Devo = Archivo_Seriales_Ret_Devo()


# Conectar el botón al mostrardor de la ventana de selección de archivo
boton_Seriales.clicked.connect(Selecionar_archivo_seriales.show)
boton_Entrada.clicked.connect(Selecionar_archivo_seriales_entrada.show)
boton_Ret_Devo.clicked.connect(Selecionar_archivo_xls_Ret_Devo.show)

ventana.show()
app.exec_()