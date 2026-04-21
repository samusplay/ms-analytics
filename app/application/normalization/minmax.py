# application/normalization/minmax.py
class MinMaxNormalizer:

    def normalize(self, values):
        min_v = min(values)
        max_v = max(values)

        if max_v == min_v:
            return [0 for _ in values]

        return [(v - min_v) / (max_v - min_v) for v in values]