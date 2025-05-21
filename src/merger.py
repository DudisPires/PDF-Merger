import os
import PyPDF2

def validar_pdf(caminho):
    return os.path.isfile(caminho) and caminho.lower().endswith('.pdf')

def mesclar_pdfs(lista_arquivos, nome_saida):
    merger = PyPDF2.PdfMerger()

    for arquivo in lista_arquivos:
        if validar_pdf(arquivo):
            try:
                merger.append(arquivo)
                print(f"✅ Adicionado: {arquivo}")
            except Exception as e:
                print(f"❌ Erro ao adicionar '{arquivo}': {e}")
        else:
            print(f"⚠️ Arquivo inválido ou não encontrado: {arquivo}")
    
    try:
        merger.write(nome_saida)
        merger.close()
        print(f"\n📄 Arquivo final salvo como: {nome_saida}")
    except Exception as e:
        print(f"❌ Erro ao salvar o arquivo final: {e}")

def obter_pdfs_diretorio_arquivos():
    diretorio = os.path.join('src', 'arquivos')
    if not os.path.exists(diretorio):
        print(f"❌ Diretório '{diretorio}' não existe.")
        return []
    arquivos = os.listdir(diretorio)
    pdfs = [os.path.join(diretorio, arquivo) for arquivo in arquivos if arquivo.lower().endswith('.pdf') and os.path.isfile(os.path.join(diretorio, arquivo))]
    return pdfs

def menu():
    print("=== PDF Merger ===\n")
    print("Escolha uma opção:")
    print("1. Informar manualmente os arquivos PDF")
    print("2. Detectar e mesclar todos os PDFs da pasta 'src/arquivos'")
    print("0. Sair\n")

    opcao = input("Opção: ").strip()
    return opcao

def main():
    while True:
        opcao = menu()

        if opcao == "1":
            caminhos = input("\nDigite os caminhos dos arquivos PDF separados por vírgula:\n")
            lista = [c.strip() for c in caminhos.split(',') if c.strip()]
        elif opcao == "2":
            lista = obter_pdfs_diretorio_arquivos()
            print("\n📂 PDFs encontrados na pasta 'src/arquivos':")
            for pdf in lista:
                print(" -", pdf)
            if not lista:
                print("❌ Nenhum PDF encontrado na pasta 'src/arquivos'.")
                continue
        elif opcao == "0":
            print("Encerrando o programa.")
            break
        else:
            print("❌ Opção inválida.\n")
            continue

        nome_saida = input("\nDigite o nome do arquivo final (ex: resultado.pdf): ").strip()
        if not nome_saida.lower().endswith('.pdf'):
            nome_saida += '.pdf'

        mesclar_pdfs(lista, nome_saida)
        print("\n--- Operação concluída ---\n")

if __name__ == "__main__":
    main()
