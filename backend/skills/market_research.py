"""
市场调研技能

组合竞品分析和趋势分析工具，完成市场调研任务
"""
from typing import Dict, Any, Optional
import json

from skills.base_skill import BaseSkill, SkillResult, SkillContext, SkillStatus


class MarketResearchSkill(BaseSkill):
    """
    市场调研技能

    功能：
    1. 分析竞品情况
    2. 分析市场趋势
    3. 生成市场调研报告
    """

    name = "market_research"
    description = "进行完整的市场调研，包括竞品分析和趋势预测"
    version = "1.0.0"

    required_tools = ["competitor_analysis", "trend_analysis"]
    required_llm = True

    def execute(
        self,
        inputs: Dict[str, Any],
        context: Optional[SkillContext] = None
    ) -> SkillResult:
        """
        执行市场调研

        Args:
            inputs: 必须包含 product_category, target_market
            context: 执行上下文

        Returns:
            SkillResult: 市场调研报告
        """
        if context is None:
            context = SkillContext(inputs=inputs)

        try:
            product_category = inputs.get("product_category")
            target_market = inputs.get("target_market", "Global")

            # 步骤1: 竞品分析
            context.add_step("competitor_analysis", inputs)
            competitor_result = self.tool_manager.execute_tool(
                "competitor_analysis",
                product_category=product_category,
                target_market=target_market,
            )

            if not competitor_result.success:
                return SkillResult(
                    success=False,
                    status=SkillStatus.ERROR,
                    error=f"Competitor analysis failed: {competitor_result.error}",
                    context=context,
                )

            # 步骤2: 趋势分析
            context.add_step("trend_analysis", inputs)
            trend_result = self.tool_manager.execute_tool(
                "trend_analysis",
                category=product_category,
                time_period="6months",
                market=target_market,
            )

            if not trend_result.success:
                return SkillResult(
                    success=False,
                    status=SkillStatus.ERROR,
                    error=f"Trend analysis failed: {trend_result.error}",
                    context=context,
                )

            # 步骤3: 使用LLM生成综合报告
            context.add_step("generate_report", {
                "competitor_data": competitor_result.data,
                "trend_data": trend_result.data,
            })

            report = self._generate_report(
                product_category,
                target_market,
                competitor_result.data,
                trend_result.data,
            )

            return SkillResult(
                success=True,
                status=SkillStatus.SUCCESS,
                output={
                    "category": product_category,
                    "market": target_market,
                    "competitor_analysis": competitor_result.data,
                    "trend_analysis": trend_result.data,
                    "report": report,
                },
                context=context,
                metadata={
                    "tools_used": ["competitor_analysis", "trend_analysis"],
                    "steps_completed": 3,
                },
            )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.ERROR,
                error=str(e),
                context=context,
            )

    def _generate_report(
        self,
        category: str,
        market: str,
        competitor_data: Dict,
        trend_data: Dict,
    ) -> str:
        """
        使用LLM生成市场调研报告

        Args:
            category: 产品类别
            market: 目标市场
            competitor_data: 竞品分析数据
            trend_data: 趋势分析数据

        Returns:
            str: 市场调研报告
        """
        # 构建提示词
        prompt = f"""你是市场研究专家。请基于以下数据分析{category}类产品在{market}市场的情况。

## 竞品分析数据
```json
{json.dumps(competitor_data['analysis'], indent=2, ensure_ascii=False)}
```

## 市场趋势数据
```json
{json.dumps(trend_data['analysis'], indent=2, ensure_ascii=False)}
```

请提供一份简洁的市场调研报告，包括：
1. 市场竞争格局
2. 价格趋势分析
3. 市场机会识别
4. 战略建议

报告长度：300-500字
"""

        try:
            response = self.llm_service.chat([{"role": "user", "content": prompt}])
            return response
        except Exception as e:
            # 降级：返回简单报告
            return f"市场调研报告（{category} - {market}）\n" \
                   f"生成失败，请查看原始数据。\n" \
                   f"错误：{str(e)}"
