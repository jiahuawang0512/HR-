# HBR日报 - 哈佛商业评论文章初始化脚本

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from database import init_database, insert_article
from models import Article

# 真实的哈佛商业评论 HR 管理相关文章
hbr_articles = [
    {
        "nature_id": "hbr-2026-suporteam",
        "title": "How to Build a Superteam That Keeps Getting Better",
        "title_en": "如何打造一个不断进步的超级团队",
        "summary": "本文探讨了如何建立和管理高效的超级团队。超级团队是由顶尖人才组成的精英团队，他们能够持续创新并超越预期。研究表明，成功的超级团队具有三个关键特征：明确的共同目标、开放的沟通文化和持续的学习机制。领导者需要创造一个让团队成员能够充分发挥潜力的环境，同时建立信任和心理安全的工作氛围。",
        "source": "Harvard Business Review",
        "source_short": "HBR",
        "authors": "Ron Friedman",
        "link": "https://hbr.org/2026/03/how-to-build-a-superteam-that-keeps-getting-better",
        "topic": "organizational-behavior",
        "topic_label": "组织行为学",
        "publish_date": "2026-03-01"
    },
    {
        "nature_id": "hbr-2026-highagency",
        "title": "How Leaders Can Build a High-Agency Culture",
        "title_en": "领导者如何建立高能动性文化",
        "summary": "本文阐述了什么是高能动性文化以及领导者如何培养它。高能动性文化是指员工感到自己对工作有控制感，能够自主决策并对结果负责的文化。研究显示，具有高能动性的员工更具创新性、更愿意承担风险、对工作更投入。领导者应该通过赋予员工自主权、提供资源支持、建立明确的期望来培养这种文化。",
        "source": "Harvard Business Review",
        "source_short": "HBR",
        "authors": "Nir Eyal",
        "link": "https://hbr.org/2026/03/how-to-build-a-high-agency-culture",
        "topic": "organizational-behavior",
        "topic_label": "组织行为学",
        "publish_date": "2026-03-25"
    },
    {
        "nature_id": "hbr-2026-ai-leadership",
        "title": "The AI Leadership Imperative",
        "title_en": "AI领导力 imperium",
        "summary": "本文探讨了领导者如何在AI时代发挥关键作用。随着生成式AI的快速发展，领导者面临着前所未有的挑战和机遇。研究指出，最有效的AI领导者具备三个共同特质：技术素养、伦理意识和变革管理能力。组织需要在AI应用中平衡效率提升与员工福祉，确保AI的使用符合伦理和价值观。",
        "source": "Harvard Business Review",
        "source_short": "HBR",
        "authors": "Adi Ignatius",
        "link": "https://hbr.org/2026/04/the-ai-leadership-imperative",
        "topic": "hr-tech",
        "topic_label": "HR科技与AI",
        "publish_date": "2026-04-17"
    },
    {
        "nature_id": "hbr-2024-high-performers",
        "title": "3 Ways to Make Sure High Performers Feel Valued",
        "title_en": "确保高绩效员工感到被重视的3种方法",
        "summary": "高绩效员工是组织最宝贵的资产，但他们往往因为表现出色而被视为理所当然，最终导致倦怠和离职。本文提供了三种确保高绩效员工感到被重视的方法：1) 认可他们的独特贡献而不只是结果；2) 提供有意义的成长机会；3) 创造让他们感到被倾听和尊重的工作环境。",
        "source": "Harvard Business Review",
        "source_short": "HBR",
        "authors": "Zach Mercurio",
        "link": "https://hbr.org/2024/11/3-ways-to-make-sure-high-performers-feel-valued",
        "topic": "employee-relations",
        "topic_label": "员工关系",
        "publish_date": "2024-11-12"
    },
    {
        "nature_id": "hbr-2026-executive-onboarding",
        "title": "How to Onboard a New Member of the Executive Team",
        "title_en": "如何成功 onboarding 高管团队新成员",
        "summary": "高管 onboarding 与普通员工不同，需要更加谨慎和系统的 approach。本文提供了帮助高管快速融入组织的实用框架，包括：明确前90天的优先事项、建立关键的 stakeholder relationships、了解组织文化和政治格局。研究表明，成功的高管 onboarding 可以将融入时间缩短50%，并显著提高留任率。",
        "source": "Harvard Business Review",
        "source_short": "HBR",
        "authors": "Ania W. Masinter",
        "link": "https://hbr.org/2026/04/how-to-onboard-a-new-member-of-the-executive-team",
        "topic": "recruitment",
        "topic_label": "招聘与选拔",
        "publish_date": "2026-04-01"
    },
    {
        "nature_id": "hbr-2026-executive-presence",
        "title": "When Executive Presence Backfires",
        "title_en": "高管影响力何时适得其反",
        "summary": "高管影响力通常被认为是成功的关键因素，但研究表明过度的高管影响力可能带来负面影响。本文探讨了高管影响力何时会适得其反，以及如何在保持影响力的同时避免常见陷阱。关键是要在自信与谦逊、果断与协作、魅力与真诚之间找到平衡。",
        "source": "Harvard Business Review",
        "source_short": "HBR",
        "authors": "Amii Barnard-Bahn",
        "link": "https://hbr.org/2026/04/when-executive-presence-backfires",
        "topic": "leadership",
        "topic_label": "领导力",
        "publish_date": "2026-04-01"
    },
    {
        "nature_id": "hbr-2026-managers-ai",
        "title": "Managers and Executives Disagree on AI—And It's Costing Companies",
        "title_en": "管理者与高管对AI的看法不一致——这正在让公司付出代价",
        "summary": "研究表明，管理者和高层管理者在AI应用方面存在显著的认知差距。基层管理者更关注AI对员工的影响和工作流程的改变，而高管更关注投资回报率。这种认知差距导致AI项目难以落地或效果不佳。研究建议组织需要建立跨层级的沟通机制，确保AI战略的一致性和有效执行。",
        "source": "Harvard Business Review",
        "source_short": "HBR",
        "authors": "Jeremy Korst, Stefano Puntoni, Prasanna Tambe",
        "link": "https://hbr.org/2026/04/managers-and-executives-disagree-on-ai",
        "topic": "hr-tech",
        "topic_label": "HR科技与AI",
        "publish_date": "2026-04-08"
    },
    {
        "nature_id": "hbr-2023-upskill-hr",
        "title": "How Can I Upskill as an HR Professional?",
        "title_en": "HR专业人士如何提升技能？",
        "summary": "随着数字化转型重塑人力资源职能，HR专业人士需要不断更新技能组合。本文提供了HR专业人士提升技能的实用建议：1) 培养数据分析能力，学会用数据驱动决策；2) 发展技术素养，了解新兴技术如AI和机器学习；3) 强化商业敏锐度，理解业务战略并与之对齐；4) 提升变革管理能力。",
        "source": "Harvard Business Review",
        "source_short": "HBR",
        "authors": "Joanne Alilovic",
        "link": "https://hbr.org/2022/11/ask-an-expert-how-can-i-upskill-as-an-hr-professional",
        "topic": "training",
        "topic_label": "培训与发展",
        "publish_date": "2022-11-07"
    },
    {
        "nature_id": "hbr-2018-agile-hr",
        "title": "HR Goes Agile",
        "title_en": "HR走向敏捷",
        "summary": "敏捷方法最初用于软件开发，如今正在改变HR的运作方式。本文探讨了HR如何采用敏捷原则来提高响应速度和员工体验。敏捷HR的核心是将HR服务视为产品，以员工需求为中心，快速迭代和实验。实施敏捷HR的组织报告称员工敬业度更高，招聘周期更短，变革能力更强。",
        "source": "Harvard Business Review",
        "source_short": "HBR",
        "authors": "Peter Cappelli, Anna Tavis",
        "link": "https://hbr.org/2018/03/hr-goes-agile",
        "topic": "hr-tech",
        "topic_label": "HR科技与AI",
        "publish_date": "2018-03-01"
    },
    {
        "nature_id": "hbr-2018-talent-management",
        "title": "The New Rules of Talent Management",
        "title_en": "人才管理的新规则",
        "summary": "传统的人才管理模式已经过时。在人才流动加速、员工期望多元化的今天，组织需要重新思考人才管理策略。研究发现，成功的人才管理需要关注：员工体验的每一个环节、个性化的发展路径、数据驱动的决策、以及构建有吸引力的雇主品牌。",
        "source": "Harvard Business Review",
        "source_short": "HBR",
        "authors": "Peter Cappelli, Anna Tavis, Lisa Burrell, Dominic Barton, Dennis Carey, Ram Charan",
        "link": "https://hbr.org/2018/03/the-new-rules-of-talent-management",
        "topic": "recruitment",
        "topic_label": "招聘与选拔",
        "publish_date": "2018-03-01"
    }
]


def seed_hbr_data():
    print("=" * 50)
    print("开始初始化 HBR 文章数据...")
    print("=" * 50)

    init_database()
    print("数据库初始化完成")

    today = datetime.now().strftime("%Y-%m-%d")
    today_articles = 0

    for article_data in hbr_articles:
        article = Article(
            nature_id=article_data["nature_id"],
            title=article_data["title"],
            title_en=article_data.get("title_en"),
            summary=article_data["summary"],
            source=article_data["source"],
            source_short=article_data.get("source_short"),
            authors=article_data["authors"],
            link=article_data["link"],
            topic=article_data["topic"],
            topic_label=article_data["topic_label"],
            publish_date=article_data["publish_date"],
            fetched_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            push_date=today,
            is_pushed=True
        )

        result = insert_article(article)
        if result:
            today_articles += 1
            print(f"新增: {article.title}")
        else:
            print(f"已存在: {article.title}")

    print(f"\n完成! 新增 {today_articles} 篇 HBR 文章")
    print("=" * 50)


if __name__ == "__main__":
    seed_hbr_data()