"""flipbudget -- scorer-induced partial identification of benchmark comparisons.

The headline function is `corrected_interval`: given someone's benchmark
records and measured scorer-error margins, it returns the identification-
corrected interval for a model's accuracy or for a pairwise comparison --
not just a report of the margins themselves. Correcting someone else's
number is the adoption path; emitting a descriptive card is secondary.
"""
from .identification import g, single_model_extrema, comparison_extrema, flip_budget
from .inference import corrected_interval, paired_bootstrap_delta

__all__ = [
    "g",
    "single_model_extrema",
    "comparison_extrema",
    "flip_budget",
    "corrected_interval",
    "paired_bootstrap_delta",
]

__version__ = "0.1.0"
