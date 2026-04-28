import os
import random
import re
import time
from typing import Dict, List, Tuple, TypedDict, Union, Optional

from atroposlib.envs.base import APIServerConfig, BaseEnv, BaseEnvConfig, ScoredDataGroup
from atroposlib.type_definitions import Item
from tinker_atropos.config import TinkerAtroposConfig

CONFIG_PATH = "configs/default.yaml"

REQUIRED_SECTIONS = ["문제", "고객", "제안", "채널", "실험", "지표", "한줄결론"]
ACTION_TERMS = ["이번 주", "다음 주", "일주일", "이주", "전환율", "클릭률", "신청", "매출", "퍼센트", "%", "건"]
BUZZWORDS = ["혁신", "최고", "완벽", "압도", "세계적", "게임체인저", "패러다임"]
BEGINNER_FRIENDLY_TERMS = ["쉬운", "바로", "하나", "먼저", "예시", "초보", "간단", "바로 눌러", "설명란"]
JARGON_TERMS = ["퍼널", "레버리지", "파이프라인", "고도화", "최적화 니즈", "솔루션"]
CHANNEL_HINTS = ["유튜브", "텔레그램", "X", "설명란", "고정글", "공지", "랜딩", "광고"]
PRIORITY_TERMS = ["하나만", "한 가지", "먼저", "우선", "지금은", "지금 해야 할"]
MIN_GENERATED_TOKENS = 4


class BusinessStrategyItem(TypedDict):
    scenario: str
    audience: str
    offer: str
    constraints: List[str]
    must_include_terms: List[str]
    success_metrics: List[str]


