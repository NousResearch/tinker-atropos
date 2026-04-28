import os
import random
import re
import time
from typing import Dict, List, Tuple, TypedDict, Union, Optional

from atroposlib.envs.base import APIServerConfig, BaseEnv, BaseEnvConfig, ScoredDataGroup
from atroposlib.type_definitions import Item
from tinker_atropos.config import TinkerAtroposConfig

CONFIG_PATH = "configs/default.yaml"

REQUIRED_SECTIONS = ["이탈원인", "온보딩수정", "리텐션장치", "운영메시지", "지표"]
SPECIFIC_TERMS = ["첫날", "둘째 날", "첫 칠 일", "체크인", "고정 공지", "텔레그램", "미션", "재방문", "이탈률"]
RETENTION_TERMS = ["체크인", "알림", "스레드", "반응", "미션", "재방문", "습관", "온보딩"]
METRIC_TERMS = ["참여율", "재방문율", "이탈률", "%", "퍼센트", "건"]
BEGINNER_TERMS = ["쉬운", "한 가지", "바로", "오늘", "부담", "먼저"]
HYPE_TERMS = ["최고", "압도", "완벽", "무조건", "대박", "혁신"]
MIN_GENERATED_TOKENS = 4


class MembershipRetentionItem(TypedDict):
    membership: str
    audience: str
    risk_stage: str
    must_include_terms: List[str]
    primary_metrics: List[str]


MEMBERSHIP_RETENTION_ITEMS: List[MembershipRetentionItem] = [
    {
        "membership": "CMDSPACE VIP 신규 멤버 첫 칠 일 리텐션 개선",
        "audience": "결제는 했지만 아직 습관이 안 잡힌 신규 VIP 멤버",
        "risk_stage": "결제 직후 이틀 안에 조용히 이탈하는 구간",
        "must_include_terms": ["VIP", "텔레그램", "체크인", "온보딩"],
        "primary_metrics": ["첫 칠 일 참여율", "재방문율", "이탈률"],
    },
    {
        "membership": "부트캠프 유료 멤버 첫 주 유지 개선",
        "audience": "결제 후 바로 실천에 못 들어가 멈추는 초보자",
        "risk_stage": "첫 주 안에 과제 진입을 못 하고 멈추는 구간",
        "must_include_terms": ["부트캠프", "체험", "미션", "체크인"],
        "primary_metrics": ["첫 주 참여율", "과제 완료율", "이탈률"],
    },
    {
        "membership": "Ailit 저가 입문 상품 구매자 후속 리텐션 개선",
        "audience": "작은 결제는 했지만 다음 단계 제안을 아직 이해 못 한 신규 고객",
        "risk_stage": "구매 직후 후속 행동 없이 조용히 이탈하는 구간",
        "must_include_terms": ["Ailit", "입문 상품", "체크인", "업셀"],
        "primary_metrics": ["후속 클릭률", "재방문율", "업셀 전환율"],
    },
    {
        "membership": "라이브 세션 참여자 다음 주 재참여 유지 개선",
        "audience": "한 번 참여했지만 다음 세션까지 습관이 이어지지 않는 멤버",
        "risk_stage": "라이브 직후 일주일 안에 관심이 식는 구간",
        "must_include_terms": ["라이브", "리플레이", "체크인", "재참여"],
        "primary_metrics": ["재참여율", "리플레이 시청률", "이탈률"],
    },
    {
        "membership": "텔레그램 커뮤니티 신규 합류자 첫 주 활성 유지 개선",
        "audience": "채널은 들어왔지만 말 한마디 안 남기고 눈팅만 하는 신규 합류자",
        "risk_stage": "첫 주 안에 발화 경험 없이 조용히 사라지는 구간",
        "must_include_terms": ["텔레그램", "체크인", "첫 주", "참여"],
        "primary_metrics": ["첫 주 발화율", "재방문율", "이탈률"],
    },
    {
        "membership": "기업 협업 후 리드 관리 유지 개선",
        "audience": "첫 미팅은 했지만 후속 자료를 받은 뒤 우선순위가 밀리는 기업 담당자",
        "risk_stage": "첫 접촉 이후 후속 응답이 끊기는 구간",
        "must_include_terms": ["협업", "후속", "체크인", "응답"],
        "primary_metrics": ["후속 응답률", "재미팅 성사", "계약 전환율"],
    },
]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def extract_section_map(answer: str) -> Dict[str, str]:
    pattern = re.compile(r"^(이탈원인|온보딩수정|리텐션장치|운영메시지|지표)\s*:\s*(.*)$", re.MULTILINE)
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
    return os.getenv("MIN_RETENTION_ULTRA_SMOKE", "").strip() in {"1", "true", "TRUE", "yes", "YES"}


