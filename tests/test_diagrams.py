"""
Tests for architecture-diagrams.html.

Run with:
    python3 -m unittest discover tests -v
    # or
    python3 -m pytest tests/ -v
"""

import pathlib
import re
import unittest
from html.parser import HTMLParser

HTML_FILE = pathlib.Path(__file__).parent.parent / "architecture-diagrams.html"

EXPECTED_ARCHITECTURES = [
    "Layered Architecture",
    "Pipeline Architecture",
    "Microkernel Architecture",
    "Service-Based Architecture",
    "Event-Driven: Broker Topology",
    "Event-Driven: Mediator Topology",
    "Space-Based Architecture",
    "Orchestration-Driven SOA",
    "Microservices Architecture",
]


class TagCollector(HTMLParser):
    """Minimal HTML parser that collects tags, classes, and text content."""

    def __init__(self):
        super().__init__()
        self.tags = []           # list of (tag, attrs_dict)
        self.classes = []        # all class values seen
        self.text_chunks = []    # all non-whitespace text
        self._current_tag = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.tags.append((tag, attrs_dict))
        cls = attrs_dict.get("class", "")
        if cls:
            self.classes.extend(cls.split())

    def handle_data(self, data):
        stripped = data.strip()
        if stripped:
            self.text_chunks.append(stripped)

    @property
    def full_text(self):
        return " ".join(self.text_chunks)


def _parse(html: str) -> TagCollector:
    collector = TagCollector()
    collector.feed(html)
    return collector


class TestFileExists(unittest.TestCase):
    def test_html_file_exists(self):
        self.assertTrue(HTML_FILE.exists(), f"{HTML_FILE} not found")

    def test_html_file_not_empty(self):
        self.assertGreater(HTML_FILE.stat().st_size, 0, "HTML file is empty")


class TestHTMLStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_FILE.read_text(encoding="utf-8")
        cls.parsed = _parse(cls.html)

    def test_has_doctype(self):
        self.assertTrue(self.html.strip().startswith("<!DOCTYPE html"))

    def test_has_charset_meta(self):
        self.assertIn("charset", self.html.lower())

    def test_has_title(self):
        self.assertIn("<title>", self.html)

    def test_mermaid_script_included(self):
        self.assertIn("mermaid", self.html)

    def test_mermaid_initialized(self):
        self.assertIn("mermaid.initialize", self.html)


class TestArchitectureCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_FILE.read_text(encoding="utf-8")
        cls.parsed = _parse(cls.html)

    def test_all_nine_architectures_present(self):
        for arch in EXPECTED_ARCHITECTURES:
            with self.subTest(architecture=arch):
                self.assertIn(arch, self.html, f"Missing: {arch}")

    def test_nine_cards_exist(self):
        card_count = self.html.count('class="card"')
        self.assertEqual(card_count, 9, f"Expected 9 cards, found {card_count}")

    def test_nine_diagrams_exist(self):
        diagram_count = self.html.count('class="diagram"')
        self.assertEqual(diagram_count, 9, f"Expected 9 diagram sections, found {diagram_count}")

    def test_nine_mermaid_blocks_exist(self):
        mermaid_count = self.html.count('class="mermaid"')
        self.assertEqual(mermaid_count, 9, f"Expected 9 mermaid blocks, found {mermaid_count}")


class TestInfoPanels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_FILE.read_text(encoding="utf-8")

    def test_pros_panels_exist(self):
        count = self.html.count('class="panel pros"')
        self.assertEqual(count, 9, f"Expected 9 pros panels, found {count}")

    def test_cons_panels_exist(self):
        count = self.html.count('class="panel cons"')
        self.assertEqual(count, 9, f"Expected 9 cons panels, found {count}")

    def test_fit_panels_exist(self):
        count = self.html.count('class="panel fit"')
        self.assertEqual(count, 9, f"Expected 9 best-fit panels, found {count}")

    def test_pros_headers_labeled(self):
        self.assertEqual(self.html.count(">Pros<"), 9)

    def test_cons_headers_labeled(self):
        self.assertEqual(self.html.count(">Cons<"), 9)

    def test_fit_headers_labeled(self):
        self.assertEqual(self.html.count(">Best Fit<"), 9)

    def test_no_empty_list_items(self):
        empty_li = re.findall(r"<li>\s*</li>", self.html)
        self.assertEqual(len(empty_li), 0, f"Found {len(empty_li)} empty <li> elements")

    def test_each_card_has_chapter_reference(self):
        for ch in range(10, 18):
            with self.subTest(chapter=ch):
                self.assertIn(f"Ch. {ch}", self.html, f"Missing chapter reference: Ch. {ch}")


