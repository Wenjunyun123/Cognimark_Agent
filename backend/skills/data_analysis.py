"""
数据分析技能

结合趋势分析和竞品数据，生成数据洞察
"""
from typing import Dict, Any, Optional, Optional
import json

from skills.base_skill import BaseSkill, SkillResult, SkillContext, SkillStatus


class DataAnalysisSkill(BaseSkill):
    """数据分析技能"""

    name = "data_analysis"
    description = "分析市场数据，提取商业洞察"
    version = "1.0.0"

    required_tools = ["trend_analysis", "competitor_analysis"]
    required_llm = True

    def execute(
        self,
        inputs: Dict[str, Any],
        context: Optional[SkillContext] = None
    ) -> SkillResult:
        """执行数据分析"""
        if context is None:
            context = SkillContext(inputs=inputs)

        try:
            category = inputs.get("category")
            market = inputs.get("market", "Global")

            # 趋势分析
            trend_result = self.tool_manager.execute_tool(
                "trend_analysis",
                category=category,
                time_period="6months",
                market=market,
            )

            # 竞品分析
            competitor_result = self.tool_manager.execute_tool(
                "competitor_analysis",
                product_category=category,
                target_market=market,
            )

            # 生成洞察
            insights = self._generate_insights(
                category,
                trend_result.data,
                competitor_result.data,
            )

            return SkillResult(
                success=True,
                status=SkillStatus.SUCCESS,
                output={
                    "category": category,
                    "trend_data": trend_result.data,
                    "competitor_data": competitor_result.data,
                    "insights": insights,
                },
                context=context,
            )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.ERROR,
                error=str(e),
                context=context,
            )

    def _generate_insights(self, category, trend_data, competitor_data) -> str:
        prompt = f"""数据分析洞察：

类别：{category}

趋势数据：增长率{trend_data['analysis']['growth_rate']}%
竞品数据：平均价格${competitor_data['analysis']['avg_price']}

请提供300字以内的数据洞察报告，包括：
1. 关键发现
2. 趋势解读
3. 行动建议
"""

        return self.llm_service.chat([{"role": "user", "content": prompt}])
