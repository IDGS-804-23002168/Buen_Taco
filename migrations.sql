-- =====================================================
-- MIGRACIONES MÓDULO 7: RECETAS
-- Ejecutar en MySQL Workbench si no tienes estos cambios
-- =====================================================

-- 1. Agregar columnas a Productos
ALTER TABLE Productos 
ADD COLUMN IF NOT EXISTS Descripcion TEXT NULL AFTER Nombre,
ADD COLUMN IF NOT EXISTS CostoUltimaActualizacion DATETIME NULL;

-- 2. Modificar tabla Recetas (clave primaria compuesta)
ALTER TABLE Recetas
DROP FOREIGN KEY IF EXISTS FK_Recetas_MateriaPrima,
DROP FOREIGN KEY IF EXISTS recetas_ibfk_2,
DROP PRIMARY KEY,
ADD COLUMN RecetaId INT AUTO_INCREMENT PRIMARY KEY FIRST,
ADD CONSTRAINT FK_Recetas_Producto FOREIGN KEY (ProductoId) REFERENCES Productos(ProductoId),
ADD CONSTRAINT FK_Recetas_MateriaPrima2 FOREIGN KEY (MateriaPrimaId) REFERENCES MateriasPrimas(MateriaPrimaId);

-- 3. Trigger de costo
DROP TRIGGER IF EXISTS trg_actualiza_costo_producto;
DELIMITER $$
CREATE TRIGGER trg_actualiza_costo_producto
AFTER INSERT ON CompraDetalle
FOR EACH ROW
BEGIN
    UPDATE Productos p
    JOIN Recetas r ON r.ProductoId = p.ProductoId
    SET p.CostoUltimaActualizacion = NOW()
    WHERE r.MateriaPrimaId = NEW.MateriaPrimaId;
END$$
DELIMITER ;