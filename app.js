// ========== HR信息日报 - 前端主逻辑 ==========

// API 基础地址
const API_BASE = 'http://localhost:8082/api';

// 全局状态
let displayedCount = 0;
const ITEMS_PER_PAGE = 3;
let allData = [];
let currentFilter = {
    search: '',
    date: 'all',
    topic: 'all',
    source: 'all'
};

// 领域映射
const TOPIC_LABELS = {
    'recruitment': '招聘与选拔',
    'training': '培训与发展',
    'performance': '绩效管理',
    'compensation': '薪酬福利',
    'employee-relations': '员工关系',
    'hr-tech': 'HR科技与AI',
    'organizational-behavior': '组织行为学',
    'diversity': '多元化与包容性'
};

// ========== 页面初始化 ==========
document.addEventListener('DOMContentLoaded', async function() {
    await loadSources();
    await loadTopics();
    await loadStats();
    await loadCalendar();
    await loadArticles();
});

// ========== 加载来源分类 ==========
async function loadSources() {
    try {
        const response = await fetch(`${API_BASE}/sources`);
        const result = await response.json();

        if (result.code === 200) {
            const sourceSelect = document.getElementById('source-filter');

            // 清空现有选项（保留"全部来源"）
            sourceSelect.innerHTML = '<option value="all">全部来源</option>';

            result.data.forEach(source => {
                if (source.value !== 'all') {  // 跳过"all"，因为已有默认值
                    const option = document.createElement('option');
                    option.value = source.value;
                    option.textContent = source.label;
                    sourceSelect.appendChild(option);
                }
            });
        }
    } catch (error) {
        console.error('加载来源分类失败:', error);
    }
}

