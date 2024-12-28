# tools/statistics_utils.py

from tools.models import Statistics
from sqlalchemy.orm import Session

def update_statistics(db: Session, school_id, class_name, section_correct, section_wrong, section_scores):
    """
    Okul ve sınıf bazında istatistikleri günceller.
    
    Parameters:
    - db: Veritabanı oturumu
    - school_id: Güncellenen okulun ID'si
    - class_name: Güncellenen sınıfın adı
    - section_correct: Bölümler bazında doğru cevap sayıları
    - section_wrong: Bölümler bazında yanlış cevap sayıları
    - section_scores: Bölümler bazında toplanan puanlar
    """
    from tools.models import Statistics

    for section in section_correct.keys():
        # Her bölüm için ayrı istatistik kaydı oluştur veya güncelle
        stat = db.query(Statistics).filter(
            Statistics.school_id == school_id,
            Statistics.class_name == class_name,
            Statistics.section_number == section
        ).first()
        
        # Doğru ve yanlış sayısı
        c = section_correct[section]
        w = section_wrong[section]
        s = section_scores[section]  # bölümdeki puan
        
        if not stat:
            # Yeni istatistik kaydı oluştur
            total_questions = c + w
            section_percentage = (c / total_questions * 100) if total_questions > 0 else 0.0
            
            stat = Statistics(
                school_id=school_id,
                class_name=class_name,
                section_number=section,
                correct_questions=c,
                wrong_questions=w,
                average_score=s,  # ilk eklenen puan => 'ortalama' olarak atayabiliriz
                section_percentage=section_percentage
            )
            db.add(stat)
        else:
            # Mevcut istatistik kaydını güncelle
            old_total_correct = stat.correct_questions
            old_total_wrong = stat.wrong_questions
            old_total_questions = old_total_correct + old_total_wrong
            
            # Toplam doğru-yanlış birikmeli ekleniyor
            stat.correct_questions += c
            stat.wrong_questions += w
            
            # Bölümdeki önceki total ve yeni total
            new_total_correct = stat.correct_questions
            new_total_wrong = stat.wrong_questions
            new_total_questions = new_total_correct + new_total_wrong
            
            # average_score: basit bir yöntemle "eski + yeni" ortalaması
            # Örneğin:
            #   eski ortalama = stat.average_score (toplam puan gibi düşünülmüş)
            #   yeni puan = s
            # dilerseniz total exam count'a göre de bölebilirsiniz
            
            # Basit yaklaşım: "average_score" a s ekleyip 2'ye bölmek değil de,
            # "ortalama = (onceki_ortalama * eski_toplam + yeni_score) / yeni_toplam" gibi düşünebilirsiniz.
            # Burada verinin neyi temsil ettiğine göre formül değişebilir.
            
            # Örnek:
            #   stat.average_score = (stat.average_score + s) / 2
            # ya da:
            if old_total_questions == 0:
                # Hiç kayıt yoksa direk s atanabilir
                stat.average_score = s
            else:
                # Birikmeli veya ortalama
                # (eski_ortalama * eski_toplam_sinav + yeni_score) / (eski_toplam_sinav+1) gibi
                # ama net formül size bağlı
                
                # Basit bir ortalama güncellemesi yapalım:
                stat.average_score = (stat.average_score + s) / 2
            
            # Section percentage
            stat.section_percentage = (new_total_correct / new_total_questions * 100) if new_total_questions > 0 else 0.0
        
    db.commit()
