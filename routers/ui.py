# routers/ui.py
import httpx
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from tools.database import get_db  # Sadece Neo4j için kullanılacak

ui_router = APIRouter()
templates = Jinja2Templates(directory="templates")
API_BASE_URL = "http://app:8000"  # Docker ortamı için

def get_token_from_session(request: Request) -> str | None:
    return request.session.get("token")

def get_role_from_session(request: Request) -> str | None:
    return request.session.get("role")

# School ID mapping (örnek)
school_id_map = {}
next_school_index = 1

@ui_router.get("/go_main_menu")
def go_main_menu(request: Request):
    role = request.session.get("role")
    if not role:
        return RedirectResponse(url="/")
    if role == "admin":
        return RedirectResponse(url="/admin_menu")
    elif role == "teacher":
        return RedirectResponse(url="/teacher_menu")
    elif role == "student":
        return RedirectResponse(url="/student_menu")
    else:
        return RedirectResponse(url="/")

@ui_router.get("/", response_class=HTMLResponse)
def main_menu(request: Request):
    token = get_token_from_session(request)
    role = get_role_from_session(request)
    if not token or not role:
        return templates.TemplateResponse("main_menu.html", {"request": request})
    else:
        if role == "admin":
            return RedirectResponse(url="/admin_menu")
        elif role == "teacher":
            return RedirectResponse(url="/teacher_menu")
        elif role == "student":
            return RedirectResponse(url="/student_menu")
        else:
            return templates.TemplateResponse("main_menu.html", {"request": request})

@ui_router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@ui_router.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    role: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    class_name: list = Form(...),  # Çoklu değer bekleniyor (öğretmen için)
    registered_section: str = Form("", alias="registered_section"),
):
    if role.lower() == "teacher":
        final_class_name = ",".join(class_name)
    else:
        final_class_name = class_name[0] if class_name else "7-A"
    payload = {
        "role": role.lower(),
        "username": username,
        "password": password,
        "name": name,
        "surname": surname,
        "class_name": final_class_name,
    }
    if role.lower() == "teacher" and registered_section.strip():
        payload["registered_section"] = registered_section.strip()
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{API_BASE_URL}/auth/register", json=payload, timeout=10.0)
            if r.status_code == 200:
                return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
            else:
                return templates.TemplateResponse("register.html", {
                    "request": request,
                    "error": r.json().get("detail", "Register error")
                })
    except httpx.ReadTimeout:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "The request timed out. Please try again later."
        })
    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": f"An error occurred: {str(e)}"
        })

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
                    "error": "No token received"
                })
            request.session["token"] = token
            request.session["role"] = role
            request.session["username"] = username
            if role == "admin":
                return RedirectResponse(url="/admin_menu", status_code=status.HTTP_303_SEE_OTHER)
            elif role == "teacher":
                return RedirectResponse(url="/teacher_menu", status_code=status.HTTP_303_SEE_OTHER)
            else:
                return RedirectResponse(url="/student_menu", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": r.json().get("detail", "Login error")
            })

@ui_router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

# ==================== Student Endpoints ====================

