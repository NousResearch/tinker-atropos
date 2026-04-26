import os
import random
import re
import time
from typing import Dict, List, Optional, Tuple, TypedDict, Union

from atroposlib.envs.base import APIServerConfig, BaseEnv, BaseEnvConfig, ScoredDataGroup
from atroposlib.type_definitions import Item
from tinker_atropos.config import TinkerAtroposConfig

CONFIG_PATH = "configs/default.yaml"
MIN_GENERATED_TOKENS = 12

REQUIRED_SECTIONS = ["작업분류", "선행경로", "실행표면", "산출물", "검증", "기록"]
HYPE_TERMS = ["무조건", "완벽", "최고", "압도", "혁신"]


class AgenticProductionRouterItem(TypedDict):
    task_id: str
    title: str
    prompt: str
    must_include_terms: List[str]
    routing_terms: List[str]
    prerequisite_terms: List[str]
    execution_terms: List[str]
    artifact_terms: List[str]
    verification_terms: List[str]
    learning_terms: List[str]


AGENTIC_PRODUCTION_ROUTER_ITEMS: List[AgenticProductionRouterItem] = [
    {
        "task_id": "production-router-landing-build",
        "title": "웹사이트 제작 요청 라우팅",
        "prompt": "새 랜딩페이지를 만들고 싶다. 피그마 시안, 디자인 엠디, 지피티 이미지 투 이미지, 코덱스 씨엘아이 구현, 브라우저 검증까지 연결해줘.",
        "must_include_terms": ["알피 씨엘아이", "DESIGN.md", "figma-use", "코덱스 씨엘아이", "브라우저 검증", "빌드"],
        "routing_terms": ["웹사이트", "랜딩", "코드", "피그마"],
        "prerequisite_terms": ["알피 씨엘아이", "DESIGN.md", "figma-use", "피그마", "디자인 문맥"],
        "execution_terms": ["헤르메스", "코덱스 씨엘아이", "구현", "지피티 이미지 투", "openai-codex-gpt-image-2-workflow"],
        "artifact_terms": ["변경 파일", "이미지 파일", "프롬프트", "스크린샷", "드리프트"],
        "verification_terms": ["빌드", "테스트", "브라우저 검증", "파일 존재", "완료 보고"],
        "learning_terms": ["옵시디언", "티커 아트로포스", "평가 세트", "실패 패턴", "성공 규칙"],
    },
    {
        "task_id": "production-router-image-to-video",
        "title": "지피티 이미지 투에서 시댄스 영상까지 이어지는 요청 라우팅",
        "prompt": "지피티 이미지 투로 제품 이미지를 만들고, 럽아트에서 시댄스 이점영 영상까지 실험해줘.",
        "must_include_terms": ["openai-codex-gpt-image-2-workflow", "파일 존재", "럽아트", "시댄스", "점수표", "다음 변수"],
        "routing_terms": ["이미지", "영상", "럽아트", "시댄스"],
        "prerequisite_terms": ["openai-codex-gpt-image-2-workflow", "지피티 이미지 투", "프롬프트", "파일 존재"],
        "execution_terms": ["이미지 생성", "럽아트", "시댄스", "영상", "변형"],
        "artifact_terms": ["이미지 파일", "영상", "링크", "프롬프트", "점수표"],
        "verification_terms": ["파일 존재", "크기", "시각 확인", "점수표", "결과"],
        "learning_terms": ["학습 질문", "기준군", "변형", "유지할 것", "버릴 것", "다음 변수"],
    },
    {
        "task_id": "production-router-figma-implementation",
        "title": "피그마 구현 요청 라우팅",
        "prompt": "피그마 파일을 기준으로 지금 웹 앱 화면을 맞춰줘. 디자인 엠디도 같이 써줘.",
        "must_include_terms": ["figma-use", "스크린샷", "디자인 문맥", "DESIGN.md", "드리프트", "코드 반영"],
        "routing_terms": ["피그마", "웹 앱", "화면", "디자인"],
        "prerequisite_terms": ["figma-use", "디자인 문맥", "스크린샷", "DESIGN.md"],
        "execution_terms": ["코드 반영", "구현", "토큰", "컴포넌트"],
        "artifact_terms": ["스크린샷", "노드", "드리프트", "변경 파일", "DESIGN.md"],
        "verification_terms": ["브라우저", "화면 비교", "린트", "빌드", "드리프트"],
        "learning_terms": ["옵시디언", "스킬", "디자인 계약", "실패 패턴"],
    },
    {
        "task_id": "production-router-codex-in-hermes",
        "title": "헤르메스 안 코덱스 씨엘아이 실행 요청 라우팅",
        "prompt": "이 저장소 버그를 코덱스로 고쳐줘. 헤르메스가 알아서 검증해줘.",
        "must_include_terms": ["알피 씨엘아이", "수락 기준", "코덱스 씨엘아이", "변경 파일", "테스트", "헤르메스 최종 검토"],
        "routing_terms": ["저장소", "버그", "코드", "검증"],
        "prerequisite_terms": ["알피 씨엘아이", "저장소", "수락 기준", "문맥"],
        "execution_terms": ["코덱스 씨엘아이", "헤르메스", "패치", "구현"],
        "artifact_terms": ["변경 파일", "로그", "diff", "테스트 결과"],
        "verification_terms": ["테스트", "빌드", "변경 파일", "헤르메스 최종 검토"],
        "learning_terms": ["회귀", "스킬", "옵시디언", "실패 패턴"],
    },
    {
        "task_id": "production-router-obsidian-research",
        "title": "연구 결과 옵시디언 기록 요청 라우팅",
        "prompt": "최근 작업 변화를 바탕으로 헤르메스를 민에게 더 맞게 개선하는 연구를 진행해줘.",
        "must_include_terms": ["큐엠디", "알피 씨엘아이", "티커 아트로포스", "옵시디언 노트", "평가 세트", "검증 근거"],
        "routing_terms": ["연구", "헤르메스", "개선", "평가"],
        "prerequisite_terms": ["큐엠디", "알피 씨엘아이", "기존 노트", "저장소 문맥"],
        "execution_terms": ["티커 아트로포스", "평가 세트", "실험", "헤르메스"],
        "artifact_terms": ["옵시디언 노트", "제이슨", "마크다운", "경로"],
        "verification_terms": ["검증 근거", "재조회", "파일 존재", "테스트"],
        "learning_terms": ["스킬", "옵시디언", "티커 아트로포스", "운영 규칙"],
    },
]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _contains_term(text: str, term: str) -> bool:
    if term.lower() in text.lower():
        return True
    aliases = {
        "DESIGN.md": ["디자인 엠디", "design.md"],
        "figma-use": ["피그마 유즈", "figma use"],
        "openai-codex-gpt-image-2-workflow": ["오픈에이아이 코덱스 지피티 이미지 투", "지피티 이미지 투 워크플로우"],
        "Repo Prompt": ["알피", "알피 씨엘아이"],
    }
    return any(alias.lower() in text.lower() for alias in aliases.get(term, []))


