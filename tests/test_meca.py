import io
import textwrap
import zipfile
from pathlib import Path

from bfg.ingest.meca import extract_meca


def _png_bytes() -> bytes:
    # Minimal 1x1 transparent PNG.
    return bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
        "890000000d49444154789c626001000000ffff03000006000557bf9c9f000000"
        "0049454e44ae426082"
    )


JATS = textwrap.dedent(
    """\
    <?xml version="1.0"?>
    <article xmlns:xlink="http://www.w3.org/1999/xlink">
      <front>
        <article-meta>
          <title-group><article-title>Test article</article-title></title-group>
          <abstract><p>An abstract.</p></abstract>
        </article-meta>
      </front>
      <body>
        <fig id="fig1">
          <label>Figure 1</label>
          <caption><p>A caption.</p></caption>
          <graphic xlink:href="images/fig1.png"/>
        </fig>
      </body>
    </article>
    """
)


def _make_meca(dest: Path) -> Path:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("content/article.xml", JATS)
        zf.writestr("content/images/fig1.png", _png_bytes())
    dest.write_bytes(buf.getvalue())
    return dest


def test_extract_meca_pulls_figures(tmp_path: Path):
    meca = _make_meca(tmp_path / "test.meca")
    article = extract_meca(meca, tmp_path / "out")

    assert article.title == "Test article"
    assert article.abstract == "An abstract."
    assert len(article.figures) == 1
    fig = article.figures[0]
    assert fig.fig_id == "fig1"
    assert fig.image_path.exists()
    assert fig.image_path.suffix == ".png"


def test_extract_meca_reuses_existing_extraction(tmp_path: Path):
    meca = _make_meca(tmp_path / "test.meca")
    first = extract_meca(meca, tmp_path / "out")
    xml = next(first.extract_dir.rglob("article.xml"))
    xml.write_text(xml.read_text().replace("Test article", "Edited title"))

    second = extract_meca(meca, tmp_path / "out")

    assert second.title == "Edited title"
