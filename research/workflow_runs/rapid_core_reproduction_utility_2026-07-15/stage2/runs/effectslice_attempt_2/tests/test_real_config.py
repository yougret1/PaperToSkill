import json
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]


class RealConfigTest(unittest.TestCase):
    def load_config(self):
        return json.loads(
            (RUN_ROOT / "configs/experiment_config.json").read_text(encoding="utf-8")
        )

    def test_every_declared_source_map_exists(self):
        config = self.load_config()
        project_root = Path(config["project_root"])

        for paper_id, relative_path in config["source_maps"].items():
            with self.subTest(paper_id=paper_id):
                self.assertTrue(
                    (project_root / relative_path).is_file(),
                    f"missing configured source map: {relative_path}",
                )

    def test_ordinary_device_protocol_is_api_first(self):
        config = self.load_config()
        execution = config["execution_model"]

        self.assertEqual(execution["inference_mode"], "trusted_vendor_api")
        self.assertFalse(execution["local_accelerator_required"])
        self.assertFalse(execution["local_quantized_model"]["required"])
        self.assertEqual(
            execution["local_quantized_model"]["role"], "optional_supplement_only"
        )
        self.assertEqual(
            execution["providers"]["primary"]["model_family"], "DeepSeek-family"
        )
        self.assertEqual(
            execution["providers"]["primary"]["request_alias"],
            "deepseek-v4-flash",
        )
        self.assertEqual(
            execution["providers"]["robustness"]["request_alias"], "gpt-5.6"
        )
        self.assertNotIn("80gb", json.dumps(config).lower())

    def test_stage2_handoff_budget_matches_api_first_ordinary_device_scope(self):
        idea = json.loads((RUN_ROOT / "idea.json").read_text(encoding="utf-8"))
        idea_markdown = (RUN_ROOT / "idea.md").read_text(encoding="utf-8")
        budget = idea["experiment_plan"]["budget"].lower()

        self.assertIn("ordinary local pc", budget)
        self.assertIn("trusted vendor api", budget)
        self.assertNotIn("gpu-days", budget)
        self.assertNotIn("80gb", budget)
        self.assertIn("api-first", idea_markdown.lower())
        self.assertNotIn("80gb", idea_markdown.lower())

    def test_snap_mfse_adapter_is_frozen_before_provider_runs(self):
        config = self.load_config()
        adapter = config["task_adapters"]["SNAP-MFSE"]
        registry_path = RUN_ROOT / adapter["case_registry"]
        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        self.assertEqual(adapter["max_actions"], 16)
        self.assertTrue(adapter["action_budget_visible_to_model"])
        self.assertEqual(adapter["development_delta_min"], 0.05)
        self.assertEqual(adapter["primary_model_family"], "DeepSeek-family")
        self.assertEqual(
            {name: len(cases) for name, cases in registry["blocks"].items()},
            {"development": 4, "eligibility": 21, "discovery": 16, "confirmation": 59},
        )
        for key in (
            "workspace",
            "full_artifact",
            "atom_map",
            "case_registry",
            "task_prompt",
            "slice_registry",
            "confirmation_family",
        ):
            self.assertTrue((RUN_ROOT / adapter[key]).exists(), key)

    def test_deepseek_provider_v2_changes_only_the_output_budget(self):
        config = self.load_config()
        protocol = config["task_adapters"]["SNAP-MFSE"]["provider_protocols"][
            "deepseek_primary_v2"
        ]

        self.assertEqual(
            protocol["version"], "effectslice-deepseek-output-budget.v2"
        )
        self.assertEqual(protocol["max_tokens"], 8192)
        self.assertEqual(protocol["only_changed_fields"], ["max_tokens"])
        self.assertEqual(protocol["harness_protocol_version"], "effectslice-snap-mfse-aci.v1")

    def test_harness_v2_scores_final_state_without_adding_model_actions(self):
        config = self.load_config()
        protocol = config["task_adapters"]["SNAP-MFSE"]["harness_protocols"][
            "final_state_scoring_v2"
        ]

        self.assertEqual(protocol["version"], "effectslice-snap-mfse-aci.v2")
        self.assertTrue(protocol["score_final_state_on_exhaustion"])
        self.assertEqual(protocol["max_actions"], 16)
        self.assertEqual(protocol["only_changed_fields"], ["terminal_scoring"])

    def test_toolformer_filter_adapter_is_api_first_and_frozen(self):
        config = self.load_config()
        adapter = config["task_adapters"]["TOOLFORMER-FILTER"]
        registry = json.loads(
            (RUN_ROOT / adapter["case_registry"]).read_text(encoding="utf-8")
        )

        self.assertEqual(adapter["status"], "frozen_before_provider_runs")
        self.assertEqual(adapter["primary_model_family"], "DeepSeek-family")
        self.assertEqual(adapter["primary_model_alias"], "deepseek-v4-flash")
        self.assertEqual(adapter["inference_mode"], "trusted_vendor_api")
        self.assertFalse(adapter["local_accelerator_required"])
        self.assertEqual(adapter["max_tokens"], 8192)
        self.assertEqual(adapter["max_actions"], 16)
        self.assertEqual(
            adapter["harness_protocol_version"],
            "effectslice-toolformer-filter-aci.v2",
        )
        self.assertEqual(
            adapter["task_contract_protocol_version"],
            "effectslice-toolformer-filter-task-contract.v2",
        )
        self.assertIn(
            "toolformer-filter:development:deepseek:bf:001",
            adapter["excluded_development_pair_ids"],
        )
        self.assertEqual(
            {name: len(cases) for name, cases in registry["blocks"].items()},
            {"development": 4, "eligibility": 21, "discovery": 16, "confirmation": 59},
        )
        for key in (
            "workspace",
            "full_artifact",
            "atom_map",
            "case_registry",
            "task_prompt",
            "slice_registry",
            "confirmation_builder",
            "confirmation_family",
        ):
            self.assertTrue((RUN_ROOT / adapter[key]).exists(), key)

    def test_confirmation_v3_freezes_vendor_transport_and_finite_schedule(self):
        config = self.load_config()
        protocol = config["task_adapters"]["TOOLFORMER-FILTER"]["confirmation_v3"]
        provider = protocol["provider"]

        self.assertEqual(
            protocol["evidence_boundary"],
            "registered_final_only_confirmation_v3",
        )
        self.assertEqual(protocol["registered_block_count"], 24)
        self.assertEqual(protocol["registered_condition_run_count"], 72)
        self.assertEqual(protocol["controls"]["identity"]["replicate_count"], 6)
        self.assertEqual(protocol["controls"]["planted"]["replicate_count"], 18)
        self.assertEqual(
            protocol["controls"]["planted"][
                "required_joint_events_for_admission"
            ],
            18,
        )
        self.assertEqual(provider["base_url"], "https://api.deepseek.com")
        self.assertEqual(provider["model_alias"], "deepseek-v4-flash")
        self.assertEqual(provider["timeout_seconds"], 240.0)
        self.assertEqual(provider["maximum_transport_attempts"], 5)
        self.assertEqual(provider["retry_delay_seconds"], 2.0)
        self.assertEqual(provider["maximum_parallel_workers"], 2)
        self.assertTrue(provider["direct_connection"])
        self.assertEqual(provider["proxy_policy"], "disabled")
        self.assertIn(
            "confirmation_transport_v3.py", protocol["execution_bindings"]
        )


if __name__ == "__main__":
    unittest.main()