def extract_section_map(answer: str) -> Dict[str, str]:
    section_pattern = "|".join(REQUIRED_SECTIONS)
    pattern = re.compile(rf"^\s*({section_pattern})\s*:\s*(.*)$", re.MULTILINE)
    matches = list(pattern.finditer(answer))
    sections: Dict[str, str] = {}
    for index, match in enumerate(matches):
        section_name = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(answer)
        sections[section_name] = _normalize_text(match.group(2) + " " + answer[start:end])
    return sections


def _coverage(text: str, terms: List[str]) -> float:
    if not terms:
        return 1.0
    hits = sum(1 for term in terms if _contains_term(text, term))
    return hits / len(terms)


def is_ultra_smoke_mode() -> bool:
    return os.getenv("MIN_PRODUCTION_ROUTER_ULTRA_SMOKE", "").strip() in {"1", "true", "TRUE", "yes", "YES"}


def format_production_router_prompt(item: AgenticProductionRouterItem) -> str:
    if is_ultra_smoke_mode():
        return (
            f"요청:{item['prompt']}\n"
            "짧고 구체적으로 작성.\n"
            "작업분류:\n선행경로:\n실행표면:\n산출물:\n검증:\n기록:\n"
        )
    must_terms = ", ".join(item["must_include_terms"])
    return (
        "너는 민의 헤르메스 제작 라우터다. 계획만 말하지 말고 어떤 선행 도구를 쓰고, 어떤 실행 표면으로 보내며, 무엇으로 검증하고, 어디에 기록할지 정리하라.\n\n"
        f"요청: {item['prompt']}\n"
        f"반드시 넣을 말: {must_terms}\n\n"
        "아래 형식을 정확히 지켜 작성하라.\n"
        "작업분류:\n"
        "선행경로:\n"
        "실행표면:\n"
        "산출물:\n"
        "검증:\n"
        "기록:\n"
    )


