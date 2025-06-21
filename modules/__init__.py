"""
XAU/USD Scalping Bot V3 - Modules Package
Contains all the enhanced v3 modules for multi-timeframe filtering,
cooldown management, signal evaluation, volatility filtering, and pause management.
"""

from .mtf_filter import mtf_filter, MultiTimeframeFilter
from .cooldown_manager import cooldown_manager, CooldownManager
from .signal_evaluator import signal_evaluator, SignalEvaluator
from .volatility_filter import volatility_filter, VolatilityFilter
from .pause_manager import pause_manager, PauseManager

__all__ = [
    'mtf_filter',
    'MultiTimeframeFilter',
    'cooldown_manager', 
    'CooldownManager',
    'signal_evaluator',
    'SignalEvaluator',
    'volatility_filter',
    'VolatilityFilter',
    'pause_manager',
    'PauseManager'
] 