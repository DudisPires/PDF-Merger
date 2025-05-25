import os
import PyPDF2
import customtkinter as ctk
from tkinter import filedialog, messagebox
from functools import partial # For passing arguments to button commands

# Valida se é um PDF (mantida, mas a validação principal ocorre na seleção)
def validar_pdf(caminho):
    """Checks if the given path is a valid PDF file."""
    return os.path.isfile(caminho) and caminho.lower().endswith('.pdf')

# Junta os PDFs
def mesclar_pdfs(lista_arquivos, nome_saida, status_callback=None):
    """
    Merges a list of PDF files into a single output PDF.

    Args:
        lista_arquivos (list): A list of paths to PDF files to merge.
        nome_saida (str): The path for the output merged PDF file.
        status_callback (function, optional): A function to call for status updates.
                                              It should accept a single string message.
    Returns:
        bool: True if merging was successful, False otherwise.
    """
    merger = PyPDF2.PdfMerger()
    total_files = len(lista_arquivos)
    merged_count = 0

    for i, arquivo in enumerate(lista_arquivos):
        if status_callback:
            status_callback(f"Processando {os.path.basename(arquivo)} ({i+1}/{total_files})...")
        
        # A validação de tipo de arquivo já é feita pelo filedialog,
        # mas uma verificação extra aqui não prejudica.
        if not validar_pdf(arquivo):
            msg = f"Arquivo inválido ou não encontrado (ignorado): {os.path.basename(arquivo)}"
            messagebox.showwarning("Aviso", msg)
            if status_callback:
                status_callback(msg)
            continue # Pula para o próximo arquivo

        try:
            merger.append(arquivo)
            merged_count += 1
        except Exception as e:
            error_msg = f"Erro ao adicionar '{os.path.basename(arquivo)}': {e}"
            messagebox.showerror("Erro de Leitura", error_msg)
            if status_callback:
                status_callback(f"Erro ao ler '{os.path.basename(arquivo)}'.")
            # Decide se quer parar ou continuar. Para este exemplo, vamos continuar.
            # return False # Descomente para parar na primeira falha de leitura

    if merged_count == 0 and total_files > 0:
        messagebox.showerror("Erro", "Nenhum arquivo PDF válido foi processado.")
        if status_callback:
            status_callback("Nenhum PDF válido processado.")
        return False
    
    if merged_count == 0 and total_files == 0: # Nenhum arquivo foi selecionado
        if status_callback:
            status_callback("Nenhum arquivo selecionado para mesclar.")
        # Não é um erro, mas nada a fazer.
        return False


    if merged_count > 0: # Só tenta salvar se algo foi adicionado
        try:
            if status_callback:
                status_callback(f"Salvando arquivo mesclado como '{os.path.basename(nome_saida)}'...")
            merger.write(nome_saida)
            merger.close()
            success_msg = f"Arquivo final salvo com sucesso como: {nome_saida}"
            messagebox.showinfo("Sucesso", success_msg)
            if status_callback:
                status_callback(f"Sucesso! Salvo como: {os.path.basename(nome_saida)}")
            return True # Indica sucesso
        except Exception as e:
            error_msg = f"Erro ao salvar o arquivo final '{nome_saida}': {e}"
            messagebox.showerror("Erro ao Salvar", error_msg)
            if status_callback:
                status_callback(f"Erro ao salvar: {e}")
            return False
    return False


