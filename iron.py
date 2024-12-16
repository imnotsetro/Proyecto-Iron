import sqlite3
import json
import os
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk

# Configuración de la base de datos
conn = sqlite3.connect('gimnasio.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                apellido TEXT,
                mes_pago TEXT,
                fecha_pago TEXT,
                monto REAL,
                descripcion TEXT)''')  # Agregar la columna de descripción
conn.commit()

# Archivo para almacenar los clientes únicos
archivo_clientes_unicos = 'clientes_unicos.json'

# Cargar datos de clientes únicos desde un archivo JSON
def cargar_clientes_unicos():
    try:
        with open(archivo_clientes_unicos, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Guardar datos de clientes únicos en un archivo JSON
def guardar_clientes_unicos(clientes):
    with open(archivo_clientes_unicos, 'w') as file:
        json.dump(clientes, file, indent=4)

# Inicializar la estructura de clientes únicos
clientes_unicos = cargar_clientes_unicos()

# Funciones del programa
def agregar_pago():
    def guardar_pago():
        nombre = entry_nombre.get()
        apellido = entry_apellido.get()
        mes_pago = combo_mes_pago.get()
        monto = entry_monto.get()
        descripcion = entry_descripcion.get()
        fecha_pago = datetime.now().strftime("%Y-%m-%d")
        
        if not (nombre and apellido and mes_pago and monto):
            messagebox.showwarning("Agregar Pago", "Por favor, complete todos los campos.")
            return
        
        try:
            monto = float(monto)
        except ValueError:
            messagebox.showwarning("Agregar Pago", "El monto debe ser un número válido.")
            return

        archivo_clientes_unicos = 'clientes_unicos.json'

        # Cargar los clientes únicos del archivo JSON
        if os.path.exists(archivo_clientes_unicos):
            with open(archivo_clientes_unicos, 'r') as file:
                clientes_unicos = json.load(file)
        else:
            clientes_unicos = {}

        cliente_key = f"{nombre.lower()}_{apellido.lower()}"
        mes_index = meses.index(mes_pago)
        
        if cliente_key in clientes_unicos:
            ultimo_mes_pago = clientes_unicos[cliente_key]
            ultimo_mes_index = meses.index(ultimo_mes_pago)
            
            if ultimo_mes_index == mes_index:
                respuesta = messagebox.askquestion("Advertencia", f"El cliente ya ha pagado el mes de {mes_pago}.\n¿Desea continuar?")
                if respuesta == 'no':
                    return
            elif ultimo_mes_index != (mes_index - 1) % 12:
                def realizar_pago():
                    c.execute("INSERT INTO clientes (nombre, apellido, mes_pago, fecha_pago, monto, descripcion) VALUES (?, ?, ?, ?, ?, ?)",
                            (nombre, apellido, mes_pago, fecha_pago, monto, descripcion))
                    conn.commit()

            if ultimo_mes_index != (mes_index - 1) % 12:
                def realizar_pago():
                    c.execute("INSERT INTO clientes (nombre, apellido, mes_pago, fecha_pago, monto, descripcion) VALUES (?, ?, ?, ?, ?, ?)",
                            (nombre, apellido, mes_pago, fecha_pago, monto, descripcion))
                    conn.commit()
                    
                    # Actualizar el archivo JSON con el nuevo último mes de pago
                    clientes_unicos[cliente_key] = mes_pago
                    with open(archivo_clientes_unicos, 'w') as file:
                        json.dump(clientes_unicos, file)

                    messagebox.showinfo("Agregar Pago", "Pago agregado exitosamente.")
                    actualizar_lista()
                    ventana_agregar.destroy()
                    advertencia.destroy()

                def cancelar_pago():
                    advertencia.destroy()

                advertencia = tk.Toplevel(root)
                advertencia.title("Advertencia")
                mensaje = f"El cliente no pagó el mes anterior.\nÚltimo mes pagado: {ultimo_mes_pago}.\n¿Desea realizar el pago de todas formas?"
                tk.Label(advertencia, text=mensaje).pack(pady=10)
                
                btn_si = tk.Button(advertencia, text="Sí", command=realizar_pago)
                btn_si.pack(side=tk.LEFT, padx=10, pady=10)
                
                btn_no = tk.Button(advertencia, text="No", command=cancelar_pago)
                btn_no.pack(side=tk.RIGHT, padx=10, pady=10)
                return
            else:
                clientes_unicos[cliente_key] = mes_pago
        else:
            clientes_unicos[cliente_key] = mes_pago

        # Guardar el pago en la base de datos
        c.execute("INSERT INTO clientes (nombre, apellido, mes_pago, fecha_pago, monto, descripcion) VALUES (?, ?, ?, ?, ?, ?)",
                (nombre, apellido, mes_pago, fecha_pago, monto, descripcion))
        conn.commit()

        # Guardar los datos actualizados en el archivo JSON
        with open(archivo_clientes_unicos, 'w') as file:
            json.dump(clientes_unicos, file)

        messagebox.showinfo("Agregar Pago", "Pago agregado exitosamente.")
        actualizar_lista()
        ventana_agregar.destroy()
    
    ventana_agregar = tk.Toplevel(root)
    ventana_agregar.title("Agregar Pago")
    
    tk.Label(ventana_agregar, text="Nombre:").grid(row=0, column=0, padx=10, pady=10)
    entry_nombre = tk.Entry(ventana_agregar)
    entry_nombre.grid(row=0, column=1, padx=10, pady=10)
    
    tk.Label(ventana_agregar, text="Apellido:").grid(row=1, column=0, padx=10, pady=10)
    entry_apellido = tk.Entry(ventana_agregar)
    entry_apellido.grid(row=1, column=1, padx=10, pady=10)
    
    tk.Label(ventana_agregar, text="Mes de Pago:").grid(row=2, column=0, padx=10, pady=10)
    combo_mes_pago = ttk.Combobox(ventana_agregar, values=meses)
    combo_mes_pago.grid(row=2, column=1, padx=10, pady=10)
    
    mes_actual = datetime.now().month
    combo_mes_pago.set(meses[mes_actual - 1])
    
    tk.Label(ventana_agregar, text="Monto:").grid(row=3, column=0, padx=10, pady=10)
    entry_monto = tk.Entry(ventana_agregar)
    entry_monto.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(ventana_agregar, text="Descripción:").grid(row=4, column=0, padx=10, pady=10)
    entry_descripcion = tk.Entry(ventana_agregar)
    entry_descripcion.grid(row=4, column=1, padx=10, pady=10)
    
    btn_guardar = tk.Button(ventana_agregar, text="Guardar", command=guardar_pago)
    btn_guardar.grid(row=5, column=0, columnspan=2, pady=10)

def mostrar_clientes_deudores():
    def actualizar_vista_deudores():
        for row in tree_deudores.get_children():
            tree_deudores.delete(row)

        ahora = datetime.now()
        mes_actual = ahora.month
        ano_actual = ahora.year

        # Lista de meses en orden
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        # Cálculo de dos meses atrás
        if mes_actual <= 2:
            mes_dos_meses_atras = 12 - (2 - mes_actual)
            ano_dos_meses_atras = ano_actual - 1
        else:
            mes_dos_meses_atras = mes_actual - 2
            ano_dos_meses_atras = ano_actual

        archivo_clientes_unicos = 'clientes_unicos.json'

        if os.path.exists(archivo_clientes_unicos):
            with open(archivo_clientes_unicos, 'r') as file:
                clientes_unicos = json.load(file)
        else:
            clientes_unicos = {}

        deudores = []

        for key, ultimo_mes_pago in clientes_unicos.items():
            nombre, apellido = key.split('_')
            mes_index = meses.index(ultimo_mes_pago) + 1  # Convertir el nombre del mes a índice 1-12

            # Comprobar si el pago fue exactamente hace dos meses
            if ano_actual == ano_dos_meses_atras and mes_index == mes_dos_meses_atras:
                deudores.append((apellido.capitalize(), nombre.capitalize(), ultimo_mes_pago))

        deudores.sort()  # Ordenar por apellido

        for deudor in deudores:
            tree_deudores.insert("", "end", values=deudor)

    ventana_deudores = tk.Toplevel(root)
    ventana_deudores.title("Clientes Deudores")

    tk.Label(ventana_deudores, text="Deudores", font=("Helvetica", 14, "bold")).grid(row=0, column=0, padx=10, pady=10)

    tk.Label(ventana_deudores, text="(SE MOSTRARA SOLAMENTE LOS CLIENTES QUE NO PAGAN HACE 2 MESES)", font=("Helvetica", 10, "bold")).grid(row=1, column=0, padx=10, pady=10)

    columnas_deudores = ("Apellido", "Nombre", "Último Mes Pagado")
    tree_deudores = ttk.Treeview(ventana_deudores, columns=columnas_deudores, show="headings")
    for col in columnas_deudores:
        tree_deudores.heading(col, text=col)
    tree_deudores.grid(row=2, column=0, padx=10, pady=10)

    actualizar_vista_deudores()

def actualizar_lista():
    # Obtener el texto de la barra de búsqueda
    query = entry_busqueda.get()

    # Limpiar el Treeview
    for row in tree.get_children():
        tree.delete(row)

    # Si hay un texto en la barra de búsqueda, usar la función de búsqueda
    if query:
        buscar_clientes(query)
        return

    mes_seleccionado = combo_mes.get()
    ano_seleccionado = combo_ano.get()

    c.execute("SELECT id, apellido, nombre, monto, mes_pago, fecha_pago, descripcion FROM clientes WHERE strftime('%Y', fecha_pago) = ? AND mes_pago = ? ORDER BY mes_pago, apellido", (ano_seleccionado, mes_seleccionado))
    for row in c.fetchall():
        tree.insert("", "end", values=(row[1], row[2], row[3], row[4], row[5], row[6], row[0]))

def mostrar_montos_acumulados():
    def actualizar_vista_montos():
        for row in tree_montos.get_children():
            tree_montos.delete(row)

        ano_seleccionado = combo_ano_montos.get()
        montos_por_mes = {mes: 0 for mes in meses}
        clientes_por_mes = {mes: 0 for mes in meses}
        total_monto_anual = 0
        total_clientes_anual = 0

        c.execute("SELECT mes_pago, monto FROM clientes WHERE strftime('%Y', fecha_pago) = ?", (ano_seleccionado,))
        for row in c.fetchall():
            mes_pago, monto = row
            montos_por_mes[mes_pago] += monto
            clientes_por_mes[mes_pago] += 1

        for mes, monto in montos_por_mes.items():
            tree_montos.insert("", "end", values=(mes, monto, clientes_por_mes[mes]))
            total_monto_anual += monto
            total_clientes_anual += clientes_por_mes[mes]

        label_total_monto.config(text=f"Total Monto Anual: {total_monto_anual}")
        label_total_clientes.config(text=f"Total Clientes Anual: {total_clientes_anual}")

    ventana_montos = tk.Toplevel(root)
    ventana_montos.title("Montos Acumulados por Mes")
    ventana_montos.geometry("640x450")  # Ajusta el tamaño de la ventana según sea necesario

    tk.Label(ventana_montos, text="Año:").grid(row=0, column=0, padx=10, pady=10)
    combo_ano_montos = ttk.Combobox(ventana_montos, values=[str(ano) for ano in range(datetime.now().year - 2, datetime.now().year + 8)])
    combo_ano_montos.grid(row=0, column=1, padx=10, pady=10)
    combo_ano_montos.set(str(datetime.now().year))
    combo_ano_montos.bind("<<ComboboxSelected>>", lambda event: actualizar_vista_montos())
    
    columnas_montos = ("Mes", "Monto", "Cantidad de Clientes")
    tree_montos = ttk.Treeview(ventana_montos, columns=columnas_montos, show="headings", height=13)  # Ajusta la altura según sea necesario
    for col in columnas_montos:
        tree_montos.heading(col, text=col)
    tree_montos.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(ventana_montos, orient="vertical", command=tree_montos.yview)
    tree_montos.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=1, column=3, sticky='ns')

    label_total_monto = tk.Label(ventana_montos, text="Total Monto Anual: 0", font=("Helvetica", 14, "bold"))
    label_total_monto.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

    label_total_clientes = tk.Label(ventana_montos, text="Total Clientes Anual: 0", font=("Helvetica", 14, "bold"))
    label_total_clientes.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
    
    actualizar_vista_montos()


def modificar_cliente():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Modificar Cliente", "Selecciona un cliente para modificar.")
        return
    
    item = tree.item(selected_item)
    cliente_id = item["values"][-1]  # El ID está en la última columna de los valores

    def guardar_modificacion():
        nombre = entry_nombre.get()
        apellido = entry_apellido.get()
        mes_pago = combo_mes_pago.get()
        monto = entry_monto.get()
        descripcion = entry_descripcion.get()

        if not (nombre and apellido and mes_pago and monto):
            messagebox.showwarning("Modificar Cliente", "Por favor, complete todos los campos.")
            return
        
        try:
            monto = float(monto)
        except ValueError:
            messagebox.showwarning("Modificar Cliente", "El monto debe ser un número válido.")
            return
        
        # Actualizar la base de datos
        c.execute("UPDATE clientes SET nombre = ?, apellido = ?, mes_pago = ?, monto = ?, descripcion = ? WHERE id = ?",
                (nombre, apellido, mes_pago, monto, descripcion, cliente_id))
        conn.commit()

        # Actualizar el archivo JSON
        key = f"{nombre.lower()}_{apellido.lower()}"
        archivo_clientes_unicos = 'clientes_unicos.json'
        
        if os.path.exists(archivo_clientes_unicos):
            with open(archivo_clientes_unicos, 'r') as file:
                clientes_unicos = json.load(file)
        else:
            clientes_unicos = {}

        clientes_unicos[key] = mes_pago

        with open(archivo_clientes_unicos, 'w') as file:
            json.dump(clientes_unicos, file)

        actualizar_lista()
        ventana_modificar.destroy()

    def eliminar_cliente():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Eliminar Pago", "Por favor, seleccione un pago para eliminar.")
            return

        confirmacion = messagebox.askyesno("Eliminar Pago", "¿Está seguro de que desea eliminar este pago?")
        if not confirmacion:
            return

        item_id = tree.item(selected_item)["values"][6]  # Obtener el ID del pago desde la última columna

        c.execute("SELECT nombre, apellido, mes_pago FROM clientes WHERE id = ?", (item_id,))
        cliente_eliminar = c.fetchone()
        if cliente_eliminar:
            nombre, apellido, mes_pago = cliente_eliminar
            c.execute("DELETE FROM clientes WHERE id = ?", (item_id,))
            conn.commit()
            actualizar_lista()
            messagebox.showinfo("Eliminar Pago", "Pago eliminado exitosamente.")
            
            # Verificar si el último mes de pago del cliente es igual al mes que se está eliminando
            archivo_clientes_unicos = 'clientes_unicos.json'
            if mes_pago == combo_mes.get():
                key = f"{nombre.lower()}_{apellido.lower()}"
                if os.path.exists(archivo_clientes_unicos):
                    with open(archivo_clientes_unicos, 'r') as file:
                        clientes_unicos = json.load(file)
                    if key in clientes_unicos:
                        del clientes_unicos[key]
                        with open(archivo_clientes_unicos, 'w') as file:
                            json.dump(clientes_unicos, file)
        else:
            messagebox.showerror("Eliminar Pago", "No se pudo encontrar el pago seleccionado en la base de datos.")

    ventana_modificar = tk.Toplevel(root)
    ventana_modificar.title("Modificar Cliente")
    
    tk.Label(ventana_modificar, text="Nombre:").grid(row=0, column=0, padx=10, pady=10)
    entry_nombre = tk.Entry(ventana_modificar)
    entry_nombre.grid(row=0, column=1, padx=10, pady=10)
    entry_nombre.insert(0, item["values"][1])
    
    tk.Label(ventana_modificar, text="Apellido:").grid(row=1, column=0, padx=10, pady=10)
    entry_apellido = tk.Entry(ventana_modificar)
    entry_apellido.grid(row=1, column=1, padx=10, pady=10)
    entry_apellido.insert(0, item["values"][0])
    
    tk.Label(ventana_modificar, text="Mes de Pago:").grid(row=2, column=0, padx=10, pady=10)
    combo_mes_pago = ttk.Combobox(ventana_modificar, values=[
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    combo_mes_pago.grid(row=2, column=1, padx=10, pady=10)
    combo_mes_pago.set(item["values"][3])
    
    tk.Label(ventana_modificar, text="Monto:").grid(row=3, column=0, padx=10, pady=10)
    entry_monto = tk.Entry(ventana_modificar)
    entry_monto.grid(row=3, column=1, padx=10, pady=10)
    entry_monto.insert(0, item["values"][2])

    tk.Label(ventana_modificar, text="Descripción:").grid(row=4, column=0, padx=10, pady=10)
    entry_descripcion = tk.Entry(ventana_modificar)
    entry_descripcion.grid(row=4, column=1, padx=10, pady=10)
    entry_descripcion.insert(0, item["values"][5])
    
    btn_guardar = tk.Button(ventana_modificar, text="Guardar", command=guardar_modificacion)
    btn_guardar.grid(row=5, column=0, columnspan=1, pady=10)

    btn_eliminar = tk.Button(ventana_modificar, text="Eliminar Cliente", command=eliminar_cliente, bg="red", fg="white")
    btn_eliminar.grid(row=5, column=1, columnspan=1, pady=10)

def buscar_clientes(query):
    # Limpiar el Treeview
    for row in tree.get_children():
        tree.delete(row)

    # Si la búsqueda está vacía, mostrar todos los clientes
    if not query:
        actualizar_lista()
        return

    # Filtrar clientes en la base de datos que coincidan con la búsqueda
    query = f"%{query}%"
    c.execute("SELECT id, apellido, nombre, monto, mes_pago, fecha_pago, descripcion FROM clientes WHERE nombre LIKE ? OR apellido LIKE ? ORDER BY mes_pago, apellido", (query, query))
    for row in c.fetchall():
        tree.insert("", "end", values=(row[1], row[2], row[3], row[4], row[5], row[6], row[0]))

# Interfaz gráfica
root = tk.Tk()
root.title("Registro de Pagos - Gimnasio")

# Aumentar el tamaño de la ventana
root.geometry("1400x750")  # Tamaño más grande de la ventana

# Aumentar el tamaño de la fuente
default_font = ("Helvetica", 14)  # Fuente más grande
root.option_add("*Font", default_font)

# Añadir barra de búsqueda encima del Treeview
frame_busqueda = tk.Frame(root)
frame_busqueda.pack(pady=10)

tk.Label(frame_busqueda, text="Buscar:").grid(row=0, column=0, padx=10, pady=10)
entry_busqueda = tk.Entry(frame_busqueda)
entry_busqueda.grid(row=0, column=1, padx=10, pady=10)

entry_busqueda.bind("<KeyRelease>", lambda event: buscar_clientes(entry_busqueda.get()))

# Configuración del Treeview con fuentes más grandes
frame = tk.Frame(root)
frame.pack(pady=10, expand=True, fill=tk.BOTH)

style = ttk.Style()
style.configure("Treeview.Heading", font=("Helvetica", 14, "bold"))
style.configure("Treeview", font=("Helvetica", 14))

tree = ttk.Treeview(frame, columns=("Apellido", "Nombre", "Monto", "Mes de Pago", "Fecha de Pago", "Descripcion", "ID"), show="headings", height=20)  # Ajustar la altura
tree.heading("Apellido", text="Apellido")
tree.heading("Nombre", text="Nombre")
tree.heading("Monto", text="Monto")
tree.heading("Mes de Pago", text="Mes de Pago")
tree.heading("Fecha de Pago", text="Fecha de Pago")
tree.heading("Descripcion", text="Descripcion")
tree.heading("ID", text="ID")  # La columna ID no se mostrará pero la incluimos para obtener el valor
tree["displaycolumns"] = ("Apellido", "Nombre", "Monto", "Mes de Pago", "Fecha de Pago", "Descripcion")  # No mostrar columna ID
tree.pack(expand=True, fill=tk.BOTH)  # Expandir para llenar el espacio disponible

# Añadir un Scrollbar para el Treeview
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
tree.configure(yscroll=scrollbar.set)

# Controles de selección de año y mes
frame_filtros = tk.Frame(root)
frame_filtros.pack(pady=10)

tk.Label(frame_filtros, text="Año:").grid(row=0, column=0, padx=10, pady=10)
anos = [str(ano) for ano in range(datetime.now().year - 2, datetime.now().year + 8)]
combo_ano = ttk.Combobox(frame_filtros, values=anos)
combo_ano.grid(row=0, column=1, padx=10, pady=10)
combo_ano.set(str(datetime.now().year))
combo_ano.bind("<<ComboboxSelected>>", lambda event: actualizar_lista())

tk.Label(frame_filtros, text="Mes:").grid(row=0, column=2, padx=10, pady=10)
meses = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
combo_mes = ttk.Combobox(frame_filtros, values=meses)
combo_mes.grid(row=0, column=3, padx=10, pady=10)
mes_actual = datetime.now().month
combo_mes.set(meses[mes_actual - 1])
combo_mes.bind("<<ComboboxSelected>>", lambda event: actualizar_lista())

# Botones de control debajo de los filtros
frame_botones_izquierda = tk.Frame(root)
frame_botones_izquierda.pack(side=tk.LEFT, padx=10, pady=10, anchor='sw')

btn_agregar = tk.Button(frame_botones_izquierda, text="Agregar Pago", command=agregar_pago, bg="green", fg="white", font=("Helvetica", 14, "bold"))
btn_agregar.grid(row=0, column=0, padx=5)

btn_deudores = tk.Button(frame_botones_izquierda, text="Mostrar Deudores", command=mostrar_clientes_deudores, bg="red", fg="white", font=("Helvetica", 14, "bold"))
btn_deudores.grid(row=0, column=1, padx=5)

btn_modificar = tk.Button(frame_botones_izquierda, text="Modificar Cliente", command=modificar_cliente, bg="yellow", fg="black", font=("Helvetica", 14, "bold"))
btn_modificar.grid(row=0, column=2, padx=5)

btn_montos_acumulados = tk.Button(root, text="Montos Acumulados", command=mostrar_montos_acumulados, bg="white", fg="black", font=("Helvetica", 14, "bold"))
btn_montos_acumulados.pack(side=tk.RIGHT, padx=10, pady=10, anchor='se')

actualizar_lista()

root.mainloop()
conn.close()