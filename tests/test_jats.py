import textwrap
from pathlib import Path

from bfg.ingest.jats import parse_jats


JATS_SAMPLE = textwrap.dedent(
    """\
    <?xml version="1.0"?>
    <article xmlns:xlink="http://www.w3.org/1999/xlink">
      <front>
        <article-meta>
          <title-group>
            <article-title>p66Shc Mediates SUMO2-induced Endothelial Dysfunction</article-title>
          </title-group>
          <abstract>
            <p>Hyperlipidemia induces endothelial dysfunction via p66Shc.</p>
          </abstract>
        </article-meta>
      </front>
      <body>
        <fig id="fig1">
          <label>Figure 1</label>
          <caption><p>p66Shc mediates SUMO2-induced ROS production.</p></caption>
          <graphic xlink:href="fig1.png"/>
        </fig>
        <fig id="fig4">
          <label>Figure 4</label>
          <caption><p>SUMO2 promotes p66ShcS36 phosphorylation.</p></caption>
          <graphic xlink:href="fig4.png"/>
        </fig>
      </body>
    </article>
    """
)


def test_parse_jats_title_abstract_and_figures(tmp_path: Path):
    xml = tmp_path / "article.xml"
    xml.write_text(JATS_SAMPLE, encoding="utf-8")

    parsed = parse_jats(xml)

    assert "SUMO2" in parsed.title
    assert "endothelial" in parsed.abstract.lower()
    assert len(parsed.figures) == 2
    fig1, fig4 = parsed.figures
    assert fig1.fig_id == "fig1"
    assert fig1.href == "fig1.png"
    assert "ROS" in fig1.caption
    assert fig4.fig_id == "fig4"
    assert fig4.href == "fig4.png"


def test_parse_jats_handles_missing_optionals(tmp_path: Path):
    xml = tmp_path / "sparse.xml"
    xml.write_text("<article><body></body></article>", encoding="utf-8")
    parsed = parse_jats(xml)
    assert parsed.title == ""
    assert parsed.abstract == ""
    assert parsed.figures == []
