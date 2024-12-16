# tools/result.py

from rich import print
from rich.table import Table
from rich.console import Console
from tools.utils import load_json

def view_results(user):
    user_answers = load_json('users/user_answers.json')
    exams = user_answers.get('exams', [])
    if not exams:
        print("No exam records found.\n")
        return
    console = Console()
    
    for idx, exam in enumerate(exams, start=1):
        console.print(f"\n[bold underline]Öğrenci No: {user['user_id']}[/bold underline]")
        console.print(f"Öğrenci Sınıfı: {user['class_name']}")
        console.print(f"Sınav {idx}")
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Soru Bölümü", style="cyan", no_wrap=True)
        table.add_column("DS", style="green")
        table.add_column("YS", style="red")
        table.add_column("SO", style="magenta")
        table.add_column("OO", style="magenta")
        table.add_column("Notu (%)", style="yellow")
        table.add_column("Ort", style="yellow")
        
        passed_sections = True  # To determine overall pass/fail
        
        for section_record in exam['sections']:
            section = section_record['section_number']
            ds = sum(1 for q in section_record['questions'] if q['is_correct'])
            ys = sum(1 for q in section_record['questions'] if not q['is_correct'])
            # Get statistics
            statistics = load_json('users/statistics.json')
            class_name = user['class_name']
            school_name = user['school_name']
            class_avg = 0.0
            school_avg = 0.0
            for school in statistics['schools']:
                if school['school_name'] == school_name:
                    class_data = school['classes'].get(class_name, {})
                    section_data = class_data.get('sections', {}).get(str(section), {})
                    class_avg = class_data.get('sections', {}).get(str(section), {}).get('average_score', 0.0)
                    school_avg = school.get('classes', {}).get(class_name, {}).get('sections', {}).get(str(section), {}).get('average_score', 0.0)
                    break
            notu = (ds / (ds + ys)) * 100 if (ds + ys) > 0 else 0
            ort = notu  # Placeholder for more complex calculations if needed
            
            if not notu >= 75:
                passed_sections = False
            
            table.add_row(
                f"Section-{section}",
                str(ds),
                str(ys),
                f"{class_avg:.2f}",
                f"{school_avg:.2f}",
                f"{notu:.2f}",
                f"{ort:.2f}"
            )
        
        console.print(table)
        
        # Genel Sonuç
        genel_sonuc = "Geçemedi" if not passed_sections else "Geçti"
        if not passed_sections:
            console.print("[bold red]Genel Sonuç: Geçemedi, her bölümden en az 75 alınması gerekir.[/bold red]\n")
        else:
            console.print("[bold green]Genel Sonuç: Geçti.[/bold green]\n")
