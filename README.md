# DAbookTest
가상환경 만들기 
python -m venv myvenv
 가상환경 실행 
source myvenv/Scripts/activate

쟝고 필요한 모듈 다운
pip install django djangorestframework
pip install pyjwt

postman 다운
https://www.postman.com/downloads/



POST 
http://127.0.0.1:8000/api/auth/register
{
    "email":"test1234@gmail.com",
    "username":"username2",
    "password":"test1234"
}

http://127.0.0.1:8000/api/auth/login

Token 복사 -> Auth 창에 Beater Token 선택
붙여넣기 후 GET
http://127.0.0.1:8000/api/auth/user
