import re
from django.core.exceptions import ValidationError

def validate_cpf(value):
    """
    Recebe uma string 'value' e faz validação de CPF:
      - Remove pontuação
      - Verifica 11 dígitos
      - Evita sequências repetidas
      - Verifica dígitos verificadores (módulo 11)
    Retorna o CPF só com dígitos caso seja válido.
    Levanta ValidationError se for inválido.
    """
    # 1) Remover caracteres que não sejam dígitos
    cpf_numeros = re.sub(r'[^0-9]', '', value or '')

    # 2) Verificar se tem 11 dígitos
    if len(cpf_numeros) != 11:
        raise ValidationError("CPF deve ter 11 dígitos.")

    # 3) Evitar sequências repetidas (ex. 11111111111, 22222222222 etc.)
    if cpf_numeros == cpf_numeros[0] * 11:
        raise ValidationError("CPF inválido (sequência repetida).")

    # 4) Verificar dígitos verificadores pelo cálculo do CPF
    #    - Primeiro dígito verificador
    #    - Segundo dígito verificador
    cpf_ints = list(map(int, cpf_numeros))

    # ---------- primeiro dígito verificador ----------
    soma_1 = 0
    for i, peso in enumerate(range(10, 1, -1)):  # 10..2
        soma_1 += cpf_ints[i] * peso
    resto_1 = (soma_1 * 10) % 11
    digito_1 = 0 if resto_1 == 10 else resto_1
    if digito_1 != cpf_ints[9]:
        raise ValidationError("CPF inválido (dígito verificador).")

    # ---------- segundo dígito verificador ----------
    soma_2 = 0
    for i, peso in enumerate(range(11, 2, -1)):  # 11..3
        soma_2 += cpf_ints[i] * peso
    resto_2 = (soma_2 * 10) % 11
    digito_2 = 0 if resto_2 == 10 else resto_2
    if digito_2 != cpf_ints[10]:
        raise ValidationError("CPF inválido (dígito verificador).")

    # Se chegou aqui, CPF é válido. Retorne somente dígitos (sem pontuação).
    return cpf_numeros