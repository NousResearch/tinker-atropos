import os
import random
import re
import time
from typing import Dict, List, Tuple, TypedDict, Union, Optional

from atroposlib.envs.base import APIServerConfig, BaseEnv, BaseEnvConfig, ScoredDataGroup
from atroposlib.type_definitions import Item
from tinker_atropos.config import TinkerAtroposConfig

CONFIG_PATH = "configs/default.yaml"

REQUIRED_SECTIONS = ["병목", "개선안", "카피수정", "실험", "지표"]
SPECIFIC_TERMS = ["첫 화면", "헤드라인", "설명란", "상담", "신청", "버튼", "문장", "일주일", "이번 주"]
COPY_TERMS = ["누구", "문제", "제안", "진단", "Ailit", "일인 사업가", "AI 도구"]
EXPERIMENT_TERMS = ["반반", "비교", "실험", "일주일", "이번 주", "기존", "새"]
METRIC_TERMS = ["클릭률", "전환율", "신청", "%", "퍼센트", "건"]
HYPE_TERMS = ["최고", "혁신", "압도", "무조건", "완벽", "대박"]
MIN_GENERATED_TOKENS = 4


class LandingCROItem(TypedDict):
    page_type: str
    audience: str
    offer: str
    must_include_terms: List[str]
    primary_metrics: List[str]


LANDING_CRO_ITEMS: List[LandingCROItem] = [
    {
        "page_type": "Ailit 상담 전환 랜딩 첫 화면 개선",
        "audience": "AI 도구는 쓰지만 매출 흐름이 아직 없는 일인 사업가",
        "offer": "Ailit 진단 세션",
        "must_include_terms": ["Ailit", "상담", "일인 사업가", "진단"],
        "primary_metrics": ["클릭률", "상담 신청", "전환율"],
    },
    {
        "page_type": "부트캠프 체험 신청 랜딩 개선",
        "audience": "무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객",
        "offer": "체험 과제와 업그레이드 안내",
        "must_include_terms": ["부트캠프", "체험", "업그레이드", "설명란"],
        "primary_metrics": ["체험 신청", "결제 전환율", "이탈률"],
    },
    {
        "page_type": "텔레그램 채널 합류 랜딩 개선",
        "audience": "영상은 봤지만 아직 채널 합류 필요성을 못 느끼는 시청자",
        "offer": "텔레그램 채널 합류와 체크리스트 보상",
        "must_include_terms": ["텔레그램", "체크리스트", "합류", "설명란"],
        "primary_metrics": ["채널 유입", "링크 클릭", "합류 전환율"],
    },
    {
        "page_type": "Ailit 입문 상품 랜딩 개선",
        "audience": "상담은 부담스럽지만 작은 결제로 먼저 시작해보고 싶은 잠재 고객",
        "offer": "입문 상품과 이후 상담 업셀",
        "must_include_terms": ["Ailit", "입문 상품", "상담", "업셀"],
        "primary_metrics": ["구매 전환율", "업셀 클릭", "환불률"],
    },
    {
        "page_type": "기업 협업 문의 랜딩 개선",
        "audience": "평범한사업가와 협업을 검토하는 기업 담당자",
        "offer": "브랜드 맞춤형 협업 패키지",
        "must_include_terms": ["협업", "브랜드", "신뢰", "사례"],
        "primary_metrics": ["문의 전환율", "미팅 성사", "응답률"],
    },
    {
        "page_type": "라이브 참여 신청 랜딩 개선",
        "audience": "유료 멤버이지만 아직 라이브 신청까지는 하지 않는 기존 고객",
        "offer": "라이브 참여 신청과 리플레이 보장",
        "must_include_terms": ["라이브", "신청", "리플레이", "참여"],
        "primary_metrics": ["신청 전환율", "참여율", "리플레이 시청률"],
    },
]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def extract_section_map(answer: str) -> Dict[str, str]:
    pattern = re.compile(r"^(병목|개선안|카피수정|실험|지표)\s*:\s*(.*)$", re.MULTILINE)
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
    return os.getenv("MIN_LANDING_CRO_ULTRA_SMOKE", "").strip() in {"1", "true", "TRUE", "yes", "YES"}


