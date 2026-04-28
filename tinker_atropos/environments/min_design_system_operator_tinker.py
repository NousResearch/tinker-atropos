import os
import random
import re
import time
from typing import Dict, List, Optional, Tuple, TypedDict, Union

from atroposlib.envs.base import APIServerConfig, BaseEnv, BaseEnvConfig, ScoredDataGroup
from atroposlib.type_definitions import Item
from tinker_atropos.config import TinkerAtroposConfig

CONFIG_PATH = "configs/default.yaml"
MIN_GENERATED_TOKENS = 0
REQUIRED_SECTIONS = ["작업분류", "디자인계약", "토큰적용", "드리프트", "검증", "기록"]
BAD_SIGNALS = ["예쁘게", "모던", "대충", "나중에", "자유롭게", "감각", "아무 색", "비슷하게"]
HYPE_TERMS = ["무조건", "완벽", "최고", "압도", "혁신"]


class DesignSystemOperatorItem(TypedDict):
    task_id: str
    title: str
    prompt: str
    must_include_terms: List[str]
    contract_terms: List[str]
    token_terms: List[str]
    drift_terms: List[str]
    routing_terms: List[str]
    verification_terms: List[str]
    style_terms: List[str]


DESIGN_SYSTEM_OPERATOR_ITEMS: List[DesignSystemOperatorItem] = [
    {
        "task_id": "design-system-ailit-landing-start",
        "title": "Ailit 랜딩 디자인 작업 착수",
        "prompt": "Ailit 랜딩 첫 화면을 더 신뢰감 있게 바꿔줘. 기존 프로젝트에 DESIGN.md가 있을 수도 있어.",
        "must_include_terms": ["DESIGN.md", "색상", "글꼴", "간격", "패치 후보", "브라우저 검증"],
        "contract_terms": ["DESIGN.md", "프로젝트 루트", "디자인 계약", "패치 후보"],
        "token_terms": ["색상", "글꼴", "간격", "모서리", "버튼", "카드", "토큰"],
        "drift_terms": ["드리프트", "피그마", "테일윈드", "코드", "브라우저 화면", "스크린샷"],
        "routing_terms": ["알피 씨엘아이", "브라우저 검증", "브라우저 화면", "검증"],
        "verification_terms": ["lint", "빌드", "브라우저 검증", "파일 존재", "스크린샷 비교"],
        "style_terms": ["쉬운", "복붙", "민", "바로", "과장 없음"],
    },
    {
        "task_id": "design-system-figma-drift-review",
        "title": "피그마와 DESIGN.md 드리프트 감사",
        "prompt": "피그마 시안은 있는데 코드랑 색이 조금 달라 보여. DESIGN.md 기준으로 어디가 틀어졌는지 봐줘.",
        "must_include_terms": ["figma-use", "DESIGN.md", "드리프트", "색상 변수", "코드 토큰", "스크린샷"],
        "contract_terms": ["figma-use", "DESIGN.md", "디자인 계약", "기준"],
        "token_terms": ["색상 변수", "코드 토큰", "토큰", "글꼴", "간격", "컴포넌트"],
        "drift_terms": ["드리프트", "피그마", "코드", "테일윈드", "스크린샷", "브라우저 화면"],
        "routing_terms": ["figma-use", "디자인 문맥", "스크린샷", "코드 반영"],
        "verification_terms": ["화면 비교", "lint", "빌드", "스크린샷 비교", "검증"],
        "style_terms": ["쉬운", "표", "바로", "민", "복붙"],
    },
    {
        "task_id": "design-system-tailwind-token-export",
        "title": "DESIGN.md에서 테일윈드 토큰 내보내기",
        "prompt": "이 프로젝트 디자인 토큰을 테일윈드에서 쓰게 정리해줘. 없는 값은 마음대로 만들지 말고 알려줘.",
        "must_include_terms": ["DESIGN.md", "npx -y @google/design.md lint", "export --format tailwind", "tailwind.theme.json", "없는 값", "패치 후보"],
        "contract_terms": ["DESIGN.md", "없는 값", "패치 후보", "디자인 계약"],
        "token_terms": ["토큰", "테일윈드", "tailwind.theme.json", "색상", "간격", "글꼴"],
        "drift_terms": ["드리프트", "테일윈드", "코드", "DESIGN.md", "없는 값"],
        "routing_terms": ["export --format tailwind", "테일윈드", "파일", "실행"],
        "verification_terms": ["npx -y @google/design.md lint", "lint", "파일 존재", "빌드", "검증"],
        "style_terms": ["마음대로", "임의", "먼저", "쉬운", "복붙"],
    },
    {
        "task_id": "design-system-public-hub-card-refresh",
        "title": "평범한사업가 공개 허브 카드 새로고침",
        "prompt": "평범한사업가 공개 허브 카드 디자인을 조금 더 선명하게 바꿔줘. 브랜드 결은 유지해야 해.",
        "must_include_terms": ["DESIGN.md", "브랜드 의도", "컴포넌트 상태", "카드", "버튼", "드리프트"],
        "contract_terms": ["DESIGN.md", "브랜드 의도", "디자인 계약", "기준"],
        "token_terms": ["컴포넌트 상태", "카드", "버튼", "색상", "글꼴", "간격"],
        "drift_terms": ["드리프트", "코드", "브라우저 화면", "스크린샷", "테일윈드"],
        "routing_terms": ["알피 씨엘아이", "코덱스 씨엘아이", "브라우저", "변경 파일"],
        "verification_terms": ["빌드", "브라우저", "스크린샷", "lint", "검증"],
        "style_terms": ["브랜드 결", "쉬운", "민", "과장 없음", "바로"],
    },
    {
        "task_id": "design-system-bootcamp-template-guardrail",
        "title": "부트캠프 수강생 템플릿 디자인 가드레일",
        "prompt": "부트캠프 수강생들이 복붙해서 쓸 수 있는 DESIGN.md 기반 앱 디자인 규칙을 만들어줘.",
        "must_include_terms": ["DESIGN.md", "복붙용 지시문", "초보자", "토큰", "하지 말 것", "검증"],
        "contract_terms": ["DESIGN.md", "복붙용 지시문", "기반", "가드레일"],
        "token_terms": ["토큰", "색상", "글꼴", "간격", "둥글기", "버튼", "카드"],
        "drift_terms": ["드리프트", "임의", "없는 값", "패치 후보", "비교"],
        "routing_terms": ["템플릿", "수강생", "복붙", "앱"],
        "verification_terms": ["검증", "npx -y @google/design.md lint", "lint", "대비율"],
        "style_terms": ["초보자", "복붙", "쉬운", "하지 말 것", "바로"],
    },
]


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _contains_term(text: str, term: str) -> bool:
    lowered = text.lower()
    if term.lower() in lowered:
        return True
    aliases = {
        "DESIGN.md": ["디자인 엠디", "design.md"],
        "figma-use": ["피그마 유즈", "figma use"],
        "알피 씨엘아이": ["rp-cli", "repo prompt", "repoprompt"],
        "코덱스 씨엘아이": ["codex cli", "codex"],
        "테일윈드": ["tailwind"],
        "npx -y @google/design.md lint": ["design.md lint", "lint design.md"],
        "export --format tailwind": ["tailwind export", "내보내기"],
        "패치 후보": ["patch 후보", "수정 후보"],
    }
    return any(alias.lower() in lowered for alias in aliases.get(term, []))


