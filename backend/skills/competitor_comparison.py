"""
竞品对比技能

深度对比竞品的优劣势
"""
from typing import Dict, Any, Optional, Optional
import json

from skills.base_skill import BaseSkill, SkillResult, SkillContext, SkillStatus


class CompetitorComparisonSkill(BaseSkill):
    """竞品对比技能"""

    name = "competitor_comparison"
    description = "深度对比竞品，识别差异化机会"
    version = "1.0.0"

    required_tools = ["competitor_analysis"]
    required_llm = True

    def execute(
        self,
        inputs: Dict[str, Any],
        context: Optional[SkillContext] = None
    ) -> SkillResult:
        """执行竞品对比"""
        if context is None:
            context = SkillContext(inputs=inputs)

        try:
            product_info = inputs.get("product_info", {})
            target_market = inputs.get("target_market", "Global")

            # 获取竞品数据
            competitor_result = self.tool_manager.execute_tool(
                "competitor_analysis",
                product_category=product_info.get("category", ""),
                target_market=target_market,
            )

            # 生成对比报告
            comparison = self._generate_comparison(
                product_info,
                competitor_result.data,
            )

            return SkillResult(
                success=True,
                status=SkillStatus.SUCCESS,
                output={
                    "product": product_info,
                    "competitors": competitor_result.data,
                    "comparison": comparison,
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

    def _generate_comparison(self, product, competitor_data) -> str:
        prompt = f"""竞品对比分析：

我们的产品：{json.dumps(product, ensure_ascii=False)}

竞品数据：{json.dumps(competitor_data['competitors'][:3], ensure_ascii=False)}

请提供详细的对比分析（300字），包括：
1. 价格对比
2. 功能差异
3. 差异化建议
"""

        return self.llm_service.chat([{"role": "user", "content": prompt}])
