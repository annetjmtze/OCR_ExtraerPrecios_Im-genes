import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.normalizer import MedicamentoNormalizer

def test_model_string():
    """Verifica que el modelo de Claude sea el correcto."""
    normalizer = MedicamentoNormalizer()
    # Inspeccionamos el método normalizar para extraer el modelo
    import inspect
    source = inspect.getsource(normalizer.normalizar)
    assert 'model="claude-haiku-4-5"' in source, \
        "El modelo debe ser 'claude-haiku-4-5'"
    print("✅ Model string correcto")

if __name__ == "__main__":
    test_model_string()