"""SymPerturb reference implementation.

This package implements model-based virtual perturbation for cross-sectional
Gaussian symptom networks. It generates target hypotheses; it does not identify
causal treatment effects.
"""

from .analysis import SymPerturbAnalyzer, run_analysis
from .network import fit_gaussian_network
from .state import post_intervention_moments

__all__ = [
    "SymPerturbAnalyzer",
    "run_analysis",
    "fit_gaussian_network",
    "post_intervention_moments",
]

__version__ = "0.1.0"
