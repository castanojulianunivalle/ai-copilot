"""Las pruebas de la evaluacion importan los modulos de evaluation/ y el paquete ai/ de la API."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "evaluation"))
sys.path.insert(0, str(RAIZ / "python-api"))
