
async function loadGestiones(container) {
    console.log('Loading');
    try{
        const response = await fetch('/gestiones/visualizar', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const gestiones = await response.json();
        // Mostrar las gestiones en la página

        gestiones.forEach((gestion) => {
            console.log('Gestión:', gestion);
            const div = document.createElement('div');
            div.classList.add('gestion-card');
            div.innerHTML = `
                <h2>${gestion.nombre_gestion}</h2>
                <p>${gestion.descripcion}</p>
                <a id=${gestion.id_gestion}-details class="view-btn">Ver Detalles</a>
                <a id=${gestion.id_gestion}-modify class="view-btn" >Modificar</a>
                <button class="delete-btn" id=${gestion.id_gestion}-borrar>🗑️</button>
            `;
            container.appendChild(div);

            document.getElementById(`${gestion.id_gestion}-borrar`).addEventListener('click', async function(){
                let token = localStorage.getItem('token');
                const gestionCard = this.closest('.gestion-card');
                if(confirm('¿Estás seguro de eliminar esta gestión?')) {
                    const id = this.id.split('-')[0];
                    const response = await fetch(`/gestiones/borrar/${id}`, {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json'
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    gestionCard.remove();
                    alert('Gestión eliminada exitosamente.');
                }
            });
            
            document.getElementById(`${gestion.id_gestion}-modify`).addEventListener('click', function(){
                const id = this.id.split('-')[0];
                window.location.href = `/gestiones/modificar?id=${id}`;
            });

            document.getElementById(`${gestion.id_gestion}-details`).addEventListener('click', function(){
                const id = this.id.split('-')[0];
                window.location.href = `/gestiones/detalles?id=${id}`; 
            });


        });

    }catch(err){
        console.error('Error al cargar las gestiones:', err);
        alert('Error al cargar las gestiones. Intente de nuevo.');
        return;
    }
}

async function validarToken(){
    const token = localStorage.getItem('token');

    if(!token) {
        alert('Necesitas iniciar sesión para acceder a esta sección.');
        window.location.href = '/login';
        return;
    }

    try {
        const response = await fetch('/gestores/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            alert('Sesión expirada. Inicia sesión nuevamente.');
            localStorage.removeItem('token');
            window.location.href = '/login'; // Redirige a la página de login si el token es inválido o ha expirado
            return false;
        }

        // Si la respuesta es ok, el token sigue siendo válido.
        return true;

    } catch (error) {
        console.error('Error al validar el token:', error);
        alert('Error al validar el token. Intenta iniciar sesión nuevamente.');
        localStorage.removeItem('token');
        window.location.href = '/login'; // Redirige a la página de login en caso de error
        return false;
    }
}


function enviarFormularioRegistro(formulario, url) {
    formulario.addEventListener('submit', async (e) => {
        e.preventDefault();
        const nombreFormulario = formulario.getAttribute('name');

        let validar = true;


        if (nombreFormulario === 'formularioRegistro') {
            validar = validarDatos(formulario);
        }

        if (validar) {
            const datos = new FormData(formulario);
            const datosJSON = {};

            datos.forEach((value, key) => {
                if (key.startsWith("confirmar-"))
                    return;
                datosJSON[key] = value;
            });

            console.log(datosJSON);

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(datosJSON)
                });
            
                if (!response.ok) {
                    const errorData = await response.json().catch(() => {
                        throw new Error('Error desconocido');
                    });
                    throw new Error(errorData.detail || 'Error desconocido');
                } else {
                    alert('Registro exitoso');
                    return;
                }
            } catch (error) {
                console.error('Error:', error.message);
                alert('Error al registrar: ' + error.message);
                return;
            }
            

        }

    });

}

function enviarFormularioLogin(formulario, url) {
    formulario.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(formulario);
        const formDataObject = Object.fromEntries(formData.entries()); // Convierte los datos del formulario en un objeto

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded' // Asegúrate de que el servidor acepte este tipo de contenido
                },
                body: new URLSearchParams(formDataObject) // Convierte el objeto en una cadena de consulta
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail);
            } else {
                const data = await response.json();
                localStorage.setItem('token', data.access_token);
                if(validarToken()){
                    window.location.href = '/gestiones'
                }else{
                    alert('No se pudo validar el token.');
                    localStorage.removeItem('token');
                    window.location.href = '/login'; // Redirige a la página de login en caso de error
                }       
            }
        } catch (error) {
            console.error('Error:', error.message);
            alert(error.message);
        }
    });
}

