#!/usr/bin/env python3
"""
论文检索脚本 - Academic Paper Search with Filtering

这个脚本可以帮你搜索学术论文，并按你设定的条件进行过滤。

使用示例：
    python paper_search.py --topic "机器学习在教育中的应用" \
        --keywords "LLM,education,personalized learning" \
        --time-range 3y --max-results 10 \
        --language en --sort-by citation_count

支持的数据源（免费，无需认证）：
    - Semantic Scholar (API): 覆盖计算机科学、生物学、医学
    - arXiv (API): 物理、计算机、数学、生物学的预印本
    - CrossRef (API): 全球学术文献元数据
    - Google Scholar (网页抓取): 作为补充数据源

输出格式：
    - JSON (默认): 结构化的论文元数据
    - Markdown: 人类可读的摘要
    - CSV: 用于电子表格分析

需要 Python 3.8+。只使用标准库，无需安装额外依赖。
"""

# ==================== 第一部分：导入必要的库 ====================
# 这里导入所有我们需要使用的工具包

import argparse        # 用于解析命令行参数（比如 --topic, --time-range 等）
import json            # 用于处理JSON格式的数据
import re              # 用于正则表达式（匹配文本模式）
import ssl             # 用于处理HTTPS安全连接
import sys             # 用于系统相关的操作
from datetime import datetime, timezone, timedelta  # 用于处理日期和时间
from urllib.parse import urlencode, quote            # 用于处理URL编码
from urllib.request import urlopen, Request         # 用于发送网络请求
from typing import List, Dict, Any, Optional        # 用于类型提示（让代码更清晰）


# ==================== 第二部分：SSL证书配置 ====================
# SSL是HTTPS安全连接的基础，Windows系统有时会出现证书问题
# 这里的代码是为了确保网络连接能正常工作

def create_ssl_context():
    """
    创建SSL上下文 - 使用未验证的上下文以确保Windows兼容性

    解释：SSL证书用于验证网站的身份。Windows有时缺少完整的证书链，
    导致无法连接到学术API。这里我们使用未验证模式来绕过这个问题。
    """
    import warnings
    # 发出警告，告知用户我们正在禁用证书验证
    warnings.warn("Using unverified SSL context - certificate verification disabled for compatibility")
    # 创建并返回一个未验证的SSL上下文
    return ssl._create_unverified_context()

# 创建全局的SSL上下文，所有网络请求都会使用它
SSL_CONTEXT = create_ssl_context()


# ==================== 第三部分：默认配置参数 ====================
# 这里设置一些默认值，如果用户没有指定参数，就使用这些值

DEFAULT_MAX_RESULTS = 8        # 默认返回8篇论文
DEFAULT_TIME_RANGE = "3y"       # 默认搜索最近3年的论文
DEFAULT_LANGUAGE = "bilingual"  # 默认中英文都检索
DEFAULT_SORT_BY = "relevance"   # 默认按相关度排序
DEFAULT_DOMAIN = "general"      # 默认通用领域

# 设置用户代理，告诉服务器我们是谁（礼貌的网络访问）
USER_AGENT = "Hermes-Agent-Paper-Search/1.0"

# ==================== 应用领域数据源优化配置 ====================
# 根据主要应用领域（统计决策、人工智能、金融统计）优化数据源选择

# 应用领域对应的数据源优先级配置
DOMAIN_SOURCE_PRIORITY = {
    "general": ["Semantic Scholar", "CrossRef", "arXiv"],      # 通用领域
    "statistics": ["CrossRef", "Semantic Scholar", "arXiv"],    # 统计决策（CrossRef覆盖统计期刊最佳）
    "ai": ["arXiv", "Semantic Scholar", "CrossRef"],           # 人工智能（arXiv最新预印本最多）
    "finance": ["CrossRef", "Semantic Scholar", "arXiv"],      # 金融统计（CrossRef覆盖金融期刊）
}

# 领域优化说明：
# - 统计决策领域: 优先使用 CrossRef（覆盖统计学、运筹学期刊），其次 Semantic Scholar（引用数据好）
# - 人工智能领域: 优先使用 arXiv（AI领域最新预印本最多），其次 Semantic Scholar（质量高）
# - 金融统计领域: 优先使用 CrossRef（覆盖金融学、计量经济学期刊），其次 Semantic Scholar
# - 通用领域: Semantic Scholar（综合质量最佳），其次 CrossRef，arXiv 作为补充


