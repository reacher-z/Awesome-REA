"""The README and /papers/ share one paper topic map and one wording for each publication status."""
from copy import deepcopy
from html import unescape
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_paper_pages import STATUS_LABELS, build_paper_pages
from build_readme import PAPER_SECTIONS, paper_venue, plain_text, render_papers


def load_papers():
    return json.loads((ROOT / 'data/papers.json').read_text(encoding='utf-8'))


def readme_topics(rendered):
    """(topic, label, count) from the README's “By topic” list."""
    block = rendered.split('**By topic**' if '**By topic**' in rendered else '**按主题**', 1)[1].split('\n\n', 2)[1]
    return [(key, label, int(count)) for label, key, count in re.findall(r'\[([^\]]+)\]\(#papers-([a-z-]+)\) \((\d+)\)', block)]


def directory_topics(html):
    """(topic, label, count) from the /papers/ topic navigation."""
    nav = re.search(r'<nav class="papers-topic-nav"[^>]*>(.*?)</nav>', html, re.S)[1]
    return [(key, unescape(label), int(count)) for key, check, label, count in re.findall(
        r'<a href="#research-([a-z-]+)" data-paper-topic="([a-z-]+)">([^<]+)<span>(\d+)</span></a>', nav)
        if key == check]


class PaperTopicTest(unittest.TestCase):
    def test_readme_and_directory_list_the_same_topics_labels_order_and_counts(self):
        papers = load_papers()
        with TemporaryDirectory() as directory:
            build_paper_pages(Path(directory), papers)
            for language, route in (('en', 'papers'), ('zh', 'zh/papers')):
                with self.subTest(language=language):
                    html = (Path(directory) / route / 'index.html').read_text(encoding='utf-8')
                    topics = readme_topics(render_papers(papers, language))
                    self.assertEqual(directory_topics(html), topics)
                    self.assertEqual(sum(count for _, _, count in topics), len(papers))
                    keys = [key for key, _, _ in topics]
                    self.assertEqual(keys, sorted(keys, key=list(PAPER_SECTIONS).index))
                    # Both headings use the README section names and anchors.
                    for key, _, _ in topics:
                        label = PAPER_SECTIONS[key][language == 'zh']
                        self.assertIn(f'<h2 id="research-{key}">{label}</h2>', html)
                        self.assertIn(f'<a id="papers-{key}"></a>\n### {label}\n', render_papers(papers, language))

    def test_agent_evaluation_split_applies_to_the_directory(self):
        papers = load_papers()
        agent = deepcopy(papers[0])
        agent.update(id='paper-programbench', targets=['binary'])
        binary = deepcopy(papers[0])
        binary.update(id='paper-binary-fixture', targets=['binary', 'protocol'])
        with TemporaryDirectory() as directory:
            build_paper_pages(Path(directory), [agent, binary])
            html = (Path(directory) / 'papers/index.html').read_text(encoding='utf-8')
        self.assertEqual(directory_topics(html), [('agent-evaluation', 'Agent evaluation', 1),
                                                  ('decompilation', 'Decompilation', 1)])
        self.assertNotIn('research-binary', html)

    def test_conference_accepted_status_reads_the_same_in_readme_and_directory(self):
        record = deepcopy(load_papers()[0])
        record.update(id='paper-accepted-fixture', publication_status='conference-accepted', targets=['website'])
        with TemporaryDirectory() as directory:
            build_paper_pages(Path(directory), [record])
            for language, route in (('en', 'papers'), ('zh', 'zh/papers')):
                with self.subTest(language=language):
                    wording = STATUS_LABELS['conference-accepted'][language == 'zh']
                    html = (Path(directory) / route / 'index.html').read_text(encoding='utf-8')
                    self.assertIn(f'paper-status-conference-accepted">{wording}<', html)
                    # README paper lines carry venue · status · first author in one metadata run.
                    self.assertIn(f'{plain_text(paper_venue(record))} · {wording} · ', render_papers([record], language))
        for name, language in (('README.md', 'en'), ('README.zh-CN.md', 'zh')):
            text = (ROOT / name).read_text(encoding='utf-8')
            self.assertNotRegex(text, r' · (Accepted|已接收) · ')


if __name__ == '__main__':
    unittest.main()