function enviarFormularioCrearGestion(formulario, url){
    formulario.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(formulario);
        const datosJSON = {};
        const token = localStorage.getItem('token');

        formData.forEach((value, key) => {
            if (key.startsWith("empresas")){
                datosJSON["empresas"] = value.split(',').map(empresa => empresa.trim())
            }else{
                datosJSON[key] = value;
            }  
        });

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(datosJSON)
            });
        
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error desconocido');
            } else {
                alert('Gestión creada exitosamente');
                return;
            }
        } catch (error) {
            console.error('Error:', error.message);
            alert('Error al crear la gestión: '+ error.message);
            return;
        }
    });
}

function validarDatos(formulario) {
    const contrasena = formulario.querySelector('#password');
    const confirmarContraseña = formulario.querySelector('#confirmar-contraseña');

    if (contrasena.value !== confirmarContraseña.value) {
        alert('Las contraseñas no coinciden');
        return false;
    }

    if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}/.test(contrasena.value)) {
        alert('La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una letra minúscula, un número y un carácter especial');
        return false;
    }

    if (!/^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/.test(formulario.email.value)) {
        alert('El email no es válido');
        return false;
    }

    const campos = formulario.querySelectorAll('input[required]');
    for (let campo of campos) {
        if (campo.value.trim() === '') {
            alert(`El campo ${campo.previousElementSibling.textContent} es obligatorio`);
            return false;
        }
    }

    return true;
}

//modificar los campos de una gestion

async function modificarGestion(idGestion, formulario){
    formulario.addEventListener('submit', async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        const formData = new FormData(formulario);
        const datosJSON = {};

        formData.forEach((value, key) => {
            datosJSON[key] = value
        });

        console.log(datosJSON);

        try {
            const response = await fetch(`/gestiones/modificar/${idGestion}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(datosJSON)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error desconocido');
            } else {
                alert('Gestión modificada exitosamente');
                window.location.href = '/gestiones';
            }
        } catch (error) {
            console.error('Error:', error.message);
            alert('Error al modificar la gestión: '+ error.message);
            return;
        }
    });
}

//cargar usuarios en la tabla de una gestion
async function loadUsuarios(nombre_tabla, id_gestion){
    try{
        const response = await fetch(`/detalles/get_usuarios/${id_gestion}`,{
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
                'Content-Type': 'aplication/json'
            }
        });
        
        if(!response.ok){
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error desconocido');
        }

        var anadir = document.getElementById("crear-usuario");
        var anadirGestor = document.getElementById("add-manager-gestion");

        anadir.addEventListener('click', async function() {
            const tokenValido = await validarToken();
            if(tokenValido){
                window.location.href = `/usuarios/creacion?id=${id_gestion}`;
            }else{
                alert('Necesitas iniciar sesión para acceder a esta sección.');
                window.location.href = '/login';
            }
        });

        anadirGestor.addEventListener('click', async function() {
            const tokenValido = await validarToken();
            if(tokenValido){
                window.location.href = `/addGestorGestión?id=${id_gestion}`;
            }else{
                alert('Necesitas iniciar sesión para acceder a esta sección.');
                window.location.href = '/login';
            }
        });

        const usuarios = await response.json();
        console.log(usuarios.length);
        if(usuarios.length<1){
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="5">No hay usuarios registrados</td>';
            nombre_tabla.appendChild(tr);
            return;
        }
        usuarios.forEach((usuario) =>{
            console.log(usuario);
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><input type="checkbox" class="user-checkbox"></td>
                <td>${usuario.id}</td>
                <td>${usuario.nombre_persona}</td>
                <td>${usuario.email}</td>
                <td>${usuario.nombre_empresa}</td>
            `;
            nombre_tabla.appendChild(tr);
        });
    }catch(error){
        console.error('Error:', error.message);
        alert('Error al cargar la tabla de usuarios: '+ error.message);
    }
}

