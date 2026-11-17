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
BMI 건강정보 관리 프로그램 - 사용자 정의 예외

  HealthRecordError            : 이 프로그램의 모든 예외의 부모
   ├─ InvalidRecordError       : 잘못된 건강정보 값 (이름, 나이, 키, 몸무게, 식별번호 등)
   ├─ DuplicateRecordError     : 이미 있는 식별번호를 다시 추가
   └─ HealthFileError          : 파일 저장/읽기 실패
        ├─ UnsupportedFormatError : 지원하지 않는 파일 확장자
        └─ CorruptedFileError     : 파일 내용이 깨졌거나 형식이 맞지 않음
"""


# [AI 작성] Claude
class HealthRecordError(Exception):
    """건강정보 프로그램의 기본 예외"""
    pass


# [AI 작성] Claude
class InvalidRecordError(HealthRecordError):
    """건강정보 값이 올바르지 않을 때"""
    pass


# [AI 작성] Claude
class DuplicateRecordError(HealthRecordError):
    """같은 식별번호가 이미 목록에 있을 때"""
    pass


# [AI 작성] Claude
class HealthFileError(HealthRecordError):
    """파일 저장/읽기 중 문제가 생겼을 때"""
    pass


# [AI 작성] Claude
class UnsupportedFormatError(HealthFileError):
    """지원하지 않는 파일 형식(확장자)일 때"""
    pass


# [AI 작성] Claude
class CorruptedFileError(HealthFileError):
    """파일 내용이 손상되었거나 필요한 항목이 없을 때"""
    pass
