"""Compatibility API for v4; implementations are split by research stage."""
from config.research import *
from util.paths import ROOT
import os
import argparse
import datetime as dt
import hashlib
import inspect
import json
import math
import platform
import re
import sys
import time
import warnings
from collections import Counter
from pathlib import Path
from typing import Any
import joblib
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import scipy
import sklearn
import statsmodels
import statsmodels.api as sm
from scipy import sparse
from sklearn.decomposition import NMF
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction.text import TfidfTransformer
from collector.datalab.datalab_keyword_sets import KEYWORD_SETS
from core.preprocessing.mine_keywords import _tokens
from util.research import sha256_bytes, sha256_file, arr_hash, text_hash, safe_path, is_nan, fnum, fpct, fratio, improvement, verdict_word
from core.regime_analysis import build_domain_pairs, dictionary_hash, claim_terms, map_topics, mapping_hash, domain_topics, domain_support, build_regime_monthly
from core.topic_analysis import run_core
from core.forecast_analysis import _design, _predict, run_forecasts, cont_metrics, class_metrics, compute_all_metrics
from core.reporting import _rel_table, cross_run_rows, render_markdown
from core.validation import _chk, independent_mapping, pre_md_checks, _predict_with_future, _numpy_predict, post_md_checks, overall_verdict
from core.train import main

if __name__ == "__main__":
    main()
