"""Serviços de domínio do app practice — temporização e classificação Morse.

O backend nunca confia nos tempos informados pelo cliente: cada duração de
pressionamento é validada contra um limite calculado dinamicamente a partir
do ``speed_wpm`` vigente nas configurações do usuário, e a classificação
ponto/traço é refeita no servidor.
"""

# Fórmula padrão (palavra de referência "PARIS"): a duração de um ponto em
# milissegundos é 1200 / WPM. O traço vale 3 unidades de ponto.
DOT_REFERENCE_MS = 1200
DASH_UNITS = 3

# Um pressionamento é classificado como traço a partir de 2 unidades de
# ponto (meio caminho entre ponto = 1 e traço = 3).
DASH_THRESHOLD_UNITS = 2

# Folga aceita sobre a duração nominal do traço antes de rejeitar a duração
# como incompatível com a velocidade configurada.
DURATION_TOLERANCE = 2.0


def dot_duration_ms(speed_wpm: int) -> float:
    """Duração nominal do ponto (ms) para a velocidade configurada."""
    return DOT_REFERENCE_MS / speed_wpm


def allowed_press_limit_ms(speed_wpm: int) -> float:
    """Limite máximo aceito para a duração de um pressionamento (ms).

    Corresponde à duração nominal do traço acrescida da tolerância; acima
    disso a duração é incompatível com o ``speed_wpm`` do usuário.
    """
    return DASH_UNITS * dot_duration_ms(speed_wpm) * DURATION_TOLERANCE


def classify_press(duration_ms: float, speed_wpm: int) -> str:
    """Classifica um pressionamento como ponto (``.``) ou traço (``-``)."""
    if duration_ms < DASH_THRESHOLD_UNITS * dot_duration_ms(speed_wpm):
        return "."
    return "-"


def code_from_press_durations(durations_ms: list[float], speed_wpm: int) -> str:
    """Forma o código Morse a partir das durações de pressionamento."""
    return "".join(classify_press(duration, speed_wpm) for duration in durations_ms)
