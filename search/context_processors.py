# search/context_processors.py
from .models import State

def states_list(request):
    """
    Deixa 'states' e 'selected_state' disponíveis em todos os templates.
    - 'selected_state' vem da querystring (?state=XX) ou assume 'CE'.
    """
    return {
        "states": State.objects.all(),
        "selected_state": request.GET.get("state", "CE").upper()
    }
