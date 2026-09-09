#
# bmi 계산 함수
# Body Mass Index (BMI) 계산 함수 
#

def get_bmi(weight_kg:float, height_cm:float) -> float:
    bmi = weight_kg / (height_cm / 100) ** 2
    return bmi

def test_get_bmi():
    height= 188
    weight= 88
    b= get_bmi(88, 188)
    print(f"키{height}cm) 몸무게{weight}kg의 BMI는 {b}입니다.")

if __name__=="__main__":
    test_get_bmi()