def extract_section_map(answer: str) -> Dict[str, str]:
    section_pattern = "|".join(REQUIRED_SECTIONS)
    pattern = re.compile(rf"^\s*({section_pattern})\s*:\s*(.*)$", re.MULTILINE)
    matches = list(pattern.finditer(answer))
    sections: Dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(answer)
        sections[match.group(1)] = _normalize_text(match.group(2) + " " + answer[start:end])
    return sections


def _coverage(text: str, terms: List[str]) -> float:
    return 1.0 if not terms else sum(1 for term in terms if _contains_term(text, term)) / len(terms)


def _bad_signal_penalty(answer: str) -> float:
    lowered = answer.lower()
    protected = any(phrase in lowered for phrase in ["임의 생성하지", "임의로 만들지", "임의 추가 금지"])
    count = sum(1 for signal in BAD_SIGNALS if signal in lowered and not (signal == "임의" and protected))
    hype_count = sum(1 for term in HYPE_TERMS if term in answer)
    return min(0.35, 0.06 * count + 0.08 * hype_count)


def is_ultra_smoke_mode() -> bool:
    return os.getenv("MIN_DESIGN_SYSTEM_OPERATOR_ULTRA_SMOKE", "").strip() in {"1", "true", "TRUE", "yes", "YES"}


