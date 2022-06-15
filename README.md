# DAbookTest
가상환경 만들기 
python -m venv myvenv
 가상환경 실행 
source myvenv/Scripts/activate

쟝고 필요한 모듈 다운
pip install django djangorestframework
pip install pyjwt

python manage.py createsuperuser
이메일, 아이디, 비밀번호 입력
그 후 
python manage.py runserver

postman 다운
https://www.postman.com/downloads/


<img width="377" alt="image" src="https://user-images.githubusercontent.com/80515822/173841690-24227fc8-75e1-4433-81f2-5645694adf7d.png">

POST 
http://127.0.0.1:8000/api/auth/register
{
    "email":"test1234@gmail.com",
    "username":"username2",
    "password":"test1234"
}

http://127.0.0.1:8000/api/auth/login
{
    "email":"test1234@gmail.com",
    "username":"username2",
    "password":"test1234"
}

Token 복사 -> Auth 창에 Beater Token 선택
붙여넣기 
<img width="831" alt="image" src="https://user-images.githubusercontent.com/80515822/173853254-4396f463-529b-4c54-97d8-6bfd366109ed.png">


user 테이블 보기
User - GET
Token 복사 -> Auth 창에 Beater Token 선택
위에 토큰 했던 것 반복 후
GET 
http://127.0.0.1:8000/api/auth/user

글쓰기 
CreateTodos - POST
Token 복사 -> Auth 창에 Beater Token 선택
위에 토큰 했던 것 반복 후
POST - http://127.0.0.1:8000/api/todos/
body에 이렇게 쓰고
{
    "title":"아무거나",
    "desc":"데이터 넣으려구요"
}
send!


글 쓴 목록 보기
위에 했던 것 그대로한 후 
GET - http://127.0.0.1:8000/api/todos/
메소드만 바꿔주시면 됩니다!
