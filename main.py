import json
import time


EPSILON = 1e-9


def mac(pattern, filter_matrix):
    """
    MAC(Multiply-Accumulate) 연산:
    같은 위치의 값끼리 곱한 뒤 모두 더해서 점수를 계산한다.
    """
    size = len(pattern)
    total = 0.0

    for i in range(size):
        for j in range(size):
            total += pattern[i][j] * filter_matrix[i][j]

    return total


def decide_label(score_cross, score_x, epsilon=EPSILON):
    """
    두 점수를 비교하여 Cross / X / UNDECIDED 판정을 반환한다.
    """
    if abs(score_cross - score_x) < epsilon:
        return "UNDECIDED"
    if score_cross > score_x:
        return "Cross"
    return "X"


def normalize_label(label):
    """
    다양한 라벨 표현을 표준 라벨로 정규화한다.
    표준 라벨: Cross, X
    """
    text = str(label).strip().lower()

    if text in ("+", "cross"):
        return "Cross"
    if text == "x":
        return "X"
    return "UNKNOWN"


def is_valid_matrix(matrix, size):
    """
    size x size 형태의 숫자 2차원 배열인지 검증한다.
    """
    if not isinstance(matrix, list):
        return False

    if len(matrix) != size:
        return False

    for row in matrix:
        if not isinstance(row, list):
            return False
        if len(row) != size:
            return False
        for value in row:
            if not isinstance(value, (int, float)):
                return False

    return True


def read_matrix_from_input(size, name):
    """
    사용자에게 size x size 행렬을 입력받는다.
    잘못 입력하면 재입력을 유도한다.
    """
    print(f"{name} ({size}줄 입력, 공백 구분)")
    matrix = []

    for row_index in range(size):
        while True:
            line = input(f"{row_index + 1}번째 줄: ").strip()
            parts = line.split()

            if len(parts) != size:
                print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.")
                continue

            try:
                row = [float(value) for value in parts]
                matrix.append(row)
                break
            except ValueError:
                print("입력 형식 오류: 숫자만 입력하세요.")

    return matrix


