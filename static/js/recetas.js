// Módulo 7 - Recetas

// Buscador en tiempo real
document.addEventListener('DOMContentLoaded', function () {
    const buscador = document.getElementById('buscador');
    if (buscador) {
        buscador.addEventListener('input', function () {
            const q = this.value.toLowerCase();
            document.querySelectorAll('.receta-item').forEach(function (item) {
                item.style.display = item.dataset.nombre.includes(q) ? '' : 'none';
            });
        });
    }

    // Re-abrir modal si hay errores de validación
    const abrirModal = document.getElementById('abrirModal');
    if (abrirModal && abrirModal.value === 'true') {
        var modal = new bootstrap.Modal(document.getElementById('modalNuevoProducto'));
        modal.show();
    }
});