# routers/ui.py
import httpx
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from tools.database import get_db
from sqlalchemy.orm import Session

ui_router = APIRouter()
templates = Jinja2Templates(directory="templates")
API_BASE_URL = "http://app:8000"  # Docker'da "app" servisini dinliyorsanız
# Lokalde iseniz "http://127.0.0.1:8000" yapabilirsiniz.

def get_token_from_session(request: Request) -> str | None:
    return request.session.get("token")

def get_role_from_session(request: Request) -> str | None:
    return request.session.get("role")

@ui_router.get("/", response_class=HTMLResponse)
def main_menu(request: Request):
    """
    Ana menü sayfası:
    - Eğer kullanıcı login değilse main_menu.html döndür.
    - Login ise rolüne göre yönlendir.
    """
    token = get_token_from_session(request)
    role = get_role_from_session(request)
    if not token or not role:
        # Login değil -> register/login menüsü
        return templates.TemplateResponse("main_menu.html", {"request": request})
    else:
        # Login -> rola göre yönlendir
        if role == "admin":
            return RedirectResponse(url="/admin_menu")
        elif role == "teacher":
            return RedirectResponse(url="/teacher_menu")
        elif role == "student":
            return RedirectResponse(url="/student_menu")
        else:
            # Hiçbiri değilse main_menu
            return templates.TemplateResponse("main_menu.html", {"request": request})

#####################################################################
# REGISTER
#####################################################################
@ui_router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@ui_router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    class_name: str = Form(...),
    role: str = Form(...),
    registered_section: str | None = Form(None),
):
    payload = {
        "username": username,
        "password": password,
        "name": name,
        "surname": surname,
        "class_name": class_name,
        "role": role,
    }
    if registered_section:
        payload["registered_section"] = registered_section

    with httpx.Client() as client:
        r = client.post(f"{API_BASE_URL}/auth/register", json=payload)
        if r.status_code == 200:
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": r.json().get("detail", "Register error")
            })

#####################################################################
# LOGIN
#####################################################################
@ui_router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@ui_router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    with httpx.Client() as client:
        r = client.post(f"{API_BASE_URL}/auth/login", json={"username": username, "password": password})
        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token")
            role = data.get("role")
            if not token:
                return templates.TemplateResponse("login.html", {
                    "request": request,
                    "error": "Token alınamadı"
                })
            # Token'ı session'a yazalım
            request.session["token"] = token
            request.session["role"] = role  # Rolu de saklayalım

            if role == "admin":
                return RedirectResponse(url="/admin_menu", status_code=status.HTTP_303_SEE_OTHER)
            elif role == "teacher":
                return RedirectResponse(url="/teacher_menu", status_code=status.HTTP_303_SEE_OTHER)
            else:
                # default student
                return RedirectResponse(url="/student_menu", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": r.json().get("detail", "Login error")
            })

#####################################################################
# LOGOUT
#####################################################################
@ui_router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

