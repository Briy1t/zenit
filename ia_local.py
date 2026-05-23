from transformers import pipeline

# Cargamos un modelo local de análisis de sentimiento
clasificador = pipeline("sentiment-analysis")

def clasificar_texto_local(texto):
    """
    Clasifica un texto en un rango 0–10 según su carga emocional.
    NEGATIVE → valores bajos
    POSITIVE → valores altos
    """
    if not texto or texto.strip() == "":
        return 5  # neutro si está vacío

    resultado = clasificador(texto)[0]
    label = resultado["label"]
    score = resultado["score"]

    # Convertimos a escala 0–10
    if label == "NEGATIVE":
        return int((1 - score) * 5)  # 0–5
    else:
        return int(5 + score * 5)    # 5–10
