"""
产品分析技能

结合SEO工具和数据，分析产品优化机会
"""
from typing import Dict, Any, Optional, Optional
import json

from skills.base_skill import BaseSkill, SkillResult, SkillContext, SkillStatus


class ProductAnalysisSkill(BaseSkill):
    """产品分析技能"""

    name = "product_analysis"
    description = "分析产品的市场定位、优化机会和竞争策略"
    version = "1.0.0"

    required_tools = ["competitor_analysis", "seo_generator"]
    required_llm = True

    def execute(
        self,
        inputs: Dict[str, Any],
        context: Optional[SkillContext] = None
    ) -> SkillResult:
        """执行产品分析"""
        if context is None:
            context = SkillContext(inputs=inputs)

        try:
            product_title = inputs.get("product_title")
            product_category = inputs.get("product_category")

            # SEO分析
            seo_result = self.tool_manager.execute_tool(
                "seo_generator",
                product_title=product_title,
                product_category=product_category,
            )

            # 竞品分析
            competitor_result = self.tool_manager.execute_tool(
                "competitor_analysis",
                product_category=product_category,
            )

            # LLM生成分析报告
            analysis = self._generate_analysis(
                product_title,
                product_category,
                seo_result.data,
                competitor_result.data,
            )

            return SkillResult(
                success=True,
                status=SkillStatus.SUCCESS,
                output={
                    "product_title": product_title,
                    "seo_analysis": seo_result.data,
                    "competitor_analysis": competitor_result.data,
                    "analysis": analysis,
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

    def _generate_analysis(self, title, category, seo_data, competitor_data) -> str:
        prompt = f"""分析产品的市场机会：

产品：{title}
类别：{category}

SEO关键词数据：{json.dumps(seo_data['primary_keywords'][:3], ensure_ascii=False)}
竞品数据：{json.dumps(competitor_data['analysis'], ensure_ascii=False)}

提供300字以内的分析报告，包括：
1. 产品优势
2. 优化建议
3. 竞争策略
"""

        return self.llm_service.chat([{"role": "user", "content": prompt}])
