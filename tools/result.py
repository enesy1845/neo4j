# tools/result.py
from rich import print
from rich.table import Table
from rich.console import Console
from tools.models import Exam, ExamAnswer, Statistics, Question

def view_results(db, user):
    exams = db.query(Exam).filter(Exam.user_id == user.user_id).all()
    if not exams:
        print("No exam records found.\n")
        return

    console = Console()
    for idx, exam in enumerate(exams, start=1):
        console.print(f"\n[bold underline]Öğrenci No: {user.user_id}[/bold underline]")
        console.print(f"Öğrenci Sınıfı: {user.class_name}")
        console.print(f"Sınav {idx}")

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Soru Bölümü", style="cyan", no_wrap=True)
        table.add_column("DS", style="green")
        table.add_column("YS", style="red")
        table.add_column("Okul(%)", style="magenta")
        table.add_column("Notu(%)", style="yellow")

        # Bu exam'e ait cevapları çek
        exam_answers = db.query(ExamAnswer).filter(ExamAnswer.exam_id == exam.exam_id).all()
        section_data = {}

        for ans in exam_answers:
            q = db.query(Question).filter(Question.id == ans.question_id).first()
            sec = q.section
            if sec not in section_data:
                section_data[sec] = {"ds": 0, "ys": 0}
            if ans.is_correct:
                section_data[sec]["ds"] += 1
            else:
                section_data[sec]["ys"] += 1

        for sec, data in section_data.items():
            ds = data["ds"]
            ys = data["ys"]
            # Okul ve class bazlı istatistiği bulalım
            stat = db.query(Statistics).filter(
                Statistics.school_id == exam.school_id,
                Statistics.class_name == user.class_name,
                Statistics.section_number == sec
            ).first()

            school_avg = stat.section_percentage if stat else 0.0

            notu = (ds / (ds + ys)) * 100 if (ds + ys) > 0 else 0

            table.add_row(
                f"Section-{sec}",
                str(ds),
                str(ys),
                f"{school_avg:.2f}",
                f"{notu:.2f}"
            )

        console.print(table)

        # Basit bir geçme kontrolü (örnek)
        if user.score_avg >= 15:  # 15/20 => %75
            console.print("[bold green]Genel Sonuç: Geçti.[/bold green]\n")
        else:
            console.print("[bold red]Genel Sonuç: Geçemedi.[/bold red]\n")
