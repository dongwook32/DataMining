"""코스피 시장 사건 정의 및 조기경보 평가 공통 기준.

DataMining 연구 프로젝트의 사건 정의 일관성을 유지하기 위한 공통 기준 모듈.
"""

# 코스피 월간 로그수익률(%) 기준
# preprocess/build_panel.py 에서 100 * np.log(KOSPI).diff() 로 계산되므로 단위는 % 임.
KOSPI_CRASH_THRESHOLD = -3.0  # 급락 사건 기준 (월간 -3% 이하)
KOSPI_DROP_THRESHOLD = 0.0    # 일반 하락 기준 (월간 음의 수익률)
