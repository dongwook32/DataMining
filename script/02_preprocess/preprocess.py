"""Step 1: build the news corpus and monthly market/search panel from local snapshots."""
from util.execution import run_modules


def run():
    run_modules(['core.preprocessing.build_corpus', 'core.preprocessing.build_panel'])


if __name__ == '__main__':
    run()