def generation_max_tokens(configured_max: int) -> int:
    return min(int(configured_max), 768)


def format_design_system_operator_prompt(item: DesignSystemOperatorItem) -> str:
    if is_ultra_smoke_mode():
        return f"요청:{item['prompt']}\n짧고 구체적으로 작성. DESIGN.md를 먼저 확인.\n작업분류:\n디자인계약:\n토큰적용:\n드리프트:\n검증:\n기록:\n"
    must_terms = ", ".join(item["must_include_terms"])
    return (
        "너는 민의 디자인 시스템 오퍼레이터다. 디자인 또는 화면 작업을 시작하기 전에 DESIGN.md를 디자인 계약서로 먼저 확인하고, "
        "토큰 적용, 드리프트 기록, 검증 증거, 옵시디언 기록까지 닫는 답변을 작성하라.\n\n"
        f"요청: {item['prompt']}\n"
        f"반드시 넣을 말: {must_terms}\n"
        f"디자인계약 기준: {', '.join(item['contract_terms'])}\n"
        f"토큰적용 기준: {', '.join(item['token_terms'])}\n"
        f"드리프트 기준: {', '.join(item['drift_terms'])}\n"
        f"작업분류 또는 디자인계약 라우팅 기준: {', '.join(item['routing_terms'])}\n"
        f"검증 기준: {', '.join(item['verification_terms'])}\n"
        f"기록 기준: {', '.join(item['style_terms'])}\n\n"
        "아래 형식을 정확히 지켜 작성하라.\n작업분류:\n디자인계약:\n토큰적용:\n드리프트:\n검증:\n기록:\n"
    )


def score_design_system_operator_answer(answer: str, item: DesignSystemOperatorItem) -> Dict[str, float]:
    normalized = _normalize_text(answer)
    sections = extract_section_map(answer)
    section_coverage = sum(1 for section in REQUIRED_SECTIONS if sections.get(section)) / len(REQUIRED_SECTIONS)
    must_include_coverage = _coverage(normalized, item["must_include_terms"])
    contract_text = sections.get("디자인계약", "") + " " + normalized
    token_text = sections.get("토큰적용", "") + " " + normalized
    drift_text = sections.get("드리프트", "") + " " + normalized
    routing_text = sections.get("작업분류", "") + " " + sections.get("디자인계약", "") + " " + normalized
    verification_text = sections.get("검증", "") + " " + normalized
    style_text = sections.get("기록", "") + " " + normalized
    design_contract_discovery = min(1.0, 0.65 * _coverage(contract_text, item["contract_terms"]) + 0.35 * must_include_coverage)
    token_fidelity = min(1.0, 0.75 * _coverage(token_text, item["token_terms"]) + 0.25 * must_include_coverage)
    drift_handling = _coverage(drift_text, item["drift_terms"])
    implementation_routing = _coverage(routing_text, item["routing_terms"])
    verification_strength = _coverage(verification_text, item["verification_terms"])
    min_style_fit = _coverage(style_text, item["style_terms"])
    bad_penalty = _bad_signal_penalty(answer)
    total = max(0.0, min(1.0, 0.06 * section_coverage + 0.18 * design_contract_discovery + 0.20 * token_fidelity + 0.18 * drift_handling + 0.14 * implementation_routing + 0.18 * verification_strength + 0.12 * min_style_fit - bad_penalty))
    return {
        "total": total,
        "section_coverage": section_coverage,
        "design_contract_discovery": design_contract_discovery,
        "token_fidelity": token_fidelity,
        "drift_handling": drift_handling,
        "implementation_routing": implementation_routing,
        "verification_strength": verification_strength,
        "min_style_fit": min_style_fit,
        "must_include_coverage": must_include_coverage,
        "bad_signal_penalty": -bad_penalty,
    }


