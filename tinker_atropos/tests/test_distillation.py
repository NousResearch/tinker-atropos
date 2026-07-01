import pytest
from tinker_atropos.trainer import TinkerAtroposTrainer
from tinker_atropos.config import TinkerAtroposConfig


@pytest.fixture
def trainer():
    config = TinkerAtroposConfig()
    trainer = TinkerAtroposTrainer(config=config)
    return trainer


def make_batch(
    tokens_list,
    logprobs_list,
    scores,
    distill_token_ids=None,
    distill_logprobs=None,
    overrides=None,
):
    """Helper to build a batch dict matching atropos format."""
    item = {
        "tokens": tokens_list,
        "inference_logprobs": logprobs_list,
        "scores": scores,
        "overrides": overrides,
    }
    if distill_token_ids is not None:
        item["distill_token_ids"] = distill_token_ids
    if distill_logprobs is not None:
        item["distill_logprobs"] = distill_logprobs
    return {"batch": [item]}


class TestDistillFieldNames:
    """Verify the trainer reads the correct field names from atropos."""

    def test_detects_distill_data(self, trainer):
        """distill_ (double L) fields should be detected."""
        batch = make_batch(
            tokens_list=[[1, 2, 3, 4, 5], [1, 2, 3, 4, 6]],
            logprobs_list=[
                [1.0, 1.0, -0.5, -0.3, -0.2],
                [1.0, 1.0, -0.4, -0.35, -0.25],
            ],
            scores=[2.0, 1.0],
            distill_token_ids=[
                [[1], [2], [3], [4], [5]],
                [[1], [2], [3], [4], [6]],
            ],
            distill_logprobs=[
                [[-0.1], [-0.1], [-0.6], [-0.4], [-0.3]],
                [[-0.1], [-0.1], [-0.5], [-0.45], [-0.35]],
            ],
        )

        _, _, has_distil = trainer.pad_data_to_good_offset(batch)
        assert has_distil is True

    def test_no_distill_without_fields(self, trainer):
        """Without distill fields, has_distil should be False."""
        batch = make_batch(
            tokens_list=[[1, 2, 3, 4], [1, 2, 3, 5]],
            logprobs_list=[
                [1.0, 1.0, -0.5, -0.3],
                [1.0, 1.0, -0.4, -0.2],
            ],
            scores=[2.0, 1.0],
        )

        _, _, has_distil = trainer.pad_data_to_good_offset(batch)
        assert has_distil is False


class TestDistillAdvantageOverwrite:
    """When distill data is present, advantages should be logp_t - logp_s."""

    def test_advantages_overwritten_with_distill(self, trainer):
        """Per-token advantages = teacher_logp - student_logp."""
        batch = make_batch(
            tokens_list=[[1, 2, 3, 4, 5]],
            logprobs_list=[[1.0, 1.0, -0.5, -0.3, -0.2]],
            scores=[1.0],
            # [seq_len, K=1] format
            distill_token_ids=[[[1], [2], [3], [4], [5]]],
            distill_logprobs=[[[-0.1], [-0.1], [-0.8], [-0.6], [-0.4]]],
        )

        datums, _, has_distil = trainer.pad_data_to_good_offset(batch)
        assert has_distil is True
        assert len(datums) == 1

        advantages = datums[0].loss_fn_inputs["advantages"].to_torch().tolist()

        # After shift, positions are [1:] so we look at target alignment:
        # target_tokens = [2, 3, 4, 5], logprobs shifted = [-0.5, -0.3, -0.2] at gen positions
        # Prompt tokens (logprob=1.0) get advantage 0.0
        # Generated tokens: teacher_lp - student_lp
        # Position 0 (was logp=1.0): advantage = 0.0 (prompt)
        # Position 1 (was logp=1.0): advantage = 0.0 (prompt)
        # Position 2 (logp=-0.5, teacher=-0.8): advantage = -0.8 - (-0.5) = -0.3
        # Position 3 (logp=-0.3, teacher=-0.6): advantage = -0.6 - (-0.3) = -0.3
        # But shift happens: all_logprobs = logprobs[1:], distil_lps from [1:]

        # Verify prompt tokens get 0.0 advantage
        assert advantages[0] == 0.0  # was logprob 1.0 (prompt sentinel)

        # Verify generated tokens have teacher-student diff
        for adv in advantages[1:]:
            assert adv != 0.0  # should be overwritten with distil values

    def test_prompt_tokens_still_masked_in_distill(self, trainer):
        """Prompt sentinel tokens (logprob=1.0) still get 0.0 advantage."""
        batch = make_batch(
            tokens_list=[[10, 20, 30, 40]],
            logprobs_list=[[1.0, 1.0, -0.5, -0.3]],
            scores=[1.0],
            distill_token_ids=[[[10], [20], [30], [40]]],
            distill_logprobs=[[[-0.2], [-0.2], [-0.7], [-0.5]]],
        )

        datums, _, _ = trainer.pad_data_to_good_offset(batch)
        advantages = datums[0].loss_fn_inputs["advantages"].to_torch().tolist()

        # First position after shift was logprob=1.0 -> advantage=0.0
        assert advantages[0] == 0.0


