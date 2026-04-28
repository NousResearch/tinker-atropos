import os
import random
import re
import time
from typing import Dict, List, Tuple, TypedDict, Union, Optional

from atroposlib.envs.base import APIServerConfig, BaseEnv, BaseEnvConfig, ScoredDataGroup
from atroposlib.type_definitions import Item
from tinker_atropos.config import TinkerAtroposConfig

CONFIG_PATH = "configs/default.yaml"

REQUIRED_SECTIONS = ["가설", "찾을정보", "비교기준", "결론", "다음행동"]
COMPARE_TERMS = ["가격", "후기", "체험", "차이", "비교", "기준", "장벽", "사례"]
ACTION_TERMS = ["오늘", "바로", "정리", "표", "바꾼다", "확인", "실험"]
SPECIFIC_TERMS = ["셋", "세 가지", "첫 화면", "가격 구간", "랜딩", "문구", "표"]
HYPE_TERMS = ["무조건", "완벽", "최고", "압도", "혁신"]
MIN_GENERATED_TOKENS = 4


class AgenticResearchItem(TypedDict):
    question: str
    audience: str
    desired_output: str
    must_include_terms: List[str]


AGENTIC_RESEARCH_ITEMS: List[AgenticResearchItem] = [
    {
        "question": "Ailit와 경쟁 컨설팅 상품을 비교 조사해 어떤 차별점을 첫 화면에서 더 강하게 보여줄지 정리한다.",
        "audience": "AI 도구 세팅이 막힌 일인 사업가",
        "desired_output": "경쟁 비교 관점과 바로 실행할 한 가지 수정안",
        "must_include_terms": ["Ailit", "경쟁사", "첫 화면", "가격"],
    },
    {
        "question": "부트캠프와 비슷한 해외 상품을 조사해 무료에서 유료 전환 장치를 비교한다.",
        "audience": "무료 콘텐츠는 보지만 아직 결제를 망설이는 예비 고객",
        "desired_output": "비교 기준과 바로 적용할 전환 장치",
        "must_include_terms": ["부트캠프", "전환", "무료", "유료"],
    },
    {
        "question": "텔레그램 커뮤니티 운영이 강한 경쟁 사례를 조사해 우리 채널 참여 루프에 어떤 차이가 있는지 정리한다.",
        "audience": "채널은 운영 중이지만 발화와 체크인이 약한 커뮤니티 운영자",
        "desired_output": "참여 루프 비교와 바로 적용할 체크인 장치",
        "must_include_terms": ["텔레그램", "참여", "체크인", "비교"],
    },
    {
        "question": "Ailit 입문 상품과 유사한 저가 오퍼를 조사해 상담 업셀 연결 방식을 비교한다.",
        "audience": "작은 결제에서 상담으로 연결할 구조를 찾는 일인 사업가",
        "desired_output": "업셀 관점 비교와 첫 화면 수정안",
        "must_include_terms": ["Ailit", "입문 상품", "상담", "업셀"],
    },
    {
        "question": "유튜브 설명란을 잘 쓰는 경쟁 채널을 조사해 상담 링크 연결 방식의 차이를 정리한다.",
        "audience": "조회수는 있지만 설명란 전환 구조가 약한 크리에이터",
        "desired_output": "설명란 비교 기준과 즉시 바꿀 문장 한 가지",
        "must_include_terms": ["유튜브", "설명란", "상담", "링크"],
    },
    {
        "question": "기업 협업 소개 페이지를 조사해 신뢰 요소와 사례 배치 방식의 차이를 비교한다.",
        "audience": "협업 문의는 오지만 신뢰 설계가 약한 개인 브랜드 운영자",
        "desired_output": "신뢰 요소 비교와 바로 추가할 사례 블록",
        "must_include_terms": ["협업", "사례", "신뢰", "페이지"],
    },
]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def extract_section_map(answer: str) -> Dict[str, str]:
    pattern = re.compile(r"^(가설|찾을정보|비교기준|결론|다음행동)\s*:\s*(.*)$", re.MULTILINE)
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
    return os.getenv("MIN_RESEARCH_ULTRA_SMOKE", "").strip() in {"1", "true", "TRUE", "yes", "YES"}


