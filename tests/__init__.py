import os
import sys

# permite importar los módulos de src/ al correr los tests con unittest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
