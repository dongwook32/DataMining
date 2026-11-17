"""Paper tables 13-14: weekly news/search panel, HAC tests and anchor sensitivity."""
from util.execution import run_modules


def run():
    run_modules(['core.search.run_study_b', 'core.search.verify_hac_news_search',
                 'core.search.verify_anchor_sensitivity'])


if __name__ == '__main__':
    run()
