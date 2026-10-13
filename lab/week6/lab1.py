# 작성자: 이승식
# 작성일: 2026-10-13
# 문제: 은행에서대출을받을때, 은행마다대출이자가다르다. 이것을메소드오버라이딩으로깔금하게해결
하여보자. 

class Bank():
    def getInterestRate(self):
        return 0.0
    
class BadBank(Bank):
    def getInterestRate(self):
        return 10.0;

class NormalBank(Bank):
    def getInterestRate(self):
        return 5.0;

class GoodBank(Bank):
    def getInterestRate(self):
        return 3.0;

b1 = BadBank()
b2 = NormalBank()
b3 = GoodBank()
print("BadBank의이자율: "+ str(b1.getInterestRate()))
print("NormalBank의이자율: "+ str(b2.getInterestRate()))
print("GoodBank의이자율: "+ str(b3.getInterestRate()))