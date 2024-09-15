// FUNCIONES PARA GENERAR TABLAS
function profileFormatter(cell) {
    var data = cell.getRow().getData();
    return `
        <div class="profile-info">
        <img src="${data.img}" alt="${data.name}">
            <div class="names">
                <div class="name">${data.name}</div>
                <div class="username">${data.username}</div>
            </div>
        </div>`;
}

function debtFormatter(cell) {
    var debt = parseFloat(cell.getValue());
    return debt === 0 ? "--" : `+${Math.round(debt)}€`;
}

function initializeLeaderboardTable(leaderboardData) {
    new Tabulator("#leaderboard-table", {
        data: leaderboardData,
        layout: "fitDataTable",
        headerVisible: false,
        columns: [
            { title: "Rank", field: "rank", hozAlign: "center", vertAlign: "middle", formatter: "rownum", headerSort: false, resizable: false },
            { title: "Profile", field: "profile", hozAlign: "left", vertAlign: "middle", formatter: profileFormatter, headerSort: false, resizable: false },
            { title: "Points", field: "points", hozAlign: "center", vertAlign: "middle", formatter: (cell) => `${cell.getValue()} PTS`, headerSort: false, resizable: false },
            { title: "Debt", field: "debt", hozAlign: "center", vertAlign: "middle", formatter: debtFormatter, headerSort: false, resizable: false }
        ],
        movableColumns: false,
        resizableColumns: false
    });
}

function initializeDebtsTable(debtData) {
    function formatDebt(value) {
        return value === "0.00" ? "-" : `${Math.round(parseFloat(value))}`;
    }

    const numberOfJornadas = debtData[0].length - 2;

    var debtColumns = [
        { 
            title: "User", 
            field: "user", 
            hozAlign: "left", 
            headerHozAlign: "center", 
            frozen: true, 
            headerSort: false, 
            resizable: false, 
        }
    ];

    for (let i = 1; i <= numberOfJornadas; i++) {
        debtColumns.push({
            title: "J" + i,
            field: `jornada${i}`,
            hozAlign: "center",
            headerHozAlign: "center",
            formatter: (cell) => formatDebt(cell.getValue()),
            headerSort: false,
            resizable: false
        });
    }

    debtColumns.push({
        title: "Total",
        field: "total",
        hozAlign: "center",
        headerHozAlign: "center",
        formatter: (cell) => `${Math.round(parseFloat(cell.getValue()))}€`,
        frozen: true,
        headerSort: false,
        resizable: false
    });

    var transformedData = debtData.map((row) => {
        let transformedRow = {
            user: row[0],
            total: row[row.length - 1]
        };

        for (let i = 1; i <= numberOfJornadas; i++) {
            transformedRow[`jornada${i}`] = row[i];
        }

        return transformedRow;
    });

    new Tabulator("#debts-table", {
        data: transformedData,
        layout: "fitDataTable",
        columns: debtColumns,
        movableColumns: false,
        resizableColumns: false
    });
    
}



document.addEventListener('DOMContentLoaded', () => {
    const selectorJornada = document.getElementById('selector-jornada');

    function cargarJornadas(){
        fetch(`/api/numjornadas`)
        .then(response => response.json())
        .then(jornadas => {
            selectorJornada.innerHTML = '';
            for (var jornada in jornadas ){
                selectorJornada.innerHTML += `
                <option value="${jornada}">${jornadas[jornada]}</option>`;
            }
            selectorJornada.selectedIndex = selectorJornada.options.length - 1
            cargarLeaderboard(selectorJornada.value);

        })
        .catch(error => console.error('Error:', error));
    }

    function cargarLeaderboard(jornada) {
        fetch(`/api/jornada?jornada=${jornada}`)
            .then(response => response.json())
            .then(data => {
                initializeLeaderboardTable(data);
            })
            .catch(error => console.error('Error:', error));
    }
    
    function cargarDebts(){
        fetch(`/api/deudas`)
            .then(response => response.json())
            .then(data => {
                initializeDebtsTable(data);
            })
            .catch(error => console.error('Error:', error));
    }

    selectorJornada.addEventListener('change', (event) => {
        cargarLeaderboard(event.target.value);
    });

    cargarJornadas();
    cargarDebts();
});

document.getElementById('update').addEventListener('click', function() {
    const button = document.getElementById('update');
    const text = button.querySelector('.button-text');
    const spinner = button.querySelector('.spinner');

    // Show the spinner and hide the button text
    text.classList.add('hidden');
    spinner.classList.remove('hidden');

    // Define the URL and the data to be sent
    const url = '/api/misterupdate'; // Cambia esto por la URL de tu API
    const data = {
        key1: 'value1',
        key2: 'value2'
    };

    // Send a POST request using fetch
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json()) // Parse the JSON response
    .then(data => {
        console.log('Success:', data);
        // Aquí puedes hacer algo con la respuesta
    })
    .catch((error) => {
        console.error('Error:', error);
    })
    .finally(() => {
        // Hide the spinner and show the button text
        spinner.classList.add('hidden');
        text.classList.remove('hidden');

        // Reload the page
        window.location.reload();
    });
});