BUSINESS_STRATEGY_ITEMS: List[BusinessStrategyItem] = [
    {
        "scenario": "유튜브 외부 유입은 강하지만 상담 신청 전환이 약한 상황에서 Ailit 진단 세션을 어떻게 제안할지 설계한다.",
        "audience": "AI 도구에는 관심이 높지만 세팅 시간이 부족한 일인 사업가",
        "offer": "Ailit 진단 세션과 빠른 세팅 패키지",
        "constraints": ["기존 유튜브 트래픽 활용", "과장 없는 제안", "일주일 안에 검증 가능"],
        "must_include_terms": ["Ailit", "유튜브", "상담", "전환"],
        "success_metrics": ["클릭률", "상담 신청", "전환율"],
    },
    {
        "scenario": "사생결단 AI 부트캠프 신규 모집에서 무료 콘텐츠와 유료 전환 사이의 간극을 줄이는 실행안을 만든다.",
        "audience": "이미 무료 콘텐츠를 소비했지만 아직 결제를 망설이는 예비 수강생",
        "offer": "부트캠프 체험 과제와 유료 멤버십 업그레이드",
        "constraints": ["광고비 급증 금지", "콘텐츠 재활용 우선", "초보자도 이해 가능"],
        "must_include_terms": ["부트캠프", "체험", "업그레이드", "멤버십"],
        "success_metrics": ["체험 신청", "결제 전환율", "첫 주 유지율"],
    },
    {
        "scenario": "CMDSPACE VIP 멤버십의 잔존율을 높이기 위해 온보딩 첫 칠 일을 다시 설계한다.",
        "audience": "결제는 했지만 아직 습관화되지 않은 신규 VIP 멤버",
        "offer": "첫 칠 일 온보딩 미션과 체크인 루프",
        "constraints": ["운영 리소스 추가 최소화", "텔레그램 중심 운영", "측정 가능한 행동 목표"],
        "must_include_terms": ["VIP", "온보딩", "텔레그램", "체크인"],
        "success_metrics": ["첫 칠 일 참여율", "이탈률", "재방문율"],
    },
    {
        "scenario": "구글 광고를 재가동하기 전에 평범한사업가 브랜드에 맞는 저위험 실험안을 만든다.",
        "audience": "검색 의도는 강하지만 아직 브랜드를 잘 모르는 잠재 고객",
        "offer": "진단형 랜딩과 저가 입문 상품",
        "constraints": ["예산 통제", "작은 실험부터 시작", "광고 문구와 랜딩 문구 일치"],
        "must_include_terms": ["구글 광고", "랜딩", "예산", "입문 상품"],
        "success_metrics": ["광고 클릭률", "랜딩 전환율", "획득 비용"],
    },
    {
        "scenario": "Ailit 저가 입문 상품을 만들어 상담 전 단계의 마찰을 줄이는 실행안을 설계한다.",
        "audience": "상담은 부담스럽지만 작은 결제는 시도할 수 있는 잠재 고객",
        "offer": "저가 입문 상품과 진단 업셀 흐름",
        "constraints": ["기존 콘텐츠를 재활용", "복잡한 신규 제작 최소화", "일주일 안에 검증 가능"],
        "must_include_terms": ["Ailit", "입문 상품", "상담", "업셀"],
        "success_metrics": ["입문 상품 구매", "상담 전환", "업셀 전환율"],
    },
    {
        "scenario": "유튜브 조회수는 높은데 텔레그램 채널 유입이 약한 상황에서 중간 다리 상품과 메시지를 설계한다.",
        "audience": "영상은 끝까지 보지만 아직 채널 참여까지는 하지 않는 시청자",
        "offer": "채널 합류 보상과 체크리스트형 리드 마그넷",
        "constraints": ["영상 재편집 최소화", "설명란과 댓글 고정 활용", "쉬운 말 사용"],
        "must_include_terms": ["유튜브", "텔레그램", "체크리스트", "설명란"],
        "success_metrics": ["채널 유입", "링크 클릭", "채널 참여율"],
    },
    {
        "scenario": "유료 멤버 대상 라이브 세션 참여율이 낮을 때 사전 기대감과 사후 재참여 루프를 설계한다.",
        "audience": "결제는 했지만 라이브 일정을 우선순위에 두지 않는 기존 멤버",
        "offer": "라이브 참여 리마인드와 요약 리플레이 흐름",
        "constraints": ["운영 인력 추가 최소화", "텔레그램 기반 안내", "즉시 측정 가능"],
        "must_include_terms": ["라이브", "리마인드", "텔레그램", "리플레이"],
        "success_metrics": ["라이브 참여율", "재시청률", "다음 세션 참여율"],
    },
    {
        "scenario": "기업 협업 문의가 들어왔을 때 평범한사업가 브랜드와 맞는 제안 구조를 간단히 정리한다.",
        "audience": "AI 도구 프로모션을 검토하는 기업 마케팅 담당자",
        "offer": "브랜드 맞춤형 협업 제안서와 검증된 노출 패키지",
        "constraints": ["브랜드 훼손 금지", "광고 티 과도하게 금지", "신뢰 요소 강조"],
        "must_include_terms": ["협업", "브랜드", "신뢰", "패키지"],
        "success_metrics": ["응답률", "미팅 성사", "계약 전환율"],
    },
    {
        "scenario": "호주 시드니 거주 맥락을 살려 해외 사례와 현지 사업 감각을 연결하는 콘텐츠형 상품 구상을 정리한다.",
        "audience": "한국 시장은 익숙하지만 해외 사례를 사업 기회로 연결하고 싶은 일인 사업가",
        "offer": "해외 사례 브리핑과 적용형 액션 노트",
        "constraints": ["현지성은 살리되 과장 금지", "콘텐츠에서 바로 판매로 몰지 않기", "실행 한 가지 우선 제시"],
        "must_include_terms": ["시드니", "해외 사례", "액션 노트", "일인 사업가"],
        "success_metrics": ["브리핑 신청", "콘텐츠 저장", "후속 상담 전환"],
    },
    {
        "scenario": "Google Workspace 중심 업무 흐름을 교육 상품으로 묶어 시간 절약 가치를 강조하는 제안을 만든다.",
        "audience": "도구는 많지만 문서, 메일, 캘린더 정리가 엉킨 소규모 사업자",
        "offer": "Google Workspace 자동화 세팅 세션",
        "constraints": ["기술 용어 최소화", "업무 시간 절약을 수치로 보여주기", "입문 상품과 연결"],
        "must_include_terms": ["Google Workspace", "자동화", "시간 절약", "세팅"],
        "success_metrics": ["세션 신청", "입문 상품 클릭", "상담 전환율"],
    },
    {
        "scenario": "유튜브 협업 제안을 받을 때 단발성 광고가 아니라 브랜드 신뢰를 지키는 장기 제안 구조를 설계한다.",
        "audience": "협업은 하고 싶지만 채널 신뢰를 잃고 싶지 않은 크리에이터",
        "offer": "장기 테스트형 협업 패키지",
        "constraints": ["한 번에 너무 많은 약속 금지", "실제 사용 경험 강조", "댓글 반응 추적 포함"],
        "must_include_terms": ["유튜브", "협업", "신뢰", "장기 테스트"],
        "success_metrics": ["협업 수락률", "댓글 반응", "후속 제안 재계약"],
    },
    {
        "scenario": "CMDSPACE VIP에서 조용한 멤버를 다시 활성화하기 위한 재참여 캠페인 구조를 설계한다.",
        "audience": "결제는 유지하지만 최근 한 달간 발화나 참여가 거의 없는 VIP 멤버",
        "offer": "재참여 체크인 캠페인과 짧은 미션",
        "constraints": ["운영자 공수 최소화", "텔레그램에서 끝낼 것", "부담 적은 행동 한 가지 제시"],
        "must_include_terms": ["VIP", "재참여", "텔레그램", "체크인"],
        "success_metrics": ["재활성화율", "발화율", "다음 달 유지율"],
    },
]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def extract_section_map(answer: str) -> Dict[str, str]:
    pattern = re.compile(r"^(문제|고객|제안|채널|실험|지표|한줄결론)\s*:\s*(.*)$", re.MULTILINE)
    matches = list(pattern.finditer(answer))
    sections: Dict[str, str] = {}
    for index, match in enumerate(matches):
        section_name = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(answer)
        body = _normalize_text(match.group(2) + " " + answer[start:end])
        sections[section_name] = body.strip()
    return sections


