# routers/ui.py
import httpx
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from tools.database import get_db
from sqlalchemy.orm import Session

ui_router = APIRouter()

# Jinja2 templates (main.py’de tanımladığımızla aynı klasör)
templates = Jinja2Templates(directory="templates")

API_BASE_URL = "http://app:8000"
# Eğer Docker içinde farklı bir host/port ise ona göre ayarlayın, 
# örn: "http://app:8000" vs.

def get_token_from_session(request: Request) -> str | None:
    """
    Session’dan JWT token’ı döndürür. Yoksa None.
    """
    return request.session.get("token")

@ui_router.get("/", response_class=HTMLResponse)
def main_menu(request: Request):
    """
    Ana menü sayfası: Register ve Login linkleri gösterilecek.
    """
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
    # Mevcut /auth/register endpoint’ine istek at
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
            # Kayıt başarılı -> login sayfasına yönlendirelim
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        else:
            # Hata -> register sayfasını tekrar göster
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
            role = data.get("role")  # role bilgisi geldi

            if not token:
                return templates.TemplateResponse("login.html", {
                    "request": request,
                    "error": "Token alınamadı"
                })

            # Token'ı session'a yazalım
            request.session["token"] = token

            # Rol bilgisine göre yönlendirme
            if role == "admin":
                return RedirectResponse(url="/admin_menu", status_code=status.HTTP_303_SEE_OTHER)
            elif role == "teacher":
                return RedirectResponse(url="/teacher_menu", status_code=status.HTTP_303_SEE_OTHER)
            else:
                # default olarak student kabul edelim
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
    # Aslında rol kontrolü yapmak istiyorsanız, token decode veya /users/current 
    # endpoint ile rol check yapılabilir. Demo’da basit tutulmuştur.
    return templates.TemplateResponse("student_menu.html", {"request": request})

#####################################################################
# STUDENT: SINAV BAŞLAT (Soruları Çek)
#####################################################################

@ui_router.get("/student_solve_exam", response_class=HTMLResponse)
def student_solve_exam(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")

    # /exams/start endpoint’ine POST atarak soruları çekelim:
    with httpx.Client() as client:
        r = client.post(f"{API_BASE_URL}/exams/start", headers={
            "Authorization": f"Bearer {token}"
        })
        if r.status_code == 200:
            data = r.json()
            exam_id = data["exam_id"]
            questions = data["questions"]  # section-based question list
            # Soru tipleri vs. data yapısı -> bu data’yı template'e paslayıp 
            # form halinde kullanıcıya göstereceğiz.
            
            return templates.TemplateResponse("student_solve_exam.html", {
                "request": request,
                "exam_id": exam_id,
                "sections": questions  # [ { "section": int, "questions": [q1, q2..] } ]
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

    # Asenkron okumak için 'await'
    form_data = await request.form()  # artık 'form_data' gerçek MultiDict

    # multiple_choice checkbox verilerini ayrıştırmak istiyorsanız:
    answers_payload = {}

    # Bu şekilde form_data'dan tüm key-value çiftlerini alabilirsiniz:
    for key in form_data.keys():
        if key.startswith("answer_"):
            question_id = key.replace("answer_", "")
            value = form_data.getlist(key)  # checkbox birden fazla olabilir
            if len(value) == 1:
                # Radio/true_false/single_choice gibi tekil veri olabilir
                answers_payload[question_id] = value[0]
            else:
                # Multiple choice
                answers_payload[question_id] = ",".join(value)

    # Artık answers_payload'ı exams/submit'e gönderelim
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
            return RedirectResponse(url="/student_view_results", status_code=status.HTTP_303_SEE_OTHER)
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
    
    # /students/results endpoint’inden verilerimizi alalım
    with httpx.Client() as client:
        r = client.get(
            f"{API_BASE_URL}/students/results",
            headers={"Authorization": f"Bearer {token}"}
        )
        if r.status_code == 200:
            data = r.json()
            # data = { "exams": [ { "exam_id":..., "answers":[...] } ] }
            return templates.TemplateResponse("student_view_results.html", {
                "request": request,
                "results": data["exams"]
            })
        else:
            return HTMLResponse(f"Sonuçlar alınamadı: {r.text}", status_code=400)

#####################################################################
# ADMIN (Örnek): TÜM KULLANICILARI LİSTELE
#####################################################################

@ui_router.get("/admin_menu", response_class=HTMLResponse)
def admin_menu(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")
    # Yine rol kontrolü vb. isterseniz yapın.
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

#####################################################################
# TEACHER (Örnek): SORU EKLEME
#####################################################################

@ui_router.get("/teacher_menu", response_class=HTMLResponse)
def teacher_menu(request: Request):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("teacher_menu.html", {"request": request})

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
    correct_answer: str = Form(...),
):
    token = get_token_from_session(request)
    if not token:
        return RedirectResponse(url="/login")

    payload = {
        "question_text": question_text,
        "q_type": q_type,
        "points": points,
        "correct_answer": correct_answer
    }
    with httpx.Client() as client:
        r = client.post(
            f"{API_BASE_URL}/questions/",
            headers={"Authorization": f"Bearer {token}"},
            json=payload
        )
        if r.status_code == 200:
            # Soru başarıyla eklendi
            return RedirectResponse(url="/teacher_menu", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return HTMLResponse(f"Soru eklenemedi: {r.text}", status_code=400)

#####################################################################
# TEACHER: İSTATİSTİK GÖRÜNTÜLEME
#####################################################################

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
            stats_data = r.json()  # list of stats
            return templates.TemplateResponse("teacher_view_stats.html", {
                "request": request,
                "stats": stats_data
            })
        else:
            return HTMLResponse(f"İstatistik alınamadı: {r.text}", status_code=400)
