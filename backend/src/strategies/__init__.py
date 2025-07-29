# Base strategy class and common strategy utilities

from .base_strategy_class import BaseStrategy
from .ma_crossover import MovingAverageCrossover
from .bollinger_breakout import BollingerBreakout
from .dual_momentum import DualMomentum
from .gap_fade import GapFade
from .rsi_pullback import RSIPullback
from .turtle_breakout import TurtleBreakout

__all__ = [
    'BaseStrategy',
    'MovingAverageCrossover',
    'BollingerBreakout',
    'DualMomentum',
    'GapFade',
    'RSIPullback',
    'TurtleBreakout'
]