class TestDistillStats:
    """Verify distil_stats are computed correctly."""

    def test_distil_stats_populated(self, trainer):
        """distil_stats should be set when distill data present."""
        batch = make_batch(
            tokens_list=[
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 6],
            ],
            logprobs_list=[
                [1.0, 1.0, -0.5, -0.3, -0.2],
                [1.0, 1.0, -0.4, -0.35, -0.25],
            ],
            scores=[2.0, 1.0],
            distill_token_ids=[
                [[1], [2], [3], [4], [5]],
                [[1], [2], [3], [4], [6]],
            ],
            distill_logprobs=[
                [[-0.1], [-0.1], [-0.6], [-0.4], [-0.3]],
                [[-0.1], [-0.1], [-0.5], [-0.45], [-0.35]],
            ],
        )

        trainer.pad_data_to_good_offset(batch)

        assert hasattr(trainer, "distil_stats")
        ds = trainer.distil_stats
        assert "distil/teacher_logp_mean" in ds
        assert "distil/student_logp_mean" in ds
        assert "distil/advantage_mean" in ds
        assert "distil/advantage_std" in ds
        assert "distil/advantage_abs_mean" in ds
        assert "distil/kl_approx" in ds
        assert "distil/num_tokens" in ds
        assert ds["distil/num_tokens"] > 0

    def test_distil_stats_empty_without_distill(self, trainer):
        """distil_stats should be empty dict when no distill data."""
        batch = make_batch(
            tokens_list=[[1, 2, 3, 4], [1, 2, 3, 5]],
            logprobs_list=[
                [1.0, 1.0, -0.5, -0.3],
                [1.0, 1.0, -0.4, -0.2],
            ],
            scores=[2.0, 1.0],
        )

        trainer.pad_data_to_good_offset(batch)

        assert hasattr(trainer, "distil_stats")
        assert trainer.distil_stats == {}

    def test_distil_stats_only_count_generated_tokens(self, trainer):
        """distil_stats should exclude prompt sentinel tokens."""
        batch = make_batch(
            tokens_list=[[1, 2, 3, 4, 5]],
            logprobs_list=[[1.0, 1.0, 1.0, -0.3, -0.2]],  # 3 prompt, 2 generated
            scores=[1.0],
            distill_token_ids=[[[1], [2], [3], [4], [5]]],
            distill_logprobs=[[[-0.1], [-0.1], [-0.1], [-0.5], [-0.4]]],
        )

        trainer.pad_data_to_good_offset(batch)
        ds = trainer.distil_stats

        # Only 2 generated tokens after shift (positions with logprob != 1.0)
        assert ds["distil/num_tokens"] == 2

    def test_kl_approx_direction(self, trainer):
        """kl_approx = mean(student - teacher), positive when student > teacher."""
        batch = make_batch(
            tokens_list=[[1, 2, 3]],
            logprobs_list=[[1.0, -0.3, -0.2]],  # student logprobs (higher)
            scores=[1.0],
            distill_token_ids=[[[1], [2], [3]]],
            distill_logprobs=[
                [
                    [-0.1],
                    [
                        -0.5,
                    ],
                    [-0.4],
                ]
            ],  # teacher logprobs (lower)
        )

        trainer.pad_data_to_good_offset(batch)
        ds = trainer.distil_stats

        # student (-0.2) > teacher (-0.4) at the gen position -> kl positive
        assert ds["distil/kl_approx"] > 0


class TestDistillValidation:
    """Test _validate_distil_field shape checks."""

    def test_valid_2d_k1(self, trainer):
        """[seq_len, 1] should pass and return squeezed 1D."""
        result = trainer._validate_distil_field([[-0.5], [-0.3], [-0.2]], "test_field", seq_len=3)
        assert result is not None
        assert len(result) == 3
        assert float(result[0]) == pytest.approx(-0.5)

    def test_rejects_1d(self, trainer):
        """1D input should raise — must be [seq_len, K]."""
        with pytest.raises(ValueError, match="1D"):
            trainer._validate_distil_field([-0.5, -0.3], "test_field", seq_len=2)

    def test_rejects_k_gt_1(self, trainer):
        """K>1 should raise for tinker (only supports K=1)."""
        with pytest.raises(ValueError, match="K=2"):
            trainer._validate_distil_field([[-0.5, -0.3], [-0.2, -0.1]], "test_field", seq_len=2)

    def test_rejects_seq_len_mismatch(self, trainer):
        """Wrong number of positions should raise."""
        with pytest.raises(ValueError, match="positions"):
            trainer._validate_distil_field([[-0.5], [-0.3]], "test_field", seq_len=3)

    def test_none_passthrough(self, trainer):
        """None input should return None."""
        result = trainer._validate_distil_field(None, "test_field", seq_len=5)
        assert result is None


