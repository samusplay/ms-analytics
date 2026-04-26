# tests/test_math_engine.py
import pytest
from app.core.math_engine import MathEngine
from app.application.calculator import WeightedScoringCalculator
from app.core.validators import ScoringValidators


class TestMathEngine:
    """Pruebas del motor matemático"""
    
    def test_min_max_normalize(self):
        """Prueba normalización Min-Max"""
        values = [10, 20, 30, 40, 50]
        normalized = MathEngine.min_max_normalize(values)
        
        assert normalized[0] == 0.0
        assert normalized[4] == 1.0
        assert all(0 <= v <= 1 for v in normalized)
    
    def test_normalize_single_value(self):
        """Prueba normalización de un solo valor"""
        values = [25]
        normalized = MathEngine.min_max_normalize(values)
        
        assert normalized[0] == 0.5
    
    def test_calculate_weighted_score(self):
        """Prueba cálculo de score ponderado"""
        score = MathEngine.calculate_weighted_score(
            poblacion_norm=0.8,
            ingreso_norm=0.6,
            educacion_norm=0.9,
            competencia_norm=0.2,
            w_pob=0.35,
            w_ing=0.35,
            w_edu=0.20,
            w_comp=0.10
        )
        
        expected = (0.35*0.8) + (0.35*0.6) + (0.20*0.9) - (0.10*0.2)
        assert score == round(expected, 3)
    
    def test_score_clamping(self):
        """Prueba que el score se clampee a [0, 1]"""
        # Score negativo
        score_neg = MathEngine.calculate_weighted_score(
            poblacion_norm=0, ingreso_norm=0, educacion_norm=0,
            competencia_norm=1, w_pob=0.35, w_ing=0.35, w_edu=0.20, w_comp=0.1
        )
        assert score_neg >= 0
        
        # Score > 1
        score_pos = MathEngine.calculate_weighted_score(
            poblacion_norm=1, ingreso_norm=1, educacion_norm=1,
            competencia_norm=0, w_pob=1, w_ing=1, w_edu=1, w_comp=0
        )
        assert score_pos <= 1
    
    def test_calculate_ranking(self):
        """Prueba cálculo de ranking"""
        scores = [('A', 0.9), ('B', 0.7), ('C', 0.5)]
        rankings = MathEngine.calculate_ranking(scores)
        
        assert rankings[0][1] == 1  # A primero
        assert rankings[1][1] == 2  # B segundo
        assert rankings[2][1] == 3  # C tercero
    
    def test_calculate_statistics(self):
        """Prueba cálculo de estadísticas"""
        scores = [0.9, 0.7, 0.5, 0.3, 0.1]
        stats = MathEngine.calculate_statistics(scores)
        
        assert stats['min'] == 0.1
        assert stats['max'] == 0.9
        assert stats['mean'] == 0.5
        assert stats['range'] == 0.8


class TestScoringValidators:
    """Pruebas de validadores"""
    
    def test_validate_normalization(self):
        """Prueba validación de normalización"""
        valid_values = {'poblacion': 0.5, 'ingreso': 0.7}
        is_valid, errors = ScoringValidators.validate_normalization_range(valid_values)
        assert is_valid is True
        
        invalid_values = {'poblacion': 1.5, 'ingreso': -0.1}
        is_valid, errors = ScoringValidators.validate_normalization_range(invalid_values)
        assert is_valid is False
        assert len(errors) == 2
    
    def test_has_penalization(self):
        """Prueba detección de penalización"""
        weights_with_penalty = {'competencia': 0.1, 'poblacion': 0.35}
        assert ScoringValidators.has_penalization(weights_with_penalty) is True
        
        weights_without_penalty = {'poblacion': 0.35, 'ingreso': 0.35}
        assert ScoringValidators.has_penalization(weights_without_penalty) is False
    
    def test_validate_math_rules(self):
        """Prueba validación de reglas de negocio"""
        valid_weights = {
            'poblacion': 0.35,
            'ingreso': 0.35,
            'educacion': 0.20,
            'competencia': 0.10
        }
        is_valid, errors = ScoringValidators.validate_math_rules(valid_weights)
        assert is_valid is True
        
        invalid_weights = {
            'poblacion': 0.35,
            'ingreso': 0.35,
            'educacion': 0.20
            # Falta competencia
        }
        is_valid, errors = ScoringValidators.validate_math_rules(invalid_weights)
        assert is_valid is False


class TestWeightedScoringCalculator:
    """Pruebas de la calculadora"""
    
    def setup_method(self):
        self.calculator = WeightedScoringCalculator()
        self.weights = {
            'poblacion': 0.35,
            'ingreso': 0.35,
            'educacion': 0.20,
            'competencia': 0.10
        }
    
    def test_calculate_score_normal(self):
        """Prueba cálculo normal"""
        score = self.calculator.calculate_score(
            poblacion_norm=0.8,
            ingreso_norm=0.6,
            educacion_norm=0.9,
            competencia_norm=0.2,
            weights=self.weights
        )
        
        expected = (0.35*0.8 + 0.35*0.6 + 0.20*0.9 - 0.10*0.2)
        assert score == round(expected, 3)
    
    def test_calculate_score_penalty_only(self):
        """Prueba con solo penalización"""
        score = self.calculator.calculate_score(
            poblacion_norm=0,
            ingreso_norm=0,
            educacion_norm=0,
            competencia_norm=1,
            weights=self.weights
        )
        assert score == 0  # No puede ser negativo
    
    def test_validate_normalized_values(self):
        """Prueba validación de valores normalizados"""
        valid_values = {'poblacion': 0.5, 'ingreso': 0.7}
        assert self.calculator.validate_normalized_values(valid_values) is True
        
        invalid_values = {'poblacion': 1.5, 'ingreso': -0.1}
        with pytest.raises(ValueError):
            self.calculator.validate_normalized_values(invalid_values)
    
    def test_batch_calculation(self):
        """Prueba cálculo batch"""
        normalized_data = [
            {'zone_code': 'A', 'poblacion_norm': 0.9, 'ingreso_norm': 0.8,
             'educacion_norm': 0.7, 'competencia_norm': 0.1},
            {'zone_code': 'B', 'poblacion_norm': 0.3, 'ingreso_norm': 0.4,
             'educacion_norm': 0.5, 'competencia_norm': 0.6}
        ]
        
        results = self.calculator.calculate_batch_scores(normalized_data, self.weights)
        
        assert len(results) == 2
        assert results[0]['zone_code'] == 'A'
        assert results[1]['zone_code'] == 'B'
        assert 0 <= results[0]['score_value'] <= 1
        assert 0 <= results[1]['score_value'] <= 1


if __name__ == "__main__":
    pytest.main([__file__, '-v'])