class TestDarkMode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_FILE.read_text(encoding="utf-8")

    def test_theme_toggle_button_exists(self):
        self.assertIn('id="theme-btn"', self.html)

    def test_button_has_aria_label(self):
        self.assertIn('aria-label=', self.html)

    def test_css_custom_properties_defined(self):
        for var in ('--bg', '--card-bg', '--text', '--text-muted', '--pros', '--cons', '--fit'):
            with self.subTest(variable=var):
                self.assertIn(var, self.html, f"Missing CSS variable: {var}")

    def test_dark_theme_selector_defined(self):
        self.assertIn('[data-theme="dark"]', self.html)

    def test_dark_theme_overrides_key_colors(self):
        dark_block_match = re.search(
            r'\[data-theme="dark"\]\s*\{([^}]+)\}', self.html, re.DOTALL
        )
        self.assertIsNotNone(dark_block_match, "No [data-theme='dark'] block found")
        dark_block = dark_block_match.group(1)
        for var in ('--bg', '--card-bg', '--text', '--pros', '--cons', '--fit'):
            with self.subTest(variable=var):
                self.assertIn(var, dark_block, f"Dark theme does not override {var}")

    def test_localstorage_persistence(self):
        self.assertIn("localStorage", self.html)

    def test_mermaid_theme_switches_on_toggle(self):
        self.assertIn("MERMAID_THEME", self.html)
        self.assertIn("'dark'", self.html)
        self.assertIn("'neutral'", self.html)

    def test_zoom_controls_injected_by_js(self):
        self.assertIn("addZoomControls", self.html)
        self.assertIn("zoom-bar", self.html)

    def test_zoom_min_max_constants_defined(self):
        self.assertIn("ZOOM_MIN", self.html)
        self.assertIn("ZOOM_MAX", self.html)
        self.assertIn("ZOOM_STEP", self.html)

    def test_mermaid_flowchart_spacing_configured(self):
        self.assertIn("nodeSpacing", self.html)
        self.assertIn("rankSpacing", self.html)

    def test_zoom_pct_label_present_in_template(self):
        self.assertIn("zoom-pct", self.html)

    def test_zoom_actions_defined(self):
        for action in ("in", "out", "reset"):
            with self.subTest(action=action):
                self.assertIn(f"data-action=\"{action}\"", self.html)


class TestMermaidDiagrams(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_FILE.read_text(encoding="utf-8")
        # Extract content of all mermaid blocks
        cls.mermaid_blocks = re.findall(
            r'class="mermaid">(.*?)</pre>', cls.html, re.DOTALL
        )

    def test_mermaid_blocks_count(self):
        self.assertEqual(len(self.mermaid_blocks), 9)

    def test_all_blocks_define_graph(self):
        for i, block in enumerate(self.mermaid_blocks):
            with self.subTest(diagram=i + 1):
                self.assertRegex(block.strip(), r"^graph (TD|LR|TB)",
                                 f"Diagram {i + 1} does not start with a graph directive")

    def test_all_blocks_have_nodes(self):
        for i, block in enumerate(self.mermaid_blocks):
            with self.subTest(diagram=i + 1):
                # A node definition looks like: ID["label"] or ID(["label"])
                nodes = re.findall(r'\w+\[', block)
                self.assertGreater(len(nodes), 1,
                                   f"Diagram {i + 1} has fewer than 2 node definitions")

    def test_all_blocks_have_edges(self):
        for i, block in enumerate(self.mermaid_blocks):
            with self.subTest(diagram=i + 1):
                edges = re.findall(r'--?>|<--?>', block)
                self.assertGreater(len(edges), 0,
                                   f"Diagram {i + 1} has no edges (arrows)")

    def test_classdefs_present_in_all_blocks(self):
        for i, block in enumerate(self.mermaid_blocks):
            with self.subTest(diagram=i + 1):
                self.assertIn("classDef", block,
                              f"Diagram {i + 1} is missing classDef colour definitions")


if __name__ == "__main__":
    unittest.main()
