"""Regression checks for the A-3.1 report template."""
import ast
import datetime as dt
from pathlib import Path
import unittest


class AuditReportTemplateTest(unittest.TestCase):
    def test_report_preserves_latex_and_expands_fields(self):
        source = Path(__file__).resolve().parents[1] / 'analysis/reviewer_readiness/audit_a3_consistency.py'
        tree = ast.parse(source.read_text(encoding='utf-8'))
        assignment = next(
            node for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == 'report_md' for target in node.targets)
        )
        expression = ast.fix_missing_locations(ast.Expression(assignment.value))
        report = eval(compile(expression, str(source), 'eval'), {
            'RUN_ID': 'test-run', 'dt': dt, 'df_hash_before': [1, 2], 'OUT_DIR': Path('test-output')
        })
        for expected in (r'\text{Adj. }', r'\hat{\beta}', r'p_{\text{holm}}', r'10^{-39}', 'test-run', 'test-output'):
            self.assertIn(expected, report)
        self.assertNotIn('\t', report)
        self.assertNotIn('\b', report)


if __name__ == '__main__':
    unittest.main()
