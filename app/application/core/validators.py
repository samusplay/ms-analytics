# app/core/validators.py
from typing import Dict, List, Tuple


class ScoringValidators:
    """Validadores para las reglas de negocio del scoring"""
    
    @staticmethod
    def validate_normalization_range(values: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Valida que todos los valores estén en rango [0, 1]
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        for var_name, value in values.items():
            if value < 0 or value > 1:
                errors.append(
                    f"Variable '{var_name}' tiene valor {value} fuera del rango [0, 1]"
                )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_weights(weights: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Valida que los pesos sean válidos
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        required_vars = ['poblacion', 'ingreso', 'educacion', 'competencia']
        
        # Verificar que existen todas las variables
        for var in required_vars:
            if var not in weights:
                errors.append(f"Peso requerido '{var}' no encontrado")
        
        # Verificar que los pesos sean positivos
        for var, weight in weights.items():
            if weight < 0:
                errors.append(f"Peso '{var}' es negativo: {weight}")
            if weight > 1:
                errors.append(f"Peso '{var}' excede 1: {weight}")
        
        # Verificar que la suma de positivos no exceda 1 (opcional)
        positive_sum = sum(weights.get(v, 0) for v in required_vars[:3])
        if positive_sum > 1:
            errors.append(f"Suma de pesos positivos ({positive_sum}) excede 1")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def has_penalization(weights: Dict[str, float]) -> bool:
        """
        Verifica que exista al menos una variable de penalización
        
        Regla de negocio: Debe aplicar al menos una variable de penalización (resta)
        """
        penalization_vars = ['competencia']
        
        for var in penalization_vars:
            if var in weights and weights[var] > 0:
                return True
        
        return False
    
    @staticmethod
    def validate_math_rules(weights: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Valida todas las reglas matemáticas de negocio
        
        Reglas:
        1. Todas las variables normalizadas
        2. Al menos una penalización
        3. Pesos válidos
        """
        errors = []
        
        # Regla: Al menos una penalización
        if not ScoringValidators.has_penalization(weights):
            errors.append("No se encontró variable de penalización (competencia)")
        
        return len(errors) == 0, errors