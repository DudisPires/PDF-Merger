import os
import PyPDF2
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Valida se é um PDF
def validar_pdf(caminho):
    return os.path.isfile(caminho) and caminho.lower().endswith('.pdf')

# Junta os PDFs
def mesclar_pdfs(lista_arquivos, nome_saida):
    merger = PyPDF2.PdfMerger()

    for arquivo in lista_arquivos:
        if validar_pdf(arquivo):
            try:
                merger.append(arquivo)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar '{arquivo}': {e}")
        else:
            messagebox.showwarning("Aviso", f"Arquivo inválido ou não encontrado: {arquivo}")

    try:
        merger.write(nome_saida)
        merger.close()
        messagebox.showinfo("Sucesso", f"Arquivo final salvo como: {nome_saida}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar o arquivo final: {e}")

# App GUI
class PDFMergerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PDF Merger")
        self.geometry("600x400")
        self.pdf_list = []

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Título
        self.label = ctk.CTkLabel(self, text="PDF Merger", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=10)

        # Botão para selecionar PDFs
        self.select_button = ctk.CTkButton(self, text="Selecionar PDFs", command=self.selecionar_pdfs)
        self.select_button.pack(pady=10)

        # Lista de arquivos
        self.listbox = ctk.CTkTextbox(self, height=120, width=350)
        self.listbox.pack(pady=10)

        # Campo para nome do arquivo de saída
        self.output_entry = ctk.CTkEntry(self, placeholder_text="Nome do arquivo final (ex: resultado.pdf)", width=400)
        self.output_entry.pack(pady=10)

        # Botão para mesclar
        self.merge_button = ctk.CTkButton(self, text="Mesclar PDFs", command=self.executar_mesclagem)
        self.merge_button.pack(pady=10)

    def selecionar_pdfs(self):
        arquivos = filedialog.askopenfilenames(filetypes=[("Arquivos PDF", "*.pdf")])
        if arquivos:
            self.pdf_list = list(arquivos)
            self.listbox.delete("1.0", "end")
            for arquivo in self.pdf_list:
                self.listbox.insert("end", f"{arquivo}\n")

    def executar_mesclagem(self):
        nome_saida = self.output_entry.get().strip()
        if not self.pdf_list:
            messagebox.showwarning("Aviso", "Nenhum arquivo PDF selecionado.")
            return
        if not nome_saida:
            messagebox.showwarning("Aviso", "Informe um nome para o arquivo de saída.")
            return
        if not nome_saida.lower().endswith('.pdf'):
            nome_saida += '.pdf'
        mesclar_pdfs(self.pdf_list, nome_saida)

if __name__ == "__main__":
    app = PDFMergerApp()
    app.mainloop()