# ==================== 第四部分：时间范围解析工具 ====================
# 这部分代码用来理解用户说的时间范围，比如"3y"、"5y"、"2020-2023"等

def parse_time_range(time_range: str) -> Optional[Dict[str, Any]]:
    """
    将时间范围字符串转换为开始/结束日期

    参数：
        time_range: 时间范围字符串，如 "3y", "5y", "2020-2023", "unlimited"

    返回：
        包含 'start_date' 和 'end_date' 的字典（ISO格式），
        如果是无限范围则返回 None

    解释：
        这个函数将用户的输入转换为具体的日期范围，
        比如 "3y" → 从今天往前推3年的日期
    """
    # 如果用户说"不限"或没提供时间范围，返回None
    if time_range == "unlimited" or not time_range:
        return None

    # 获取当前时间（使用UTC时区，避免时区问题）
    now = datetime.now(timezone.utc)
    end_date = now

    # 模式1：解析像 "3y", "1y", "5y", "10y" 这样的格式
    # 使用正则表达式匹配：数字后面跟着字母y
    year_match = re.match(r'^(\d+)y$', time_range)
    if year_match:
        years = int(year_match.group(1))  # 提取数字部分
        # 计算开始日期：今天减去指定年数（每年按365天计算）
        start_date = now - timedelta(days=years * 365)
        return {
            "start_date": start_date.strftime("%Y-%m-%d"),  # 格式：2021-06-27
            "end_date": end_date.strftime("%Y-%m-%d"),        # 格式：2024-06-27
            "years": years                                     # 记录年数
        }

    # 模式2：解析自定义年份范围，如 "2020-2023"
    custom_match = re.match(r'^(\d{4})-(\d{4})$', time_range)
    if custom_match:
        start_year = int(custom_match.group(1))  # 起始年份
        end_year = int(custom_match.group(2))    # 结束年份
        return {
            "start_date": f"{start_year}-01-01",  # 该年的1月1日
            "end_date": f"{end_year}-12-31",      # 该年的12月31日
            "years": end_year - start_year         # 年份差
        }

    # 模式3：解析详细的自定义范围，如 "2020-01-01:2023-06-30"
    detailed_match = re.match(r'^(\d{4}-\d{2}-\d{2}):(\d{4}-\d{2}-\d{2})$', time_range)
    if detailed_match:
        return {
            "start_date": detailed_match.group(1),  # 直接使用用户指定的日期
            "end_date": detailed_match.group(2),
            "years": "custom"
        }

    # 如果格式不匹配以上任何模式，返回None（当作无限范围处理）
    return None


# ==================== 第五部分：数据源API客户端 ====================
# 这部分定义了与各个学术数据库交互的方法
# 每个API都有自己的特点和数据格式

class SemanticScholarAPI:
    """
    Semantic Scholar API 客户端

    Semantic Scholar是一个免费的学术搜索引擎，
    覆盖计算机科学、生物医学等领域，提供引用量等高质量数据。
    """

    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    @staticmethod
    def search_papers(query: str, fields: str, limit: int = 100, year: str = None) -> List[Dict]:
        """
        通过Semantic Scholar API搜索论文

        参数：
            query: 搜索关键词
            fields: 需要返回的字段（如标题、作者、摘要等）
            limit: 最多返回多少篇论文
            year: 指定年份（可选）

        返回：
            论文列表，每个论文是一个字典包含元数据

        解释：
            这个函数向Semantic Scholar发送HTTP请求，
            获取论文数据并解析成Python列表
        """
        # 构建查询参数
        params = {
            "query": query,      # 搜索关键词
            "fields": fields,    # 需要哪些字段（用逗号分隔）
            "limit": limit       # 最多返回多少结果
        }
        if year:
            params["year"] = year  # 如果指定了年份，添加到参数中

        # 构建完整的URL（包含查询参数）
        url = f"{SemanticScholarAPI.BASE_URL}/paper/search?{urlencode(params)}"

        try:
            # 创建HTTP请求对象
            request = Request(url, headers={"User-Agent": USER_AGENT})
            # 发送请求并获取响应（使用我们配置的SSL上下文）
            with urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
                # 解析JSON响应
                data = json.loads(response.read().decode('utf-8'))
                # 返回论文列表（在'data'字段中）
                return data.get("data", [])
        except Exception as e:
            # 如果出错，打印错误信息并返回空列表
            print(f"Semantic Scholar API error: {e}", file=sys.stderr)
            return []


