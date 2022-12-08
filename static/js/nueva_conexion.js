document.querySelector("#aerolinea1").addEventListener('change', (e) => {
    e.preventDefault();
    const aerolinea_select = e.target.value;
    document.querySelector("#vuelo1").innerHTML = `<option selected value="">Seleccione uno</option>`;
    document.querySelector("#aeropuerto1").innerHTML = `<option selected value="">Seleccione uno</option>`;
    if (aerolinea_select != "") {
        document.querySelector("#cargando").classList.add("activo");

        fetch(`/api/vuelo/${aerolinea_select}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }).then(response => response.json())
        .then(data => {
            document.querySelector("#cargando").classList.remove("activo");
            if (data.success) {
                const vuelo1 = document.querySelector("#vuelo1");
                const vuelos = data.vuelos;
                vuelo1.innerHTML = `<option selected value="">Seleccione uno</option>`;
                vuelos.forEach(vuelo => {
                    vuelo1.innerHTML += `<option value="${vuelo[0]}">${vuelo[0]}</option>`;
                });
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

})


document.querySelector("#vuelo1").addEventListener('change', (e) => {
    e.preventDefault();
    const aerolinea_select = document.querySelector("#aerolinea1").value;
    const vuelo_select = document.querySelector("#vuelo1").value;

    document.querySelector("#aeropuerto1").innerHTML = `<option selected value="">Seleccione uno</option>`;
    if (aerolinea_select != "" && vuelo_select != "") {

        document.querySelector("#cargando").classList.add("activo");

        fetch(`/api/aeropuertos/${aerolinea_select}/${vuelo_select}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }).then(response => response.json())
        .then(data => {
            document.querySelector("#cargando").classList.remove("activo");
            if (data.success) {
                const aeropuerto1 = document.querySelector("#aeropuerto1");
                const aeropuertos = data.aeropuertos;
                aeropuerto1.innerHTML = `<option selected value="">Seleccione uno</option>`;
                for (let i = 0; i < aeropuertos.length; i++) {
                    const aeropuerto = aeropuertos[i];
                    aeropuerto1.innerHTML += `<option value="${aeropuerto[0]}">${aeropuerto[1]}</option>`;
                    
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
    }

})





document.querySelector("#aerolinea2").addEventListener('change', (e) => {
    e.preventDefault();
    const aerolinea_select = e.target.value;
    document.querySelector("#vuelo2").innerHTML = `<option selected value="">Seleccione uno</option>`;
    document.querySelector("#aeropuerto2").innerHTML = `<option selected value="">Seleccione uno</option>`;
    if (aerolinea_select != "") {
        document.querySelector("#cargando").classList.add("activo");

        fetch(`/api/vuelo/${aerolinea_select}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }).then(response => response.json())
        .then(data => {
            document.querySelector("#cargando").classList.remove("activo");
            if (data.success) {
                const vuelo2 = document.querySelector("#vuelo2");
                const vuelos = data.vuelos;
                vuelo2.innerHTML = `<option selected value="">Seleccione uno</option>`;
                vuelos.forEach(vuelo => {
                    vuelo2.innerHTML += `<option value="${vuelo[0]}">${vuelo[0]}</option>`;
                });
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

})


document.querySelector("#vuelo2").addEventListener('change', (e) => {
    e.preventDefault();
    const aerolinea_select = document.querySelector("#aerolinea2").value;
    const vuelo_select = document.querySelector("#vuelo2").value;

    document.querySelector("#aeropuerto2").innerHTML = `<option selected value="">Seleccione uno</option>`;
    if (aerolinea_select != "" && vuelo_select != "") {

        document.querySelector("#cargando").classList.add("activo");

        fetch(`/api/aeropuertos/${aerolinea_select}/${vuelo_select}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }).then(response => response.json())
        .then(data => {
            document.querySelector("#cargando").classList.remove("activo");
            if (data.success) {
                const aeropuerto2 = document.querySelector("#aeropuerto2");
                const aeropuertos = data.aeropuertos;
                aeropuerto2.innerHTML = `<option selected value="">Seleccione uno</option>`;
                for (let i = 0; i < aeropuertos.length; i++) {
                    const aeropuerto = aeropuertos[i];
                    aeropuerto2.innerHTML += `<option value="${aeropuerto[0]}">${aeropuerto[1]}</option>`;
                    
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
    }

})


