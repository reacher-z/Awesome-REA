# Security policy

This policy covers the Awesome REA repository itself: its workflows and scripts, its catalog data, and the website built from it. Only the current `main` branch and the published website are maintained; there are no separately supported releases.

## Report privately

Use GitHub private vulnerability reporting: open the repository's [Security tab](https://github.com/reacher-z/Awesome-REA/security) and choose **Report a vulnerability**. Only you and the repository maintainers can see the report.

If **Report a vulnerability** is not shown, private reporting has not been enabled yet; a maintainer has to enable it in the repository settings. Until then, open a public issue that only asks for a private contact channel. Do not name the affected file, workflow, record or value in that issue.

Report these privately:

- Weaknesses in the workflows in `.github/workflows/` or in the pull request reviewer `scripts/review_pr.py`, for example a way to run contributor code in the review job or to misuse its pull request write token.
- Problems in the build scripts or the generated website that could affect visitors, such as script injection through catalog data.
- Credentials, tokens, private account details, personal filesystem paths or other personal data in the repository, its git history, pull requests, workflow logs or artifacts, or the published website.
- A listed resource that appears compromised or malicious, such as a taken-over repository, a tampered release or a link that now serves malware. Please also notify that project's own maintainers through their security channel; this repository can only change how the collection lists it.

## Report publicly

Dead or moved links, outdated descriptions, category or target corrections, translation fixes and new suggestions belong in the [issue forms](https://github.com/reacher-z/Awesome-REA/issues/new/choose) or a pull request. Issues and pull requests are public, so follow the privacy guidance in the [contribution guide](CONTRIBUTING.md#review-and-publication). A bug in a linked tool itself belongs in that project's own tracker or security policy.

## What to include

Name the affected file, workflow, page URL or catalog ID, and explain how the problem can be observed or reproduced. Do not paste live secrets: say where a credential appears, such as the file, commit or page, and remove tokens, cookies and account identifiers from logs and screenshots.

## Accidental exposures

If a credential was committed or published, rotate or revoke it at the issuing service first. Deleting the file in a new commit does not remove it from git history, forks, clones or caches, so treat any exposed secret as compromised. Then report it privately; maintainers decide whether further cleanup is needed.

## Scope and limits

The collection links to third-party reverse-engineering tools, projects and papers. It does not audit them. `source-reviewed` means that a resource's documentation was checked; it does not mean the project was installed, tested or reviewed for security, and inclusion is not a statement that a resource is safe to run. Evaluate linked tools yourself before using them.

There is no guaranteed response time. Maintainers review private reports when they are able to.

## 中文摘要

请私下报告本仓库的安全问题：在仓库的 [Security 页面](https://github.com/reacher-z/Awesome-REA/security)选择 **Report a vulnerability**，即 GitHub 私密漏洞报告。如果看不到这个按钮，说明维护者尚未启用该功能，需要由维护者在仓库设置中开启；在此之前，请只开一个公开 issue 请求私下联系方式，不要写出受影响的文件、工作流、记录或具体内容。

需要私下报告的包括：`.github/workflows/` 中的工作流或 `scripts/review_pr.py` 评审脚本的漏洞，构建脚本或生成网站中可能影响访问者的问题，仓库、提交历史、PR、工作流日志或已发布网站中出现的凭据或个人信息，以及看起来已被入侵或含有恶意内容的收录资源。失效链接、普通更正和翻译修正请照常通过公开 issue 或 PR 提交。

报告中不要粘贴仍然有效的密钥，只需说明其位置，并删除日志和截图中的令牌、Cookie 和账号标识。如果凭据意外泄露，请先到签发方撤销或轮换：在新提交中删除文件并不能把它从 git 历史中清除。

本合集不审计所收录的工具。`source-reviewed` 只表示查阅过文档，不代表经过安装、测试或安全审查。本政策不承诺响应时间。
