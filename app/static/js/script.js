document.addEventListener('DOMContentLoaded', () => {
    const selectorJornada = document.getElementById('selector-jornada');
    const cuerpoTabla = document.getElementById('cuerpo-tabla');

    function cargarPuntuaciones(jornada) {
        fetch(`/api/puntos?jornada=${jornada}`)
            .then(response => response.json())
            .then(puntuaciones => {
                cuerpoTabla.innerHTML = '';
                puntuaciones.forEach(jugador => {
                    const fila = document.createElement('tr');
                    const celdaNombre = document.createElement('td');
                    const celdaPuntos = document.createElement('td');

                    celdaNombre.textContent = jugador.nombre;
                    celdaPuntos.textContent = jugador.puntos;

                    fila.appendChild(celdaNombre);
                    fila.appendChild(celdaPuntos);

                    cuerpoTabla.appendChild(fila);
                });
            })
            .catch(error => console.error('Error:', error));
    }

    // Cargar puntuaciones al cambiar la jornada
    selectorJornada.addEventListener('change', (event) => {
        cargarPuntuaciones(event.target.value);
    });

    // Cargar la jornada 1 por defecto al cargar la página
    cargarPuntuaciones(selectorJornada.value);
});