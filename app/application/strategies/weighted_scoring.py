# application/strategies/weighted_scoring.py

class WeightedScoringStrategy:

    def __init__(self, normalizer):
        self.normalizer = normalizer

    def calculate(self, zones, config):

        population = [z.population for z in zones]
        income = [z.income for z in zones]
        education = [z.education for z in zones]
        competition = [z.competition for z in zones]

        pop_n = self.normalizer.normalize(population)
        inc_n = self.normalizer.normalize(income)
        edu_n = self.normalizer.normalize(education)
        comp_n = self.normalizer.normalize(competition)

        results = []

        for i, z in enumerate(zones):
            score = (
                config["population_weight"] * pop_n[i] +
                config["income_weight"] * inc_n[i] +
                config["education_weight"] * edu_n[i] -
                config["competition_weight"] * comp_n[i]  # penalización
            )

            results.append({
                "zone_code": z.code,
                "score": score,
                "trace": {
                    "population_norm": pop_n[i],
                    "income_norm": inc_n[i],
                    "education_norm": edu_n[i],
                    "competition_norm": comp_n[i]
                }
            })

        return results