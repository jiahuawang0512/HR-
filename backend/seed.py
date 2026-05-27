# Nature HR日报 - 数据初始化脚本
# 使用真实的 Nature 期刊文章

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from database import init_database, insert_article
from models import Article

# 真实的 Nature 期刊 HR 相关文章
sample_articles = [
    {
        "nature_id": "s41586-024-07500-2",
        "title": "混合居家办公提高员工留存率且不影响绩效",
        "title_en": "Hybrid working from home improves retention without damaging performance",
        "summary": "本研究通过一项为期六个月的随机对照试验，研究了混合居家办公对2021-2022年间一家中国科技公司1,612名员工的影响。研究发现：混合办公使员工离职率降低三分之一（从7.20%降至4.80%），工作满意度显著提高，而绩效评级无显著影响。这项研究来自斯坦福大学、香港中文大学（深圳）和携程团队，发表在Nature正刊。",
        "source": "Nature",
        "authors": "Nicholas Bloom, Ruobing Han, James Liang",
        "link": "https://www.nature.com/articles/s41586-024-07500-2",
        "topic": "employee-relations",
        "topic_label": "员工关系",
        "publish_date": "2024-06-12"
    },
    {
        "nature_id": "s41598-024-67122-6",
        "title": "员工在办公室工作、居家办公和混合办公模式下的创新表现差异",
        "title_en": "Employee innovation during office work, work from home and hybrid work",
        "summary": "本研究利用印度IT服务公司HCL Technologies超过48,000名员工的创新活动详细数据，分析了三种工作模式对员工创新的影响。研究发现：居家办公期间创意数量无显著变化但质量下降；混合办公期间创意数量显著下降，尤其是团队成员办公出勤差异较大的团队。表明远程和混合办公模式可能抑制协作与创新。",
        "source": "Scientific Reports",
        "authors": "Michael Gibbs, Friederike Mengel, Christoph Siemroth",
        "link": "https://www.nature.com/articles/s41598-024-67122-6",
        "topic": "employee-relations",
        "topic_label": "员工关系",
        "publish_date": "2024-07-24"
    },
    {
        "nature_id": "s41562-025-02259-6",
        "title": "四天工作周减少工作时间改善员工福祉",
        "title_en": "Work time reduction via a 4-day workweek finds improvements in workers' well-being",
        "summary": "本研究探讨了组织范围内不减薪的四天工作周干预措施如何影响员工的健康状况。研究来自6个国家141个组织的2,896名员工，结果显示：员工在职业倦怠、工作满意度、心理健康和身体健康方面均有改善。这一模式在12家对照组公司中未观察到。保持收入的四天工作周是提高员工福祉的有效组织干预措施。",
        "source": "Nature Human Behaviour",
        "authors": "Wen Fan, Juliet B. Schor, Orla Kelly, Guolin Gu",
        "link": "https://www.nature.com/articles/s41562-025-02259-6",
        "topic": "employee-relations",
        "topic_label": "员工关系",
        "publish_date": "2025-07-21"
    },
    {
        "nature_id": "s41562-024-02093-2",
        "title": "技能依赖揭示嵌套的人力资本结构",
        "title_en": "Skill dependencies uncover nested human capital",
        "summary": "本研究分析了美国调查数据，揭示了技能组合中的嵌套结构。职业在需要某项技能的情况下，会要求另一项技能，先进和专业的技能往往建立在更广泛、更基础的技能之上。研究检查了7000万次工作转换，结果表明人力资本发展和职业发展遵循这种结构化路径，与嵌套结构更一致的技能具有更高的工资溢价。",
        "source": "Nature Human Behaviour",
        "authors": "Moh Hosseinioun, Frank Neffke, Letian Zhang, Hyejin Youn",
        "link": "https://www.nature.com/articles/s41562-024-02093-2",
        "topic": "training",
        "topic_label": "培训与发展",
        "publish_date": "2025-02-24"
    },
    {
        "nature_id": "s41599-026-07246-4",
        "title": "伦理型领导与组织价值观的协同效应：通过心理安全感和组织认同培养员工亲环境行为",
        "title_en": "The Synergy of Ethical Leaders and Corporate Values: nurturing employee pro-environmental behavior through psychological safety and organizational identification",
        "summary": "本研究基于韩国421名专业人士的四波时间滞后数据集，探讨伦理型领导如何激发员工的亲环境行为。研究发现伦理型领导通过心理安全感和组织认同的顺序路径间接影响员工环保行为，企业伦理氛围调节伦理型领导对心理安全感的影响。整合了社会学习理论、社会交换理论和组织伦理框架。",
        "source": "Humanities and Social Sciences Communications",
        "authors": "Byung-Jik Kim, Eung Il Kim",
        "link": "https://www.nature.com/articles/s41599-026-07246-4",
        "topic": "leadership",
        "topic_label": "领导力",
        "publish_date": "2026-04-14"
    },
    {
        "nature_id": "s41598-023-49000-9",
        "title": "三种个人资源干预对员工职业倦怠的影响",
        "title_en": "Effects of three personal resources interventions on employees' burnout",
        "summary": "本研究旨在评估三种个人资源干预措施对降低员工职业倦怠的有效性。研究假设积极心理资本干预（PsyCap）、工作塑造干预和综合干预都会对倦怠水平产生积极影响。研究结果表明：个人资源干预能有效降低员工职业倦怠， PsyCap干预和综合干预显示出最大的有效性。",
        "source": "Scientific Reports",
        "authors": "Mariola Pérez-Marqués, Onintze Letona-Ibañez, Alejandro Amillano, María Carrasco, Silvia Martínez-Rodríguez",
        "link": "https://www.nature.com/articles/s41598-023-49000-9",
        "topic": "hr-tech",
        "topic_label": "HR科技与AI",
        "publish_date": "2023-12-06"
    },
    {
        "nature_id": "s41599-025-05656-4",
        "title": "生成式AI采纳与员工 outcomes：基于资源保护理论的工作重塑和职业承诺视角",
        "title_en": "Generative AI adoption and employee outcomes: a conservation of resources perspective on job crafting, career commitment, and the moderating role of liking of AI",
        "summary": "本研究应用资源保护理论，探讨生成式AI采纳如何通过工作重塑和职业承诺的序列中介作用影响员工 outcomes。研究数据来自中国企业的291对参与者，结果表明生成式AI采纳正向影响工作重塑的三个维度，进而影响职业承诺和员工行为。对AI的喜好程度调节了这一关系。",
        "source": "Humanities and Social Sciences Communications",
        "authors": "Yanyan Liu, Fan Sheng, Ruyue Liu",
        "link": "https://www.nature.com/articles/s41599-025-05656-4",
        "topic": "hr-tech",
        "topic_label": "HR科技与AI",
        "publish_date": "2025-08-22"
    },
    {
        "nature_id": "s41599-026-06989-4",
        "title": "算法人力资源管理作为算法治理的一种模式：数字工作场所中的透明度、公平性与人类能动性",
        "title_en": "Algorithmic human resource management as a mode of algorithmic governance: transparency, fairness, and human agency in the digital workplace",
        "summary": "工作场所的快速数字化正在重塑人力资源管理的基础。本文将算法HRM概念化为一种业务流程技术，通过自动化、预测分析和工作流程重新设计来转变传统的人员管理实践。通过在六个核心领域——劳动力规划、招聘、培训、绩效管理、薪酬和员工关系——对算法型和传统型HRM流程进行比较研究，揭示了算法如何将HRM从直觉驱动的决策转向基于数据和自适应系统的决策。",
        "source": "Humanities and Social Sciences Communications",
        "authors": "Zhisheng Chen",
        "link": "https://www.nature.com/articles/s41599-026-06989-4",
        "topic": "hr-tech",
        "topic_label": "HR科技与AI",
        "publish_date": "2026-03-16"
    }
]


def seed_data():
    print("=" * 50)
    print("开始初始化数据（使用真实Nature文章）...")
    print("=" * 50)

    init_database()
    print("数据库初始化完成")

    today = datetime.now().strftime("%Y-%m-%d")
    today_articles = 0

    for article_data in sample_articles:
        article = Article(
            nature_id=article_data["nature_id"],
            title=article_data["title"],
            title_en=article_data.get("title_en"),
            summary=article_data["summary"],
            source=article_data["source"],
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

    print(f"\n完成! 今日新增 {today_articles} 篇文章")
    print("=" * 50)


if __name__ == "__main__":
    seed_data()