// ========== 加载领域分类 ==========
async function loadTopics() {
    try {
        const response = await fetch(`${API_BASE}/topics`);
        const result = await response.json();

        if (result.code === 200) {
            const topicSelect = document.getElementById('topic-filter');

            // 清空现有选项（保留"全部领域"）
            topicSelect.innerHTML = '<option value="all">全部领域</option>';

            result.data.forEach(topic => {
                const option = document.createElement('option');
                option.value = topic.value;
                option.textContent = topic.label;
                topicSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载领域分类失败:', error);
    }
}

// ========== 加载统计数据 ==========
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const result = await response.json();

        if (result.code === 200) {
            document.getElementById('total-articles').textContent = result.data.total_articles;
            document.getElementById('total-subscribers').textContent = result.data.total_subscribers;
        }

        // 加载系统状态
        const statusResponse = await fetch(`${API_BASE}/admin/status`);
        const statusResult = await statusResponse.json();

        if (statusResult.code === 200) {
            document.getElementById('latest-date').textContent = statusResult.data.last_push || '--';
            document.getElementById('next-push').textContent = statusResult.data.next_push || '--';
            document.getElementById('scheduler-status').textContent =
                statusResult.data.scheduler_running ? '🟢 运行中' : '🔴 已停止';
        }
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

// ========== 加载推送日历 ==========
async function loadCalendar() {
    try {
        const response = await fetch(`${API_BASE}/push-calendar?days=30`);
        const result = await response.json();

        if (result.code === 200) {
            // 更新日期筛选器
            const dateSelect = document.getElementById('date-filter');
            dateSelect.innerHTML = '<option value="all">全部日期</option>';

            // 只添加有文章的日期作为快捷筛选
            result.data.forEach(item => {
                if (item.article_count > 0) {
                    const option = document.createElement('option');
                    option.value = item.date;
                    option.textContent = `${item.date} ${item.weekday} (${item.article_count}篇)`;
                    dateSelect.appendChild(option);
                }
            });
        }
    } catch (error) {
        console.error('加载推送日历失败:', error);
    }
}

// ========== 加载文章列表 ==========
async function loadArticles() {
    try {
        const params = new URLSearchParams();
        if (currentFilter.date !== 'all') params.append('date', currentFilter.date);
        if (currentFilter.topic !== 'all') params.append('topic', currentFilter.topic);
        if (currentFilter.source !== 'all') params.append('source', currentFilter.source);
        if (currentFilter.search) params.append('search', currentFilter.search);

        params.append('page', '1');
        params.append('page_size', '100');

        const response = await fetch(`${API_BASE}/articles?${params}`);
        const result = await response.json();

        if (result.code === 200) {
            allData = result.data.articles || [];
            console.log(`[DEBUG] 加载文章: ${allData.length} 篇, 总计: ${result.data.total || 0}`);
            if (allData.length > 0) {
                console.log('[DEBUG] 第一篇示例:', {
                    title: allData[0].title?.substring(0, 30),
                    push_date: allData[0].push_date,
                    publish_date: allData[0].publish_date,
                    fetched_date: allData[0].fetched_date
                });
            }
            displayedCount = 0;
            renderCards();
        } else {
            console.error('[DEBUG] API 返回非 200:', result);
            showError(`加载文章失败: ${result.message || '未知错误'}`);
        }
    } catch (error) {
        console.error('加载文章列表失败:', error);
        showError('加载文章失败，请刷新页面重试');
    }
}

// ========== 按日期分组文章 ==========
function groupArticlesByDate(articles) {
    const groups = {};

    articles.forEach(article => {
        // 优先使用 push_date，其次 publish_date，再其次 fetched_date，最后 created_at
        let rawDate = article.push_date || article.publish_date || article.fetched_date || article.created_at;
        // 处理空字符串情况
        if (!rawDate || rawDate.trim() === '') {
            rawDate = article.created_at || '1970-01-01';
        }

        const date = rawDate.split(' ')[0];
        if (!groups[date]) {
            groups[date] = {
                date: date,
                weekday: getWeekday(date),
                articles: []
            };
        }
        groups[date].articles.push(article);
    });

    // 转换为数组并排序
    return Object.values(groups).sort((a, b) => b.date.localeCompare(a.date));
}

// ========== 渲染日期卡片 ==========
function renderCards() {
    const container = document.getElementById('cards-container');
    const filteredData = getFilteredData();
    const groupedData = groupArticlesByDate(filteredData);

    // 计算本次要渲染的天数
    const dataToShow = groupedData.slice(0, displayedCount + ITEMS_PER_PAGE);

    if (dataToShow.length === 0) {
        container.innerHTML = '';
        document.getElementById('empty-state').style.display = 'block';
        document.getElementById('load-more-container').style.display = 'none';
        return;
    }

    document.getElementById('empty-state').style.display = 'none';

    let html = '';
    dataToShow.forEach((day, index) => {
        html += createDateCardHTML(day, index);
    });

    container.innerHTML = html;
    displayedCount = dataToShow.length;

    // 控制加载更多按钮
    if (displayedCount >= groupedData.length) {
        document.getElementById('load-more-container').style.display = 'none';
    } else {
        document.getElementById('load-more-container').style.display = 'block';
    }
}

// ========== 创建日期卡片HTML ==========
function createDateCardHTML(day, index) {
    const articlesHTML = day.articles.map(article => createArticleCardHTML(article)).join('');

    return `
        <div class="date-card" style="animation-delay: ${index * 0.1}s">
            <div class="date-header">
                <div class="date-info">
                    <span class="date-badge">${formatDateDisplay(day.date)}</span>
                    <span class="date-weekday">${day.weekday}</span>
                </div>
                <span class="article-count-badge">📰 ${day.articles.length} 篇文章</span>
            </div>
            <div class="articles-list">
                ${articlesHTML}
            </div>
        </div>
    `;
}

// ========== 创建文章卡片HTML ==========
function createArticleCardHTML(article) {
    const sourceDisplay = article.source_short || article.source;
    const sourceClass = sourceDisplay === 'HBR' ? 'source-hbr' : 'source-nature';

    return `
        <div class="article-card">
            <div class="article-top">
                <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="article-title-link">
                    <h3 class="article-title">${escapeHtml(article.title)}</h3>
                </a>
                <span class="article-topic-tag topic-${article.topic}">${TOPIC_LABELS[article.topic] || article.topic_label || article.topic}</span>
            </div>
            <p class="article-summary">${escapeHtml(article.summary)}</p>
            <div class="article-footer">
                <div class="article-meta">
                    <span class="meta-item source-badge ${sourceClass}">
                        ${escapeHtml(sourceDisplay)}
                    </span>
                    <span class="meta-item">
                        <span class="icon">✍️</span>
                        ${escapeHtml(article.authors)}
                    </span>
                </div>
                <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="article-link" onclick="event.stopPropagation()">
                    查看原文 →
                </a>
            </div>
        </div>
    `;
}

// ========== 筛选功能 ==========
function getFilteredData() {
    let filtered = [...allData];

    // 搜索筛选
    if (currentFilter.search) {
        const search = currentFilter.search.toLowerCase();
        filtered = filtered.filter(article => {
            const searchableText = `${article.title} ${article.summary} ${article.authors} ${article.source}`.toLowerCase();
            return searchableText.includes(search);
        });
    }

    // 日期筛选（已经在API层面处理，但保留前端过滤作为备用）
    if (currentFilter.date !== 'all') {
        filtered = filtered.filter(article => {
            const date = article.push_date ? article.push_date.split(' ')[0] : '';
            return date === currentFilter.date;
        });
    }

    // 领域筛选
    if (currentFilter.topic !== 'all') {
        filtered = filtered.filter(article => article.topic === currentFilter.topic);
    }

    // 来源筛选
    if (currentFilter.source !== 'all') {
        filtered = filtered.filter(article => {
            return article.source_short === currentFilter.source ||
                   article.source === currentFilter.source ||
                   article.source.includes(currentFilter.source);
        });
    }

    return filtered;
}

function filterArticles() {
    currentFilter.search = document.getElementById('search-input').value;
    currentFilter.date = document.getElementById('date-filter').value;
    currentFilter.topic = document.getElementById('topic-filter').value;
    currentFilter.source = document.getElementById('source-filter').value;

    displayedCount = 0;
    renderCards();
}

// ========== 加载更多 ==========
function loadMore() {
    renderCards();
}

// ========== 文章详情弹窗 ==========
async function openArticleDetail(articleId) {
    let article = allData.find(a => a.id === articleId);
    if (!article) {
        // 从API获取详情
        try {
            const response = await fetch(`${API_BASE}/articles/${articleId}`);
            const result = await response.json();
            if (result.code === 200) {
                article = result.data;
            }
        } catch (error) {
            console.error('加载文章详情失败:', error);
            return;
        }
    }

    if (!article) return;

    const content = document.getElementById('article-detail-content');
    content.innerHTML = `
        <h2 class="detail-title">${escapeHtml(article.title)}</h2>
        <span class="detail-topic topic-${article.topic}">${TOPIC_LABELS[article.topic] || article.topic_label || article.topic}</span>

        <div class="detail-section">
            <h4>📋 内容提炼</h4>
            <p>${escapeHtml(article.summary)}</p>
        </div>

        <div class="detail-section">
            <h4>📚 来源期刊</h4>
            <p>${escapeHtml(article.source)}</p>
        </div>

        <div class="detail-section">
            <h4>✍️ 作者</h4>
            <p>${escapeHtml(article.authors)}</p>
        </div>

        <div class="detail-section">
            <h4>📅 发布日期</h4>
            <p>${article.publish_date}</p>
        </div>

        <div class="detail-section">
            <h4>🔗 原文链接</h4>
            <a href="${article.link}" target="_blank" rel="noopener noreferrer" class="detail-link">
                访问原始文章 →
            </a>
        </div>
    `;

    document.getElementById('article-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeArticleModal(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('article-modal').style.display = 'none';
    document.body.style.overflow = '';
}

// ========== 订阅弹窗 ==========
function handleSubscribe() {
    document.getElementById('subscribe-modal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('subscribe-modal').style.display = 'none';
    document.body.style.overflow = '';
}

async function submitSubscribe(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;

    // 获取选中的领域
    const checkboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');
    const interests = Array.from(checkboxes).map(cb => cb.value);

    try {
        const response = await fetch(`${API_BASE}/subscribe`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, interests })
        });

        const result = await response.json();

        if (result.code === 200) {
            alert(`✅ 订阅成功！\n\n邮箱：${email}\n推送时间：每日中午 12:00\n\n您将收到人力资源管理领域的最新学术动态。`);
            closeModal();
            loadStats(); // 更新统计
        } else {
            alert(`❌ 订阅失败：${result.message}`);
        }
    } catch (error) {
        alert('❌ 订阅失败，请稍后重试');
        console.error('订阅请求失败:', error);
    }
}

// ========== 工具函数 ==========
function formatDateDisplay(dateStr) {
    const date = new Date(dateStr);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${month}月${day}日`;
}

function getWeekday(dateStr) {
    const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
    const date = new Date(dateStr);
    return weekdays[date.getDay()];
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    const container = document.getElementById('cards-container');
    container.innerHTML = `
        <div class="empty-state" style="display: block;">
            <div class="empty-icon">❌</div>
            <h3>加载失败</h3>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
}

// ========== 键盘快捷键 ==========
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
        closeArticleModal();
    }
});