def is_ultra_smoke_mode() -> bool:
    return os.getenv("MIN_BUSINESS_ULTRA_SMOKE", "").strip() in {"1", "true", "TRUE", "yes", "YES"}


def format_business_prompt(item: BusinessStrategyItem) -> str:
    if is_ultra_smoke_mode():
        return (
            f"상황:{item['scenario']}\n"
            f"제안:{item['offer']}\n"
            "짧고 구체적으로 작성.\n"
            "문제:\n고객:\n제안:\n채널:\n실험:\n지표:\n한줄결론:\n"
        )

    constraints = " / ".join(item["constraints"])
    metrics = ", ".join(item["success_metrics"])
    terms = ", ".join(item["must_include_terms"])
    return (
        "너는 평범한사업가 브랜드를 돕는 실전 사업 전략가다. 과장 없이, 실행 가능하고, 바로 시험할 수 있는 안만 제시하라.\n\n"
        f"상황: {item['scenario']}\n"
        f"핵심 고객: {item['audience']}\n"
        f"제안 대상: {item['offer']}\n"
        f"제약: {constraints}\n"
        f"반드시 넣을 말: {terms}\n"
        f"우선 지표: {metrics}\n\n"
        "아래 형식을 정확히 지켜 작성하라. 각 항목은 한두 문장으로 짧고 구체적으로 쓴다.\n"
        "문제:\n"
        "고객:\n"
        "제안:\n"
        "채널:\n"
        "실험:\n"
        "지표:\n"
        "한줄결론:\n"
    )


def score_business_answer(answer: str, item: BusinessStrategyItem) -> Dict[str, float]:
    normalized = _normalize_text(answer)
    lowered = normalized.lower()
    sections = extract_section_map(answer)

    section_hits = sum(1 for section in REQUIRED_SECTIONS if sections.get(section))
    section_coverage = section_hits / len(REQUIRED_SECTIONS)

    keyword_hits = 0
    keywords = item["must_include_terms"] + item["success_metrics"]
    for term in keywords:
        if term.lower() in lowered:
            keyword_hits += 1
    keyword_coverage = keyword_hits / len(keywords)

    actionability = 1.0 if any(term.lower() in lowered for term in ACTION_TERMS) else 0.0

    friendly_hits = sum(1 for term in BEGINNER_FRIENDLY_TERMS if term.lower() in lowered)
    jargon_hits = sum(1 for term in JARGON_TERMS if term.lower() in lowered)
    beginner_friendliness = min(1.0, 0.2 * friendly_hits)
    if jargon_hits:
        beginner_friendliness = max(0.0, beginner_friendliness - 0.2 * jargon_hits)

    proposal_section = sections.get("제안", "")
    channel_section = sections.get("채널", "")
    experiment_section = sections.get("실험", "")
    metric_section = sections.get("지표", "")

    channel_hint_hits = sum(1 for term in CHANNEL_HINTS if term.lower() in channel_section.lower())
    offer_hint_hits = sum(1 for term in item["must_include_terms"] if term.lower() in channel_section.lower())
    channel_fit = 1.0 if channel_hint_hits and offer_hint_hits else 0.5 if channel_hint_hits else 0.0

    priority_text = normalized
    priority_hits = sum(1 for term in PRIORITY_TERMS if term in priority_text)
    priority_clarity = min(1.0, 0.25 * priority_hits)

    proposal_alignment_hits = sum(
        1 for term in item["must_include_terms"] if term.lower() in proposal_section.lower()
    )
    proposal_alignment = min(1.0, 0.5 * proposal_alignment_hits)

    metric_alignment_hits = sum(
        1 for term in item["success_metrics"] if term.lower() in metric_section.lower()
    )
    metric_alignment = metric_alignment_hits / len(item["success_metrics"])

    experiment_alignment = 1.0 if any(term.lower() in experiment_section.lower() for term in ACTION_TERMS) else 0.0
    section_alignment = (proposal_alignment + metric_alignment + experiment_alignment) / 3.0

    buzzword_count = sum(1 for word in BUZZWORDS if word in normalized)
    buzzword_penalty = min(0.3, buzzword_count * 0.1)

    brevity = 1.0 if 120 <= len(normalized) <= 800 else 0.5 if len(normalized) >= 60 else 0.0

    total = (
        0.28 * section_coverage
        + 0.18 * keyword_coverage
        + 0.15 * actionability
        + 0.1 * beginner_friendliness
        + 0.08 * channel_fit
        + 0.1 * priority_clarity
        + 0.05 * brevity
        + 0.06 * section_alignment
        - buzzword_penalty
    )
    total = max(0.0, min(1.0, total))

    return {
        "total": total,
        "section_coverage": section_coverage,
        "keyword_coverage": keyword_coverage,
        "actionability": actionability,
        "beginner_friendliness": beginner_friendliness,
        "channel_fit": channel_fit,
        "priority_clarity": priority_clarity,
        "section_alignment": section_alignment,
        "proposal_alignment": proposal_alignment,
        "metric_alignment": metric_alignment,
        "experiment_alignment": experiment_alignment,
        "brevity": brevity,
        "buzzword_penalty": -buzzword_penalty,
    }


