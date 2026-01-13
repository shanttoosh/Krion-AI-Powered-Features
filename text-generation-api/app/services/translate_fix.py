from app.models.phi_model import get_phi_model


def fix_translation(english_text: str) -> str:
    """
    Whisper already translated → Phi only polishes
    """

    # Short text = no rewrite
    if not english_text or len(english_text.split()) < 3:
        return english_text

    phi = get_phi_model()
    return phi.rewrite(english_text)