# App GUI
class PDFMergerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Agrupador de PDFs Pro")
        self.geometry("700x580") # Aumentar um pouco o tamanho
        self.pdf_list = [] # Lista de caminhos completos dos PDFs
        self.output_path = "" # Caminho completo para o arquivo de saída

        ctk.set_appearance_mode("System") # System, Dark, Light
        ctk.set_default_color_theme("blue") # blue, dark-blue, green

        # --- Configure grid layout (1 row, 1 column for the main_frame) ---
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Main Frame ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1) # Coluna única para conteúdo
        # As linhas abaixo serão configuradas conforme necessário

        # --- Título ---
        self.title_label = ctk.CTkLabel(self.main_frame, text="📄 Agrupador de PDFs 📄", font=ctk.CTkFont(size=26, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=10, pady=(15, 25))
        self.main_frame.grid_rowconfigure(0, weight=0)

        # --- Frame de Seleção de Arquivos ---
        self.selection_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.selection_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.selection_frame.grid_columnconfigure(0, weight=1) # Botão de selecionar
        self.selection_frame.grid_columnconfigure(1, weight=0) # Botão de limpar
        self.main_frame.grid_rowconfigure(1, weight=0)

        self.select_button = ctk.CTkButton(self.selection_frame, text="➕ Adicionar PDFs à Lista", command=self.selecionar_pdfs, height=40, font=ctk.CTkFont(size=14))
        self.select_button.grid(row=0, column=0, padx=(0,10), pady=5, sticky="ew")

        self.clear_button = ctk.CTkButton(self.selection_frame, text="🗑️ Limpar Lista", command=self.limpar_lista_pdfs, height=40, font=ctk.CTkFont(size=14), fg_color="#D32F2F", hover_color="#B71C1C")
        self.clear_button.grid(row=0, column=1, padx=(0,0), pady=5, sticky="e")


        # --- Lista de arquivos (Scrollable Frame) ---
        self.list_label = ctk.CTkLabel(self.main_frame, text="Arquivos Selecionados (ordem de mesclagem):", font=ctk.CTkFont(size=12, slant="italic"))
        self.list_label.grid(row=2, column=0, padx=10, pady=(15,2), sticky="w")
        self.main_frame.grid_rowconfigure(2, weight=0)

        self.scrollable_file_list_frame = ctk.CTkFrame(self.main_frame, corner_radius=5, border_width=1)
        self.scrollable_file_list_frame.grid(row=3, column=0, padx=10, pady=(0,10), sticky="nsew")
        self.main_frame.grid_rowconfigure(3, weight=1) # Faz o scrollable frame expandir
        
        self.scrollable_file_list_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_file_list_frame.grid_columnconfigure(0, weight=1)

        self.scrollable_file_list = ctk.CTkScrollableFrame(self.scrollable_file_list_frame, fg_color="transparent")
        self.scrollable_file_list.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)


        # --- Frame de Saída ---
        self.output_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.output_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.output_frame.grid_columnconfigure(0, weight=1) # Entry
        self.output_frame.grid_columnconfigure(1, weight=0) # Botão Browse
        self.main_frame.grid_rowconfigure(4, weight=0)

        self.output_entry_label = ctk.CTkLabel(self.output_frame, text="Nome e Local do Arquivo de Saída:", font=ctk.CTkFont(size=12, slant="italic"))
        self.output_entry_label.grid(row=0, column=0, columnspan=2, padx=0, pady=(0,2), sticky="w")

        self.output_entry = ctk.CTkEntry(self.output_frame, placeholder_text="Clique em 'Salvar Como...' ou digite o caminho/nome.pdf", height=35, font=ctk.CTkFont(size=13))
        self.output_entry.grid(row=1, column=0, padx=(0,10), pady=5, sticky="ew")

        self.browse_output_button = ctk.CTkButton(self.output_frame, text="💾 Salvar Como...", command=self.browse_output_file, height=35, font=ctk.CTkFont(size=14))
        self.browse_output_button.grid(row=1, column=1, padx=(0,0), pady=5, sticky="e")

        # --- Botão para mesclar ---
        self.merge_button = ctk.CTkButton(self.main_frame, text="✨ Unir PDFs ✨", command=self.executar_mesclagem, height=45, font=ctk.CTkFont(size=16, weight="bold"))
        self.merge_button.grid(row=5, column=0, padx=10, pady=(15,5), sticky="ew")
        self.main_frame.grid_rowconfigure(5, weight=0)

        # --- Status Label ---
        self.status_label = ctk.CTkLabel(self.main_frame, text="Pronto para começar!", anchor="w", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=6, column=0, padx=10, pady=(5,10), sticky="ew")
        self.main_frame.grid_rowconfigure(6, weight=0)

        self._atualizar_display_pdfs() # Inicializa a lista de display vazia

    def _atualizar_status(self, message):
        """Updates the status label text."""
        self.status_label.configure(text=message)
        self.update_idletasks() # Força a atualização da GUI

    def _atualizar_display_pdfs(self):
        """Rebuilds the scrollable list of selected PDF files."""
        # Limpar widgets antigos da lista
        for widget in self.scrollable_file_list.winfo_children():
            widget.destroy()

        if not self.pdf_list:
            no_files_label = ctk.CTkLabel(self.scrollable_file_list, text="Nenhum PDF selecionado.", text_color="gray50", font=ctk.CTkFont(size=13))
            no_files_label.pack(pady=20, padx=10, anchor="center")
            self.merge_button.configure(state="disabled")
            self.clear_button.configure(state="disabled" if not self.pdf_list else "normal")
            return

        self.merge_button.configure(state="normal")
        self.clear_button.configure(state="normal")

        for idx, filepath in enumerate(self.pdf_list):
            filename = os.path.basename(filepath)
            
            # Frame para cada item da lista
            item_frame = ctk.CTkFrame(self.scrollable_file_list, fg_color="transparent") # Usar fg_color do parent
            item_frame.pack(fill="x", pady=(2,3), padx=2)
            item_frame.grid_columnconfigure(0, weight=1) # Label
            item_frame.grid_columnconfigure(1, weight=0) # Button

            label_text = f"{idx+1}. {filename}"
            if len(label_text) > 70: # Truncate long names for display
                label_text = label_text[:67] + "..."

            label = ctk.CTkLabel(item_frame, text=label_text, anchor="w", font=ctk.CTkFont(size=13))
            label.grid(row=0, column=0, padx=(5,10), pady=2, sticky="w")
            
            # Tooltip para nomes completos (se truncados)
            if len(filename) > len(label_text) - (len(str(idx+1)) + 3) : # 3 for ". " and "..."
                 # Basic tooltip implementation (could be improved with a custom tooltip class)
                 # label.bind("<Enter>", lambda e, fn=filename: self._atualizar_status(f"Arquivo: {fn}"))
                 # label.bind("<Leave>", lambda e: self._atualizar_status("Pronto.")) # Ou o status anterior
                 pass


            # Botão para remover
            remove_btn = ctk.CTkButton(item_frame, text="✕", width=28, height=28,
                                       command=partial(self.remover_pdf_da_lista, filepath),
                                       fg_color="#E57373", hover_color="#EF5350", text_color="white",
                                       font=ctk.CTkFont(size=14, weight="bold"), corner_radius=5)
            remove_btn.grid(row=0, column=1, padx=(0,5), pady=2, sticky="e")

    def selecionar_pdfs(self):
        """Opens a dialog to select PDF files and adds them to the list."""
        arquivos = filedialog.askopenfilenames(
            title="Selecione os arquivos PDF para unir",
            filetypes=[("Arquivos PDF", "*.pdf")]
        )
        if arquivos:
            novos_arquivos_adicionados_count = 0
            for arq in list(arquivos): # Convert to list
                if arq not in self.pdf_list:
                    self.pdf_list.append(arq)
                    novos_arquivos_adicionados_count +=1
            
            if novos_arquivos_adicionados_count > 0:
                self._atualizar_display_pdfs()
                self._atualizar_status(f"{novos_arquivos_adicionados_count} novo(s) PDF(s) adicionado(s) à lista. Total: {len(self.pdf_list)}.")
            else:
                self._atualizar_status("Nenhum arquivo novo adicionado (possivelmente já estavam na lista).")


    def remover_pdf_da_lista(self, filepath_to_remove):
        """Removes a specific PDF file from the list."""
        if filepath_to_remove in self.pdf_list:
            filename = os.path.basename(filepath_to_remove)
            self.pdf_list.remove(filepath_to_remove)
            self._atualizar_display_pdfs()
            self._atualizar_status(f"'{filename}' removido da lista.")
        if not self.pdf_list:
            self._atualizar_status("Lista de PDFs está vazia.")


    def limpar_lista_pdfs(self):
        """Clears all selected PDF files from the list after confirmation."""
        if not self.pdf_list:
            messagebox.showinfo("Informação", "A lista de PDFs já está vazia.")
            return
        
        confirmed = messagebox.askyesno("Confirmar Limpeza", "Tem certeza que deseja remover todos os PDFs da lista?")
        if confirmed:
            self.pdf_list = []
            self.output_path = "" # Também limpar o caminho de saída se a lista for limpa
            self.output_entry.delete(0, "end")
            self._atualizar_display_pdfs()
            self._atualizar_status("Lista de PDFs e nome de saída foram limpos.")

    def browse_output_file(self):
        """Opens a 'Save As' dialog to choose the output file name and location."""
        suggested_name = "documento_unificado.pdf"
        if self.pdf_list: # Sugere um nome baseado no primeiro arquivo da lista
            try:
                base_name = os.path.splitext(os.path.basename(self.pdf_list[0]))[0]
                suggested_name = f"{base_name}_unificado.pdf"
            except IndexError: # Caso a lista seja limpa entre o if e o try
                pass
        
        current_entry_val = self.output_entry.get().strip()
        if current_entry_val and current_entry_val.lower().endswith(".pdf"):
            initial_dir = os.path.dirname(current_entry_val)
            initial_file = os.path.basename(current_entry_val)
        elif current_entry_val: # Se não for um pdf, mas houver texto, use como nome inicial
            initial_dir = os.getcwd()
            initial_file = current_entry_val if not current_entry_val.lower().endswith(".pdf") else suggested_name
            if not initial_file.lower().endswith(".pdf"): initial_file += ".pdf"
        else:
            initial_dir = os.getcwd()
            initial_file = suggested_name


        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")],
            title="Salvar arquivo PDF unificado como...",
            initialdir=initial_dir,
            initialfile=initial_file
        )
        if path:
            self.output_path = path # Armazena o caminho completo
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, self.output_path) 
            self._atualizar_status(f"Arquivo de saída será salvo como: {os.path.basename(self.output_path)}")


    def _set_buttons_state(self, state):
        """Enable or disable main action buttons."""
        self.select_button.configure(state=state)
        self.clear_button.configure(state=state)
        self.browse_output_button.configure(state=state)
        self.merge_button.configure(state=state)
        # Os botões de remover da lista são gerenciados por _atualizar_display_pdfs


    def executar_mesclagem(self):
        """Handles the PDF merging process."""
        if not self.pdf_list:
            messagebox.showwarning("Aviso", "Nenhum arquivo PDF selecionado para unir.")
            self._atualizar_status("Falha: Nenhum PDF selecionado.")
            return

        # Prioriza o output_path (definido pelo "Salvar Como...")
        # Se não, usa o que estiver no output_entry.
        final_output_name = self.output_path if self.output_path else self.output_entry.get().strip()

        if not final_output_name:
            messagebox.showwarning("Aviso", "Por favor, especifique um nome e local para o arquivo de saída.")
            self._atualizar_status("Falha: Especifique o arquivo de saída.")
            self.browse_output_file() # Tenta ajudar o usuário
            final_output_name = self.output_path if self.output_path else self.output_entry.get().strip()
            if not final_output_name: # Se ainda não escolheu
                 return
        
        if not final_output_name.lower().endswith('.pdf'):
            final_output_name += '.pdf'
        
        # Se final_output_name não é um caminho absoluto (usuário só digitou nome.pdf)
        # e self.output_path não foi setado (não usou "Salvar Como"),
        # então salva no diretório do script ou no diretório atual.
        if not os.path.isabs(final_output_name) and not self.output_path:
            # Tenta salvar no diretório do primeiro PDF da lista, se houver
            # Senão, no diretório atual de trabalho.
            base_dir = os.path.dirname(self.pdf_list[0]) if self.pdf_list and os.path.dirname(self.pdf_list[0]) else os.getcwd()
            final_output_name = os.path.join(base_dir, os.path.basename(final_output_name)) # Garante que usa só o nome do arquivo
            
            # Atualiza a entrada para refletir o caminho completo
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, final_output_name)
            self.output_path = final_output_name # Garante que self.output_path está atualizado

        self._set_buttons_state("disabled")
        self._atualizar_status("Unindo PDFs... Por favor, aguarde.")

        # Executa a mesclagem em si
        success = mesclar_pdfs(self.pdf_list, final_output_name, self._atualizar_status)

        if success:
            # Opcional: limpar a lista e o nome de saída após mesclagem bem-sucedida
            # self.pdf_list = []
            # self.output_path = ""
            # self.output_entry.delete(0, "end")
            # self._atualizar_display_pdfs()
            # self._atualizar_status("Pronto. PDFs unidos com sucesso!")
            # A mensagem de sucesso já é dada por mesclar_pdfs e pelo status_callback
            pass
        else:
            # A mensagem de erro já foi dada por mesclar_pdfs e pelo status_callback
            # Se mesclar_pdfs retornou False mas não deu uma mensagem específica (ex: 0 arquivos)
            if not self.pdf_list: # Se a lista estava vazia e tentou mesclar
                 self._atualizar_status("Operação cancelada: Nenhum PDF para unir.")
            else:
                 self._atualizar_status("Falha ao unir os PDFs. Verifique as mensagens de erro.")


        self._set_buttons_state("normal")
        # Habilita/desabilita merge e clear button com base na lista
        self._atualizar_display_pdfs()


if __name__ == "__main__":
    app = PDFMergerApp()
    app.mainloop()