@ui_router.get("/student_menu", response_class=HTMLResponse)
def student_menu(request: Request):
    token = request.session.get("token")
    role = request.session.get("role")
    if not token or role != "student":
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        user_resp = client.get(f"{API_BASE_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
        if user_resp.status_code == 200:
            user_data = user_resp.json()
            global next_school_index
            if user_data["school_id"] not in school_id_map:
                school_id_map[user_data["school_id"]] = next_school_index
                next_school_index += 1
            mapped_school_id = school_id_map[user_data["school_id"]]
            left_attempts = max(0, 2 - user_data.get("attempts", 0))
            return templates.TemplateResponse("student_menu.html", {
                "request": request,
                "user_info": user_data,
                "mapped_school_id": mapped_school_id,
                "left_attempts": left_attempts
            })
        else:
            request.session.clear()
            return RedirectResponse(url="/login")

@ui_router.get("/student_solve_exam", response_class=HTMLResponse)
def student_solve_exam(request: Request):
    token = request.session.get("token")
    role = request.session.get("role")
    if not token or role != "student":
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        user_resp = client.get(f"{API_BASE_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
        if user_resp.status_code != 200:
            request.session.clear()
            return RedirectResponse(url="/login")
        user_data = user_resp.json()
        if user_data.get("attempts", 0) >= 2:
            return templates.TemplateResponse("student_no_attempts_left.html", {
                "request": request,
                "user_info": user_data
            })
        r = client.post(f"{API_BASE_URL}/exams/start", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            data = r.json()
            exam_id = data["exam_id"]
            questions = data["questions"]
            return templates.TemplateResponse("student_solve_exam.html", {
                "request": request,
                "exam_id": exam_id,
                "sections": questions,
            })
        else:
            return HTMLResponse(f"Exam could not be started: {r.text}", status_code=400)

@ui_router.post("/student_submit_exam", response_class=HTMLResponse)
async def student_submit_exam(
    request: Request,
):
    token = request.session.get("token")
    role = request.session.get("role")
    if not token or role != "student":
        return RedirectResponse(url="/login")
    form_data = await request.form()
    answers_payload = {}
    for key in form_data.keys():
        if key.startswith("answer_"):
            question_id = key.replace("answer_", "").replace("[]", "")
            value_list = form_data.getlist(key)
            answers_payload[question_id] = {"selected_texts": value_list}
    exam_id = form_data.get("exam_id")
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
            return RedirectResponse(url="/student_view_results?exam_submitted=1", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return HTMLResponse(f"Exam could not be submitted: {r.text}", status_code=400)

@ui_router.get("/student_view_results", response_class=HTMLResponse)
def student_view_results(request: Request):
    token = request.session.get("token")
    role = request.session.get("role")
    if not token or role != "student":
        return RedirectResponse(url="/login")
    hide_back = bool(request.query_params.get("exam_submitted", None))
    with httpx.Client() as client:
        r = client.get(f"{API_BASE_URL}/students/results_v2", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            data = r.json()
            return templates.TemplateResponse(
                "student_view_results.html",
                {
                    "request": request,
                    "results_data": data,
                    "hide_back_button": hide_back
                }
            )
        else:
            request.session.clear()
            return RedirectResponse(url="/login")

# ==================== Admin Endpoints ====================

@ui_router.get("/admin_menu", response_class=HTMLResponse)
def admin_menu(request: Request):
    token = request.session.get("token")
    role = request.session.get("role")
    if not token or role != "admin":
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        user_resp = client.get(f"{API_BASE_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
        if user_resp.status_code == 200:
            user_data = user_resp.json()
            global next_school_index
            if user_data["school_id"] not in school_id_map:
                school_id_map[user_data["school_id"]] = next_school_index
                next_school_index += 1
            mapped_school_id = school_id_map[user_data["school_id"]]
            msg = request.query_params.get("msg", "")
            return templates.TemplateResponse("admin_menu.html", {
                "request": request,
                "user_info": user_data,
                "mapped_school_id": mapped_school_id,
                "msg": msg
            })
        else:
            request.session.clear()
            return RedirectResponse(url="/login")

@ui_router.get("/admin_list_users", response_class=HTMLResponse)
def admin_list_users(request: Request):
    token = request.session.get("token")
    role = request.session.get("role")
    if not token or role != "admin":
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        r = client.get(f"{API_BASE_URL}/users/", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            users_data = r.json()
            msg = request.query_params.get("msg", "")
            return templates.TemplateResponse("admin_list_user.html", {
                "request": request,
                "users": users_data,
                "msg": msg
            })
        else:
            request.session.clear()
            return RedirectResponse(url="/login")

@ui_router.get("/admin_update_user", response_class=HTMLResponse)
def admin_update_user_form(request: Request, username: str):
    token = request.session.get("token")
    role = request.session.get("role")
    if not token or role != "admin":
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        r = client.get(f"{API_BASE_URL}/users/", headers={"Authorization": f"Bearer {token}"})
        if r.status_code != 200:
            request.session.clear()
            return RedirectResponse(url="/login")
        all_users = r.json()
        target_user = None
        for u in all_users:
            if u["username"] == username:
                target_user = u
                break
        if not target_user:
            return HTMLResponse("User to update not found", status_code=404)
        msg = request.query_params.get("msg", "")
        return templates.TemplateResponse("admin_update_user.html", {
            "request": request,
            "user_info": target_user,
            "msg": msg
        })

@ui_router.post("/admin_update_user", response_class=HTMLResponse)
def admin_update_user_submit(
    request: Request,
    user_id: str = Form(...),
    username: str = Form(...),
    name: str = Form(...),
    surname: str = Form(...),
    class_name: str = Form(...),
    role: str = Form(...),
    registered_section: str = Form(""),
    new_password: str = Form("")
):
    token = request.session.get("token")
    role_session = request.session.get("role")
    if not token or role_session != "admin":
        return RedirectResponse(url="/login")
    payload = {
        "username": username,
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
            f"{API_BASE_URL}/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            json=payload
        )
        if r.status_code == 200:
            return RedirectResponse(url=f"/admin_list_users?msg=User+{username}+successfully+updated", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return RedirectResponse(url=f"/admin_update_user?username={username}&msg=Update+error:{r.text}", status_code=status.HTTP_303_SEE_OTHER)

@ui_router.get("/admin_delete_user", response_class=HTMLResponse)
def admin_delete_user(request: Request, username: str):
    token = request.session.get("token")
    role = request.session.get("role")
    if not token or role != "admin":
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        r = client.delete(f"{API_BASE_URL}/users/{username}", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            return RedirectResponse(url="/admin_list_users?msg=User+deleted", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return RedirectResponse(url=f"/admin_list_users?msg=User+could+not+be+deleted:{r.text}", status_code=status.HTTP_303_SEE_OTHER)

# ==================== Teacher Endpoints ====================

@ui_router.get("/teacher_menu", response_class=HTMLResponse)
def teacher_menu(request: Request):
    token = request.session.get("token")
    role = request.session.get("role")
    if not token or role != "teacher":
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        user_resp = client.get(f"{API_BASE_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
        if user_resp.status_code == 200:
            user_data = user_resp.json()
            global next_school_index
            if user_data["school_id"] not in school_id_map:
                school_id_map[user_data["school_id"]] = next_school_index
                next_school_index += 1
            mapped_school_id = school_id_map[user_data["school_id"]]
            msg = request.query_params.get("msg", "")
            return templates.TemplateResponse("teacher_menu.html", {
                "request": request,
                "user_info": user_data,
                "mapped_school_id": mapped_school_id,
                "msg": msg
            })
        else:
            request.session.clear()
            return RedirectResponse(url="/login")

@ui_router.get("/teacher_add_question", response_class=HTMLResponse)
def teacher_add_question_form(request: Request):
    token = request.session.get("token")
    role = request.session.get("role")
    if not token or role != "teacher":
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("teacher_add_question.html", {"request": request})

@ui_router.post("/teacher_add_question", response_class=HTMLResponse)
def teacher_add_question_submit(
    request: Request,
    question_text: str = Form(...),
    q_type: str = Form(...),
    points: int = Form(...),
    single_correct: str = Form("", alias="single_correct"),
    single_a: str = Form("", alias="single_A"),
    single_b: str = Form("", alias="single_B"),
    single_c: str = Form("", alias="single_C"),
    single_d: str = Form("", alias="single_D"),
    multi_correct: list[str] = Form([], alias="multi_correct"),
    multi_a: str = Form("", alias="multi_A"),
    multi_b: str = Form("", alias="multi_B"),
    multi_c: str = Form("", alias="multi_C"),
    multi_d: str = Form("", alias="multi_D"),
    tf_correct: str = Form("", alias="tf_correct"),
    ordering_correct: str = Form("", alias="ordering_correct"),
    ordering_all: str = Form("", alias="ordering_all")
):
    token = request.session.get("token")
    role_session = request.session.get("role")
    if not token or role_session != "teacher":
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        me_resp = client.get(f"{API_BASE_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
        if me_resp.status_code != 200:
            request.session.clear()
            return RedirectResponse(url="/login")
        me_data = me_resp.json()
        teacher_section = me_data.get("registered_section")
        if not teacher_section:
            return HTMLResponse("You do not have a registered section, you cannot add questions.", status_code=400)
        choices_list = []
        if q_type == "true_false":
            correct_val = tf_correct.strip().lower()
            choices_list = [
                {"choice_text": "True", "is_correct": (correct_val == "true"), "correct_position": None},
                {"choice_text": "False", "is_correct": (correct_val == "false"), "correct_position": None}
            ]
        elif q_type == "single_choice":
            sc = single_correct.upper()
            choices_list = [
                {"choice_text": single_a.strip(), "is_correct": (sc == "A"), "correct_position": None},
                {"choice_text": single_b.strip(), "is_correct": (sc == "B"), "correct_position": None},
                {"choice_text": single_c.strip(), "is_correct": (sc == "C"), "correct_position": None},
                {"choice_text": single_d.strip(), "is_correct": (sc == "D"), "correct_position": None},
            ]
        elif q_type == "multiple_choice":
            correct_set = {x.upper() for x in multi_correct}
            choices_list = [
                {"choice_text": multi_a.strip(), "is_correct": ("A" in correct_set), "correct_position": None},
                {"choice_text": multi_b.strip(), "is_correct": ("B" in correct_set), "correct_position": None},
                {"choice_text": multi_c.strip(), "is_correct": ("C" in correct_set), "correct_position": None},
                {"choice_text": multi_d.strip(), "is_correct": ("D" in correct_set), "correct_position": None},
            ]
        elif q_type == "ordering":
            correct_seq = [x.strip() for x in ordering_correct.split(",")] if ordering_correct.strip() else []
            ordering_list = [x.strip() for x in ordering_all.split(",")] if ordering_all.strip() else []
            correct_map = {}
            for idx, val in enumerate(correct_seq):
                correct_map[val.lower()] = idx
            for item in ordering_list:
                key = item.lower()
                cp = correct_map.get(key, None)
                choices_list.append({
                    "choice_text": item,
                    "is_correct": False,
                    "correct_position": cp
                })
        payload = {
            "question_text": question_text,
            "q_type": q_type,
            "points": points,
            "section": int(teacher_section),
            "choices": choices_list
        }
        r = client.post(
            f"{API_BASE_URL}/questions/",
            headers={"Authorization": f"Bearer {token}"},
            json=payload
        )
        if r.status_code == 200:
            return RedirectResponse(url="/teacher_menu?msg=Question+added", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return templates.TemplateResponse("teacher_add_question.html", {
                "request": request,
                "msg": f"Question could not be added: {r.text}"
            })

@ui_router.get("/teacher_view_stats", response_class=HTMLResponse)
def teacher_view_stats(request: Request):
    token = request.session.get("token")
    role = request.session.get("role")
    if not token or role != "teacher":
        return RedirectResponse(url="/login")
    with httpx.Client() as client:
        r = client.get(f"{API_BASE_URL}/stats/", headers={"Authorization": f"Bearer {token}"})
        if r.status_code == 200:
            stats_data = r.json()
            return templates.TemplateResponse("teacher_view_stats.html", {
                "request": request,
                "stats": stats_data
            })
        else:
            request.session.clear()
            return RedirectResponse(url="/login")

# ==================== Common: Update Profile =====================

@ui_router.get("/user_profile", response_class=HTMLResponse)
def user_profile_get(request: Request):
    token = request.session.get("token")
    if not token:
        return RedirectResponse(url="/login")
    msg = request.query_params.get("msg", "")
    with httpx.Client() as client:
        resp = client.get(f"{API_BASE_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
        if resp.status_code == 200:
            user_data = resp.json()
            return templates.TemplateResponse("user_profile.html", {
                "request": request,
                "user_data": user_data,
                "msg": msg
            })
        else:
            request.session.clear()
            return RedirectResponse(url="/login")

@ui_router.post("/user_profile", response_class=HTMLResponse)
def user_profile_post(
    request: Request,
    name: str = Form(""),
    surname: str = Form(""),
    class_name: str = Form(""),
    new_password: str = Form("")
):
    token = request.session.get("token")
    if not token:
        return RedirectResponse(url="/login")
    payload = {}
    if name:
        payload["name"] = name
    if surname:
        payload["surname"] = surname
    if class_name:
        payload["class_name"] = class_name
    if new_password.strip():
        payload["new_password"] = new_password.strip()
    with httpx.Client() as client:
        r = client.put(f"{API_BASE_URL}/users/me", headers={"Authorization": f"Bearer {token}"}, json=payload)
        if r.status_code == 200:
            return RedirectResponse(url="/user_profile?msg=Profile+updated", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return RedirectResponse(url=f"/user_profile?msg=Profile+update+error:{r.text}", status_code=status.HTTP_303_SEE_OTHER)
