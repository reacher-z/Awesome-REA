"""Visible contribution answers shared by the bilingual static discovery pages."""
from html import escape

TITLES = ('Contribute to Awesome REA', '向 Awesome REA 投稿与贡献')
FORMS = (
    ('resource.yml', 'Suggest a tool or resource', '推荐工具或资源'),
    ('case-study.yml', 'Suggest a reconstruction case', '推荐重建案例'),
    ('paper.yml', 'Suggest a research paper', '推荐研究论文'),
    ('broken-resource.yml', 'Report an outdated entry', '修正过时条目'),
    ('translation.yml', 'Correct a translation', '修正翻译'),
)


def contribution_content(repository_url, language):
    zh = language == 'zh'
    if language not in ('en', 'zh'):
        raise ValueError('Contribution language must be en or zh')
    repo = repository_url.rstrip('/')
    guide = 'docs/agent-contributing' + ('.zh-CN' if zh else '') + '.md'
    rules = 'CONTRIBUTING.zh-CN.md' if zh else 'CONTRIBUTING.md'

    def link(path, label):
        return '<a href="' + escape(repo + path, quote=True) + '">' + escape(label) + '</a>'

    forms = ''.join(link('/issues/new?template=' + name, chinese if zh else english)
                    for name, english, chinese in FORMS)
    intro = ('通过 GitHub 表单推荐逆向工程工具、重建案例或论文；能够补齐一手证据和中英文记录时，也可直接提交 PR。'
             if zh else 'Suggest reverse-engineering tools, reconstruction cases or papers through GitHub forms, or submit a PR with primary evidence and English/Chinese records.')
    first = ('先按规范 URL、项目名或论文标识搜索精选目录与已开启的 issue、PR。已有提议时更新原提议，不重复提交。'
             if zh else 'Search the curated catalog and open issues/PRs by canonical URL, project name or paper identifier. Update an existing submission instead of creating a duplicate.')
    evidence = ('提供维护者原始链接、资源类型、目标领域、前提条件与局限，并用一手来源支持声明。固定 GitHub 证据链接到复核的 commit；不清楚的事实写 unknown。'
                if zh else 'Supply the maintainer’s original URL, resource type, target areas, prerequisites and limits. Support claims with primary sources, pin GitHub evidence to the reviewed commit and mark unknown facts explicitly.')
    edit = ('独立资源写入 data/tool-resources.json，证据支持的 REA 关系写入 data/rea-resources.json，论文写入 data/papers.json。中文名称和使用条件在 site/translations.zh-CN.json。字段定义以目录格式指南为准。'
            if zh else 'Edit data/tool-resources.json for independent resources, data/rea-resources.json for documented REA relationships, or data/papers.json for papers. Chinese resource names and requirements belong in site/translations.zh-CN.json; the catalog schema defines the fields.')
    submit = ('重新生成 README 与仓库目录，通过相关校验后，推送到自己的分支或 fork，并向 main 创建 PR。使用现有 PR 模板，写明来源、局限和真实运行过的检查。'
              if zh else 'Regenerate the READMEs and repository directories, run the relevant checks, push to your branch or fork, and open a PR against main. Use the existing template and state evidence, limits and checks actually run.')
    steps = ''.join('<li><p>' + escape(text) + '</p></li>' for text in (first, evidence, edit, submit))
    questions = [
        ('Agent 可以提交吗？' if zh else 'Can an agent contribute?',
         '可以，人工和 AI 辅助贡献适用相同的证据、去重和审核规则。公开提交应符合用户授权，并说明资源与 REA 的关系及贡献者与资源的关系。' if zh else 'Yes. Human and agent-assisted contributions follow the same evidence, deduplication and review rules. Public submissions must respect user authorization and distinguish the resource’s REA relationship from the contributor’s own connection.'),
        ('自动扫描等于精选收录吗？' if zh else 'Does an automated scan mean curated inclusion?',
         '不等于。README 自动扫描是发现证据；精选收录需要单独核查一手来源。source-reviewed 不表示运行复现、安全保证或兼容性验证。' if zh else 'No. An automated README scan is discovery evidence. Curation requires separate primary-source review; source-reviewed does not establish runtime reproduction, safety or compatibility.'),
        ('校验通过就会发布吗？' if zh else 'Do passing checks publish the submission?',
         '不会。维护者审核相关性与事实声明。不要把检查通过、AI 审查意见或创建 PR 说成已接收、合并或部署。' if zh else 'No. Maintainers review relevance and factual claims. Passing checks, an AI review or opening a PR must not be described as acceptance, merge or deployment.'),
    ]
    answers = ''.join('<section class="source-card browse-repository"><h2>' + escape(q) + '</h2><p class="card-description">' + escape(a) + '</p></section>' for q, a in questions)
    docs = [('/blob/main/' + rules, '贡献规则' if zh else 'Contribution rules'),
            ('/blob/main/' + guide, 'Agent 投稿与 PR 指南' if zh else 'Agent submission and PR guide'),
            ('/blob/main/AGENTS.md', '仓库 Agent 指令' if zh else 'Repository agent instructions'),
            ('/blob/main/data/README.md', '目录格式（英文）' if zh else 'Catalog schema'),
            ('/blob/main/.github/PULL_REQUEST_TEMPLATE.md', 'PR 模板' if zh else 'PR template')]
    return ('<p class="card-description">' + escape(intro) + '</p>'
            '<div class="source-results"><section class="source-card browse-repository"><h2>' + ('选择提交入口' if zh else 'Choose a submission form') + '</h2><nav class="browse-category-nav" aria-label="' + ('提交表单' if zh else 'Submission forms') + '">' + forms + '</nav></section>'
            '<section class="source-card browse-repository"><h2>' + ('如何准备 pull request' if zh else 'Prepare a pull request') + '</h2><ol>' + steps + '</ol></section></div>'
            '<nav class="browse-category-nav" aria-label="' + ('贡献文档' if zh else 'Contribution documentation') + '">' + ''.join(link(path, label) for path, label in docs) + '</nav>'
            '<div class="source-results">' + answers + '</div>')