//cargar empresas en la tabla de una gestion
async function addEmpresasSeleccionar(idGestion) {
    var selectEmpresa = document.getElementById('user_company');

    fetch(`/users/getEmpresas-usuarios/${idGestion}`)
        .then(response => response.json())
        .then(data => {
            // Verifica si la respuesta contiene empresas
            if (data.empresas && data.empresas.length > 0) {
                data.empresas.forEach(empresa => {
                    // Crea un nuevo elemento <option> para cada empresa
                    var option = document.createElement('option');
                    option.value = empresa.toLowerCase().replace(/\s+/g, '-'); // Opcional: Formatea el valor
                    option.textContent = empresa;
                    // Añade la opción al select
                    selectEmpresa.appendChild(option);
                });
            } else {
                // Si no hay empresas, puedes manejar el caso aquí
                var option = document.createElement('option');
                option.value = "";
                option.textContent = "No hay empresas disponibles";
                selectEmpresa.appendChild(option);
                selectEmpresa.disabled = true; // Opcional: Desactiva el select si no hay opciones
            }
        })
        .catch(error => {
            console.error('Error al obtener las empresas:', error);
            // Maneja el error, por ejemplo, mostrando un mensaje al usuario
            var option = document.createElement('option');
            option.value = "";
            option.textContent = "Error al cargar empresas";
            selectEmpresa.appendChild(option);
            selectEmpresa.disabled = true; // Opcional: Desactiva el select en caso de error
        });
}

async function addUsuario(id_gestion, usuario_form){
    usuario_form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(usuario_form);
        const datosJSON = {};

        formData.forEach((value, key) => {
            datosJSON[key] = value
        });

        console.log(datosJSON);
        try{
            const response = await fetch(`/users/crearUsuario/${id_gestion}`, {
                method: 'POST',
                headers: { 'Content-Type':'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(datosJSON)
            });
    
            if(!response.ok){
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error desconocido');
            }
            alert('Usuario creado exitosamente');
        }catch(error){
            console.error('Error:', error.message);
            alert('Error al crear el usuario: '+ error.message);
        }
        
    });
   
}

function searchUsers(tableRows){
    const searchIdInput = document.getElementById('search-id');
    const searchNameInput = document.getElementById('search-name');
    const searchCompanyInput = document.getElementById('search-company');

    // Resetear el display de las filas para mostrar todas
    const idQuery = searchIdInput.value.toLowerCase();
    const nameQuery = searchNameInput.value.toLowerCase();
    const companyQuery = searchCompanyInput.value.toLowerCase();

    tableRows.forEach(row => {
        const idCell = row.cells[1].textContent.toLowerCase();
        const nameCell = row.cells[2].textContent.toLowerCase();
        const companyCell = row.cells[4].textContent.toLowerCase();

        if (
            (idQuery && !idCell.includes(idQuery)) ||
            (nameQuery && !nameCell.includes(nameQuery)) ||
            (companyQuery && !companyCell.includes(companyQuery))
        ) {
            row.style.display = 'none';
        } else {
            row.style.display = '';
        }
    });
}

