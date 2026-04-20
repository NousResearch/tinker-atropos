import os
import random
import re
import time
from typing import Dict, List, Tuple, TypedDict, Union, Optional

from atroposlib.envs.base import APIServerConfig, BaseEnv, BaseEnvConfig, ScoredDataGroup
from atroposlib.type_definitions import Item
from tinker_atropos.config import TinkerAtroposConfig

CONFIG_PATH = "configs/default.yaml"

REQUIRED_SECTIONS = ["후크", "본문", "댓글유도", "행동유도", "금지"]
HOOK_TERMS = ["이유", "문제", "비밀", "착각", "바로", "먼저", "왜"]
ENGAGEMENT_TERMS = ["댓글", "남겨", "어디", "무엇", "당신", "직접"]
ACTION_TERMS = ["오늘", "지금", "바꿔", "확인", "실험", "클릭률", "전환"]
HYPE_TERMS = ["혁신", "최고", "압도", "무조건", "인생역전", "대박"]
SINGLE_ACTION_TERMS = ["하나만", "한 가지", "먼저", "오늘", "지금"]
MIN_GENERATED_TOKENS = 4


class XStrategyItem(TypedDict):
    topic: str
    audience: str
    desired_action: str
    must_include_terms: List[str]
    forbidden_tones: List[str]


X_STRATEGY_ITEMS: List[XStrategyItem] = [
    {
        "topic": "AI 도구를 많이 써도 매출이 안 오르는 이유를 민 톤으로 설명하는 X 글",
        "audience": "AI 도구에 관심은 많지만 구조화된 사업 흐름이 없는 일인 사업가",
        "desired_action": "댓글로 현재 가장 막힌 지점을 남기게 만들기",
        "must_include_terms": ["AI 도구", "매출", "유튜브", "상담"],
        "forbidden_tones": ["허풍", "근거 없는 자랑"],
    },
    {
        "topic": "부트캠프 무료 콘텐츠 소비자를 유료 전환으로 이끄는 X 글",
        "audience": "무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객",
        "desired_action": "체험 과제 또는 상담 링크를 눌러보게 만들기",
        "must_include_terms": ["부트캠프", "체험", "전환", "설명란"],
        "forbidden_tones": ["과장", "공허한 동기부여"],
    },
    {
        "topic": "텔레그램 채널은 있는데 참여가 낮을 때 댓글과 행동 유도를 살리는 X 글",
        "audience": "채널은 들어왔지만 아직 반응을 잘 안 남기는 구독자",
        "desired_action": "댓글로 현재 막힌 한 지점을 남기게 만들기",
        "must_include_terms": ["텔레그램", "댓글", "체크인", "참여"],
        "forbidden_tones": ["허풍", "뜬구름 잡는 격려"],
    },
    {
        "topic": "Ailit 입문 상품을 소개하면서 상담보다 쉬운 첫 행동을 유도하는 X 글",
        "audience": "상담은 부담스럽지만 작은 결제는 시도할 수 있는 잠재 고객",
        "desired_action": "입문 상품 링크를 눌러보게 만들기",
        "must_include_terms": ["Ailit", "입문 상품", "상담", "링크"],
        "forbidden_tones": ["과장", "근거 없는 자랑"],
    },
    {
        "topic": "유튜브 조회수는 높은데 상담 전환이 약할 때 설명란 개선 필요성을 말하는 X 글",
        "audience": "콘텐츠는 만들지만 퍼널 연결이 약한 창업자",
        "desired_action": "오늘 설명란 첫 문장을 바꿔보게 만들기",
        "must_include_terms": ["유튜브", "설명란", "상담", "전환"],
        "forbidden_tones": ["허세", "뜬구름 잡는 약속"],
    },
    {
        "topic": "기업 협업 문의를 받을 때 브랜드 훼손 없이 제안해야 한다는 점을 설명하는 X 글",
        "audience": "협업 제안은 오지만 기준 없이 다 받는 크리에이터",
        "desired_action": "브랜드 기준 세 가지를 댓글로 적어보게 만들기",
        "must_include_terms": ["협업", "브랜드", "기준", "댓글"],
        "forbidden_tones": ["자랑", "무조건 수락"],
    },
    {
        "topic": "시드니에서 본 해외 AI 비즈니스 사례를 한국 일인 사업가 맥락으로 번역하는 X 글",
        "audience": "해외 사례는 궁금하지만 자기 사업에 어떻게 붙일지 모르는 구독자",
        "desired_action": "지금 적용할 한 가지를 댓글로 적게 만들기",
        "must_include_terms": ["시드니", "해외 사례", "일인 사업가", "댓글"],
        "forbidden_tones": ["허세", "뜬구름 잡는 해외 자랑"],
    },
    {
        "topic": "Google Workspace 자동화가 왜 시간 절약형 상품이 될 수 있는지 설명하는 X 글",
        "audience": "메일, 문서, 일정 정리 때문에 자주 멈추는 소규모 사업자",
        "desired_action": "오늘 줄이고 싶은 반복 업무 하나를 댓글로 남기게 만들기",
        "must_include_terms": ["Google Workspace", "자동화", "시간 절약", "반복 업무"],
        "forbidden_tones": ["과장", "복잡한 기술 자랑"],
    },
    {
        "topic": "VIP 멤버가 조용해지는 이유와 재참여 체크인이 필요한 이유를 설명하는 X 글",
        "audience": "커뮤니티를 운영하지만 조용한 유료 멤버가 늘어나는 운영자",
        "desired_action": "오늘 보낼 체크인 문장 하나를 떠올리게 만들기",
        "must_include_terms": ["VIP", "재참여", "체크인", "운영자"],
        "forbidden_tones": ["비난", "감정 과잉"],
    },
    {
        "topic": "랜딩에서 헤드라인 하나가 상담 전환을 바꾸는 이유를 설명하는 X 글",
        "audience": "광고나 콘텐츠는 하지만 랜딩 첫 문장을 자주 방치하는 창업자",
        "desired_action": "오늘 헤드라인 한 줄만 바꿔보게 만들기",
        "must_include_terms": ["랜딩", "헤드라인", "상담", "전환"],
        "forbidden_tones": ["과장", "만능 해결사 톤"],
    },
]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def extract_section_map(answer: str) -> Dict[str, str]:
    pattern = re.compile(r"^(후크|본문|댓글유도|행동유도|금지)\s*:\s*(.*)$", re.MULTILINE)
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
    return os.getenv("MIN_X_ULTRA_SMOKE", "").strip() in {"1", "true", "TRUE", "yes", "YES"}