def format_landing_prompt(item: LandingCROItem) -> str:
    if is_ultra_smoke_mode():
        return (
            f"페이지:{item['page_type']}\n"
            f"상품:{item['offer']}\n"
            "짧고 구체적으로 작성.\n"
            "병목:\n개선안:\n카피수정:\n실험:\n지표:\n"
        )

    must_terms = ", ".join(item["must_include_terms"])
    metrics = ", ".join(item["primary_metrics"])
    return (
        "너는 평범한사업가 브랜드의 랜딩 전환을 개선하는 CRO 전략가다. 과장 없이 실제로 바꿀 문장과 실험만 제안하라.\n\n"
        f"페이지 유형: {item['page_type']}\n"
        f"핵심 고객: {item['audience']}\n"
        f"제안 상품: {item['offer']}\n"
        f"반드시 넣을 말: {must_terms}\n"
        f"중요 지표: {metrics}\n\n"
        "아래 형식을 정확히 지켜 작성하라.\n"
        "병목:\n"
        "개선안:\n"
        "카피수정:\n"
        "실험:\n"
        "지표:\n"
    )


def score_landing_answer(answer: str, item: LandingCROItem) -> Dict[str, float]:
    normalized = _normalize_text(answer)
    lowered = normalized.lower()
    sections = extract_section_map(answer)

    section_hits = sum(1 for section in REQUIRED_SECTIONS if sections.get(section))
    section_coverage = section_hits / len(REQUIRED_SECTIONS)

    specific_hits = sum(1 for term in SPECIFIC_TERMS if term in normalized)
    specificity = min(1.0, 0.15 * specific_hits)

    copy_text = sections.get("카피수정", "")
    copy_hits = sum(1 for term in COPY_TERMS if term.lower() in copy_text.lower())
    copy_quality = min(1.0, 0.2 * copy_hits)
    if len(copy_text) >= 25:
        copy_quality = min(1.0, copy_quality + 0.2)

    experiment_text = sections.get("실험", "")
    experiment_hits = sum(1 for term in EXPERIMENT_TERMS if term in experiment_text)
    experiment_quality = min(1.0, 0.15 * experiment_hits)

    metric_text = sections.get("지표", "")
    metric_hits = sum(1 for term in METRIC_TERMS if term in metric_text)
    metric_quality = metric_hits / len(METRIC_TERMS) if METRIC_TERMS else 0.0

    keyword_hits = sum(1 for term in item["must_include_terms"] if term.lower() in lowered)
    keyword_coverage = keyword_hits / len(item["must_include_terms"])

    hype_count = sum(1 for term in HYPE_TERMS if term in normalized)
    hype_penalty = min(0.3, 0.1 * hype_count)

    total = (
        0.2 * section_coverage
        + 0.2 * specificity
        + 0.2 * copy_quality
        + 0.15 * experiment_quality
        + 0.15 * metric_quality
        + 0.1 * keyword_coverage
        - hype_penalty
    )
    total = max(0.0, min(1.0, total))

    return {
        "total": total,
        "section_coverage": section_coverage,
        "specificity": specificity,
        "copy_quality": copy_quality,
        "experiment_quality": experiment_quality,
        "metric_quality": metric_quality,
        "keyword_coverage": keyword_coverage,
        "hype_penalty": -hype_penalty,
    }


class MinLandingCROEnv(BaseEnv):
    """민 전용 랜딩 전환 최적화 실험 환경."""

    name = "min_landing_cro"

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
        self.items = LANDING_CRO_ITEMS
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

    async def collect_trajectories(self, item: LandingCROItem) -> Tuple[ScoredDataGroup, List[Item]]:
        user_message = {"role": "user", "content": format_landing_prompt(item)}
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
            reward_info = score_landing_answer(item["messages"][-1]["content"], item["item"])
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

    async def rollout_and_score_eval(self, item: LandingCROItem) -> Dict[str, object]:
        completion = await self.server.chat_completion(
            messages=[{"role": "user", "content": format_landing_prompt(item)}],
            n=1,
            max_tokens=self.config.max_token_length,
            temperature=0.0,
            split="eval",
        )
        response_content = completion.choices[0].message.content
        reward_info = score_landing_answer(response_content, item)
        sample = {
            "page_type": item["page_type"],
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

    async def get_next_item(self) -> LandingCROItem:
        next_item = self.items[self.iter % len(self.items)]
        self.iter += 1
        return next_item


if __name__ == "__main__":
    MinLandingCROEnv.cli()
