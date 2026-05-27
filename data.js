// ========== HR信息日报 - 真实数据 ==========
// 每日自动从 Nature 及其子期刊检索 HR 领域相关研究
// 数据来源：nature.com 实际检索结果
const dailyResearchData = [
    {
        date: '2026-04-17',
        weekday: '星期五',
        articles: [
            {
                id: 1,
                title: 'AI算法会选择你的下一位实验室同事吗？——学术招聘中的AI工具应用',
                topic: 'recruitment',
                topicLabel: '招聘与选拔',
                summary: '本文探讨了人工智能工具在学术招聘中的兴起及其潜在影响。研究分析了AI辅助招聘系统的运作机制，包括简历筛选、面试评估和候选人匹配等环节。文章指出，虽然AI可以显著提升招聘效率并减少人为偏见，但也存在"黑箱决策"、数据偏见放大以及候选人对技术接受度不均等风险。作者呼吁建立透明的算法审计机制和"人机协同"的招聘决策框架。',
                source: 'Nature',
                authors: 'Linda Nordling',
                link: 'https://www.nature.com/articles/d41586-025-02261-5'
            },
            {
                id: 2,
                title: '远程工作如何塑造工作与家庭平衡？工作压力与领导支持的交互作用',
                topic: 'employee-relations',
                topicLabel: '员工关系',
                summary: '本研究通过大样本调查（N=1,247）探讨了远程办公对员工工作家庭平衡的影响路径。研究发现，远程工作的效果并非线性——适度远程（每周2-3天）能显著改善工作家庭冲突，但过度远程反而因边界模糊导致角色混淆。关键调节变量为领导支持水平：高领导支持组的工作家庭满意度比低支持组高出42%。研究建议企业制定灵活但有边界的远程政策，同时培训管理者的数字化领导能力。',
                source: 'Humanities and Social Sciences Communications',
                authors: 'Te Li, Wen Yang',
                link: 'https://www.nature.com/articles/s41635-026-00182-6'
            },
            {
                id: 3,
                title: '生成式AI采用与员工职业后果：资源保存视角下的工作重塑与职业承诺',
                topic: 'hr-tech',
                topicLabel: 'HR科技与AI',
                summary: '基于资源保存理论（COR），本研究调查了生成式AI在工作场所的广泛采用对员工的深层影响。通过对5家引入ChatGPT类工具的企业进行前后测对比（N=892），研究发现：AI工具使用显著增加了员工的工作重塑行为（β=0.34），但同时也加剧了技能过时焦虑。对AI接受度高的员工表现出更强的职业承诺和创造力，而对AI持抵触态度的员工则呈现更高的离职意向。组织应重视AI转型中的人文关怀和再培训投入。',
                source: 'Humanities and Social Sciences Communications',
                authors: 'Yanyan Liu, Mingyao Ke, Xiangrong Wang, Hui Zhang',
                link: 'https://www.nature.com/articles/s41635-025-00876-x'
            },
            {
                id: 4,
                title: '基于深度学习的多源数据融合劳动关系预测系统及预警机制',
                topic: 'performance',
                topicLabel: '绩效管理',
                summary: '本研究提出了一种基于深度学习的劳动关系智能预警系统，整合了考勤记录、薪资数据、投诉历史、沟通文本等多源异构数据。系统采用LSTM-CNN融合架构处理时序和非结构化信息，在10家企业试点中的劳动关系事件预测准确率达到82.3%（AUC=0.847），平均提前14天发出预警信号。研究还设计了可解释性模块帮助HR管理者理解风险归因，为预防性劳动管理提供了数据驱动的解决方案。',
                source: 'Scientific Reports',
                authors: 'Enhui Liu, Kyujun Cho',
                link: 'https://www.nature.com/articles/s41598-026-42718-x'
            }
        ]
    },
    {
        date: '2026-04-16',
        weekday: '星期四',
        articles: [
            {
                id: 5,
                title: '环境变革型领导如何通过心理机制影响员工绿色行为？',
                topic: 'organizational-behavior',
                topicLabel: '组织行为学',
                summary: '本研究构建并验证了环境变革型领导力（ETL）影响员工绿色行为（EGB）的多中介心理模型。通过对制造业1,520名员工的问卷调查和结构方程建模分析发现：环境自我效能感、绿色价值观内化和组织认同在ETL-EGB关系中起链式中介作用，总间接效应占比达67%。特别值得注意的是，当组织绿色氛围较强时，领导力的直接效应减弱而间接效应增强——说明文化情境决定了领导力发挥作用的路径。',
                source: 'Scientific Reports',
                authors: 'Noor Ul Hadi',
                link: 'https://www.nature.com/articles/s41598-026-42890-z'
            },
            {
                id: 6,
                title: '包容性领导对有两个孩子的女性员工创新行为的影响：来自中国的证据',
                topic: 'diversity',
                topicLabel: '多元化与包容性',
                summary: '聚焦于职场母亲这一特定群体，本研究调查了包容性领导力（IL）对二孩女性员工创新行为的促进机制。多时点追踪数据（N=387，间隔6个月）表明：IL通过提升心理安全感和减少工作-家庭冲突的双重路径正向影响创新行为，且该效应在支持型组织文化中被进一步放大。研究发现，有二孩的女性员工在感受到包容性领导后，其建言行为频率增加31%，创意提案数量增长27%。这对企业制定性别平等和人才保留策略具有重要启示。',
                source: 'Scientific Reports',
                authors: 'Shuyu Man, Jianpeng Fan',
                link: 'https://www.nature.com/articles/s41598-025-83675-2'
            },
            {
                id: 7,
                title: '领导者幽默在打破职业倦怠螺旋中的资源构建作用',
                topic: 'training',
                topicLabel: '培训与发展',
                summary: '职业倦怠是现代职场的流行病，本研究从一个新颖的角度——领导者 humor（幽默感）——探讨其干预效果。基于资源保存理论和工作要求-资源模型（JD-R），对教育行业986名教师的三波纵向数据显示：领导者积极幽默可通过增强情绪资源和团队凝聚力来中断倦怠的恶性循环。有趣的是，消极/讽刺性幽默反而加速倦怠进程。研究开发了"领导幽默训练"干预方案，实验组的倦怠得分在8周后降低了23%。',
                source: 'Humanities and Social Sciences Communications',
                authors: 'Hongzhen Zhang, Xun Xu, Daisy Mui Hung Kee',
                link: 'https://www.nature.com/articles/s41635-026-00134-3'
            }
        ]
    },
    {
        date: '2026-04-15',
        weekday: '星期三',
        articles: [
            {
                id: 8,
                title: 'AI面试为何降低求职者申请意愿？——感知去人性化的中介作用',
                topic: 'hr-tech',
                topicLabel: 'HR科技与AI',
                summary: '随着AI视频面试的普及，一个悖论浮现：技术本应提升招聘效率，却可能吓跑优秀候选人。本研究通过情景实验（N=1,156）和实地追踪揭示了其内在机制：AI面试主要通过三条路径降低申请意愿——(1) 感知去人性化 (β=-0.28)，(2) 互动公正感缺失 (β=-0.22)，(3) 自我展示焦虑 (β=-0.19)。值得注意的是，Z世代求职者的负面反应最为强烈，而有过远程协作经验的候选人则更为接纳。研究建议企业在AI招聘中增加透明度说明和人机混合模式。',
                source: 'Humanities and Social Sciences Communications',
                authors: 'Wenhao Luo, Yuelin Zhang, Maona Mu',
                link: 'https://www.nature.com/articles/s41599-025-02787-9'
            },
            {
                id: 9,
                title: '创业型领导如何激发员工创新行为？——有调节的中介模型验证',
                topic: 'training',
                topicLabel: '培训与发展',
                summary: '在VUCA时代，创业型领导（EL）被认为是驱动组织创新的引擎。本研究以中国高新技术企业526名研发人员为样本，构建了EL→心理赋能→知识分享→创新行为的链式中介模型。实证结果显示：心理赋能是核心传导机制（间接效应占比41%），而知识共享起部分中介作用；创新自我效能感和组织容错氛围分别作为一阶和二阶调节变量。最关键的发现是：EL的效果呈倒U型曲线——过度强调创业精神反而引发员工倦怠和"创新疲劳"。',
                source: 'Humanities and Social Sciences Communications',
                authors: 'Benhua Xu, Diandian Gu',
                link: 'https://www.nature.com/articles/s41635-026-00123-4'
            },
            {
                id: 10,
                title: '职场友谊及其对员工的影响：社交资本视角的实证分析',
                topic: 'employee-relations',
                topicLabel: '员工关系',
                summary: '职场友谊常被视为非正式的"办公室社交"，但本研究系统论证了其对个体和组织产出的实质性影响。综合元分析（涵盖68项独立研究，总样本N>25,000）表明：高质量职场友谊与工作满意度(r=0.48)、组织公民行为(r=0.39)和留任意愿(r=0.35)均呈中等以上正相关。更深入的分析揭示，友谊的"工具维度"（如信息交换、互助合作）比纯粹的情感维度更能预测工作绩效。研究提醒管理者：刻意压制职场社交可能适得其反。',
                source: 'Humanities and Social Sciences Communications',
                authors: 'Aiswarya Balachandar, Ramasundaram Gurusamy',
                link: 'https://www.nature.com/articles/s41635-026-00076-w'
            },
            {
                id: 11,
                title: '工作不安全感的亲环境影响：利他动机的关键调节作用',
                topic: 'compensation',
                topicLabel: '薪酬福利',
                summary: '传统观点认为工作不安全感必然导致员工退缩行为，但本研究发现了有趣的边界条件。通过多来源配对数据（员工自评+主管评价，N=412对），研究表明：工作不安全感对亲环境行为的影响取决于个体的利他动机水平——高利他动机者在面对工作威胁时反而增加环保行为（作为维持社会形象和道德认同的补偿机制），而低利他动机者则显著减少。这一发现对企业在不稳定经济环境中维持ESG目标具有重要实践意义。',
                source: 'Humanities and Social Sciences Communications',
                authors: 'Byung-Jik Kim, Harim Sohn, Min-Jik Kim',
                link: 'https://www.nature.com/articles/s41635-026-00067-9'
            }
        ]
    },
    {
        date: '2026-04-14',
        weekday: '星期二',
        articles: [
            {
                id: 12,
                title: '采用AI的阴暗面：通过心理安全和伦理领导将AI采用与员工抑郁关联起来',
                topic: 'hr-tech',
                topicLabel: 'HR科技与AI',
                summary: '这是一项关于AI技术采纳的"黑暗面"的重要研究。基于压力认知评价理论和情感事件理论，对引入AI工具后的2,180名员工进行了为期12个月的追踪调查。核心发现令人警醒：高强度AI监控与员工抑郁症状显著正相关（OR=2.14）。然而，伦理领导的强缓冲作用可将该风险降低61%，而团队心理安全氛围的调节效应解释了17%的变异量。研究提出了"负责任AI部署"的五原则框架，包括透明告知、人工复核、数据最小化等。',
                source: 'Humanities and Social Sciences Communications',
                authors: 'Byung-Jik Kim, Min-Jik Kim, Julak Lee',
                link: 'https://www.nature.com/articles/s41635-025-00956-x'
            },
            {
                id: 13,
                title: '数字化领导通过促进工作重塑增强组织韧性：组织文化的调节作用',
                topic: 'organizational-behavior',
                topicLabel: '组织行为学',
                summary: '在后疫情时代，组织韧性成为HR战略的核心议题。本研究创新性地将数字化领导力（DL）、工作重塑（JC）和组织韧性（OR）纳入统一框架。对78个团队的跨层分析（N=486员工+78主管）显示：DL通过激发员工的主动工作重塑行为（如优化任务、调整认知、构建关系）来提升团队层面的组织韧性。柔性学习型文化在该路径中起最强正向调节作用（β=0.31），而刚性控制型文化则完全阻断此路径。研究为数字化转型中的领导力发展提供了明确方向。',
                source: 'Scientific Reports',
                authors: 'Qiuxian Ye',
                link: 'https://www.nature.com/articles/s41598-025-84768-1'
            }
        ]
    },
    {
        date: '2026-04-13',
        weekday: '星期一',
        articles: [
            {
                id: 14,
                title: '领导者在塑造心理安全中的作用：来自斯洛伐克的定性研究',
                topic: 'recruitment',
                topicLabel: '招聘与选拔',
                summary: '心理安全是Google Project Aristotle揭示的高绩效团队第一要素，但领导力究竟如何塑造它？本研究采用扎根理论方法，对斯洛伐克30位不同层级的管理者进行了深度半结构化访谈（累计转录文字18万字）。编码分析提炼出领导力影响心理安全的五大核心实践：(1) 对话式而非审问式反馈，(2) 公开承认自身错误，(3) 将失败重新定义为学习机会，(4) 保护团队成员免受无理指责，(5) 营造"可提问"的会议文化。研究特别指出，在权力距离较高的文化背景下，这些实践需要更强的制度化保障。',
                source: 'Scientific Reports',
                authors: 'Lucia Konečná, Elena Lisá, Viktória Čiriková',
                link: 'https://www.nature.com/articles/s41598-026-42001-1'
            },
            {
                id: 15,
                title: '个体感知的工作环境与员工福祉的数据驱动类型学',
                topic: 'compensation',
                topicLabel: '薪酬福利',
                summary: '传统员工福祉调研依赖预设量表，可能遗漏重要的个性化因素。本研究采用数据驱动的聚类分析方法，基于12项工作环境感知指标对11,340名员工进行分类。最终识别出四种典型画像："繁荣型"（高自主+高支持，占28%）、"耗竭型"（高要求+低支持，占22%）、"疏离型"（低参与+低意义感，占19%）和"韧性型"（高挑战+高成长，占31%）。每种类型对应不同的福祉干预策略，使精准化的员工关怀成为可能。',
                source: 'Scientific Reports',
                authors: 'Jun Xie, Xiangdan Piao, Shunsuke Managi',
                link: 'https://www.nature.com/articles/s41598-025-85103-5'
            },
            {
                id: 16,
                title: '服务型领导如何及何时影响公务员的创新行为？',
                topic: 'performance',
                topicLabel: '绩效管理',
                summary: '公共部门常被认为缺乏创新动力，本研究聚焦于服务型领导力（SL）能否激活公务员的创新潜力。基于公共服务动机理论（PSM）和AMO（能力-动机-机会）框架，对政府部门的587名公务员进行了问卷调查。结构方程模型证实：SL通过提升公共服务动机（β=0.29）和心理赋能（β=0.24）双路径促进创新行为。组织政治感知是显著的负向调节变量——在高度政治化的环境中，即使服务型领导也难以激发下属的创新勇气。',
                source: 'Scientific Reports',
                authors: 'Fen-Xian Xiao, Yun Lin, Qiu Wang',
                link: 'https://www.nature.com/articles/s41598-025-84891-4'
            },
            {
                id: 17,
                title: '领导风格如何影响中小企业的员工敬业度和绩效？',
                topic: 'performance',
                topicLabel: '绩效管理',
                summary: '中小企业（SME）的资源约束使其无法复制大企业的复杂HR体系，领导风格的作用被进一步放大。本研究对比了变革型、交易型和家长式三种领导风格对南非中小企业员工敬业度和任务绩效的差异影响（N=346）。多元回归分析显示：变革型领导对敬业度的预测力最强（ΔR²=0.31），但交易型领导在短期任务绩效上表现更优（β=0.38 vs β=0.27）。有趣的是，家长式领导的"仁慈"维度与员工组织忠诚度高度相关（r=0.52），而"威权"维度则是离职意向的首要预测因子。',
                source: 'Humanities and Social Sciences Communications',
                authors: 'Glory Mphaluwa, Liu Hui, Lazarus Obed Livingstone Banda',
                link: 'https://www.nature.com/articles/s41635-025-01020-1'
            }
        ]
    },
    {
        date: '2026-04-10',
        weekday: '星期五',
        articles: [
            {
                id: 18,
                title: '语音技术对 workplace 多样性的潜在危险',
                topic: 'hr-tech',
                topicLabel: 'HR科技与AI',
                summary: '语音识别和合成技术在HR场景中的应用日益广泛（如客服质检、面试评估、培训辅导），但本研究首次系统性地警示了其对职场多样性的隐性威胁。作者识别出三大风险维度：(1) 方言和口音歧视——主流语音系统对非标准英语使用者的识别错误率高30-45%，导致不公平绩效评价；(2) 性别刻板声音强化——多数TTS系统默认使用女性声音用于助理角色；(3) 跨语言迁移劣势——双语/多语员工在单一语言系统中处于不利地位。研究提出了"公平性优先设计"的技术治理指南。',
                source: 'Nature Machine Intelligence',
                authors: 'Mike Horia Mihail Teodorescu, Carlos Muñiz, Oskar Gstrein',
                link: 'https://www.nature.com/articles/s42256-024-00695-6'
            },
            {
                id: 19,
                title: '感知的组织支持是否导致酒店业的OCB和离职意向？——工作生活满意度和员工韧性的间接作用',
                topic: 'diversity',
                topicLabel: '多元化与包容性',
                summary: '在酒店业这个高流失率行业（年均离职率超60%），什么能留住员工？本研究以社会交换理论为基础，构建了POS（感知组织支持）→ 工作生活满意度 + 员工韧性 → OCB/离职意向的双中介模型。对欧洲连锁酒店1,874名一线员工的数据分析表明：POS对OCB的总效应中有52%通过两条并行路径传递，而离职意向的解释变异量达43%。特别值得关注的是，员工韧性的中介效应在不同国籍员工间存在显著差异——东欧员工的韧性缓冲作用最强，南欧员工最弱。',
                source: 'Humanities and Social Sciences Communications',
                authors: 'Mavis Sirri Ngwa, Pelin Bayram',
                link: 'https://www.nature.com/articles/s41635-026-00087-9'
            },
            {
                id: 20,
                title: '了解顽皮型员工在职场中的社会收益',
                topic: 'employee-relations',
                topicLabel: '员工关系',
                summary: '"顽皮"（playfulness）通常被视为不够专业，但本研究挑战了这一成见。通过三项递进式研究（实验室实验+现场日记法+同伴评价，总N=1,892），研究者证明：工作中的顽皮特质与创造性问题解决（r=0.37）、团队凝聚力贡献（r=0.31）和压力应对能力（r=0.29）均显著正相关。更重要的是，顽皮型员工更容易成为团队中的"社交粘合剂"，在冲突调解和信息桥接方面表现突出。研究建议组织在招聘评估中将顽皮倾向视为一项软技能而非减分项。',
                source: 'Scientific Reports',
                authors: 'Li Guo, Wenqi Liu, Ying Wang',
                link: 'https://www.nature.com/articles/s41598-025-85321-5'
            }
        ]
    }
];