def format_x_prompt(item: XStrategyItem) -> str:
    if is_ultra_smoke_mode():
        return (
            f"주제:{item['topic']}\n"
            "짧고 강하게 작성.\n"
            "후크:\n본문:\n댓글유도:\n행동유도:\n금지:\n"
        )

    must_terms = ", ".join(item["must_include_terms"])
    forbidden = ", ".join(item["forbidden_tones"])
    return (
        "너는 평범한사업가 톤으로 X 글 한 개를 설계하는 전략가다. 짧고 강하게 쓰되 허풍은 금지다.\n\n"
        f"주제: {item['topic']}\n"
        f"독자: {item['audience']}\n"
        f"목표 행동: {item['desired_action']}\n"
        f"반드시 넣을 말: {must_terms}\n"
        f"피해야 할 톤: {forbidden}\n\n"
        "아래 형식을 정확히 지켜 작성하라.\n"
        "후크:\n"
        "본문:\n"
        "댓글유도:\n"
        "행동유도:\n"
        "금지:\n"
    )


def score_x_answer(answer: str, item: XStrategyItem) -> Dict[str, float]:
    normalized = _normalize_text(answer)
    lowered = normalized.lower()
    sections = extract_section_map(answer)

    section_hits = sum(1 for section in REQUIRED_SECTIONS if sections.get(section))
    section_coverage = section_hits / len(REQUIRED_SECTIONS)

    keyword_hits = sum(1 for term in item["must_include_terms"] if term.lower() in lowered)
    keyword_coverage = keyword_hits / len(item["must_include_terms"])

    hook_text = sections.get("후크", "")
    body_text = sections.get("본문", "")
    comment_text = sections.get("댓글유도", "")
    action_text = sections.get("행동유도", "")
    guardrail_text = sections.get("금지", "")

    hook_strength = min(1.0, 0.25 * sum(1 for term in HOOK_TERMS if term in hook_text))
    if len(hook_text) >= 25:
        hook_strength = min(1.0, hook_strength + 0.35)

    engagement_hits = sum(1 for term in ENGAGEMENT_TERMS if term in comment_text)
    engagement = min(1.0, 0.25 * engagement_hits)
    if "?" in comment_text or "어디" in comment_text or "무엇" in comment_text:
        engagement = min(1.0, engagement + 0.3)
    if "가장" in comment_text or "한 지점" in comment_text:
        engagement = min(1.0, engagement + 0.1)

    action_hits = sum(1 for term in ACTION_TERMS if term in action_text)
    actionability = min(1.0, 0.25 * action_hits)
    if "바꾸" in action_text or "확인해" in action_text:
        actionability = min(1.0, actionability + 0.15)

    single_action_hits = sum(1 for term in SINGLE_ACTION_TERMS if term in action_text or term in guardrail_text)
    single_action_clarity = min(1.0, 0.3 * single_action_hits)

    body_alignment_hits = sum(1 for term in item["must_include_terms"] if term.lower() in body_text.lower())
    body_alignment = body_alignment_hits / len(item["must_include_terms"])

    comment_alignment = min(1.0, 0.3 * engagement_hits)
    action_alignment = min(1.0, 0.2 * action_hits + 0.2 * single_action_hits)
    section_alignment = (body_alignment + comment_alignment + action_alignment) / 3.0

    hype_count = sum(1 for term in HYPE_TERMS if term in normalized)
    hype_penalty = min(0.3, 0.1 * hype_count)

    total = (
        0.22 * section_coverage
        + 0.18 * keyword_coverage
        + 0.18 * hook_strength
        + 0.12 * engagement
        + 0.12 * actionability
        + 0.05 * single_action_clarity
        + 0.08 * section_alignment
        + 0.05 * (1.0 if 80 <= len(normalized) <= 500 else 0.5)
        - hype_penalty
    )
    total = max(0.0, min(1.0, total))

    return {
        "total": total,
        "section_coverage": section_coverage,
        "keyword_coverage": keyword_coverage,
        "hook_strength": hook_strength,
        "engagement": engagement,
        "actionability": actionability,
        "single_action_clarity": single_action_clarity,
        "section_alignment": section_alignment,
        "body_alignment": body_alignment,
        "comment_alignment": comment_alignment,
        "action_alignment": action_alignment,
        "hype_penalty": -hype_penalty,
    }


