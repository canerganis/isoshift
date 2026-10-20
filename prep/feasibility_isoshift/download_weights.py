"""Pre-download all default model weights."""
from isoshift.calculators import DEFAULT_MODELS, calculator_info, get_calculator

for n in DEFAULT_MODELS:
    c = get_calculator(n, "cpu")
    print(calculator_info(c))