def format_retention_prompt(item: MembershipRetentionItem) -> str:
    if is_ultra_smoke_mode():
        return (
            f"멤버십:{item['membership']}\n"
            f"위험:{item['risk_stage']}\n"
            "짧고 구체적으로 작성.\n"
            "이탈원인:\n온보딩수정:\n리텐션장치:\n운영메시지:\n지표:\n"
        )

    must_terms = ", ".join(item["must_include_terms"])
    metrics = ", ".join(item["primary_metrics"])
    return (
        "너는 평범한사업가 멤버십 유지율을 높이는 운영 전략가다. 과장 없이 실제 운영에 바로 넣을 수 있는 온보딩과 체크인 장치만 제안하라.\n\n"
        f"멤버십: {item['membership']}\n"
        f"핵심 고객: {item['audience']}\n"
        f"위험 구간: {item['risk_stage']}\n"
        f"반드시 넣을 말: {must_terms}\n"
        f"중요 지표: {metrics}\n\n"
        "아래 형식을 정확히 지켜 작성하라.\n"
        "이탈원인:\n"
        "온보딩수정:\n"
        "리텐션장치:\n"
        "운영메시지:\n"
        "지표:\n"
    )


def score_retention_answer(answer: str, item: MembershipRetentionItem) -> Dict[str, float]:
    normalized = _normalize_text(answer)
    lowered = normalized.lower()
    sections = extract_section_map(answer)

    section_hits = sum(1 for section in REQUIRED_SECTIONS if sections.get(section))
    section_coverage = section_hits / len(REQUIRED_SECTIONS)

    specific_hits = sum(1 for term in SPECIFIC_TERMS if term in normalized)
    specificity = min(1.0, 0.15 * specific_hits)

    retention_text = sections.get("리텐션장치", "") + " " + sections.get("온보딩수정", "")
    retention_hits = sum(1 for term in RETENTION_TERMS if term in retention_text)
    retention_mechanism = min(1.0, 0.15 * retention_hits)

    metric_text = sections.get("지표", "")
    metric_hits = sum(1 for term in METRIC_TERMS if term in metric_text)
    metric_quality = min(1.0, 0.18 * metric_hits)

    beginner_text = sections.get("운영메시지", "")
    beginner_hits = sum(1 for term in BEGINNER_TERMS if term in beginner_text)
    beginner_friendliness = min(1.0, 0.2 * beginner_hits)

    keyword_hits = sum(1 for term in item["must_include_terms"] if term.lower() in lowered)
    keyword_coverage = keyword_hits / len(item["must_include_terms"])

    hype_count = sum(1 for term in HYPE_TERMS if term in normalized)
    hype_penalty = min(0.3, 0.1 * hype_count)

    total = (
        0.2 * section_coverage
        + 0.22 * specificity
        + 0.22 * retention_mechanism
        + 0.16 * metric_quality
        + 0.1 * beginner_friendliness
        + 0.15 * keyword_coverage
        - hype_penalty
    )
    total = max(0.0, min(1.0, total))

    return {
        "total": total,
        "section_coverage": section_coverage,
        "specificity": specificity,
        "retention_mechanism": retention_mechanism,
        "metric_quality": metric_quality,
        "beginner_friendliness": beginner_friendliness,
        "keyword_coverage": keyword_coverage,
        "hype_penalty": -hype_penalty,
    }


class MinMembershipRetentionEnv(BaseEnv):
    """민 전용 멤버십 유지율 개선 실험 환경."""

    name = "min_membership_retention"

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
        self.items = MEMBERSHIP_RETENTION_ITEMS
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

    async def collect_trajectories(self, item: MembershipRetentionItem) -> Tuple[ScoredDataGroup, List[Item]]:
        user_message = {"role": "user", "content": format_retention_prompt(item)}
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
            reward_info = score_retention_answer(item["messages"][-1]["content"], item["item"])
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

    async def rollout_and_score_eval(self, item: MembershipRetentionItem) -> Dict[str, object]:
        completion = await self.server.chat_completion(
            messages=[{"role": "user", "content": format_retention_prompt(item)}],
            n=1,
            max_tokens=self.config.max_token_length,
            temperature=0.0,
            split="eval",
        )
        response_content = completion.choices[0].message.content
        reward_info = score_retention_answer(response_content, item)
        sample = {
            "membership": item["membership"],
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

    async def get_next_item(self) -> MembershipRetentionItem:
        next_item = self.items[self.iter % len(self.items)]
        self.iter += 1
        return next_item


if __name__ == "__main__":
    MinMembershipRetentionEnv.cli()
