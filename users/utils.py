import re
from django.core.exceptions import ValidationError

def validate_cpf(cpf: str) -> str:
    """
    Valida um CPF e devolve somente os 11 dígitos se for válido.
    Lança ValidationError em caso de erro.
    """

    # Mantém só os dígitos
    cpf_num = re.sub(r'\D', '', cpf)

    if len(cpf_num) != 11:
        raise ValidationError("CPF deve ter 11 dígitos.")

    # Rejeita sequências repetidas (000… / 111… etc.)
    if cpf_num == cpf_num[0] * 11:
        raise ValidationError("CPF inválido (sequência repetida).")

    digitos = list(map(int, cpf_num))

    # ---------- primeiro dígito verificador ----------
    soma_1 = sum(d * p for d, p in zip(digitos[:9], range(10, 1, -1)))   # pesos 10..2
    resto_1 = (soma_1 * 10) % 11
    dv1 = 0 if resto_1 == 10 else resto_1
    if dv1 != digitos[9]:
        raise ValidationError("CPF inválido (1º dígito verificador).")

    # ---------- segundo dígito verificador ----------
    soma_2 = sum(d * p for d, p in zip(digitos[:10], range(11, 1, -1)))  # pesos 11..2
    resto_2 = (soma_2 * 10) % 11
    dv2 = 0 if resto_2 == 10 else resto_2
    if dv2 != digitos[10]:
        raise ValidationError("CPF inválido (2º dígito verificador).")

    # Se chegou aqui, CPF é válido
    return cpf_num