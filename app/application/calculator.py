from decimal import Decimal
from typing import Dict


#Servicio Para crear logica Matematica del Scoring
class WeightedScoringCalculator:
    """
    CA2: Aplica fórmula ponderada con penalización.
    Fórmula: Score = (w_poblacion * pob) + (w_ingresos * ing) - (w_competencia * comp)

    SRP: Solo calcula scores, no persiste ni consulta nada.
    """

    POSITIVE_VARS = ["peso_poblacion", "peso_ingresos"]
    PENALTY_VARS = ["peso_competencia"]

    def __init__(self, decimal_places: int = 3):
        self.decimal_places = decimal_places

    def calculate(
        self,
        normalized_values: Dict[str, float],
        weights: Dict[str, float],
    ) -> float:
        """
        normalized_values: valores ya normalizados [0,1] por zona
        weights: pesos activos desde ms-configuration
        """

        # CA2: validar que todos los valores estén normalizados
        for var, value in normalized_values.items():
            if not (0 <= value <= 1):
                raise ValueError(
                    f"Variable '{var}' fuera de rango: {value}. "
                    f"Debe estar normalizada entre 0 y 1."
                )

        # Suma de términos positivos
        positive_sum = Decimal("0")
        for var in self.POSITIVE_VARS:
            norm_key = var.replace("peso_", "")  # peso_poblacion → poblacion
            if norm_key in normalized_values and var in weights:
                positive_sum += (
                    Decimal(str(weights[var])) *
                    Decimal(str(normalized_values[norm_key]))
                )

        # CA2: penalización (resta)
        penalty = Decimal("0")
        for var in self.PENALTY_VARS:
            norm_key = var.replace("peso_", "")  # peso_competencia → competencia
            if norm_key in normalized_values and var in weights:
                penalty += (
                    Decimal(str(weights[var])) *
                    Decimal(str(normalized_values[norm_key]))
                )

        score = float(positive_sum - penalty)

        # Clampear al rango [0, 1]
        return round(max(0.0, min(1.0, score)), self.decimal_places)