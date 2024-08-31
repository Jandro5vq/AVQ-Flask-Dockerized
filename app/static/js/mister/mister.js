document.addEventListener('DOMContentLoaded', () => {
    const selectorJornada = document.getElementById('selector-jornada');
    const cuerpoTabla = document.getElementById('user-list');

    function cargarPuntuaciones(jornada) {
        fetch(`/api/jornada?jornada=${jornada}`)
            .then(response => response.json())
            .then(puntuaciones => {
                cuerpoTabla.innerHTML = ''
                puntuaciones.forEach(function (jugador, i) {
                    cuerpoTabla.innerHTML += `
                    <li>
                        <div class="user-row">
                            <p class="user-pos">${i+1}</p>
                            <div class="user-info">
                                <img class="user-image"
                                    src="${jugador.img}" />
                                <div class="user-names">
                                    <p class="user-name">${jugador.name}</p>
                                    <p class="user-username">${jugador.username}</p>
                                </div>
                            </div>
                            <p class="user-points">${jugador.points} PTS</p>
                            <p class="user-debt">+2€</p>
                        </div>
                    </li>
                    `
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