#####################################################################
# STUDENT MENU
#####################################################################
@ui_router.get("/student_menu", response_class=HTMLResponse)
def student_menu(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("student_menu.html", {"request": request})

#####################################################################
# STUDENT: SINAV BAŞLAT
#####################################################################
@ui_router.get("/student_solve_exam", response_class=HTMLResponse)
def student_solve_exam(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")
    # /exams/start endpoint’ine POST
    with httpx.Client() as client:
        r = client.post(f"{API_BASE_URL}/exams/start", headers={
            "Authorization": f"Bearer {token}"
        })
        if r.status_code == 200:
            data = r.json()
            exam_id = data["exam_id"]
            questions = data["questions"]
            return templates.TemplateResponse("student_solve_exam.html", {
                "request": request,
                "exam_id": exam_id,
                "sections": questions,
                # Sınav sayfasında geri butonu görünmesini istiyorsanız hide_back_button=False
                # Ama isterseniz kapatabilirsiniz. Örnek: "hide_back_button": True
            })
        else:
            return HTMLResponse(f"Sınav başlatılamadı: {r.text}", status_code=400)

#####################################################################
# STUDENT: SINAV CEVAPLARINI GÖNDER
#####################################################################
@ui_router.post("/student_submit_exam", response_class=HTMLResponse)
async def student_submit_exam(
    request: Request,
    exam_id: str = Form(...),
    db: Session = Depends(get_db)
):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")
    form_data = await request.form()
    answers_payload = {}
    for key in form_data.keys():
        if key.startswith("answer_"):
            question_id = key.replace("answer_", "")
            value = form_data.getlist(key)
            if len(value) == 1:
                answers_payload[question_id] = value[0]
            else:
                # Multiple choice
                answers_payload[question_id] = ",".join(value)

    submit_data = {
        "exam_id": exam_id,
        "answers": answers_payload
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{API_BASE_URL}/exams/submit",
            headers={"Authorization": f"Bearer {token}"},
            json=submit_data
        )
        if r.status_code == 200:
            # Sınav bitince geri tuşunu kapatmak için hide_back_button=True
            return RedirectResponse(url="/student_view_results?exam_submitted=1", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return HTMLResponse(f"Sınav gönderilemedi: {r.text}", status_code=400)

#####################################################################
# STUDENT: SONUÇLARI GÖRÜNTÜLE
#####################################################################
@ui_router.get("/student_view_results", response_class=HTMLResponse)
def student_view_results(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")

    # Geri tuşu kapatılacak mı?
    # exam_submitted query param'ı geldiyse hide_back_button=True
    hide_back = bool(request.query_params.get("exam_submitted", None))

    with httpx.Client() as client:
        r = client.get(
            f"{API_BASE_URL}/students/results",
            headers={"Authorization": f"Bearer {token}"}
        )
        if r.status_code == 200:
            data = r.json()
            return templates.TemplateResponse(
                "student_view_results.html",
                {
                    "request": request,
                    "results": data["exams"],
                    "hide_back_button": hide_back
                }
            )
        else:
            return HTMLResponse(f"Sonuçlar alınamadı: {r.text}", status_code=400)

#####################################################################
# ADMIN
#####################################################################
@ui_router.get("/admin_menu", response_class=HTMLResponse)
def admin_menu(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("admin_menu.html", {"request": request})

@ui_router.get("/admin_list_users", response_class=HTMLResponse)
def admin_list_users(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        r = client.get(
            f"{API_BASE_URL}/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if r.status_code == 200:
            users_data = r.json()
            return templates.TemplateResponse("admin_list_user.html", {
                "request": request,
                "users": users_data
            })
        else:
            return HTMLResponse(f"Kullanıcılar listelenemedi: {r.text}", status_code=400)

@ui_router.get("/admin_update_user", response_class=HTMLResponse)
def admin_update_user_form(request: Request, username: str):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        r = client.get(f"{API_BASE_URL}/users/", headers={"Authorization": f"Bearer {token}"})
        if r.status_code != 200:
            return HTMLResponse(f"Kullanıcı bilgileri alınamadı: {r.text}", status_code=400)
        all_users = r.json()
        target_user = None
        for u in all_users:
            if u["username"] == username:
                target_user = u
                break
        if not target_user:
            return HTMLResponse("Güncellenecek kullanıcı bulunamadı", status_code=404)
        return templates.TemplateResponse("admin_update_user.html", {
            "request": request,
            "user_info": target_user
        })

@ui_router.post("/admin_update_user", response_class=HTMLResponse)
def admin_update_user_submit(
    request: Request,
    username: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    class_name: str = Form(...),
    role: str = Form(...),
    registered_section: str = Form(""),
    new_password: str = Form(""),
):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")

    payload = {
        "name": name,
        "surname": surname,
        "class_name": class_name,
        "role": role,
        "registered_section": registered_section
    }
    if new_password.strip():
        payload["new_password"] = new_password.strip()

    with httpx.Client() as client:
        r = client.put(
            f"{API_BASE_URL}/users/{username}",
            headers={"Authorization": f"Bearer {token}"},
            json=payload
        )
        if r.status_code == 200:
            return RedirectResponse(url="/admin_list_users", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return HTMLResponse(f"Kullanıcı güncellenemedi: {r.text}", status_code=400)

@ui_router.get("/admin_delete_user", response_class=HTMLResponse)
def admin_delete_user(request: Request, username: str):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")

    with httpx.Client() as client:
        r = client.delete(
            f"{API_BASE_URL}/users/{username}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if r.status_code == 200:
            return RedirectResponse(url="/admin_list_users", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return HTMLResponse(f"Kullanıcı silinemedi: {r.text}", status_code=400)

#####################################################################
# TEACHER
#####################################################################
@ui_router.get("/teacher_menu", response_class=HTMLResponse)
def teacher_menu(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")

    # Soru eklendi mesajı varsa al
    msg = request.query_params.get("msg", "")
    return templates.TemplateResponse("teacher_menu.html", {"request": request, "msg": msg})

@ui_router.get("/teacher_add_question", response_class=HTMLResponse)
def teacher_add_question_form(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("teacher_add_question.html", {"request": request})

@ui_router.post("/teacher_add_question", response_class=HTMLResponse)
def teacher_add_question_submit(
    request: Request,
    question_text: str = Form(...),
    q_type: str = Form(...),
    points: int = Form(...),

    # Single choice
    single_correct: str = Form("", alias="single_correct"),
    single_a: str = Form("", alias="single_A"),
    single_b: str = Form("", alias="single_B"),
    single_c: str = Form("", alias="single_C"),
    single_d: str = Form("", alias="single_D"),

    # Multiple choice
    multi_correct: list[str] = Form([], alias="multi_correct"),  # checkbox
    multi_a: str = Form("", alias="multi_A"),
    multi_b: str = Form("", alias="multi_B"),
    multi_c: str = Form("", alias="multi_C"),
    multi_d: str = Form("", alias="multi_D"),

    # True/False
    tf_correct: str = Form("", alias="tf_correct"),

    # Ordering
    ordering_correct: str = Form("", alias="ordering_correct"),
    ordering_all: str = Form("", alias="ordering_all"),
):
    """
    Formdan gelen veriyi parse ediyoruz.
    Soru tipine göre choices'ı ve correct_answer'ı oluşturup API'ye POST edeceğiz.
    """
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")

    # Hazırlık
    all_choices = []
    correct_answer_str = ""

    # SINGLE CHOICE
    if q_type == "single_choice":
        # 4 şıkkı listede tut
        # A,B,C,D => text
        # single_correct => mesela "B"
        a_text = single_a.strip()
        b_text = single_b.strip()
        c_text = single_c.strip()
        d_text = single_d.strip()
        all_choices = [a_text, b_text, c_text, d_text]
        correct_answer_str = single_correct  # "A" "B" "C" veya "D"

    # MULTIPLE CHOICE
    elif q_type == "multiple_choice":
        # 4 şıkkı listede tut
        a_text = multi_a.strip()
        b_text = multi_b.strip()
        c_text = multi_c.strip()
        d_text = multi_d.strip()
        all_choices = [a_text, b_text, c_text, d_text]
        if multi_correct:
            # list[str] mesela ["A","C"]
            correct_answer_str = ",".join(multi_correct)  # "A,C"

    # TRUE/FALSE
    elif q_type == "true_false":
        # Sabit 2 şık
        all_choices = ["True", "False"]
        correct_answer_str = tf_correct.strip()  # "True" veya "False"

    # ORDERING
    elif q_type == "ordering":
        # ordering_correct = "1,2,3,4"
        correct_answer_str = ordering_correct.strip()
        # Tüm adımlar (opsiyonel)
        if ordering_all.strip():
            # virgülle ayır
            all_choices = [x.strip() for x in ordering_all.split(",")]
        else:
            # user vermediyse empty
            all_choices = []

    payload = {
        "question_text": question_text,
        "q_type": q_type,
        "points": points,
        "correct_answer": correct_answer_str
    }

    # Ek olarak, API tarafında "choices" kaydedebilmemiz için
    # custom bir endpoint yoksa (mevcut /questions/ endpoint'i "choices" alanını sadece json'a dönüştürebilir)
    # mevcut endpoint'te choices'ı doldurmak için de => "choices" alanını veremiyoruz orada
    # ama default implementasyonda "choices" => orada "None" kalıyordu. 
    # Yine de "choices" saklamak istiyorsak, en azından 'correct_answer' set ediliyor. 
    # API'yi de ufak ekleme ile "choices" desteği verecek biçimde güncelleyelim
    # => /questions/ endpoint'ine "choices" parametresi eklenmediği için,
    #    pratikte "PUT" vs. gerekecek. 
    # => Projenizde /questions/ ekleme logic'ini ufak modifiye etmelisiniz.
    #  Aşağıda mevcuda ek bir "choices" alanı koydum (AddQuestionRequest'e).
    payload["choices"] = ",".join(all_choices)

    with httpx.Client() as client:
        r = client.post(
            f"{API_BASE_URL}/questions/",
            headers={"Authorization": f"Bearer {token}"},
            json=payload
        )
        if r.status_code == 200:
            # Soru başarıyla eklendi -> teacher_menu'ya msg paramıyla dön
            return RedirectResponse(
                url="/teacher_menu?msg=Soru+eklendi",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            return templates.TemplateResponse(
                "teacher_add_question.html",
                {
                    "request": request,
                    "msg": f"Soru eklenemedi: {r.text}"
                }
            )

@ui_router.get("/teacher_view_stats", response_class=HTMLResponse)
def teacher_view_stats(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        r = client.get(
            f"{API_BASE_URL}/stats/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if r.status_code == 200:
            stats_data = r.json()
            return templates.TemplateResponse("teacher_view_stats.html", {
                "request": request,
                "stats": stats_data
            })
        else:
            return HTMLResponse(f"İstatistik alınamadı: {r.text}", status_code=400)
