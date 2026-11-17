"""Paper tables 14-15: search robustness, NMF convergence and downstream sensitivity."""
from util.execution import run_modules


def run():
    run_modules(['core.robustness.verify_search_robustness',
                 'core.robustness.verify_nmf_convergence',
                 'core.robustness.compare_nmf_downstream_sensitivity'])


if __name__ == '__main__':
    run()