def score_production_router_answer(answer: str, item: AgenticProductionRouterItem) -> Dict[str, float]:
    normalized = _normalize_text(answer)
    sections = extract_section_map(answer)
    section_coverage = sum(1 for section in REQUIRED_SECTIONS if sections.get(section)) / len(REQUIRED_SECTIONS)

    routing_text = sections.get("작업분류", "") + " " + normalized
    prerequisite_text = sections.get("선행경로", "")
    execution_text = sections.get("실행표면", "")
    artifact_text = sections.get("산출물", "")
    verification_text = sections.get("검증", "")
    learning_text = sections.get("기록", "")

    must_include_coverage = _coverage(normalized, item["must_include_terms"])
    routing_accuracy = min(1.0, 0.55 * _coverage(routing_text, item["routing_terms"]) + 0.45 * must_include_coverage)
    prerequisite_gate_compliance = _coverage(prerequisite_text, item["prerequisite_terms"])
    execution_surface_choice = _coverage(execution_text, item["execution_terms"])
    artifact_contract = _coverage(artifact_text, item["artifact_terms"])
    verification_strength = _coverage(verification_text, item["verification_terms"])
    learning_loop_capture = _coverage(learning_text, item["learning_terms"])

    hype_count = sum(1 for term in HYPE_TERMS if term in normalized)
    hype_penalty = min(0.3, 0.1 * hype_count)
    total = (
        0.06 * section_coverage
        + 0.18 * routing_accuracy
        + 0.18 * prerequisite_gate_compliance
        + 0.14 * execution_surface_choice
        + 0.16 * artifact_contract
        + 0.18 * verification_strength
        + 0.10 * learning_loop_capture
        - hype_penalty
    )
    total = max(0.0, min(1.0, total))
    return {
        "total": total,
        "section_coverage": section_coverage,
        "routing_accuracy": routing_accuracy,
        "prerequisite_gate_compliance": prerequisite_gate_compliance,
        "execution_surface_choice": execution_surface_choice,
        "artifact_contract": artifact_contract,
        "verification_strength": verification_strength,
        "learning_loop_capture": learning_loop_capture,
        "must_include_coverage": must_include_coverage,
        "hype_penalty": -hype_penalty,
    }


class MinAgenticProductionRouterEnv(BaseEnv):
    """민 전용 헤르메스 제작 라우터 실험 환경."""

    name = "min_agentic_production_router"

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
        self.items = AGENTIC_PRODUCTION_ROUTER_ITEMS
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
                "{% if message['role'] == 'user' %}"
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

    async def collect_trajectories(self, item: AgenticProductionRouterItem) -> Tuple[ScoredDataGroup, List[Item]]:
        user_message = {"role": "user", "content": format_production_router_prompt(item)}
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
            to_score.append(
                {
                    "messages": (user_message, {"role": "assistant", "content": choice.message.content}),
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
            reward_info = score_production_router_answer(item["messages"][-1]["content"], item["item"])
            masked_tokens = item["masked_tokens"]
            if len([1 for token in masked_tokens if token != -100]) < MIN_GENERATED_TOKENS:
                continue
            scores["tokens"].append(item["tokens"])
            scores["masks"].append(masked_tokens)
            scores["inference_logprobs"].append(item["logprobs"])
            scores["scores"].append(float(reward_info["total"]))
            self.percent_correct_buffer.append(1.0 if reward_info["total"] >= 0.85 else 0.0)
            if len(scores["tokens"]) >= self.config.group_size:
                break
        return scores if scores["scores"] else None

    async def rollout_and_score_eval(self, item: AgenticProductionRouterItem) -> Dict[str, object]:
        completion = await self.server.chat_completion(
            messages=[{"role": "user", "content": format_production_router_prompt(item)}],
            n=1,
            max_tokens=self.config.max_token_length,
            temperature=0.0,
            split="eval",
        )
        response_content = completion.choices[0].message.content
        reward_info = score_production_router_answer(response_content, item)
        sample = {
            "prompt": item["prompt"],
            "answer": response_content,
            "score": reward_info["total"],
            "details": reward_info,
            "finish_reason": completion.choices[0].finish_reason,
        }
        return {"score": reward_info["total"], "sample": sample}

    async def evaluate(self, *args, **kwargs):
        start_time = time.time()
        results = [await self.rollout_and_score_eval(item) for item in self.items]
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

    async def get_next_item(self) -> AgenticProductionRouterItem:
        next_item = self.items[self.iter % len(self.items)]
        self.iter += 1
        return next_item


if __name__ == "__main__":
    MinAgenticProductionRouterEnv.cli()
