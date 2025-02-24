from django import template

register = template.Library()

@register.filter
def mask_cpf(cpf):
    """Aplica a máscara XXX.XXX.XXX-XX em um valor numérico de 11 dígitos."""
    if cpf and len(cpf) == 11 and cpf.isdigit():
        return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
    return cpf

@register.filter
def mask_cep(cep):
    if cep and len(cep) == 8 and cep.isdigit():
        return f"{cep[:5]}-{cep[5:]}"
    return cep

@register.filter
def mask_cnpj(cnpj):
    if cnpj and len(cnpj) == 14 and cnpj.isdigit():
        return f"{cnpj[0:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
    return cnpj

@register.filter
def mask_phone(phone):
    """
    Exemplo simples para DDD (2 dígitos) + número (9 dígitos).
    """
    if phone and len(phone) == 11 and phone.isdigit():
        return f"({phone[0:2]}) {phone[2:7]}-{phone[7:11]}"
    return phone


