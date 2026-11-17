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
BMI 건강정보 관리 프로그램 - 모듈 1 (클래스 정의)

[구현 노트 대응]
 (1) 한 사람의 건강정보를 저장할 클래스        -> HealthRecord
 (2) 건강정보 객체 목록을 관리할 클래스        -> HealthRecordManager
     건강정보 객체를 추가하는 메소드           -> add_record(), new_record()
 (3) JSON, CSV, TXT, PICKLE 저장/읽기 메소드   -> save_json / load_json
                                                save_csv  / load_csv
                                                save_txt  / load_txt
                                                save_pickle / load_pickle
 (4) 저장된 목록의 내용을 읽어 화면에 출력     -> print_records(), print_file()

[식별번호 규칙]
 등록날짜(YYYYMMDD) + '-' + 그날의 등록 순번(3자리)
 예) 2026년 11월 17일에 두 번째로 등록한 사람 -> "20261117-002"

[예외 처리]
 health_exceptions.py 에 정의한 예외를 사용한다.
"""
import csv
import json
import os
import pickle
import re
from datetime import date, datetime

from health_exceptions import (
    InvalidRecordError,
    DuplicateRecordError,
    HealthFileError,
    UnsupportedFormatError,
    CorruptedFileError,
)


# ======================================================================
# (1) 한 사람의 건강정보를 저장하는 클래스
# ======================================================================
# [AI 작성] Claude
class HealthRecord:
    """한 사람의 BMI 건강정보"""

    # 파일에 저장할 항목(순서 고정)
    FIELDS = ["id", "name", "gender", "age", "height", "weight"]

    ID_PATTERN = re.compile(r"^\d{8}-\d{3}$")   # 예: 20261117-001

    def __init__(self, id, name, gender, age, height, weight):
        # 값 검사 후 저장 (CSV/TXT에서 읽은 문자열도 여기서 형 변환된다)
        self.id = self._check_id(id)
        self.name = self._check_name(name)
        self.gender = self._check_gender(gender)
        self.age = self._to_number(age, int, "나이", 1, 120)
        self.height = self._to_number(height, float, "키(cm)", 50, 250)
        self.weight = self._to_number(weight, float, "몸무게(kg)", 10, 300)

    # ---------- 값 검사 ----------
    @classmethod
    def _check_id(cls, value):
        value = str(value).strip()
        if not cls.ID_PATTERN.match(value):
            raise InvalidRecordError(
                f"식별번호 형식 오류: '{value}' (예: 20261117-001)")
        try:
            datetime.strptime(value[:8], "%Y%m%d")
        except ValueError:
            raise InvalidRecordError(f"식별번호의 날짜가 올바르지 않음: '{value}'")
        if value[9:] == "000":
            raise InvalidRecordError(f"순번은 001부터 시작: '{value}'")
        return value

    @staticmethod
    def _check_name(value):
        value = str(value).strip()
        if not value:
            raise InvalidRecordError("이름이 비어 있음")
        return value

    @staticmethod
    def _check_gender(value):
        value = str(value).strip()
        if value not in ("남", "여"):
            raise InvalidRecordError(f"성별은 '남' 또는 '여'만 가능: '{value}'")
        return value

    @staticmethod
    def _to_number(value, type_, label, low, high):
        try:
            num = type_(value)
        except (TypeError, ValueError):
            raise InvalidRecordError(f"{label} 값이 숫자가 아님: '{value}'")
        if not (low <= num <= high):
            raise InvalidRecordError(f"{label} 범위 오류: {num} (허용 {low}~{high})")
        return num

    # ---------- 식별번호에서 등록일 꺼내기 ----------
    def get_reg_date(self):
        """식별번호 앞 8자리 -> 등록일(date)"""
        return datetime.strptime(self.id[:8], "%Y%m%d").date()

    # ---------- BMI ----------
    def get_bmi(self):
        """BMI = 몸무게(kg) / 키(m)^2, 소수 첫째 자리까지"""
        h = self.height / 100
        return round(self.weight / (h * h), 1)

    def get_category(self):
        """대한비만학회 기준 비만도 판정"""
        bmi = self.get_bmi()
        if bmi < 18.5:
            return "저체중"
        elif bmi < 23:
            return "정상"
        elif bmi < 25:
            return "비만전단계"
        elif bmi < 30:
            return "1단계 비만"
        elif bmi < 35:
            return "2단계 비만"
        else:
            return "3단계 비만"

    # ---------- 변환 ----------
    def to_dict(self):
        """객체 -> 딕셔너리 (파일 저장용)"""
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
        }

    @classmethod
    def from_dict(cls, d):
        """딕셔너리 -> 객체 (파일 읽기용)"""
        if not isinstance(d, dict):
            raise InvalidRecordError(f"레코드가 딕셔너리가 아님: {d!r}")
        missing = [f for f in cls.FIELDS if f not in d]
        if missing:
            raise InvalidRecordError(f"필수 항목 누락: {missing}")
        return cls(d["id"], d["name"], d["gender"], d["age"], d["height"], d["weight"])

    def __eq__(self, other):
        """두 레코드의 내용이 같은지 비교 (검증용)"""
        if not isinstance(other, HealthRecord):
            return False
        return self.to_dict() == other.to_dict()

    def __str__(self):
        return (f"{self.id} | {self.name:<5} | {self.gender:^3} | {self.age:>3} | "
                f"{self.height:>6.1f} | {self.weight:>6.1f} | "
                f"{self.get_bmi():>5.1f} | {self.get_category()}")


# ======================================================================
# (2) 건강정보 객체 목록을 관리하는 클래스
# ======================================================================
# [AI 작성] Claude
class HealthRecordManager:
    """HealthRecord 객체 목록 관리"""

    def __init__(self):
        self.records = []          # HealthRecord 객체 리스트

    # ---------- 식별번호 생성 ----------
    def make_id(self, reg_date=None):
        """등록일 기준으로 다음 식별번호를 만든다. reg_date 생략 시 오늘."""
        if reg_date is None:
            reg_date = date.today()
        elif isinstance(reg_date, str):
            try:
                reg_date = datetime.strptime(reg_date, "%Y-%m-%d").date()
            except ValueError:
                raise InvalidRecordError(
                    f"등록일 형식 오류: '{reg_date}' (예: 2026-11-17)")
        prefix = reg_date.strftime("%Y%m%d")
        same_day = [r for r in self.records if r.id.startswith(prefix)]
        seq = max((int(r.id[9:]) for r in same_day), default=0) + 1
        if seq > 999:
            raise InvalidRecordError(f"{prefix} 등록 인원이 999명을 넘음")
        return f"{prefix}-{seq:03d}"

    # ---------- 추가 ----------
    def add_record(self, record):
        """건강정보 객체를 목록에 추가 (식별번호 중복 검사)"""
        if not isinstance(record, HealthRecord):
            raise InvalidRecordError("HealthRecord 객체만 추가할 수 있음")
        if any(r.id == record.id for r in self.records):
            raise DuplicateRecordError(f"이미 등록된 식별번호: {record.id}")
        self.records.append(record)

    def new_record(self, name, gender, age, height, weight, reg_date=None):
        """식별번호를 자동으로 만들어 새 건강정보를 추가하고 반환"""
        record = HealthRecord(self.make_id(reg_date), name, gender, age, height, weight)
        self.add_record(record)
        return record

    def to_list(self):
        """목록 -> 딕셔너리의 리스트"""
        return [r.to_dict() for r in self.records]

    def from_list(self, data, filename=""):
        """딕셔너리의 리스트 -> 목록 (잘못된 레코드가 있으면 몇 번째인지 알려 줌)"""
        if not isinstance(data, list):
            raise CorruptedFileError(f"{filename}: 데이터가 리스트 형태가 아님")
        new_records = []
        seen = set()
        for i, d in enumerate(data, start=1):
            try:
                rec = HealthRecord.from_dict(d)
            except InvalidRecordError as e:
                raise CorruptedFileError(f"{filename}: {i}번째 레코드 오류 - {e}")
            if rec.id in seen:
                raise CorruptedFileError(f"{filename}: 식별번호 중복 - {rec.id}")
            seen.add(rec.id)
            new_records.append(rec)
        self.records = new_records   # 모두 정상일 때만 교체

    # ------------------------------------------------------------------
    # (3) 4가지 파일 형식 저장 / 읽기
    #     읽기 메소드는 파일 내용을 '딕셔너리의 리스트'로 반환하고,
    #     동시에 self.records 도 그 내용으로 채운다.
    # ------------------------------------------------------------------

    # ---------- JSON ----------
    def save_json(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.to_list(), f, ensure_ascii=False, indent=2)

    def load_json(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CorruptedFileError(f"{filename}: JSON 형식 오류 ({e})")
        self.from_list(data, filename)
        return data

    # ---------- CSV ----------
    def save_csv(self, filename):
        # utf-8-sig : 엑셀에서 열어도 한글이 깨지지 않도록
        with open(filename, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=HealthRecord.FIELDS)
            writer.writeheader()
            writer.writerows(self.to_list())

    def load_csv(self, filename):
        try:
            with open(filename, "r", encoding="utf-8-sig", newline="") as f:
                data = [dict(row) for row in csv.DictReader(f)]
        except csv.Error as e:
            raise CorruptedFileError(f"{filename}: CSV 형식 오류 ({e})")
        self.from_list(data, filename)
        return data

    # ---------- TXT (첫 줄 헤더, 탭으로 구분) ----------
    def save_txt(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\t".join(HealthRecord.FIELDS) + "\n")
            for d in self.to_list():
                f.write("\t".join(str(d[k]) for k in HealthRecord.FIELDS) + "\n")

    def load_txt(self, filename):
        data = []
        with open(filename, "r", encoding="utf-8") as f:
            header = f.readline().strip().split("\t")
            for line_no, line in enumerate(f, start=2):
                line = line.strip()
                if not line:
                    continue
                values = line.split("\t")
                if len(values) != len(header):
                    raise CorruptedFileError(
                        f"{filename}: {line_no}번째 줄 항목 수 불일치 "
                        f"({len(values)}개, 필요 {len(header)}개)")
                data.append(dict(zip(header, values)))
        self.from_list(data, filename)
        return data

    # ---------- PICKLE ----------
    def save_pickle(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self.to_list(), f)

    def load_pickle(self, filename):
        try:
            with open(filename, "rb") as f:
                data = pickle.load(f)
        except (pickle.UnpicklingError, EOFError) as e:
            raise CorruptedFileError(f"{filename}: PICKLE 형식 오류 ({e})")
        self.from_list(data, filename)
        return data

    # ---------- 확장자로 자동 선택 ----------
    def _pick(self, filename, table):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in table:
            raise UnsupportedFormatError(
                f"{filename}: 지원하지 않는 형식 '{ext}' (json, csv, txt, pkl만 가능)")
        return table[ext]

    def save_file(self, filename):
        func = self._pick(filename, {".json": self.save_json, ".csv": self.save_csv,
                                     ".txt": self.save_txt, ".pkl": self.save_pickle})
        try:
            func(filename)
        except OSError as e:
            raise HealthFileError(f"{filename}: 저장 실패 ({e.strerror})")

    def load_file(self, filename):
        func = self._pick(filename, {".json": self.load_json, ".csv": self.load_csv,
                                     ".txt": self.load_txt, ".pkl": self.load_pickle})
        try:
            return func(filename)
        except FileNotFoundError:
            raise HealthFileError(f"{filename}: 파일이 없음")
        except UnicodeDecodeError:
            raise CorruptedFileError(f"{filename}: 문자 인코딩 오류 (UTF-8 아님)")
        except OSError as e:
            raise HealthFileError(f"{filename}: 읽기 실패 ({e.strerror})")

    # ------------------------------------------------------------------
    # (4) 목록 내용을 화면에 출력
    # ------------------------------------------------------------------
    def print_records(self, title="건강정보 목록"):
        """현재 목록을 표 형태로 출력 (BMI, 판정 포함)"""
        print(f"\n===== {title} ({len(self.records)}명) =====")
        print("  식별번호    | 이름  | 성별 | 나이 |   키   | 몸무게 |  BMI  | 판정")
        print("-" * 78)
        for r in self.records:
            print(r)

    def print_file(self, filename):
        """저장된 파일을 읽어 리스트(딕셔너리) 원형과 표 형태로 출력"""
        data = self.load_file(filename)
        print(f"\n[{filename}] 에서 읽은 리스트(딕셔너리) 원형:")
        for d in data:
            print("  ", d)
        self.print_records(f"{filename} 내용")
        return data
