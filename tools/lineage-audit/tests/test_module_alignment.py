"""Focused regression tests for G-007 static module-alignment evidence."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
SRC_PYTHON = TOOL_ROOT / "src-python"
if str(SRC_PYTHON) not in sys.path:
    sys.path.insert(0, str(SRC_PYTHON))

from audit.common import add_row_ids, clean_tool_outputs
from builders.module_alignment import build_module_alignment_outputs
from scanners.backend import parse_backend_function_index, parse_backend_routes, parse_model_tables
from scanners.frontend import (
    list_frontend_api_files,
    list_frontend_source_files,
    parse_frontend_api_file,
    parse_frontend_manifest_routes,
)


class ModuleAlignmentEvidenceTests(unittest.TestCase):
    def test_static_router_tags_are_attached_to_routes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            backend_root = Path(temp_dir) / "app"
            route_file = backend_root / "sample" / "api" / "routes.py"
            model_file = backend_root / "sample" / "models" / "widget.py"
            route_file.parent.mkdir(parents=True)
            model_file.parent.mkdir(parents=True)
            route_file.write_text(
                "from fastapi import APIRouter\n"
                "router = APIRouter(prefix='/widgets', tags=['Widget management'])\n"
                "@router.get('/')\n"
                "def list_widgets():\n"
                "    return []\n",
                encoding="utf-8",
            )
            model_file.write_text(
                "class Widget:\n"
                "    __tablename__ = 'widgets'\n",
                encoding="utf-8",
            )

            _, models = parse_model_tables(backend_root)
            routes = parse_backend_routes(backend_root, models, parse_backend_function_index(backend_root))

            self.assertEqual(len(routes), 1)
            self.assertEqual(routes[0].router_tags, ("Widget management",))
            self.assertEqual(routes[0].tag_evidence_state, "confirmed")
            self.assertIn("APIRouter", routes[0].tag_evidence_symbol)

    def test_empty_policy_emits_manual_review_not_nonconformance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            policy_path = Path(temp_dir) / "module_alignment_policy.yaml"
            policy_path.write_text(
                "version: 1\nmodules: []\nfrontend_only: []\nbackend_only: []\napproved_exceptions: []\n",
                encoding="utf-8",
            )
            policy, outputs = build_module_alignment_outputs(
                policy_path,
                [{"row_id": "frontend_api_refs:one", "api_file": "frontend-js/src/app/widgets/api/index.js"}],
                [{"row_id": "backend_routes:one", "backend_module": "widgets"}],
                [],
                {"tables": []},
                add_row_ids,
            )

            self.assertEqual(policy["version"], 1)
            self.assertTrue(outputs["alignment_overview"])
            self.assertTrue(outputs["alignment_findings"])
            self.assertNotIn("nonconformant", {row["frontend_policy_state"] for row in outputs["alignment_overview"]})
            self.assertTrue(all(row["evidence_state"] == "manual_review" for row in outputs["alignment_findings"]))

    def test_dynamic_router_tags_require_manual_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            backend_root = Path(temp_dir) / "app"
            route_file = backend_root / "sample" / "api" / "routes.py"
            route_file.parent.mkdir(parents=True)
            route_file.write_text(
                "from fastapi import APIRouter\n"
                "ROUTER_TAGS = ['Widget management']\n"
                "router = APIRouter(prefix='/widgets', tags=ROUTER_TAGS)\n"
                "@router.get('/')\n"
                "def list_widgets():\n"
                "    return []\n",
                encoding="utf-8",
            )
            routes = parse_backend_routes(backend_root, {}, parse_backend_function_index(backend_root))

            self.assertEqual(len(routes), 1)
            self.assertEqual(routes[0].router_tags, ())
            self.assertEqual(routes[0].tag_evidence_state, "manual_review")

    def test_policy_pair_and_table_role_are_confirmed_as_policy_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            policy_path = Path(temp_dir) / "module_alignment_policy.yaml"
            policy_path.write_text(
                "version: 1\n"
                "modules:\n"
                "  - key: widgets\n"
                "    frontend: widgets\n"
                "    backend: widgets\n"
                "    table_roles:\n"
                "      - table: widgets\n"
                "        role: read_model\n"
                "frontend_only: []\nbackend_only: []\napproved_exceptions: []\n",
                encoding="utf-8",
            )
            _, outputs = build_module_alignment_outputs(
                policy_path,
                [{"row_id": "frontend_api_refs:one", "api_file": "frontend-js/src/app/widgets/api/index.js"}],
                [{"row_id": "backend_routes:one", "backend_module": "widgets"}],
                [],
                {"tables": [{"table_name": "widgets"}]},
                add_row_ids,
            )

            row = outputs["alignment_overview"][0]
            self.assertEqual(row["frontend_policy_state"], "conformant")
            self.assertEqual(row["backend_policy_state"], "conformant")
            self.assertEqual(row["data_roles"], "widgets:read_model")
            self.assertFalse(outputs["alignment_findings"])

    def test_deterministic_cleanup_preserves_ai_authored_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs_dir = Path(temp_dir)
            ai_report = outputs_dir / "reports" / "ai_audit_report.md"
            ai_report.parent.mkdir(parents=True)
            ai_report.write_text("human-authored analysis\n", encoding="utf-8")
            generated_frontend = outputs_dir / "frontend" / "frontend_sources.csv"
            generated_frontend.parent.mkdir(parents=True)
            generated_frontend.write_text("row_id\n", encoding="utf-8")

            clean_tool_outputs(outputs_dir)

            self.assertTrue(ai_report.exists())
            self.assertFalse(generated_frontend.exists())

    def test_mjs_and_ts_production_sources_exclude_tests_fixtures_and_mocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            frontend_root = Path(temp_dir) / "src"
            paths = {
                "mjs": frontend_root / "app" / "performance" / "views" / "list" / "presentation.mjs",
                "ts": frontend_root / "app" / "performance" / "components" / "chart.ts",
                "test": frontend_root / "app" / "performance" / "views" / "list" / "presentation.test.mjs",
                "spec": frontend_root / "pages" / "overview.spec.ts",
                "tests": frontend_root / "components" / "__tests__" / "card.ts",
                "fixture": frontend_root / "views" / "fixtures" / "sample.ts",
            }
            for path in paths.values():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("export const value = 1\n", encoding="utf-8")

            sources = {path.relative_to(frontend_root).as_posix() for path in list_frontend_source_files(frontend_root)}

            self.assertEqual(
                sources,
                {
                    "app/performance/views/list/presentation.mjs",
                    "app/performance/components/chart.ts",
                },
            )

    def test_typed_ts_api_and_manifest_are_parsed_without_compiler(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            frontend_root = Path(temp_dir) / "src"
            api_file = frontend_root / "app" / "performance" / "api" / "metrics.ts"
            api_file.parent.mkdir(parents=True)
            api_file.write_text(
                "export async function loadMetrics(query: MetricsQuery): Promise<Page<Metric>> {\n"
                "  return request.get<Page<Metric>>('/performance/metrics', { params: query })\n"
                "}\n"
                "export const createMetric: (body: MetricInput) => Promise<Metric> = async (body: MetricInput): Promise<Metric> =>\n"
                "  request.post<Metric>('/performance/metrics', body)\n",
                encoding="utf-8",
            )
            manifest = frontend_root / "app" / "performance" / "manifest.ts"
            manifest.write_text(
                "export default [{\n"
                "  path: 'performance',\n"
                "  name: 'Performance',\n"
                "  component: () => import('./views/list/index.vue'),\n"
                "}]\n",
                encoding="utf-8",
            )
            for excluded in (
                frontend_root / "api" / "mock.ts",
                frontend_root / "app" / "performance" / "api" / "mock" / "fixture.ts",
                frontend_root / "api" / "fixtures" / "fixture.ts",
            ):
                excluded.parent.mkdir(parents=True, exist_ok=True)
                excluded.write_text(
                    "export function ignored() { return request.get('/ignored') }\n",
                    encoding="utf-8",
                )

            api_files = list_frontend_api_files(frontend_root)
            self.assertEqual(api_files, [api_file])
            apis = parse_frontend_api_file(api_file, frontend_root)
            self.assertEqual(
                [(api.function, api.method, api.path, api.confidence) for api in apis],
                [
                    ("loadMetrics", "GET", "/performance/metrics", "confirmed"),
                    ("createMetric", "POST", "/performance/metrics", "confirmed"),
                ],
            )
            routes = parse_frontend_manifest_routes(frontend_root)
            self.assertEqual(len(routes), 1)
            self.assertEqual(routes[0].route_path, "/performance")


if __name__ == "__main__":
    unittest.main()