def format_research_prompt(item: AgenticResearchItem) -> str:
    if is_ultra_smoke_mode():
        return (
            f"질문:{item['question']}\n"
            "짧고 구체적으로 작성.\n"
            "가설:\n찾을정보:\n비교기준:\n결론:\n다음행동:\n"
        )

    must_terms = ", ".join(item["must_include_terms"])
    return (
        "너는 평범한사업가 비즈니스를 돕는 조사 전략가다. 검색을 하기 전에 무엇을 어떻게 비교할지 먼저 구조화한다. 허풍 없이 바로 조사 가능한 계획만 제안하라.\n\n"
        f"질문: {item['question']}\n"
        f"대상 고객: {item['audience']}\n"
        f"원하는 결과: {item['desired_output']}\n"
        f"반드시 넣을 말: {must_terms}\n\n"
        "아래 형식을 정확히 지켜 작성하라.\n"
        "가설:\n"
        "찾을정보:\n"
        "비교기준:\n"
        "결론:\n"
        "다음행동:\n"
    )


def score_research_answer(answer: str, item: AgenticResearchItem) -> Dict[str, float]:
    normalized = _normalize_text(answer)
    lowered = normalized.lower()
    sections = extract_section_map(answer)

    section_hits = sum(1 for section in REQUIRED_SECTIONS if sections.get(section))
    section_coverage = section_hits / len(REQUIRED_SECTIONS)

    comparison_text = sections.get("찾을정보", "") + " " + sections.get("비교기준", "")
    comparison_hits = sum(1 for term in COMPARE_TERMS if term in comparison_text)
    comparison_quality = min(1.0, 0.15 * comparison_hits)

    action_text = sections.get("다음행동", "")
    action_hits = sum(1 for term in ACTION_TERMS if term in action_text)
    actionability = min(1.0, 0.18 * action_hits)

    specific_hits = sum(1 for term in SPECIFIC_TERMS if term in normalized)
    specificity = min(1.0, 0.16 * specific_hits)

    keyword_hits = sum(1 for term in item["must_include_terms"] if term.lower() in lowered)
    keyword_coverage = keyword_hits / len(item["must_include_terms"])

    hype_count = sum(1 for term in HYPE_TERMS if term in normalized)
    hype_penalty = min(0.3, 0.1 * hype_count)

    total = (
        0.22 * section_coverage
        + 0.24 * comparison_quality
        + 0.2 * actionability
        + 0.18 * specificity
        + 0.16 * keyword_coverage
        - hype_penalty
    )
    total = max(0.0, min(1.0, total))

    return {
        "total": total,
        "section_coverage": section_coverage,
        "comparison_quality": comparison_quality,
        "actionability": actionability,
        "specificity": specificity,
        "keyword_coverage": keyword_coverage,
        "hype_penalty": -hype_penalty,
    }


class MinAgenticResearchEnv(BaseEnv):
    """민 전용 조사 계획 실험 환경."""

    name = "min_agentic_research"

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
        self.items = AGENTIC_RESEARCH_ITEMS
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

    async def collect_trajectories(self, item: AgenticResearchItem) -> Tuple[ScoredDataGroup, List[Item]]:
        user_message = {"role": "user", "content": format_research_prompt(item)}
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
            reward_info = score_research_answer(item["messages"][-1]["content"], item["item"])
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

    async def rollout_and_score_eval(self, item: AgenticResearchItem) -> Dict[str, object]:
        completion = await self.server.chat_completion(
            messages=[{"role": "user", "content": format_research_prompt(item)}],
            n=1,
            max_tokens=self.config.max_token_length,
            temperature=0.0,
            split="eval",
        )
        response_content = completion.choices[0].message.content
        reward_info = score_research_answer(response_content, item)
        sample = {
            "question": item["question"],
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

    async def get_next_item(self) -> AgenticResearchItem:
        next_item = self.items[self.iter % len(self.items)]
        self.iter += 1
        return next_item


if __name__ == "__main__":
    MinAgenticResearchEnv.cli()
