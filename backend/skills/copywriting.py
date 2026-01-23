"""
营销文案生成技能

结合SEO和产品信息，生成营销文案
"""
from typing import Dict, Any, Optional, Optional

from skills.base_skill import BaseSkill, SkillResult, SkillContext, SkillStatus


class CopywritingSkill(BaseSkill):
    """营销文案生成技能"""

    name = "copywriting"
    description = "生成SEO优化的营销文案"
    version = "1.0.0"

    required_tools = ["seo_generator"]
    required_llm = True

    def execute(
        self,
        inputs: Dict[str, Any],
        context: Optional[SkillContext] = None
    ) -> SkillResult:
        """执行文案生成"""
        if context is None:
            context = SkillContext(inputs=inputs)

        try:
            product_title = inputs.get("product_title")
            product_category = inputs.get("product_category")
            target_language = inputs.get("target_language", "English")
            channel = inputs.get("channel", "Facebook Ads")

            # 获取SEO关键词
            seo_result = self.tool_manager.execute_tool(
                "seo_generator",
                product_title=product_title,
                product_category=product_category,
            )

            # 生成文案
            copy = self._generate_copy(
                product_title,
                product_category,
                seo_result.data,
                target_language,
                channel,
            )

            return SkillResult(
                success=True,
                status=SkillStatus.SUCCESS,
                output={
                    "copy": copy,
                    "keywords": seo_result.data["primary_keywords"][:5],
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

    def _generate_copy(self, title, category, seo_data, language, channel) -> str:
        # 提取关键词
        keywords = [kw["keyword"] for kw in seo_data["primary_keywords"][:5]]

        prompt = f"""生成营销文案：

产品：{title}
类别：{category}
目标语言：{language}
渠道：{channel}
关键词：{', '.join(keywords)}

请生成包含以下内容的文案：
1. 吸引人的标题（50字以内）
2. 3个核心卖点
3. 广告正文（100-150字）

使用{language}语言。
"""

        return self.llm_service.chat([{"role": "user", "content": prompt}])
