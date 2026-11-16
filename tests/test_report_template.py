import ast
import datetime
from pathlib import Path
import unittest


class ReportTemplateTests(unittest.TestCase):
    def test_audit_template_preserves_latex_and_dynamic_header(self):
        source = Path(__file__).resolve().parents[1] / 'analysis/reviewer_readiness/audit_a3_consistency.py'
        tree = ast.parse(source.read_text(encoding='utf-8'))
        assignment = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == 'report_md' for t in node.targets))
        report = eval(compile(ast.Expression(assignment.value), str(source), 'eval'),
                      {'RUN_ID': 'TEST_RUN', 'dt': datetime, 'df_hash_before': [], 'OUT_DIR': 'test-output'})
        self.assertIn('TEST_RUN', report)
        self.assertIn(r'\text{Adj. }', report)
        self.assertIn(r'$r_{400}', report)
