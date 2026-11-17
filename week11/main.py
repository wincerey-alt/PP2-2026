# ======================================================================
# [AI 활용 표시]
#  - 이 파일의 코드는 생성형 AI(Anthropic Claude)의 도움을 받아 작성하였음.
#  - '# [AI 작성]' 주석이 붙은 클래스/함수는 AI가 작성한 부분이며,
#    클래스 안의 메소드도 모두 AI가 작성함.
#  - 사용한 프롬프트는 '202611835이승식_프롬프트.txt' 참고.
#  - 제출자는 AI가 작성한 부분을 포함한 모든 코드에 대한 책임을 진다.
#  - 작성자: 202611835 이승식
# ======================================================================
"""
BMI 건강정보 관리 프로그램 - 모듈 1 (실행 파일)

[구현 노트 (5)]
 main()에서 전체를 통합하여
   1) 임의의 건강정보를 입력하고 화면에 출력 (식별번호는 등록일-순번 자동 생성)
   2) JSON, CSV, TXT, PICKLE 4가지 파일로 저장
   3) 저장된 파일을 각각 읽어 리스트(딕셔너리)로 출력
   4) 저장 전 값과 읽어 온 값이 일치하는지 검증
   5) 예외 처리 동작 확인
"""
import os

from health_record import HealthRecord, HealthRecordManager
from health_exceptions import HealthRecordError

FILES = ["health.json", "health.csv", "health.txt", "health.pkl"]


# [AI 작성] Claude
def run_main_flow():
    # 1) 임의 데이터 입력 후 출력 ------------------------------------
    #    식별번호는 등록일 기준으로 자동 생성된다. (예: 20261110-001)
    original = HealthRecordManager()
    original.new_record("김민수", "남", 23, 175.0, 70.5, reg_date="2026-11-10")
    original.new_record("이서연", "여", 21, 162.3, 50.2, reg_date="2026-11-10")
    original.new_record("박지훈", "남", 25, 180.2, 92.0, reg_date="2026-11-12")
    original.new_record("최유진", "여", 22, 158.0, 44.0, reg_date="2026-11-15")
    original.new_record("정우성", "남", 24, 170.5, 78.3)          # 등록일 생략 -> 오늘

    original.print_records("원본 데이터 (저장 전)")
    print("\n원본 리스트(딕셔너리):")
    for d in original.to_list():
        print("  ", d)

    # 2) 4가지 형식으로 저장 ----------------------------------------
    print("\n===== 파일 저장 =====")
    for filename in FILES:
        original.save_file(filename)
        print(f"  {filename} 저장 완료")

    # 3) 각 파일을 읽어 출력  /  4) 원본과 비교 ----------------------
    results = {}
    for filename in FILES:
        loaded = HealthRecordManager()
        try:
            loaded.print_file(filename)
            same = (loaded.records == original.records)
        except HealthRecordError as e:
            print(f"[오류] {e}")
            same = False
        results[filename] = same
        print(f"→ 원본과 {'일치' if same else '불일치'}")

    # 검증 결과 요약 -------------------------------------------------
    print("\n===== 검증 결과 요약 =====")
    for filename, same in results.items():
        print(f"  {filename:<12}: {'✔ 일치' if same else '✘ 불일치'}")

    if all(results.values()):
        print("모든 파일 형식에서 저장 전/후 데이터가 일치합니다.")
    else:
        print("일치하지 않는 파일이 있습니다.")


# [AI 작성] Claude
def run_exception_tests():
    """잘못된 입력·파일을 일부러 넣어 예외 처리가 동작하는지 확인"""
    print("\n\n===== 예외 처리 확인 =====")
    m = HealthRecordManager()
    m.new_record("홍길동", "남", 30, 172.0, 68.0, reg_date="2026-11-17")

    # 잘못된 내용의 테스트 파일 만들기
    with open("broken.json", "w", encoding="utf-8") as f:
        f.write("{ 이건 JSON이 아님")
    with open("broken.csv", "w", encoding="utf-8") as f:
        f.write("id,name,gender,age,height,weight\n20261117-001,홍길동,남,서른,172,68\n")
    with open("broken.txt", "w", encoding="utf-8") as f:
        f.write("id\tname\tgender\tage\theight\tweight\n20261117-001\t홍길동\t남\n")
    with open("broken.pkl", "wb") as f:
        f.write(b"not a pickle")

    tests = [
        ("이름이 빈 값",         lambda: m.new_record("", "남", 20, 170, 60)),
        ("성별 오류",            lambda: m.new_record("김철수", "M", 20, 170, 60)),
        ("나이가 숫자가 아님",    lambda: m.new_record("김철수", "남", "스물", 170, 60)),
        ("키 범위 초과",          lambda: m.new_record("김철수", "남", 20, 999, 60)),
        ("몸무게 음수",           lambda: m.new_record("김철수", "남", 20, 170, -5)),
        ("등록일 형식 오류",      lambda: m.new_record("김철수", "남", 20, 170, 60, reg_date="2026/11/17")),
        ("식별번호 형식 오류",    lambda: HealthRecord("A-1", "김철수", "남", 20, 170, 60)),
        ("식별번호 날짜 오류",    lambda: HealthRecord("20261345-001", "김철수", "남", 20, 170, 60)),
        ("식별번호 중복 추가",    lambda: m.add_record(HealthRecord("20261117-001", "김철수", "남", 20, 170, 60))),
        ("지원하지 않는 확장자",  lambda: m.save_file("health.xlsx")),
        ("없는 파일 읽기",        lambda: HealthRecordManager().load_file("no_such_file.json")),
        ("깨진 JSON 파일",        lambda: HealthRecordManager().load_file("broken.json")),
        ("CSV 값 오류",           lambda: HealthRecordManager().load_file("broken.csv")),
        ("TXT 항목 수 불일치",    lambda: HealthRecordManager().load_file("broken.txt")),
        ("깨진 PICKLE 파일",      lambda: HealthRecordManager().load_file("broken.pkl")),
    ]

    passed = 0
    for i, (label, func) in enumerate(tests, start=1):
        try:
            func()
            print(f"{i:>2}. {label:<14} -> 예외가 발생하지 않음 (확인 필요)")
        except HealthRecordError as e:
            passed += 1
            print(f"{i:>2}. {label:<14} -> {type(e).__name__}: {e}")
    print(f"\n예외 처리 확인: {passed}/{len(tests)}건 정상 처리")

    # 예외가 나도 기존 목록은 그대로 유지되는지 확인
    print(f"예외 발생 후에도 목록 유지: {len(m.records)}명 ({m.records[0].id} {m.records[0].name})")

    # 테스트용으로 만든 깨진 파일 정리
    for name in ("broken.json", "broken.csv", "broken.txt", "broken.pkl"):
        if os.path.exists(name):
            os.remove(name)


# [AI 작성] Claude
def main():
    try:
        run_main_flow()
        run_exception_tests()
    except HealthRecordError as e:
        print(f"\n[프로그램 오류] {type(e).__name__}: {e}")
    except Exception as e:
        print(f"\n[예상하지 못한 오류] {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