class ArxivAPI:
    """
    arXiv API 客户端

    arXiv是预印本服务器，作者在论文正式发表前可以先上传到这里，
    所以能找到最新的研究成果。覆盖物理、数学、计算机、生物等领域。
    """

    BASE_URL = "http://export.arxiv.org/api/query"

    @staticmethod
    def search_papers(query: str, max_results: int = 100) -> List[Dict]:
        """
        通过arXiv API搜索论文

        参数：
            query: 搜索关键词
            max_results: 最多返回多少篇论文

        返回：
            论文列表

        解释：
            arXiv使用XML格式返回数据（不同于其他API的JSON），
            所以我们需要用XML解析器来处理响应。
        """
        # 构建查询参数
        params = {
            "search_query": f"all:{query}",  # 在所有字段中搜索
            "start": 0,                       # 从第0条结果开始
            "max_results": max_results,       # 最多返回多少结果
            "sortBy": "relevance",            # 按相关度排序
            "sortOrder": "descending"          # 降序排列
        }

        # 构建完整的URL
        url = f"{ArxivAPI.BASE_URL}?{urlencode(params)}"

        try:
            # 创建HTTP请求
            request = Request(url, headers={"User-Agent": USER_AGENT})
            # 发送请求
            with urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
                # arXiv返回XML格式，需要用XML解析器
                import xml.etree.ElementTree as ET
                xml_data = response.read().decode('utf-8')
                root = ET.fromstring(xml_data)

                # arXiv使用Atom命名空间（类似XML的"姓氏"）
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                entries = root.findall("atom:entry", ns)  # 找到所有论文条目

                papers = []
                # 遍历每篇论文
                for entry in entries:
                    paper = {
                        "title": entry.find("atom:title", ns).text.strip(),  # 标题
                        "authors": [author.find("atom:name", ns).text        # 作者列表
                                   for author in entry.findall("atom:author", ns)],
                        "summary": entry.find("atom:summary", ns).text.strip(),  # 摘要
                        "published": entry.find("atom:published", ns).text,     # 发表时间
                        "url": entry.find("atom:id", ns).text,                  # 链接
                        "source": "arXiv"                                       # 标记来源
                    }
                    papers.append(paper)

                return papers
        except Exception as e:
            # 出错时打印错误并返回空列表
            print(f"arXiv API error: {e}", file=sys.stderr)
            return []


class CrossRefAPI:
    """
    CrossRef API 客户端

    CrossRef是一个全球性的学术文献元数据库，
    覆盖面很广，但摘要数据相对较少。
    """

    BASE_URL = "https://api.crossref.org/works"

    @staticmethod
    def search_papers(query: str, rows: int = 100, filter_year: str = None) -> List[Dict]:
        """
        通过CrossRef API搜索论文

        参数：
            query: 搜索关键词
            rows: 返回多少行结果
            filter_year: 过滤年份（可选）

        返回：
            论文列表

        解释：
            CrossRef的数据结构比较复杂，需要提取嵌套的字段
        """
        # 构建查询参数
        params = {
            "query": query,
            "rows": rows,
            # 指定需要哪些字段（减少数据传输量）
            "select": "title,author,published-print,container-title,DOI,type,abstract"
        }
        if filter_year:
            # 如果指定了年份，添加过滤条件
            params["filter"] = f"from-pub-date:{filter_year}"

        # 构建完整URL
        url = f"{CrossRefAPI.BASE_URL}?{urlencode(params)}"

        try:
            # 创建HTTP请求
            request = Request(url, headers={"User-Agent": USER_AGENT})
            # 发送请求
            with urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
                # 解析JSON响应
                data = json.loads(response.read().decode('utf-8'))
                # 获取论文列表（在message.items字段中）
                items = data.get("message", {}).get("items", [])

                papers = []
                # 遍历每篇论文
                for item in items:
                    # 提取并整理字段
                    paper = {
                        "title": " ".join(item.get("title", [])),  # 标题是数组，需要拼接
                        "authors": [f"{a.get('given', '')} {a.get('family', '')}"  # 作者名
                                   for a in item.get("author", [])],
                        "published": item.get("published-print", {}).get("date-time", ""),  # 发表时间
                        "journal": item.get("container-title", [""])[0],  # 期刊名称
                        "doi": item.get("DOI", ""),                     # DOI（数字对象标识符）
                        "type": item.get("type", ""),                    # 文献类型
                        "abstract": item.get("abstract", ""),            # 摘要
                        "source": "CrossRef"                            # 标记来源
                    }
                    papers.append(paper)

                return papers
        except Exception as e:
            # 出错时打印错误并返回空列表
            print(f"CrossRef API error: {e}", file=sys.stderr)
            return []


