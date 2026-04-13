from sqlalchemy import func
from models import db, Receta, MovimientoMateriaPrima

def obtener_disponibilidad_producto(producto_id):
    """
    Calcula cuántas unidades se pueden producir de un producto 
    basado en el stock actual de sus materias primas y su receta.
    """
    recetas = Receta.query.filter_by(ProductoId=producto_id).all()
    if not recetas:
        return 0
    
    minimo_posible = None
    
    for r in recetas:
        # Stock actual de la materia prima (campo 'stock' en MateriaPrima)
        # o podríamos calcularlo de movimientos, pero el modelo ya tiene 'stock' actualizado
        stock_actual = float(r.materia_prima.stock or 0)
        
        # Cantidad necesaria según la receta
        # Consideramos la merma si existe (algunos cálculos ya la incluyen en CantidadBase, 
        # pero según la lógica previa en disponibilidadProductos, se dividía directamente)
        cantidad_necesaria = float(r.CantidadBase or 0)
        
        if cantidad_necesaria <= 0:
            continue
            
        unidades_con_este_insumo = int(stock_actual // cantidad_necesaria)
        
        if minimo_posible is None or unidades_con_este_insumo < minimo_posible:
            minimo_posible = unidades_con_este_insumo
            
    return minimo_posible if minimo_posible is not None else 0