async function delUsers(){
    const checkedCheckboxes = document.querySelectorAll('.user-checkbox:checked');
    // Array de boxes con la obción checked , se eligen su elemento tr más cercano y el elemento id 
    const checkedRows = Array.from(checkedCheckboxes).map(checkbox => checkbox.closest('tr'));
    const ids = checkedRows.map(row => row.cells[1].textContent.toLowerCase())

    if (checkedRows.length > 0) {
        try{
            const response = await fetch('/users/eliminar', {
                method: 'POST',
                headers: { 'Content-Type':'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({ ids: ids})
            });
    
            if(!response.ok){
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error desconocido');
            }

            checkedRows.forEach(checkedCheckbox =>
                checkedCheckbox.closest('tr').remove()
            );

        }catch(error){
            console.error('Error:', error.message);
            alert('Error al eliminar los usuarios: '+ error.message);
        }
    } else {
        alert('Debes seleccionar el usuario');
    }
}

async function addGestorGestionExistente(nombreFormularioGestor, id_gestion) {
    nombreFormularioGestor.addEventListener('submit',async (e) => {
        e.preventDefault();
        const formData = new FormData(nombreFormularioGestor);
        const datosJSON = {};

        formData.forEach((value, key) => {
            datosJSON[key] = value
        });

        console.log(datosJSON);
        try{
            const response = await fetch(`/gestores/addGestorExistente/${id_gestion}`, {
                method: 'POST',
                headers: { 'Content-Type':'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(datosJSON)
            });
    
            if(!response.ok){
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error desconocido');
            }
            alert('Usuario creado exitosamente');
        }catch(error){
            console.error('Error:', error.message);
            alert('Error al crear el usuario: '+ error.message);
        }
        
    });
}

document.addEventListener('DOMContentLoaded', async() => {

    const formularioRegistro = document.getElementById('formularioRegistro');
    const formularioInicio = document.getElementById('formularioInicio');
    const accederCrearGestion = document.getElementById('crear-gestion');
    const crearGestion = document.getElementById('create-management-form');
    const gestiones = document.getElementById('gestiones-container');
    const cerrar = document.getElementById('finish');
    const modificar = document.getElementById('edit-gestion-form');
    const tabla_visualizar = document.getElementById('tabla-usuarios-info');
    const crearUsuario = document.getElementById('add-user-form');
    const addManager = document.getElementById('add-manager-form');
    
    //Elementos del menu desplegable 

    const menuToggle = document.querySelector('.menu-toggle');
    const body = document.body;

    const searchBtn = document.querySelector('.search-btn');
    const selectAllBtn = document.getElementById('select-all-btn');
    const deselectAllBtn = document.getElementById('deselect-all-btn');
    const deleteSelectedBtn = document.getElementById('delete-selected-btn');
    
    if (formularioRegistro) {
        enviarFormularioRegistro(formularioRegistro, '/gestores/registro');
    }

    if (formularioInicio) {
        enviarFormularioLogin(formularioInicio, '/gestores/login');
    }

    if (accederCrearGestion) {
        accederCrearGestion.addEventListener('click', async() => {
            const tokenValido = await validarToken();
            if(tokenValido){
                window.location.href = '/gestiones/nueva';
            }else{
                alert('Necesitas iniciar sesión para acceder a esta sección.');
                window.location.href = '/login';
            }
        });
    }

    if (crearGestion) {
        (async () => {
            const tokenValido = await validarToken(); // Espera a que validarToken se resuelva
            if (tokenValido) {
                enviarFormularioCrearGestion(crearGestion, '/gestiones/crear');  
            }
        })();    
    }

    if (gestiones) {
        console.log('Cargando gestiones...');
        (async () => {
            const tokenValido = await validarToken(); // Espera a que validarToken se resuelva
            if (tokenValido) {
                loadGestiones(gestiones);  // Carga las gestiones solo si el token es válido
            }
        })();
    }

    if(modificar) {
        (async () => {
            const tokenValido = await validarToken(); 
            if (tokenValido) {
                const urlParams = new URLSearchParams(window.location.search);
                const id = urlParams.get('id');
                console.log('Cargando gestión...', id);
                modificarGestion(id, modificar);
            }
        })();
    }

    if(cerrar) {
        cerrar.addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = '/login'; 
        });
    }

    if (tabla_visualizar){
        (async () => {
            const tokenValido = await validarToken(); // Espera a que validarToken se resuelva
            if (tokenValido) {
                const urlParams = new URLSearchParams(window.location.search);
                const id = urlParams.get('id');

                await loadUsuarios(tabla_visualizar, id);  // Carga los usuarios solo si el token es válido

                const tableRows = document.querySelectorAll('#tabla-usuarios tbody tr');

                searchBtn.addEventListener('click', () => searchUsers(tableRows)); // Carga una busqueda por id/empresa/nombre y pasar referencia a función
                
                if (deleteSelectedBtn) {
                    deleteSelectedBtn.addEventListener('click', () => delUsers()); // Eliminar los usuarios que estén seleccionados
                } else {
                    console.error("deleteSelectedBtn no encontrado");
                }

                if(selectAllBtn) { 
                    selectAllBtn.addEventListener('click', () => {
                        const checkboxes = document.querySelectorAll('.user-checkbox');
                        checkboxes.forEach(checkbox => checkbox.checked = true);
                    });
                }

                if(deselectAllBtn) { 
                    deselectAllBtn.addEventListener('click', () => {
                        const checkboxes = document.querySelectorAll('.user-checkbox');
                        checkboxes.forEach(checkbox => checkbox.checked = false);
                    });
                }
            }
        })();
    }

    if(crearUsuario){
        (async () => {
            const tokenValido = await validarToken(); 
            if (tokenValido) {
                const urlParams = new URLSearchParams(window.location.search);
                const id = urlParams.get('id');
                const vis = document.getElementById('visualizar')
                vis.addEventListener('click', () => {
                    window.location.href = `/gestiones/detalles?id=${id}`;
                }); 
                addEmpresasSeleccionar(id);
                addUsuario(id, crearUsuario);
            }
        })();
    }

    if(addManager){
        (async () => {
            const tokenValido = await validarToken(); // Espera a que validarToken se resuelva
            const urlParams = new URLSearchParams(window.location.search);
            const id = urlParams.get('id');
            const vis = document.getElementById('visualizar')
            vis.addEventListener('click', () => {
                window.location.href = `/gestiones/detalles?id=${id}`;
            }); 
            if (tokenValido) {
                 addGestorGestionExistente(addManager,id)
            }
        })();   
    }

    if(menuToggle){
        menuToggle.addEventListener('click', () => {
            body.classList.toggle('menu-open');
        });
    }

});