class MinBusinessStrategyEnv(BaseEnv):
    """
    민 전용 사업 전략 실험 환경.
    유튜브, 멤버십, 광고, 컨설팅 같은 실제 사업 상황에 대해
    짧고 실행 가능한 한국어 전략 답변을 만들고 부분 보상으로 채점한다.
    """

    name = "min_business_strategy"

    def __init__(
        self,
        config: BaseEnvConfig,
        server_configs: List[APIServerConfig],
        slurm: bool = True,
        testing: bool = False,
    ):
        super().__init__(config, server_configs, slurm, testing)
        self.percent_correct_buffer = []
        self.eval_metrics = []
        self.items = BUSINESS_STRATEGY_ITEMS
        self.iter = 0

    @classmethod
    def config_init(cls) -> Tuple[BaseEnvConfig, List[APIServerConfig]]:
        config = TinkerAtroposConfig.from_yaml(CONFIG_PATH) if CONFIG_PATH else TinkerAtroposConfig()
        env_config = BaseEnvConfig(
            tokenizer_name=config.base_model,
            group_size=config.group_size,
            use_wandb=config.use_wandb,
            rollout_server_url=config.atropos_api_url,
            total_steps=config.num_steps,
            batch_size=config.batch_size,
            steps_per_eval=config.steps_per_eval,
            max_token_length=config.max_token_env_length,
            max_num_workers=config.max_num_workers,
            max_batches_offpolicy=config.max_batches_offpolicy,
            wandb_name=f"{config.wandb_run_name}-env",
            ensure_scores_are_not_same=False,
        )
        server_configs = [
            APIServerConfig(
                model_name=config.base_model,
                base_url=config.inference_api_url + "/v1",
                api_key="x",
                server_type="sglang",
                num_requests_for_eval=config.num_requests_for_eval,
            )
        ]
        return env_config, server_configs

    async def setup(self):
        if self.tokenizer.chat_template is None:
            self.tokenizer.chat_template = (
                "{% for message in messages %}"
                "{% if message['role'] == 'system' %}"
                "{{ '<|start_header_id|>system<|end_header_id|>\\n\\n' + message['content'] + '<|eot_id|>' }}"
                "{% elif message['role'] == 'user' %}"
                "{{ '<|start_header_id|>user<|end_header_id|>\\n\\n' + message['content'] + '<|eot_id|>' }}"
                "{% elif message['role'] == 'assistant' %}"
                "{{ '<|start_header_id|>assistant<|end_header_id|>\\n\\n' + message['content'] + '<|eot_id|>' }}"
                "{% endif %}"
                "{% if loop.last and message['role'] != 'assistant' %}"
                "{{ '<|start_header_id|>assistant<|end_header_id|>\\n\\n' }}"
                "{% endif %}"
                "{% endfor %}"
            )

    async def wandb_log(self, wandb_metrics: Optional[Dict] = None):
        if wandb_metrics is None:
            wandb_metrics = {}
        if self.percent_correct_buffer:
            wandb_metrics["train/percent_correct"] = sum(self.percent_correct_buffer) / len(
                self.percent_correct_buffer
            )
        self.percent_correct_buffer = []
        for item in self.eval_metrics:
            wandb_metrics[item[0]] = item[1]
        self.eval_metrics = []
        await super().wandb_log(wandb_metrics)

    async def collect_trajectories(self, item: BusinessStrategyItem) -> Tuple[ScoredDataGroup, List[Item]]:
        user_message = {"role": "user", "content": format_business_prompt(item)}
        messages = [user_message]

        async with self.server.managed_server(tokenizer=self.tokenizer) as managed:
            chat_completion = await managed.chat_completion(
                messages=messages,
                n=self.config.group_size,
                max_tokens=self.config.max_token_length,
                temperature=1.0,
                stop=[self.tokenizer.eos_token_id],
            )
            state = managed.get_state()
            nodes = state["nodes"]

        to_score = []
        to_backlog: List[Item] = []
        for choice, node in zip(chat_completion.choices, nodes):
            completion_messages = (
                user_message,
                {"role": "assistant", "content": choice.message.content},
            )
            to_score.append(
                {
                    "messages": completion_messages,
                    "item": item,
                    "finish_reason": choice.finish_reason,
                    "tokens": node.tokens,
                    "masked_tokens": node.masked_tokens,
                    "logprobs": node.logprobs,
                }
            )
        to_postprocess = await self.score(to_score)
        return to_postprocess, to_backlog

    async def score(
        self, rollout_group_data
    ) -> Union[Optional[ScoredDataGroup], List[Optional[ScoredDataGroup]]]:
        scores = ScoredDataGroup()
        scores["tokens"] = []
        scores["masks"] = []
        scores["scores"] = []
        scores["inference_logprobs"] = []

        random.shuffle(rollout_group_data)
        for item in rollout_group_data:
            answer = item["messages"][-1]["content"]
            reward_info = score_business_answer(answer, item["item"])
            reward = reward_info["total"]

            tokens = item["tokens"]
            masked_tokens = item["masked_tokens"]
            logprobs = item["logprobs"]

            if len([1 for token in masked_tokens if token != -100]) < MIN_GENERATED_TOKENS:
                continue

            scores["tokens"].append(tokens)
            scores["masks"].append(masked_tokens)
            scores["inference_logprobs"].append(logprobs)
            scores["scores"].append(float(reward))

            if reward >= 0.8:
                self.percent_correct_buffer.append(1.0)
            else:
                self.percent_correct_buffer.append(0.0)

            if len(scores["tokens"]) >= self.config.group_size:
                break

        return scores if scores["scores"] else None

    async def rollout_and_score_eval(self, item: BusinessStrategyItem) -> Dict[str, object]:
        completion = await self.server.chat_completion(
            messages=[{"role": "user", "content": format_business_prompt(item)}],
            n=1,
            max_tokens=self.config.max_token_length,
            temperature=0.0,
            split="eval",
        )
        response_content = completion.choices[0].message.content
        reward_info = score_business_answer(response_content, item)
        sample = {
            "scenario": item["scenario"],
            "answer": response_content,
            "score": reward_info["total"],
            "details": reward_info,
            "finish_reason": completion.choices[0].finish_reason,
        }
        return {"score": reward_info["total"], "sample": sample}

    async def evaluate(self, *args, **kwargs):
        start_time = time.time()
        results = []
        for item in self.items:
            results.append(await self.rollout_and_score_eval(item))
        scores = [result["score"] for result in results]
        samples = [result["sample"] for result in results]
        mean_score = sum(scores) / len(scores)
        end_time = time.time()

        self.eval_metrics.append(("eval/mean_score", mean_score))
        await self.evaluate_log(
            metrics={"eval/mean_score": mean_score},
            samples=samples,
            start_time=start_time,
            end_time=end_time,
            generation_parameters={
                "temperature": 0.0,
                "max_tokens": self.config.max_token_length,
            },
        )

    async def get_next_item(self) -> BusinessStrategyItem:
        next_item = self.items[self.iter % len(self.items)]
        self.iter += 1
        return next_item


if __name__ == "__main__":
    MinBusinessStrategyEnv.cli()