class TestZeroAdvantageSkip:
    """The zero-advantage skip must not drop distillation groups.

    For an on-policy-distillation group the per-token signal is
    (logp_teacher - logp_student), which is independent of the RL scores. A
    distillation group whose trajectories all have equal scores has all-zero
    RL advantages, but its teacher signal is still valid and must be kept.
    """

    def test_distill_group_with_equal_scores_not_skipped(self, trainer):
        """Equal scores -> zero RL advantages, but distill group is kept."""
        group_size = 2
        batch = make_batch(
            tokens_list=[
                [1, 2, 3, 4, 5],
                [1, 2, 3, 4, 6],
            ],
            # Prompt sentinel (1.0) for first two positions, then student logprobs.
            logprobs_list=[
                [1.0, 1.0, -0.5, -0.3, -0.2],
                [1.0, 1.0, -0.4, -0.35, -0.25],
            ],
            # Equal scores => RL advantages all 0.0 => would be skipped if not distil.
            scores=[1.0, 1.0],
            distill_token_ids=[
                [[1], [2], [3], [4], [5]],
                [[1], [2], [3], [4], [6]],
            ],
            distill_logprobs=[
                [[-0.1], [-0.1], [-0.8], [-0.6], [-0.4]],
                [[-0.1], [-0.1], [-0.7], [-0.65], [-0.45]],
            ],
        )

        datums, _, has_distil = trainer.pad_data_to_good_offset(batch)

        # Group must NOT be dropped.
        assert has_distil is True
        assert len(datums) == group_size

        # Per-token advantages must equal logp_teacher - logp_student, not 0.0.
        advantages_0 = datums[0].loss_fn_inputs["advantages"].to_torch().tolist()
        # After the [1:] shift: positions align with logprobs [1.0, -0.5, -0.3, -0.2]
        # and teacher logprobs [-0.1, -0.8, -0.6, -0.4].
        # Position 0: student logprob 1.0 (prompt sentinel) -> advantage 0.0.
        assert advantages_0[0] == 0.0
        # Generated positions: teacher - student.
        assert advantages_0[1] == pytest.approx(-0.8 - (-0.5))
        assert advantages_0[2] == pytest.approx(-0.6 - (-0.3))
        assert advantages_0[3] == pytest.approx(-0.4 - (-0.2))
        # None of the generated-token advantages should be zero here.
        assert all(a != 0.0 for a in advantages_0[1:])

    def test_non_distill_group_with_equal_scores_still_skipped(self, trainer):
        """Preserve existing behavior: RL-only group with equal scores is dropped."""
        batch = make_batch(
            tokens_list=[
                [1, 2, 3, 4],
                [1, 2, 3, 5],
            ],
            logprobs_list=[
                [1.0, 1.0, -0.5, -0.3],
                [1.0, 1.0, -0.4, -0.2],
            ],
            # Equal scores => all-zero RL advantages, no distill => skipped.
            scores=[1.0, 1.0],
        )

        datums, _, has_distil = trainer.pad_data_to_good_offset(batch)

        assert has_distil is False
        assert len(datums) == 0

    def test_rl_group_with_varying_scores_kept(self, trainer):
        """Sanity: an RL group with non-equal scores is still kept."""
        batch = make_batch(
            tokens_list=[
                [1, 2, 3, 4],
                [1, 2, 3, 5],
            ],
            logprobs_list=[
                [1.0, 1.0, -0.5, -0.3],
                [1.0, 1.0, -0.4, -0.2],
            ],
            scores=[2.0, 1.0],
        )

        datums, _, has_distil = trainer.pad_data_to_good_offset(batch)

        assert has_distil is False
        assert len(datums) == 2


class TestConfigInferenceUrl:
    """Test the inference_api_url property fix."""

    def test_strips_v1_suffix(self):
        config = TinkerAtroposConfig(
            openai=[{"model_name": "test", "base_url": "http://localhost:8001/v1"}]
        )
        assert config.inference_api_url == "http://localhost:8001"

    def test_no_v1_suffix(self):
        config = TinkerAtroposConfig(
            openai=[{"model_name": "test", "base_url": "http://localhost:8001"}]
        )
        assert config.inference_api_url == "http://localhost:8001"

    def test_strips_trailing_slash(self):
        config = TinkerAtroposConfig(
            openai=[{"model_name": "test", "base_url": "http://localhost:8001/"}]
        )
        assert config.inference_api_url == "http://localhost:8001"

    def test_doesnt_mangle_port(self):
        """Regression: old rstrip('/v1') would eat chars from port '8001'."""
        config = TinkerAtroposConfig(
            openai=[{"model_name": "test", "base_url": "http://localhost:8001/v1"}]
        )
        # Old buggy rstrip would give "http://localhost:800"
        assert "8001" in config.inference_api_url

    def test_default_url(self):
        config = TinkerAtroposConfig(openai=[])
        assert config.inference_api_url == "http://localhost:8001"
