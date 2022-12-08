let pilotos = [];
const llenar_pilotos = () => {
    document.querySelectorAll(".piloto").forEach(element => {
        element.innerHTML = `<option selected value="">Seleccione uno</option>`;
        pilotos.forEach(piloto => {
            element.innerHTML += `<option value="${piloto[0]}">${piloto[1]}</option>`;
        });
    });

}

document.querySelector("#no_segmentos").addEventListener('blur', (e) => {
    let aeropuertos = [];
    const no_segmentos_1 = parseInt(e.target.value);

    document.querySelector("#cargando").classList.add("activo");
    fetch(`/api/aeropuertos`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    }).then(response => response.json())
    .then(data => {
        document.querySelector("#cargando").classList.remove("activo");
        if (data.success) {
            let aeropuerto_select = `<option selected value="">Seleccione uno</option>`;
            data.aeropuertos.forEach(aeropuerto => {
                aeropuerto_select += `<option value="${aeropuerto[0]}">${aeropuerto[1]}</option>`;
            });

            let pilotos_select = `<option selected value="">Seleccione uno</option>`;
            pilotos.forEach(piloto => {
                pilotos_select += `<option value="${piloto[0]}">${piloto[1]}</option>`;
            });


            const contSeg = document.querySelector(".contenedor-segmentos");
            contSeg.innerHTML = "";
            for (let i = 2; i < (no_segmentos_1+2); i++) {
                contSeg.innerHTML += `
                <div class="form-floating mb-3">
                    <select class="form-select aeropuerto" required name="aeropuerto[]" id="aeropuerto${i}">
                        ${aeropuerto_select}
                    </select>
                    <label for="aeropuerto${i}">Aeropuerto ${i}:</label>
                </div>`
                if(i < (no_segmentos_1+1)){
                    contSeg.innerHTML += `
                    <div class="form-floating mb-3">
                        <select class="form-select piloto" required name="piloto[]" id="piloto${i}">
                            ${pilotos_select}
                        </select>
                        <label for="piloto${i}">Piloto ${i} - ${i+1}:</label>
                    </div>
                    <div class="form-floating mb-3">
                        <input type="date" class="form-control fecha" required name="fecha[]" id="fecha${i}" placeholder="Fecha ${i} - ${i+1}:" >
                        <label for="fecha1">Fecha ${i} - ${i+1}:</label>
                    </div>
                    <div class="form-floating mb-3">
                        <input type="number" min="0" max="23" class="form-control hora" required name="hora[]" id="hora${i}" placeholder="Hora ${i} - ${i+1}:" >
                        <label for="hora1">Hora ${i} - ${i+1}:</label>
                    </div>
                    `;
                }
                
            }
        }
        else {
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: data.error
            });                
        }
    }).catch(data => {
        document.querySelector("#cargando").classList.remove("activo");
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: data
        });
    });

    
    
    
});

document.querySelector("#aerolinea").addEventListener('change', (e) => {
    e.preventDefault();
    const aerolinea_select = e.target.value;
    if (aerolinea_select != "") {
        document.querySelector("#cargando").classList.add("activo");

        fetch(`/api/aerolinea/${aerolinea_select}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }).then(response => response.json())
        .then(data => {
            document.querySelector("#cargando").classList.remove("activo");
            if (data.success) {
                document.querySelector("#no_vuelo").value = data.proximo_vuelo
                pilotos = data.pilotos
                llenar_pilotos()
            }
            else {
                Swal.fire({
                    icon: 'error',
                    title: 'Oops...',
                    text: data.error
                });                
            }
        }).catch(data => {
            document.querySelector("#cargando").classList.remove("activo");
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: data
            });
        });
    }
    else{
        document.querySelector("#no_vuelo").value = ""
        pilotos = []
        llenar_pilotos()
    }
})