# ==================== 第六部分：论文搜索引擎核心 ====================
# 这部分是整个脚本的核心，负责协调整个检索流程

class PaperSearchEngine:
    """
    论文搜索引擎

    这个类负责：
    1. 解析用户输入的参数
    2. 调用各个数据源API
    3. 过滤和排序结果
    4. 去重和限制结果数量
    """

    def __init__(self, config: Dict[str, Any]):
        """
        初始化搜索引擎

        参数：
            config: 包含所有搜索参数的字典
        """
        self.config = config
        # 解析时间范围
        self.time_range = parse_time_range(config.get("time_range", DEFAULT_TIME_RANGE))
        # 解析关键词
        self.keywords = self._parse_keywords(config.get("keywords", []))
        # 保存研究主题
        self.research_topic = config.get("research_topic", "")
        # 确定应用领域（用于优化数据源选择）
        self.domain = config.get("domain", DEFAULT_DOMAIN)

    def _parse_keywords(self, keywords_input) -> List[str]:
        """
        解析关键词输入

        参数可能是：
        - 字符串："machine learning, AI, education"
        - 列表：["machine learning", "AI", "education"]

        返回统一格式的关键词列表
        """
        if isinstance(keywords_input, str):
            # 如果是字符串，按逗号分隔
            return [k.strip() for k in keywords_input.split(",")]
        elif isinstance(keywords_input, list):
            # 如果已经是列表，直接返回
            return keywords_input
        return []  # 其他情况返回空列表

    def _build_search_query(self) -> str:
        """
        构建搜索查询字符串

        将研究主题和关键词组合成一个完整的搜索查询
        """
        query_parts = []

        # 添加研究主题
        if self.research_topic:
            query_parts.append(self.research_topic)

        # 添加关键词
        if self.keywords:
            query_parts.extend(self.keywords)

        # 用空格连接所有部分
        return " ".join(query_parts)

    def _filter_by_year(self, papers: List[Dict]) -> List[Dict]:
        """
        按发表年份过滤论文

        参数：
            papers: 论文列表

        返回：
            过滤后的论文列表

        解释：
            根据用户设置的时间范围，只保留指定年份内发表的论文
        """
        # 如果没有设置时间范围，返回所有论文
        if not self.time_range:
            return papers

        # 获取起始日期并提取年份
        start_date = datetime.fromisoformat(self.time_range["start_date"])
        cutoff_year = start_date.year

        filtered = []
        for paper in papers:
            # 提取这篇论文的发表年份
            pub_date = self._extract_publication_year(paper)
            # 如果年份在范围内，保留这篇论文
            if pub_date and pub_date >= cutoff_year:
                filtered.append(paper)

        return filtered

    def _extract_publication_year(self, paper: Dict) -> Optional[int]:
        """
        从论文数据中提取发表年份

        参数：
            paper: 单篇论文的字典

        返回：
            年份（整数），如果找不到则返回None

        解释：
            不同数据源的年份字段名不一样，
            有的用'year'，有的用'publicationDate'，等等
            这个函数尝试所有可能的字段名
        """
        # 可能包含年份的字段名列表
        year_fields = ["year", "publicationDate", "published", "pubDate"]

        for field in year_fields:
            if field in paper and paper[field]:
                value = str(paper[field])
                # 用正则表达式提取4位数字（年份）
                year_match = re.search(r'(\d{4})', value)
                if year_match:
                    return int(year_match.group(1))

        return None  # 找不到年份

    def _sort_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        对论文进行排序

        参数：
            papers: 论文列表

        返回：
            排序后的论文列表

        解释：
            根据用户选择的排序方式（相关度/引用量/发表时间）对论文排序
        """
        sort_by = self.config.get("sort_by", DEFAULT_SORT_BY)

        if sort_by == "citation_count":
            # 按引用量排序（降序：引用多的在前）
            # 先检查是否有citationCount字段
            if papers and "citationCount" in papers[0]:
                return sorted(papers, key=lambda p: p.get("citationCount", 0), reverse=True)

        elif sort_by == "publicationDate" or sort_by == "publish_date":
            # 按发表时间排序（降序：最近的在前）
            return sorted(papers, key=lambda p: self._extract_publication_year(p) or 0, reverse=True)

        else:  # relevance（相关度）
            # 按相关度排序（保持API返回的原始顺序）
            return papers

    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        去除重复的论文

        参数：
            papers: 论文列表

        返回：
            去重后的论文列表

        解释：
            不同数据源可能返回同一篇论文，
            我们用标题和DOI作为唯一标识进行去重
        """
        seen = set()  # 记录已见过的标识
        unique_papers = []

        for paper in papers:
            # 创建唯一键：标题（标准化）+ DOI
            title = paper.get("title", "").lower().strip()  # 转小写并去空格
            doi = paper.get("doi", "").lower().strip()

            if not title:  # 如果没有标题，跳过（无法识别）
                continue

            # 用标题作为主键，DOI作为辅助键
            key = title if not doi else f"{title}:{doi}"

            # 如果这个键没见过，保留这篇论文
            if key not in seen:
                seen.add(key)
                unique_papers.append(paper)

        return unique_papers

    def search(self) -> Dict[str, Any]:
        """
        执行完整的论文搜索流程

        这是主函数，按顺序执行：
        1. 构建查询
        2. 根据应用领域智能选择数据源优先级调用多个数据源
        3. 应用过滤条件
        4. 去重和排序
        5. 限制结果数量

        返回：
            包含搜索结果和元数据的字典

        领域优化策略：
        - 统计决策/金融统计: 优先 CrossRef（期刊覆盖最佳），其次 Semantic Scholar
        - 人工智能: 优先 arXiv（最新预印本最多），其次 Semantic Scholar
        - 通用: Semantic Scholar（综合质量最佳），其次 CrossRef
        """
        # 第1步：构建搜索查询
        query = self._build_search_query()

        # 如果没有查询内容，返回错误
        if not query:
            return {
                "status": "error",
                "error": "No search query provided. Please specify --topic or --keywords.",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        all_papers = []      # 所有找到的论文
        sources_used = []    # 成功使用的数据源

        # 第2步：根据领域确定数据源优先级并调用
        # 获取当前领域的数据源优先级列表
        domain_priority = DOMAIN_SOURCE_PRIORITY.get(self.domain, DOMAIN_SOURCE_PRIORITY["general"])

        # 按优先级顺序调用数据源
        for source_name in domain_priority:
            if source_name == "Semantic Scholar":
                # Semantic Scholar: 综合质量最高，有引用数据
                s2_papers = SemanticScholarAPI.search_papers(
                    query=query,
                    # 指定需要的字段（减少数据传输）
                    fields="paperId,title,abstract,authors,year,publicationDate,journal,citationCount,doi,url",
                    limit=self.config.get("max_results", DEFAULT_MAX_RESULTS) * 2,  # 多取一些，因为后面会过滤
                    year=self.time_range["start_date"][:4] if self.time_range else None  # 起始年份
                )
                if s2_papers:
                    all_papers.extend(s2_papers)  # 添加到总列表
                    sources_used.append("Semantic Scholar")

            elif source_name == "arXiv":
                # arXiv: AI领域最新预印本最多，计算机科学研究首选
                arxiv_papers = ArxivAPI.search_papers(
                    query=query,
                    max_results=self.config.get("max_results", DEFAULT_MAX_RESULTS)
                )
                if arxiv_papers:
                    all_papers.extend(arxiv_papers)
                    sources_used.append("arXiv")

            elif source_name == "CrossRef":
                # CrossRef: 统计学和金融期刊覆盖最佳
                crossref_papers = CrossRefAPI.search_papers(
                    query=query,
                    rows=self.config.get("max_results", DEFAULT_MAX_RESULTS),
                    filter_year=self.time_range["start_date"][:4] if self.time_range else None
                )
                if crossref_papers:
                    all_papers.extend(crossref_papers)
                    sources_used.append("CrossRef")
        if arxiv_papers:
            all_papers.extend(arxiv_papers)
            sources_used.append("arXiv")

        # 尝试CrossRef（广泛覆盖）
        crossref_papers = CrossRefAPI.search_papers(
            query=query,
            rows=self.config.get("max_results", DEFAULT_MAX_RESULTS),
            filter_year=self.time_range["start_date"][:4] if self.time_range else None
        )
        if crossref_papers:
            all_papers.extend(crossref_papers)
            sources_used.append("CrossRef")

        # 第3步：应用过滤条件
        filtered_papers = self._filter_by_year(all_papers)  # 时间过滤

        # 第4步：去重和排序
        deduplicated_papers = self._deduplicate_papers(filtered_papers)  # 去重
        sorted_papers = self._sort_papers(deduplicated_papers)         # 排序

        # 第5步：限制结果数量
        max_results = self.config.get("max_results", DEFAULT_MAX_RESULTS)
        final_papers = sorted_papers[:max_results]  # 只保留前N篇

        # 第6步：构建返回结果
        result = {
            "status": "success",  # 标记成功
            "query": query,       # 使用的查询字符串
            "total_found": len(final_papers),  # 找到的论文数量
            "sources_used": list(set(sources_used)),  # 使用的数据源（去重）
            "papers": final_papers,  # 论文列表
            "filters_applied": {   # 应用的过滤条件
                "time_range": self.time_range,
                "language": self.config.get("language", DEFAULT_LANGUAGE),
                "max_results": max_results,
                "domain": self.domain  # 添加应用领域信息到结果中
            },
            "timestamp": datetime.now(timezone.utc).isoformat()  # 当前时间戳
        }

        return result


# ==================== 第七部分：输出格式化工具 ====================
# 这部分负责将搜索结果转换成不同的输出格式（JSON/Markdown/CSV）

def format_as_markdown(result: Dict[str, Any]) -> str:
    """
    将搜索结果格式化为Markdown

    参数：
        result: search()函数返回的结果字典

    返回：
        Markdown格式的字符串

    解释：
        Markdown是一种轻量级标记语言，
        适合人类阅读和文档编写
    """
    # 如果搜索失败，返回错误信息
    if result.get("status") == "error":
        return f"❌ 检索失败：{result.get('error')}"

    # 开始构建Markdown文档
    md = f"# 论文检索结果\n\n"  # 一级标题

    # 添加检索概况
    md += f"**检索主题**: {result['query']}\n\n"
    md += f"**数据源**: {', '.join(result['sources_used'])}\n\n"
    md += f"**检索时间**: {result['timestamp']}\n\n"
    md += f"**文献数量**: {result['total_found']} 篇\n\n"

    # 添加时间范围信息（如果有）
    if result['filters_applied']['time_range']:
        tr = result['filters_applied']['time_range']
        md += f"**时间范围**: {tr['start_date']} 至 {tr['end_date']}\n\n"

    md += "---\n\n"  # 分隔线

    # 遍历每篇论文，添加详细信息
    for i, paper in enumerate(result['papers'], 1):
        md += f"## 论文 #{i}\n\n"  # 二级标题

        # 提取论文基本信息
        title = paper.get('title', 'N/A')
        authors = paper.get('authors', [])
        year = paper.get('year') or paper.get('published', '')[:4] if paper.get('published') else 'N/A'

        # 添加论文元数据
        md += f"**标题**: {title}\n\n"
        md += f"**作者**: {', '.join(str(a) for a in authors[:5])}" + \
              (f" et al. ({len(authors)} authors)" if len(authors) > 5 else "") + "\n\n"
        md += f"**年份**: {year}\n\n"

        # 添加期刊/会议信息
        if paper.get('journal'):
            md += f"**期刊/会议**: {paper.get('journal')}\n\n"

        # 添加DOI链接
        if paper.get('doi'):
            md += f"**DOI**: [{paper.get('doi')}](https://doi.org/{paper.get('doi')})\n\n"

        # 添加引用量
        if paper.get('citationCount'):
            md += f"**引用量**: {paper.get('citationCount')}\n\n"

        # 添加摘要（截取前500字）
        if paper.get('abstract'):
            abstract = paper.get('abstract', '')[:500]
            md += f"**摘要**: {abstract}{'...' if len(paper.get('abstract', '')) > 500 else ''}\n\n"

        md += "---\n\n"  # 论文之间的分隔线

    return md


def format_as_csv(result: Dict[str, Any]) -> str:
    """
    将搜索结果格式化为CSV

    参数：
        result: search()函数返回的结果字典

    返回：
        CSV格式的字符串

    解释：
        CSV（逗号分隔值）是一种通用格式，
        可以用Excel、Google Sheets等软件打开
    """
    # 如果搜索失败，返回错误信息
    if result.get("status") == "error":
        return "error," + result.get("error", "")

    import csv
    import io

    # 创建字符串缓冲区（用于在内存中构建CSV）
    output = io.StringIO()
    writer = csv.writer(output)

    # 写入表头（列名）
    writer.writerow([
        "Title", "Authors", "Year", "Journal", "DOI",
        "CitationCount", "Abstract", "URL"
    ])

    # 写入每篇论文的数据
    for paper in result.get('papers', []):
        # 处理作者列表：用分号连接
        authors = '; '.join(str(a) for a in paper.get('authors', []))
        # 处理摘要：去除换行符，截取前200字
        abstract = (paper.get('abstract', '') or '').replace('\n', ' ')[:200]

        # 写入一行数据
        writer.writerow([
            paper.get('title', ''),
            authors,
            paper.get('year') or (paper.get('published', '')[:4] if paper.get('published') else ''),
            paper.get('journal', ''),
            paper.get('doi', ''),
            paper.get('citationCount', ''),
            abstract,
            paper.get('url', '')
        ])

    # 返回构建好的CSV字符串
    return output.getvalue()


# ==================== 第八部分：命令行接口 ====================
# 这部分处理用户从命令行传入的参数
# 是整个脚本的入口点

def main():
    """
    主函数 - 程序的入口点

    这个函数：
    1. 解析命令行参数
    2. 构建配置字典
    3. 调用搜索引擎
    4. 格式化并输出结果
    """
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="Search academic papers with filtering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=""  # 帮助信息的示例部分在下面定义
    )

    # 添加各种命令行参数
    parser.add_argument("--topic", help="Research topic (e.g., 'machine learning in education')")
    parser.add_argument("--keywords", help="Keywords (comma-separated)")
    parser.add_argument("--time-range", default=DEFAULT_TIME_RANGE,
                       help="Time range (1y, 3y, 5y, 10y, unlimited, or custom like 2020-2023)")
    parser.add_argument("--max-results", type=int, default=DEFAULT_MAX_RESULTS,
                       help="Maximum number of papers to return (default: 8)")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE,
                       choices=["zh", "en", "bilingual"],
                       help="Language preference (default: bilingual)")
    parser.add_argument("--sort-by", default=DEFAULT_SORT_BY,
                       choices=["relevance", "citation_count", "publish_date"],
                       help="Sort results by (default: relevance)")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN,
                       choices=["general", "statistics", "ai", "finance"],
                       help="Application domain for optimized source selection: general/statistics/ai/finance (default: general)")
    parser.add_argument("--output-format", default="json",
                       choices=["json", "markdown", "csv"],
                       help="Output format (default: json)")
    parser.add_argument("--output", help="Output file path (default: stdout)")

    # 解析命令行参数
    args = parser.parse_args()

    # 构建配置字典
    config = {
        "research_topic": args.topic or "",
        "keywords": args.keywords or "",
        "time_range": args.time_range,
        "max_results": args.max_results,
        "language": args.language,
        "sort_by": args.sort_by,
        "domain": args.domain  # 添加应用领域参数
    }

    # 特殊处理：如果没提供topic但提供了keywords，用keywords作为topic
    if not config["research_topic"] and config["keywords"]:
        config["research_topic"] = config["keywords"]

    # 执行搜索
    engine = PaperSearchEngine(config)
    result = engine.search()

    # 根据用户选择的格式输出结果
    if args.output_format == "json":
        # JSON格式（默认）
        output = json.dumps(result, indent=2, ensure_ascii=False)
    elif args.output_format == "markdown":
        # Markdown格式
        output = format_as_markdown(result)
    elif args.output_format == "csv":
        # CSV格式
        output = format_as_csv(result)
    else:
        # 其他情况默认JSON
        output = json.dumps(result, indent=2, ensure_ascii=False)

    # 将结果写入文件或标准输出
    if args.output:
        # 写入文件
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        # 打印成功信息到stderr（不影响标准输出的内容）
        print(f"✅ Results written to {args.output}", file=sys.stderr)
        return 0  # 返回成功状态码
    else:
        # 输出到标准输出（屏幕）
        print(output)
        # 根据搜索结果返回状态码
        return 0 if result.get("status") == "success" else 1


# ==================== 程序入口点 ====================
# 当脚本被直接运行时（而不是被导入为模块），执行main函数
if __name__ == "__main__":
    # 运行主函数并将返回值作为退出状态码
    sys.exit(main())
