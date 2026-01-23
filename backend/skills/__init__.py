"""
Skills技能系统 - 基于LangChain设计思想

参考LangChain的Chain概念，实现可组合的技能系统
"""
from .base_skill import BaseSkill, SkillResult, SkillContext
from .skill_manager import SkillManager

__all__ = [
    "BaseSkill",
    "SkillResult",
    "SkillContext",
    "SkillManager",
]
