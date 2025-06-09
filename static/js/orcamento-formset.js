document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    
    // Elementos principais
    const addButton = document.getElementById('add-item');
    const tbody = document.getElementById('itens-tbody');
    const totalFormsInput = document.getElementById('id_itens-TOTAL_FORMS');
    const maxFormsInput = document.getElementById('id_itens-MAX_NUM_FORMS');
    
    // Verificações de segurança
    if (!addButton || !tbody || !totalFormsInput) {
        console.error('Elementos essenciais do formset não encontrados');
        return;
    }
    
    // Variáveis de controle
    const maxForms = parseInt(maxFormsInput?.value || '1000');
    
    /**
     * Atualiza todos os índices do formset após adicionar/remover itens
     */
    function updateFormsetIndices() {
        const rows = tbody.querySelectorAll('.formset-row');
        let formIndex = 0;
        
        rows.forEach((row) => {
            // Pula linhas marcadas para exclusão
            const deleteInput = row.querySelector('input[name*="DELETE"]');
            if (deleteInput && deleteInput.checked) return;
            
            // Atualiza a linha principal
            row.querySelectorAll('input, select, textarea').forEach(element => {
                // Atualiza name
                if (element.name) {
                    element.name = element.name.replace(/itens-\d+-/, `itens-${formIndex}-`);
                }
                // Atualiza id
                if (element.id) {
                    element.id = element.id.replace(/id_itens-\d+-/, `id_itens-${formIndex}-`);
                }
            });
            
            // Atualiza labels da linha principal
            row.querySelectorAll('label').forEach(label => {
                if (label.htmlFor) {
                    label.htmlFor = label.htmlFor.replace(/id_itens-\d+-/, `id_itens-${formIndex}-`);
                }
            });
            
            // Atualiza a linha de campos específicos (próxima linha)
            const camposEspecificosRow = row.nextElementSibling;
            if (camposEspecificosRow && camposEspecificosRow.classList.contains('campos-especificos')) {
                camposEspecificosRow.querySelectorAll('input, select, textarea').forEach(element => {
                    if (element.name) {
                        element.name = element.name.replace(/itens-\d+-/, `itens-${formIndex}-`);
                    }
                    if (element.id) {
                        element.id = element.id.replace(/id_itens-\d+-/, `id_itens-${formIndex}-`);
                    }
                });
                
                camposEspecificosRow.querySelectorAll('label').forEach(label => {
                    if (label.htmlFor) {
                        label.htmlFor = label.htmlFor.replace(/id_itens-\d+-/, `id_itens-${formIndex}-`);
                    }
                });
            }
            
            formIndex++;
        });
        
        // Atualiza o total de formulários (conta apenas linhas principais não deletadas)
        totalFormsInput.value = formIndex;
    }
    
    /**
     * Atualiza visibilidade dos botões de remover
     */
    function updateRemoveButtons() {
        const rows = tbody.querySelectorAll('.formset-row');
        const showRemove = rows.length > 1;
        
        rows.forEach(row => {
            const removeBtn = row.querySelector('.remove-item');
            if (removeBtn) {
                removeBtn.style.display = showRemove ? 'inline-block' : 'none';
            }
        });
    }
    
    /**
     * Mostra/oculta campos específicos baseado no tipo selecionado
     */
    function toggleSpecificFields(row) {
        const tipoSelect = row.querySelector('select[name*="tipo"]');
        if (!tipoSelect) return;
        
        // Campos específicos estão na próxima linha (tr)
        const camposEspecificosRow = row.nextElementSibling;
        if (!camposEspecificosRow || !camposEspecificosRow.classList.contains('campos-especificos')) return;
        
        const tipo = tipoSelect.value;
        const camposMaterial = camposEspecificosRow.querySelector('.campos-material');
        const camposServico = camposEspecificosRow.querySelector('.campos-servico');
        
        if (tipo === 'MAT') {
            camposEspecificosRow.style.display = 'table-row';
            if (camposMaterial) camposMaterial.style.display = 'block';
            if (camposServico) camposServico.style.display = 'none';
        } else if (tipo === 'SRV') {
            camposEspecificosRow.style.display = 'table-row';
            if (camposMaterial) camposMaterial.style.display = 'none';
            if (camposServico) camposServico.style.display = 'block';
        } else {
            camposEspecificosRow.style.display = 'none';
        }
        
        updateSubtotal(row);
    }
    
    /**
     * Calcula o subtotal de uma linha
     */
    function updateSubtotal(row) {
        const quantidade = parseFloat(row.querySelector('input[name*="quantidade"]')?.value) || 0;
        const valorUnitario = parseFloat(row.querySelector('input[name*="valor_unitario"]')?.value) || 0;
        const subtotalCell = row.querySelector('.subtotal');
        
        if (subtotalCell) {
            const subtotal = quantidade * valorUnitario;
            subtotalCell.textContent = `R$ ${subtotal.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}`;
        }
        
        updateTotal();
    }
    
    /**
     * Calcula o total geral
     */
    function updateTotal() {
        let total = 0;
        
        tbody.querySelectorAll('.formset-row').forEach(row => {
            // Ignora linhas marcadas para exclusão
            const deleteCheckbox = row.querySelector('input[name*="DELETE"]');
            if (deleteCheckbox?.checked) return;
            
            const subtotalText = row.querySelector('.subtotal')?.textContent || 'R$ 0,00';
            const subtotal = parseFloat(
                subtotalText.replace('R$', '').replace(/\./g, '').replace(',', '.')
            ) || 0;
            
            total += subtotal;
        });
        
        const totalElement = document.getElementById('total-geral');
        if (totalElement) {
            totalElement.textContent = `R$ ${total.toLocaleString('pt-BR', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}`;
        }
    }
    
    /**
     * Adiciona uma nova linha de item
     */
    function addItem() {
        const currentForms = parseInt(totalFormsInput.value);
        
        if (currentForms >= maxForms) {
            alert('Número máximo de itens atingido.');
            return;
        }
        
        // Encontra a primeira linha para clonar
        const templateRow = tbody.querySelector('.formset-row');
        if (!templateRow) {
            console.error('Nenhuma linha modelo encontrada');
            return;
        }
        
        // Clona a linha principal
        const newRow = templateRow.cloneNode(true);
        
        // Clona a linha de campos específicos
        const templateSpecificRow = templateRow.nextElementSibling;
        let newSpecificRow = null;
        if (templateSpecificRow && templateSpecificRow.classList.contains('campos-especificos')) {
            newSpecificRow = templateSpecificRow.cloneNode(true);
        }
        
        // Limpa os valores da linha principal
        newRow.querySelectorAll('input, select, textarea').forEach(element => {
            if (element.type === 'checkbox' || element.type === 'radio') {
                element.checked = false;
            } else {
                element.value = '';
            }
            
            // Remove classes de erro
            element.classList.remove('is-invalid');
        });
        
        // Limpa os valores da linha de campos específicos
        if (newSpecificRow) {
            newSpecificRow.querySelectorAll('input, select, textarea').forEach(element => {
                if (element.type === 'checkbox' || element.type === 'radio') {
                    element.checked = false;
                } else {
                    element.value = '';
                }
                element.classList.remove('is-invalid');
            });
            
            // Oculta a linha de campos específicos
            newSpecificRow.style.display = 'none';
            newSpecificRow.querySelector('.campos-material').style.display = 'none';
            newSpecificRow.querySelector('.campos-servico').style.display = 'none';
        }
        
        // Remove mensagens de erro
        newRow.querySelectorAll('.text-danger').forEach(error => error.remove());
        if (newSpecificRow) {
            newSpecificRow.querySelectorAll('.text-danger').forEach(error => error.remove());
        }
        
        // Reset subtotal
        const subtotalCell = newRow.querySelector('.subtotal');
        if (subtotalCell) {
            subtotalCell.textContent = 'R$ 0,00';
        }
        
        // Adiciona as novas linhas
        tbody.appendChild(newRow);
        if (newSpecificRow) {
            tbody.appendChild(newSpecificRow);
        }
        
        // Atualiza todos os índices
        updateFormsetIndices();
        updateRemoveButtons();
        
        // Foca no primeiro campo da nova linha
        const firstInput = newRow.querySelector('input, select');
        if (firstInput) {
            firstInput.focus();
        }
    }
    
    /**
     * Remove uma linha de item
     */
    function removeItem(button) {
        const row = button.closest('.formset-row');
        const deleteInput = row.querySelector('input[name*="DELETE"]');
        const camposEspecificosRow = row.nextElementSibling;
        
        if (deleteInput) {
            // Se existe campo DELETE, apenas marca para exclusão
            deleteInput.checked = true;
            row.style.display = 'none';
            
            // Oculta também a linha de campos específicos
            if (camposEspecificosRow && camposEspecificosRow.classList.contains('campos-especificos')) {
                camposEspecificosRow.style.display = 'none';
            }
        } else {
            // Remove fisicamente as linhas
            if (camposEspecificosRow && camposEspecificosRow.classList.contains('campos-especificos')) {
                camposEspecificosRow.remove();
            }
            row.remove();
        }
        
        updateFormsetIndices();
        updateRemoveButtons();
        updateTotal();
    }
    
    // Event Listeners
    
    // Botão adicionar
    addButton.addEventListener('click', function(e) {
        e.preventDefault();
        addItem();
    });
    
    // Delegação de eventos para o tbody
    tbody.addEventListener('click', function(e) {
        // Botão remover
        if (e.target.classList.contains('remove-item') || e.target.closest('.remove-item')) {
            e.preventDefault();
            const button = e.target.classList.contains('remove-item') ? 
                           e.target : e.target.closest('.remove-item');
            removeItem(button);
        }
    });
    
    tbody.addEventListener('change', function(e) {
        const target = e.target;
        const row = target.closest('.formset-row');
        
        if (!row) return;
        
        // Mudança no tipo
        if (target.name && target.name.includes('tipo')) {
            toggleSpecificFields(row);
        }
        
        // Mudança em quantidade ou valor
        if (target.name && (target.name.includes('quantidade') || 
                           target.name.includes('valor_unitario'))) {
            updateSubtotal(row);
        }
    });
    
    tbody.addEventListener('input', function(e) {
        const target = e.target;
        const row = target.closest('.formset-row');
        
        if (!row) return;
        
        // Atualização em tempo real para quantidade e valor
        if (target.name && (target.name.includes('quantidade') || 
                           target.name.includes('valor_unitario'))) {
            updateSubtotal(row);
        }
    });
    
    // Inicialização
    tbody.querySelectorAll('.formset-row').forEach(row => {
        toggleSpecificFields(row);
        updateSubtotal(row);
    });
    
    updateRemoveButtons();
    updateTotal();
    
    console.log('Formset de orçamento inicializado com sucesso');
}); 