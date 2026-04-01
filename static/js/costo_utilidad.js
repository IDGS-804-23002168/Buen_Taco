// Módulo 11 - Costo y Utilidad

document.addEventListener('DOMContentLoaded', function () {

    // Filtro por categoría
    const filtroCat = document.getElementById('filtroCategoria');
    if (filtroCat) {
        filtroCat.addEventListener('change', filtrar);
    }

    // Toggle inactivos
    const toggleInactivos = document.getElementById('toggleInactivos');
    if (toggleInactivos) {
        toggleInactivos.addEventListener('change', filtrar);
    }

    function filtrar() {
        const cat        = filtroCat ? filtroCat.value : '';
        const verInactivos = toggleInactivos ? toggleInactivos.checked : false;

        document.querySelectorAll('tbody tr[data-categoria]').forEach(function (fila) {
            const filaCat      = fila.dataset.categoria;
            const filaActivo   = fila.dataset.activo === '1';

            const pasaCat      = !cat || filaCat === cat;
            const pasaActivo   = filaActivo || verInactivos;

            fila.style.display = (pasaCat && pasaActivo) ? '' : 'none';
        });
    }

    // Buscador por nombre
    const buscador = document.getElementById('buscadorProducto');
    if (buscador) {
        buscador.addEventListener('input', function () {
            const q = this.value.toLowerCase();
            document.querySelectorAll('tbody tr[data-nombre]').forEach(function (fila) {
                fila.style.display = fila.dataset.nombre.includes(q) ? '' : 'none';
            });
        });
    }

});