class MinDesignSystemOperatorEnv(BaseEnv):
    """민 전용 DESIGN.md 디자인 시스템 오퍼레이터 실험 환경."""

    name = "min_design_system_operator"

    def __init__(self, config: BaseEnvConfig, server_configs: List[APIServerConfig], slurm: bool = True, testing: bool = False):
        super().__init__(config, server_configs, slurm, testing)
        self.percent_correct_buffer = []
        self.eval_metrics = []
        self.items = DESIGN_SYSTEM_OPERATOR_ITEMS
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
        server_configs = [APIServerConfig(model_name=config.base_model, base_url=config.inference_api_url + "/v1", api_key="x", server_type="sglang", num_requests_for_eval=config.num_requests_for_eval)]
        return env_config, server_configs

    async def setup(self):
        if self.tokenizer.chat_template is None:
            self.tokenizer.chat_template = "{% for message in messages %}{% if message['role'] == 'user' %}{{ '<|start_header_id|>user<|end_header_id|>\\n\\n' + message['content'] + '<|eot_id|>' }}{% elif message['role'] == 'assistant' %}{{ '<|start_header_id|>assistant<|end_header_id|>\\n\\n' + message['content'] + '<|eot_id|>' }}{% endif %}{% if loop.last and message['role'] != 'assistant' %}{{ '<|start_header_id|>assistant<|end_header_id|>\\n\\n' }}{% endif %}{% endfor %}"

    async def wandb_log(self, wandb_metrics: Optional[Dict] = None):
        wandb_metrics = wandb_metrics or {}
        if self.percent_correct_buffer:
            wandb_metrics["train/percent_correct"] = sum(self.percent_correct_buffer) / len(self.percent_correct_buffer)
        self.percent_correct_buffer = []
        for item in self.eval_metrics:
            wandb_metrics[item[0]] = item[1]
        self.eval_metrics = []
        await super().wandb_log(wandb_metrics)

    async def collect_trajectories(self, item: DesignSystemOperatorItem) -> Tuple[ScoredDataGroup, List[Item]]:
        user_message = {"role": "user", "content": format_design_system_operator_prompt(item)}
        async with self.server.managed_server(tokenizer=self.tokenizer) as managed:
            chat_completion = await managed.chat_completion(messages=[user_message], n=self.config.group_size, max_tokens=generation_max_tokens(self.config.max_token_length), temperature=1.0)
            nodes = managed.get_state()["nodes"]
        to_score = []
        for choice, node in zip(chat_completion.choices, nodes):
            to_score.append({"messages": (user_message, {"role": "assistant", "content": choice.message.content}), "item": item, "finish_reason": choice.finish_reason, "tokens": node.tokens, "masked_tokens": node.masked_tokens, "logprobs": node.logprobs})
        return await self.score(to_score), []

    async def score(self, rollout_group_data) -> Union[Optional[ScoredDataGroup], List[Optional[ScoredDataGroup]]]:
        scores = ScoredDataGroup()
        scores["tokens"] = []
        scores["masks"] = []
        scores["scores"] = []
        scores["inference_logprobs"] = []
        random.shuffle(rollout_group_data)
        for item in rollout_group_data:
            reward_info = score_design_system_operator_answer(item["messages"][-1]["content"], item["item"])
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

    async def rollout_and_score_eval(self, item: DesignSystemOperatorItem) -> Dict[str, object]:
        completion = await self.server.chat_completion(messages=[{"role": "user", "content": format_design_system_operator_prompt(item)}], n=1, max_tokens=generation_max_tokens(self.config.max_token_length), temperature=0.0, split="eval")
        response_content = completion.choices[0].message.content
        reward_info = score_design_system_operator_answer(response_content, item)
        return {"score": reward_info["total"], "sample": {"prompt": item["prompt"], "answer": response_content, "score": reward_info["total"], "details": reward_info, "finish_reason": completion.choices[0].finish_reason}}

    async def evaluate(self, *args, **kwargs):
        start_time = time.time()
        results = [await self.rollout_and_score_eval(item) for item in self.items]
        mean_score = sum(result["score"] for result in results) / len(results)
        self.eval_metrics.append(("eval/mean_score", mean_score))
        await self.evaluate_log(metrics={"eval/mean_score": mean_score}, samples=[result["sample"] for result in results], start_time=start_time, end_time=time.time(), generation_parameters={"temperature": 0.0, "max_tokens": generation_max_tokens(self.config.max_token_length)})

    async def get_next_item(self) -> DesignSystemOperatorItem:
        next_item = self.items[self.iter % len(self.items)]
        self.iter += 1
        return next_item


if __name__ == "__main__":
    MinDesignSystemOperatorEnv.cli()