class MinXStrategyEnv(BaseEnv):
    """민 전용 X 글 전략 실험 환경."""

    name = "min_x_strategy"

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
        self.items = X_STRATEGY_ITEMS
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
            wandb_metrics["train/percent_correct"] = sum(self.percent_correct_buffer) / len(self.percent_correct_buffer)
        self.percent_correct_buffer = []
        for item in self.eval_metrics:
            wandb_metrics[item[0]] = item[1]
        self.eval_metrics = []
        await super().wandb_log(wandb_metrics)

    async def collect_trajectories(self, item: XStrategyItem) -> Tuple[ScoredDataGroup, List[Item]]:
        user_message = {"role": "user", "content": format_x_prompt(item)}
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
        return await self.score(to_score), to_backlog

    async def score(self, rollout_group_data) -> Union[Optional[ScoredDataGroup], List[Optional[ScoredDataGroup]]]:
        scores = ScoredDataGroup()
        scores["tokens"] = []
        scores["masks"] = []
        scores["scores"] = []
        scores["inference_logprobs"] = []

        random.shuffle(rollout_group_data)
        for item in rollout_group_data:
            reward_info = score_x_answer(item["messages"][-1]["content"], item["item"])
            reward = reward_info["total"]
            masked_tokens = item["masked_tokens"]
            if len([1 for token in masked_tokens if token != -100]) < MIN_GENERATED_TOKENS:
                continue
            scores["tokens"].append(item["tokens"])
            scores["masks"].append(masked_tokens)
            scores["inference_logprobs"].append(item["logprobs"])
            scores["scores"].append(float(reward))
            self.percent_correct_buffer.append(1.0 if reward >= 0.8 else 0.0)
            if len(scores["tokens"]) >= self.config.group_size:
                break
        return scores if scores["scores"] else None

    async def rollout_and_score_eval(self, item: XStrategyItem) -> Dict[str, object]:
        completion = await self.server.chat_completion(
            messages=[{"role": "user", "content": format_x_prompt(item)}],
            n=1,
            max_tokens=self.config.max_token_length,
            temperature=0.0,
            split="eval",
        )
        response_content = completion.choices[0].message.content
        reward_info = score_x_answer(response_content, item)
        sample = {
            "topic": item["topic"],
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
            generation_parameters={"temperature": 0.0, "max_tokens": self.config.max_token_length},
        )

    async def get_next_item(self) -> XStrategyItem:
        next_item = self.items[self.iter % len(self.items)]
        self.iter += 1
        return next_item


if __name__ == "__main__":
    MinXStrategyEnv.cli()
