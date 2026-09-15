"""Sistema de Inventario y Ventas - Microempresa (SENATI)"""

from datetime import datetime

ARCH_INV = "inventario.txt"
ARCH_VEN = "ventas.txt"


# ============================ PERSISTENCIA ============================
# Estas funciones son las únicas que abren archivos (with open, modos r/w/a).

def cargar_inventario():
    """Lee inventario.txt y devuelve un diccionario anidado {id: {nombre, precio, stock}}.
    Si el archivo no existe o tiene líneas corruptas, no rompe el programa."""
    inventario = {}
    try:
        with open(ARCH_INV, "r", encoding="utf-8") as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print("No existe inventario previo, se crea uno nuevo.")
    else:
        for linea in lineas:
            if linea.strip():
                try:
                    id_p, nombre, precio, stock = linea.strip().split(";")
                    inventario[id_p] = {"nombre": nombre, "precio": float(precio), "stock": int(stock)}
                except ValueError:
                    print(f"Línea con formato inválido, se ignora: {linea.strip()}")
    finally:
        print("Carga de inventario finalizada.")
    return inventario


def guardar_inventario(inventario):
    """Sobrescribe inventario.txt (modo 'w') con el diccionario completo en memoria."""
    try:
        with open(ARCH_INV, "w", encoding="utf-8") as f:
            for id_p, d in inventario.items():
                f.write(f"{id_p};{d['nombre']};{d['precio']};{d['stock']}\n")
    except OSError as error:
        print(f"No se pudo guardar el inventario: {error}")
        return False
    else:
        return True


def cargar_ventas():
    """Lee ventas.txt y devuelve la lista de ventas registradas."""
    ventas = []
    try:
        with open(ARCH_VEN, "r", encoding="utf-8") as f:
            for linea in f:
                if linea.strip():
                    try:
                        idv, id_p, cant, total, fecha = linea.strip().split(";")
                        ventas.append({"id_venta": int(idv), "id_producto": id_p,
                                       "cantidad": int(cant), "total": float(total), "fecha": fecha})
                    except ValueError:
                        print(f"Línea de venta inválida, se ignora: {linea.strip()}")
    except FileNotFoundError:
        pass
    return ventas


def guardar_venta(venta):
    """Agrega (modo 'a') una venta nueva al final de ventas.txt sin borrar el historial."""
    try:
        with open(ARCH_VEN, "a", encoding="utf-8") as f:
            f.write(f"{venta['id_venta']};{venta['id_producto']};{venta['cantidad']};{venta['total']};{venta['fecha']}\n")
    except OSError as error:
        print(f"No se pudo guardar la venta: {error}")
        return False
    else:
        return True


# ========================= LÓGICA DE NEGOCIO =========================
# No imprimen nada: reciben datos, devuelven (éxito, mensaje) o (éxito, dato, mensaje).

def listar_productos(inventario):
    """Devuelve un texto con una línea por producto (id, nombre, precio, stock)."""
    if not inventario:
        return "Inventario vacío."
    lineas = [f"{id_p} | {d['nombre']} | S/ {d['precio']:.2f} | stock: {d['stock']}"
              for id_p, d in inventario.items()]
    return "\n".join(lineas)


def agregar_producto(inventario, id_p, nombre, precio, stock):
    """Valida ID duplicado y valores negativos; si todo ok, agrega el producto."""
    if id_p in inventario:
        return False, "ID ya existe."
    if precio < 0 or stock < 0:
        return False, "Precio o stock no pueden ser negativos."
    inventario[id_p] = {"nombre": nombre, "precio": precio, "stock": stock}
    return True, "Producto agregado."


def registrar_venta(inventario, ventas, id_p, cantidad):
    """Valida stock, descuenta cantidad, calcula total y arma el registro de venta."""
    producto = inventario.get(id_p)
    if producto is None:
        return False, None, "Producto no encontrado."
    if cantidad <= 0 or cantidad > producto["stock"]:
        return False, None, "Cantidad inválida o stock insuficiente."
    producto["stock"] -= cantidad
    total = round(producto["precio"] * cantidad, 2)
    venta = {"id_venta": len(ventas) + 1, "id_producto": id_p, "cantidad": cantidad,
              "total": total, "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")}
    ventas.append(venta)
    return True, venta, f"Venta registrada. Total: S/ {total:.2f}"


def reporte_ventas(ventas):
    """Devuelve el número de ventas y el ingreso total acumulado."""
    if not ventas:
        return "No hay ventas registradas."
    total = sum(v["total"] for v in ventas)
    return f"Ventas realizadas: {len(ventas)} | Ingreso total: S/ {total:.2f}"


# ========================= INTERFAZ DE CONSOLA =========================

def pedir_numero(mensaje, es_entero=False):
    """Pide un número por consola y no deja avanzar hasta que sea válido
    (try-except-else-finally: valida, retorna si ok, siempre pasa por finally)."""
    while True:
        entrada = input(mensaje)
        try:
            valor = int(entrada) if es_entero else float(entrada)
        except ValueError:
            print("Ingrese un número válido.")
        else:
            return valor
        finally:
            pass  # espacio reservado para log/limpieza; se ejecuta siempre, haya o no error


def menu():
    """Bucle principal: carga datos una vez, muestra el menú (while + if-elif-else)
    y despacha cada opción a su función de lógica de negocio correspondiente."""
    inventario = cargar_inventario()
    ventas = cargar_ventas()

    while True:
        print("\n1. Agregar producto  2. Ver productos  3. Registrar venta  4. Ver reporte  5. Salir")
        opcion = input("Opción: ").strip()

        if opcion == "1":
            id_p = input("ID: ").strip()
            nombre = input("Nombre: ").strip()
            precio = pedir_numero("Precio: ")
            stock = pedir_numero("Stock: ", es_entero=True)
            ok, msg = agregar_producto(inventario, id_p, nombre, precio, stock)
            print(msg)
            if ok:
                guardar_inventario(inventario)

        elif opcion == "2":
            print(listar_productos(inventario))

        elif opcion == "3":
            id_p = input("ID del producto: ").strip()
            cantidad = pedir_numero("Cantidad: ", es_entero=True)
            ok, venta, msg = registrar_venta(inventario, ventas, id_p, cantidad)
            print(msg)
            if ok:
                guardar_inventario(inventario)
                guardar_venta(venta)

        elif opcion == "4":
            print(reporte_ventas(ventas))

        elif opcion == "5":
            print("Hasta pronto.")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    menu()