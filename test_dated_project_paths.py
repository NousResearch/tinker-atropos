from pathlib import Path
import tempfile

from build_business_to_x_loop import business_to_x_variants, save_variants as save_x_variants
from build_business_to_landing_loop import business_to_landing_variants, save_variants as save_landing_variants
from build_business_to_retention_loop import business_to_retention_variants, save_variants as save_retention_variants

SAMPLE = """문제: 입문은 쉬우나 신뢰 근거는 약하다.
고객: 무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객
제안: 신뢰 근거를 앞세운 단일 제안을 먼저 보여준다.
채널: X 고정글과 랜딩 첫 화면에서 같은 제안을 먼저 보여준다.
실험: 오늘 후기 블록 위치 하나만 바꾸고 일주일 동안 전환율을 본다.
지표: 클릭률, 신청 수, 전환율을 함께 본다.
한줄결론: 지금은 비교 결과를 한 문장 제안으로 압축하는 것이 우선이다.
"""


def test_individual_savers_work_in_nested_project_dir():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "2026-04-13" / "ordinarybiz-test"
        xv = business_to_x_variants(SAMPLE, count=3, preset="ordinarybiz")
        lv = business_to_landing_variants(SAMPLE, count=3, preset="ordinarybiz")
        rv = business_to_retention_variants(SAMPLE, count=3, preset="ordinarybiz")
        x_text, _ = save_x_variants(xv, root / "x", "sample")
        l_text, _ = save_landing_variants(lv, root / "landing", "sample")
        r_text, _ = save_retention_variants(rv, root / "retention", "sample")
        assert root.name == "ordinarybiz-test"
        assert x_text.exists() and "x" in str(x_text.parent)
        assert l_text.exists() and "landing" in str(l_text.parent)
        assert r_text.exists() and "retention" in str(r_text.parent)
