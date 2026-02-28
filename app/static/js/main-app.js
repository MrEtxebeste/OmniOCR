/**
 * Lógica Global de OmniOCR
 */

let editando = false;

// Alternar entre modo lectura y modo edición
function toggleEdicion() {
    editando = !editando;
    const btn = document.getElementById('btnModoEdicion');
    const btnGuardar = document.getElementById('btnGuardar');
    const form = document.getElementById('formDocumento');
    const inputs = document.querySelectorAll('.clsField');
    const cells = document.querySelectorAll('[contenteditable]');

    if (editando) {
        btn.innerHTML = '<i class="fa-solid fa-xmark"></i> Cancelar Edición';
        btn.classList.replace('btn-primary', 'btn-danger');
        btnGuardar.classList.remove('d-none');
        form.classList.add('edit-mode-active');
        
        inputs.forEach(i => i.removeAttribute('readonly'));
        cells.forEach(c => c.setAttribute('contenteditable', 'true'));
    } else {
        window.location.reload(); 
    }
}

// Recalcular totales al editar
document.addEventListener('input', function(e) {
    if (!editando) return;

    const target = e.target;
    if (target.classList.contains('clsUnid') || target.classList.contains('clsPrec')) {
        const tr = target.closest('.clsLine');
        const unid = parseFloat(tr.querySelector('.clsUnid').innerText) || 0;
        const prec = parseFloat(tr.querySelector('.clsPrec').innerText) || 0;
        const totalLine = (unid * prec).toFixed(2);
        
        tr.querySelector('.clsTotal').innerText = totalLine;
        recalcularTotalesCabecera();
    }
});

function recalcularTotalesCabecera() {
    let subtotal = 0;
    document.querySelectorAll('.clsTotal').forEach(td => {
        subtotal += parseFloat(td.innerText) || 0;
    });
    
    document.getElementById('importebruto').value = subtotal.toFixed(2);
    // Asumimos un IVA simple del 21% para el ejemplo, o podrías leerlo de un campo
    const iva = subtotal * 0.21;
    document.getElementById('importeiva').value = iva.toFixed(2);
    document.getElementById('importeneto').value = (subtotal + iva).toFixed(2);
}

// Enviar datos al servidor
async function guardarCambios(docId) {
    const data = {
        emisor: document.getElementById('emisor').value,
        cifemisor: document.getElementById('cifemisor').value,
        fechadocumento: document.getElementById('fechadocumento').value,
        importebruto: parseFloat(document.getElementById('importebruto').value),
        importeiva: parseFloat(document.getElementById('importeiva').value),
        importeneto: parseFloat(document.getElementById('importeneto').value),
        lines: []
    };

    document.querySelectorAll('.clsLine').forEach((tr, index) => {
        data.lines.push({
            numlinea: index + 1,
            referencia: tr.querySelector('.clsRef').innerText,
            descripcion: tr.querySelector('.clsDesc').innerText,
            unidades: parseFloat(tr.querySelector('.clsUnid').innerText),
            preciounitario: parseFloat(tr.querySelector('.clsPrec').innerText),
            preciototal: parseFloat(tr.querySelector('.clsTotal').innerText)
        });
    });

    try {
        const response = await fetch(`/document/update/${docId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (result.result === 1) {
            alert("¡Guardado correctamente!");
            window.location.reload();
        } else {
            alert("Error: " + result.error);
        }
    } catch (err) {
        alert("Fallo en la conexión con el servidor");
    }
}

async function validarContraERP(docId) {
    const btn = document.getElementById('btnValidarERP');
    const originalHTML = btn.innerHTML;
    
    // 1. Estado de carga
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Consultando ERP...';

    // 2. Recolectamos los datos actuales de la pantalla (como en guardarCambios)
    const currentData = {
        cifemisor: document.getElementById('cifemisor').value,
        lines: []
    };
    document.querySelectorAll('.clsLine').forEach(tr => {
        currentData.lines.push({
            referencia: tr.querySelector('.clsRef').innerText,
            preciounitario: parseFloat(tr.querySelector('.clsPrec').innerText)
        });
    });

    try {
        const response = await fetch(`/document/validate-erp/${docId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentData)
        });

        const result = await response.json();
        
        // 3. Procesar resultados del ERP
        if (result.success) {
            alert("✅ Verificación exitosa: El proveedor y todos los artículos existen en el ERP.");
        } else {
            // Aquí podrías incluso resaltar en rojo las líneas que fallan
            let msg = "❌ Errores encontrados en el ERP:\n";
            result.errors.forEach(err => msg += `- ${err}\n`);
            alert(msg);
        }
    } catch (error) {
        alert("Error de conexión con el servicio de validación.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
}