def load_json_data(path):
    """
    JSON 파일을 읽어 Python 객체로 반환한다.
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_size_from_key(key):
    """
    예: size_13_1 -> 13
    """
    parts = key.split("_")
    if len(parts) < 3:
        return None

    try:
        return int(parts[1])
    except ValueError:
        return None


def build_filters_by_size(filters_data):
    """
    JSON의 filters 데이터를
    {
        5: {"Cross": [...], "X": [...]},
        13: {"Cross": [...], "X": [...]},
        ...
    }
    형태로 변환한다.
    """
    filters_by_size = {}

    for size_key, filter_group in filters_data.items():
        try:
            size = int(size_key.split("_")[1])
        except (IndexError, ValueError):
            continue

        normalized_group = {}

        for raw_label, matrix in filter_group.items():
            normalized_label = normalize_label(raw_label)
            if normalized_label in ("Cross", "X"):
                normalized_group[normalized_label] = matrix

        filters_by_size[size] = normalized_group

    return filters_by_size


def measure_average_time(func, repeat=10):
    """
    함수 실행 시간을 repeat회 측정하고 평균(ms)을 반환한다.
    I/O가 아니라 연산 함수 호출 구간 중심으로 측정한다.
    + returns averagee that converts seconds to milliseconds
    """
    total_time = 0.0

    for _ in range(repeat):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        total_time += (end - start)

    return (total_time / repeat) * 1000.0


def create_cross_pattern(size):
    """
    size x size Cross 패턴 생성
    """
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    center = size // 2

    for i in range(size):
        matrix[i][center] = 1.0
        matrix[center][i] = 1.0

    return matrix


def run_performance_analysis(filters_by_size):
    """
    크기별 성능 분석 결과를 출력한다.
    3x3은 예시 Cross 패턴을 직접 생성해서 포함한다.
    5x5, 13x13, 25x25는 JSON 필터 기준으로 측정한다.
    """
    print("#----------------------------------------")
    print("# [3] 성능 분석 (평균/10회)")
    print("#----------------------------------------")
    print("크기\t평균 시간(ms)\t연산 횟수(N²)")

    # 3x3 성능 분석
    pattern_3 = create_cross_pattern(3)
    filter_3 = create_cross_pattern(3)
    avg_time_3 = measure_average_time(lambda: mac(pattern_3, filter_3), repeat=10)
    print(f"3x3\t{avg_time_3:.6f}\t{3 * 3}")

    # JSON에 있는 크기들 성능 분석
    for size in sorted(filters_by_size.keys()):
        filter_group = filters_by_size[size]
        cross_filter = filter_group.get("Cross")

        if cross_filter is None or not is_valid_matrix(cross_filter, size):
            print(f"{size}x{size}\t측정 불가\t{size * size}")
            continue

        pattern = cross_filter
        avg_time = measure_average_time(lambda: mac(pattern, cross_filter), repeat=10)
        operations = size * size

        print(f"{size}x{size}\t{avg_time:.6f}\t{operations}")


def run_user_input_mode():
    """
    모드 1: 사용자 입력(3x3)
    """
    print("#----------------------------------------")
    print("# [1] 필터 입력")
    print("#----------------------------------------")
    filter_a = read_matrix_from_input(3, "필터 A")
    filter_b = read_matrix_from_input(3, "필터 B")

    print("저장 확인: 필터 A, B 입력 완료")

    print("#----------------------------------------")
    print("# [2] 패턴 입력")
    print("#----------------------------------------")
    pattern = read_matrix_from_input(3, "패턴")

    print("#----------------------------------------")
    print("# [3] MAC 결과")
    print("#----------------------------------------")
    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    result_ab = "UNDECIDED"
    if abs(score_a - score_b) >= EPSILON:
        result_ab = "A" if score_a > score_b else "B"

    avg_time = measure_average_time(
        lambda: (mac(pattern, filter_a), mac(pattern, filter_b)),
        repeat=10
    )

    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")

    if result_ab == "UNDECIDED":
        print(f"판정: 판정 불가 (|A-B| < {EPSILON})")
    else:
        print(f"판정: {result_ab}")

    print("#----------------------------------------")
    print("# [4] 성능 분석 (3x3, 평균/10회)")
    print("#----------------------------------------")
    print("크기\t평균 시간(ms)\t연산 횟수(N²)")
    print(f"3x3\t{avg_time:.6f}\t{3 * 3}")


def analyze_json_mode():
    """
    모드 2: data.json 분석
    """
    try:
        data = load_json_data("data.json")
    except FileNotFoundError:
        print("오류: data.json 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError:
        print("오류: data.json 형식이 올바르지 않습니다.")
        return

    filters_data = data.get("filters", {})
    patterns_data = data.get("patterns", {})
    filters_by_size = build_filters_by_size(filters_data)

    print("#----------------------------------------")
    print("# [1] 필터 로드")
    print("#----------------------------------------")
    if not filters_by_size:
        print("로드할 필터가 없습니다.")
    else:
        for size in sorted(filters_by_size.keys()):
            loaded_labels = []
            if "Cross" in filters_by_size[size]:
                loaded_labels.append("Cross")
            if "X" in filters_by_size[size]:
                loaded_labels.append("X")

            label_text = ", ".join(loaded_labels) if loaded_labels else "없음"
            print(f"✓ size_{size} 필터 로드 완료 ({label_text})")

    print("#----------------------------------------")
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#----------------------------------------")

    total_count = 0
    pass_count = 0
    fail_count = 0
    fail_cases = []

    for pattern_key, pattern_info in patterns_data.items():
        total_count += 1
        print(f"--- {pattern_key} ---")

        size = extract_size_from_key(pattern_key)
        if size is None:
            reason = "패턴 키에서 크기 추출 실패"
            print(f"FAIL: {reason}")
            fail_count += 1
            fail_cases.append((pattern_key, reason))
            continue

        pattern_matrix = pattern_info.get("input")
        expected_raw = pattern_info.get("expected")
        expected_label = normalize_label(expected_raw)

        if expected_label == "UNKNOWN":
            reason = f"지원하지 않는 expected 라벨: {expected_raw}"
            print(f"FAIL: {reason}")
            fail_count += 1
            fail_cases.append((pattern_key, reason))
            continue

        if size not in filters_by_size:
            reason = f"size_{size} 필터 없음"
            print(f"FAIL: {reason}")
            fail_count += 1
            fail_cases.append((pattern_key, reason))
            continue

        filter_group = filters_by_size[size]
        cross_filter = filter_group.get("Cross")
        x_filter = filter_group.get("X")

        if cross_filter is None or x_filter is None:
            reason = "Cross 또는 X 필터 누락"
            print(f"FAIL: {reason}")
            fail_count += 1
            fail_cases.append((pattern_key, reason))
            continue

        if not is_valid_matrix(pattern_matrix, size):
            reason = f"패턴 크기 불일치 또는 형식 오류 (expected {size}x{size})"
            print(f"FAIL: {reason}")
            fail_count += 1
            fail_cases.append((pattern_key, reason))
            continue

        if not is_valid_matrix(cross_filter, size) or not is_valid_matrix(x_filter, size):
            reason = f"필터 크기 불일치 또는 형식 오류 (expected {size}x{size})"
            print(f"FAIL: {reason}")
            fail_count += 1
            fail_cases.append((pattern_key, reason))
            continue

        score_cross = mac(pattern_matrix, cross_filter)
        score_x = mac(pattern_matrix, x_filter)
        result = decide_label(score_cross, score_x)

        print(f"Cross 점수: {score_cross}")
        print(f"X 점수: {score_x}")
        print(f"판정: {result} | expected: {expected_label}", end="")

        if result == expected_label:
            print(" | PASS")
            pass_count += 1
        else:
            print(" | FAIL")
            fail_count += 1
            fail_cases.append(
                (pattern_key, f"예상값 불일치 (expected={expected_label}, actual={result})")
            )

    run_performance_analysis(filters_by_size)

    print("#----------------------------------------")
    print("# [4] 결과 요약")
    print("#----------------------------------------")
    print(f"총 테스트: {total_count}개")
    print(f"통과: {pass_count}개")
    print(f"실패: {fail_count}개")

    if fail_cases:
        print("실패 케이스:")
        for case_id, reason in fail_cases:
            print(f"- {case_id}: {reason}")


def main():
    print("=== Mini NPU Simulator ===")
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")

    choice = input("선택: ").strip()

    if choice == "1":
        run_user_input_mode()
    elif choice == "2":
        analyze_json_mode()
    else:
        print("잘못된 입력입니다. 1 또는 2를 선택하세요.")
        
"""
Only run the full simulator when this file is executed directly,
not when it is imported for reuse.
"""

if __name__ == "__main__":
    main()
