from pathlib import Path
import tempfile

from build_business_to_x_loop import business_to_x_variants, save_variants as save_x_variants
from build_business_to_landing_loop import business_to_landing_variants, save_variants as save_landing_variants


SAMPLE = """문제: 유튜브 조회수는 높은데 상담 신청 이유가 첫 화면에서 바로 안 보인다.
고객: AI는 궁금하지만 무엇부터 해야 할지 몰라 멈추는 일인 사업가다.
제안: Ailit 진단 세션 하나만 먼저 강조하고 나머지 제안은 뒤로 뺀다.
채널: 유튜브 설명란과 텔레그램 공지에서 같은 한 문장 제안을 반복한다.
실험: 오늘 설명란 첫 문장 하나만 바꾸고 일주일 동안 클릭률과 상담 신청 수를 본다.
지표: 클릭률 3퍼센트, 상담 신청 10건, 전환율 5퍼센트를 확인한다.
한줄결론: 지금은 한 가지 제안을 앞세워 전환 마찰을 줄이는 것이 우선이다.
"""


def test_save_x_variants_creates_text_and_json_files():
    variants = business_to_x_variants(SAMPLE, count=3)
    with tempfile.TemporaryDirectory() as tmp:
        text_path, json_path = save_x_variants(variants, Path(tmp), "sample")
        assert text_path.exists()
        assert json_path.exists()
        assert "RANK 1" in text_path.read_text(encoding="utf-8")
        assert '"rank": 1' in json_path.read_text(encoding="utf-8")


def test_save_landing_variants_creates_text_and_json_files():
    variants = business_to_landing_variants(SAMPLE, count=3)
    with tempfile.TemporaryDirectory() as tmp:
        text_path, json_path = save_landing_variants(variants, Path(tmp), "sample")
        assert text_path.exists()
        assert json_path.exists()
        assert "헤드라인" in text_path.read_text(encoding="utf-8")
        assert '"rank": 1' in json_path.read_text(encoding="utf-8")
