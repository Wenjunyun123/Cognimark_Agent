"""
SEO关键词生成工具

使用LLM生成SEO优化的关键词
"""
from typing import Dict, Any, List
import random

from ..base_tool import BaseTool, ToolResult, ToolStatus, ToolParameter


class SEOKeywordGeneratorTool(BaseTool):
    """
    SEO关键词生成工具

    功能：
    1. 根据产品描述生成SEO关键词
    2. 生成长尾关键词
    3. 提供关键词优化建议
    """

    name = "seo_generator"
    description = "生成SEO优化的产品关键词和长尾词"
    version = "1.0.0"

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="product_title",
                type="str",
                description="产品标题",
                required=True,
            ),
            ToolParameter(
                name="product_category",
                type="str",
                description="产品类别",
                required=True,
            ),
            ToolParameter(
                name="target_market",
                type="str",
                description="目标市场",
                required=False,
                default="US",
            ),
            ToolParameter(
                name="keyword_count",
                type="int",
                description="生成关键词数量",
                required=False,
                default=10,
            ),
        ]

    def execute(self, **kwargs) -> ToolResult:
        """
        执行SEO关键词生成

        Args:
            product_title: 产品标题
            product_category: 产品类别
            target_market: 目标市场
            keyword_count: 关键词数量

        Returns:
            ToolResult: SEO关键词和优化建议
        """
        try:
            product_title = kwargs["product_title"]
            product_category = kwargs["product_category"]
            target_market = kwargs.get("target_market", "US")
            keyword_count = kwargs.get("keyword_count", 10)

            # 生成主关键词
            primary_keywords = self._generate_primary_keywords(
                product_title,
                product_category,
                keyword_count // 2
            )

            # 生成长尾关键词
            long_tail_keywords = self._generate_long_tail_keywords(
                product_title,
                product_category,
                target_market,
                keyword_count // 2
            )

            # 生成优化建议
            recommendations = self._generate_recommendations(
                product_title,
                primary_keywords + long_tail_keywords
            )

            return ToolResult(
                success=True,
                status=ToolStatus.SUCCESS,
                data={
                    "product_title": product_title,
                    "product_category": product_category,
                    "target_market": target_market,
                    "primary_keywords": primary_keywords,
                    "long_tail_keywords": long_tail_keywords,
                    "recommendations": recommendations,
                },
                metadata={
                    "total_keywords": len(primary_keywords) + len(long_tail_keywords),
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                status=ToolStatus.ERROR,
                error=str(e),
            )

    def _generate_primary_keywords(
        self,
        title: str,
        category: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """
        生成主关键词

        在实际应用中，这里应该使用LLM生成
        """
        # 从标题中提取关键词
        words = title.lower().split()
        keywords = []

        # 添加类别相关关键词
        category_keywords = {
            "Sports & Outdoor": ["sports", "outdoor", "fitness", "hiking", "camping"],
            "Electronics": ["electronics", "gadget", "tech", "digital", "smart"],
            "Office Supplies": ["office", "desk", "work", "productivity", "business"],
            "Fitness": ["fitness", "workout", "gym", "exercise", "training"],
        }

        category_words = category_keywords.get(category, [category.lower()])

        # 生成关键词组合
        for i in range(min(count, len(category_words) * 2)):
            if i < len(category_words):
                keyword = category_words[i]
            else:
                # 组合词
                keyword = f"{random.choice(category_words)} {random.choice(words[:3])}"

            # 模拟搜索量
            search_volume = random.randint(1000, 50000)

            keywords.append({
                "keyword": keyword.title(),
                "search_volume": search_volume,
                "competition": round(random.uniform(0.3, 0.9), 2),
                "cpc": round(random.uniform(0.5, 3.0), 2),  # Cost Per Click
            })

        return keywords

    def _generate_long_tail_keywords(
        self,
        title: str,
        category: str,
        market: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """
        生成长尾关键词

        长尾关键词通常包含3-5个词，搜索量较小但转化率高
        """
        templates = [
            f"best {category.lower()} for",
            f"{category.lower()} for",
            f"affordable {category.lower()}",
            f"top rated {category.lower()}",
            f"{category.lower()} near me",
            f"cheap {category.lower()}",
            f"how to choose {category.lower()}",
        ]

        long_tail_keywords = []

        # 提取标题中的关键词
        title_words = [w for w in title.lower().split() if len(w) > 3]

        for i in range(count):
            template = random.choice(templates)

            # 添加标题关键词
            if title_words and random.random() > 0.3:
                suffix = random.choice(title_words[:3])
                keyword = f"{template} {suffix}"
            else:
                keyword = template

            search_volume = random.randint(100, 5000)

            long_tail_keywords.append({
                "keyword": keyword.title(),
                "search_volume": search_volume,
                "competition": round(random.uniform(0.1, 0.5), 2),
                "cpc": round(random.uniform(0.2, 1.5), 2),
                "type": "long_tail",
            })

        return long_tail_keywords

    def _generate_recommendations(
        self,
        title: str,
        keywords: List[Dict]
    ) -> List[str]:
        """生成SEO优化建议"""
        recommendations = []

        # 建议1：标题优化
        recommendations.append(
            "建议在产品标题中包含主关键词，以提高搜索排名"
        )

        # 建议2：长尾词策略
        long_tail_count = sum(1 for k in keywords if k.get("type") == "long_tail")
        if long_tail_count > 0:
            recommendations.append(
                f"发现{long_tail_count}个长尾关键词机会，竞争度较低，建议优先使用"
            )

        # 建议3：关键词密度
        recommendations.append(
            "建议在产品描述中自然融入关键词，密度控制在2-3%"
        )

        # 建议4：高价值关键词
        high_value = [k for k in keywords if k.get("search_volume", 0) > 10000]
        if high_value:
            recommendations.append(
                f"识别到{len(high_value)}个高搜索量关键词，可用于广告投放"
            )

        return recommendations
