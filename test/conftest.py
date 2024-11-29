import sys
import os
from pathlib import Path

# Proje kök dizinini bulmak için
root_dir = Path(__file__).resolve().parent.parent

# src dizinini sys.path'e ekle
src_dir = root_dir / 'src'
sys.path.append(str(src_dir))
print("sys.path includes:",sys.path)