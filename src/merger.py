import os
from PyPDF2 import PdfMerger


# Lista com os caminhos dos arquivos PDF
arquivos_pdf = [
    "teste1.pdf",
    "teste2.pdf"
]

# Cria o objeto merger
merger = PdfMerger()

# Adiciona cada PDF
for pdf in arquivos_pdf:
    merger.append(pdf)

# Salva o PDF final
merger.write("PDF_unificado.pdf")
merger.close()

print("PDFs unidos com sucesso!")
