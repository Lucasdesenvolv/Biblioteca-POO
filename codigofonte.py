import tkinter as tk
from tkinter import ttk, messagebox
from uuid import uuid4
from datetime import datetime
import json
import os

DATA_FILE = "biblioteca_dados.json"

class LoginAdmin(tk.Tk):
    def __init__(self, usuario="admin", senha="123"):
        super().__init__()
        self.usuario_correto = usuario
        self.senha_correta = senha

        self.title("Login do Administrador")
        self.geometry("300x200")
        self.resizable(False, False)

        ttk.Label(self, text=f"(Teste: Usuário='{usuario}' | Senha='{senha}')", foreground="blue").pack(pady=5)

        ttk.Label(self, text="Usuário:").pack(pady=5)
        self.entrada_usuario = ttk.Entry(self)
        self.entrada_usuario.pack(pady=5)

        ttk.Label(self, text="Senha:").pack(pady=5)
        self.entrada_senha = ttk.Entry(self, show="*")
        self.entrada_senha.pack(pady=5)

        ttk.Button(self, text="Entrar", command=self.verificar_login).pack(pady=10)


    def verificar_login(self):
        usuario = self.entrada_usuario.get()
        senha = self.entrada_senha.get()

        if usuario == self.usuario_correto and senha == self.senha_correta:
            self.destroy()
            self.resultado = True
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")
            self.resultado = False


class BibliotecaModelo:
    def __init__(self):
        self.livros = {}
        self.usuarios = {}
        self.emprestimos = []
        self._carregar_dados()

    def _carregar_dados(self):

        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    dados = json.load(f)
                    self.livros = dados.get("livros", {})
                    self.usuarios = dados.get("usuarios", {})
                    self.emprestimos = dados.get("emprestimos", [])
            except Exception as e:
                print(f"Erro ao carregar dados: {e}. Iniciando vazio.")
        
        if not self.livros:
            self.cadastrar_livro("1984", "George Orwell", "1949")
        if not self.usuarios:
            self.cadastrar_usuario("Maria Silva")
            self.cadastrar_usuario("João Alves")

    def _salvar_dados(self):

        dados = {
            "livros": self.livros,
            "usuarios": self.usuarios,
            "emprestimos": self.emprestimos
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(dados, f, indent=4)

    def cadastrar_livro(self, titulo, autor, ano):
   
        if not autor.replace(" ", "").isalpha():
            raise ValueError("O campo 'Autor' deve conter apenas letras.")

        if not titulo.strip():
            raise ValueError("O campo 'Título' não pode estar vazio.")

        for livro in self.livros.values():
            if (livro["titulo"].lower() == titulo.lower() and 
                livro["autor"].lower() == autor.lower() and 
                livro["ano"] == ano):
                raise ValueError("Um livro com este Título, Autor e Ano já está cadastrado.")

        id_livro = str(uuid4())[:8]
        self.livros[id_livro] = {
            "id": id_livro,
            "titulo": titulo.strip(),
            "autor": autor.strip(),
            "ano": ano,
            "status": "Disponível"
        }
        self._salvar_dados()
        return id_livro


    def listar_livros(self):
        return list(self.livros.values())
    
    def buscar_livro_por_id(self, id_livro):
        return self.livros.get(id_livro)

    def cadastrar_usuario(self, nome):
        nome_limpo = nome.strip()
        
        if not nome_limpo:
            raise ValueError("O nome do usuário não pode estar vazio.")

        id_usuario = str(uuid4())[:8]
        self.usuarios[id_usuario] = {
            "id": id_usuario,
            "nome": nome_limpo
        }
        self._salvar_dados()
        return id_usuario

    def listar_usuarios(self):
        return list(self.usuarios.values())

    def emprestar_livro(self, id_livro, id_usuario):
        livro = self.livros.get(id_livro)
        usuario = self.usuarios.get(id_usuario)

        if not livro:
            raise ValueError("Livro não encontrado.")
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        if livro["status"] != "Disponível":
            raise ValueError("Livro já emprestado.")
        
        livro["status"] = "Emprestado"
        livro["emprestado_para"] = id_usuario 

        registro = {
            "livro": livro["titulo"],
            "usuario": usuario["nome"],
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "acao": "empréstimo"
        }
        self.emprestimos.append(registro)
        self._salvar_dados()


    def devolver_livro(self, id_livro, id_usuario):
        livro = self.livros.get(id_livro)
        usuario = self.usuarios.get(id_usuario)

        if not livro:
            raise ValueError("Livro não encontrado.")
        if not usuario:
            raise ValueError("Usuário não encontrado.") 
        if livro["status"] != "Emprestado":
            raise ValueError("Livro não está emprestado.")

        if livro.get("emprestado_para") != id_usuario:
            raise ValueError("Apenas o usuário que pegou o livro emprestado pode devolvê-lo.")

        livro["status"] = "Disponível"
        livro["emprestado_para"] = None 

        registro = {
            "livro": livro["titulo"],
            "usuario": usuario["nome"],
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "acao": "devolução"
        }
        self.emprestimos.append(registro)
        self._salvar_dados()


    def listar_emprestimos(self):
        return self.emprestimos
    
    def excluir_livro(self, id_livro):
        livro = self.livros.get(id_livro)
        if not livro:
            raise ValueError("Livro não encontrado.")
        if livro["status"] == "Emprestado":
            raise ValueError("Não é possível excluir um livro que está emprestado.")
        
        del self.livros[id_livro]
        self._salvar_dados()

    def excluir_usuario(self, id_usuario):
        usuario = self.usuarios.get(id_usuario)
        if not usuario:
            raise ValueError("Usuário não encontrado.")

        for livro in self.livros.values():
            if livro["status"] == "Emprestado":
                for emprestimo in reversed(self.emprestimos):
                    if emprestimo["livro"] == livro["titulo"] and emprestimo["usuario"] == usuario["nome"] and emprestimo["acao"] == "empréstimo":
                        raise ValueError("Usuário possui livro emprestado, não pode ser excluído.")

        del self.usuarios[id_usuario]
        self._salvar_dados()


class BibliotecaApp(tk.Tk):
    def __init__(self, modelo):
        super().__init__()
        self.title("Sistema de Biblioteca - Fase 1 (Completo)")
        self.geometry("1000x600")
        self.modelo = modelo
        self.filtro_var = tk.StringVar()
        self._construir_interface()
        
        self.filtro_var.trace_add("write", lambda *args: self.atualizar_tabela())
        self.tabela.bind("<<TreeviewSelect>>", self._on_tabela_select)
        
        self.atualizar_tabela()

    def _construir_interface(self):
        self.tabela_style = ttk.Style()
        self.tabela_style.configure("Treeview", rowheight=25)

        quadro_principal = ttk.Frame(self)
        quadro_principal.pack(fill="both", expand=True, padx=10, pady=6)

        lado_esquerdo = ttk.LabelFrame(quadro_principal, text="Ações")
        lado_esquerdo.pack(side="left", fill="y", padx=6, pady=6)
        ttk.Separator(lado_esquerdo, orient='horizontal').pack(fill='x', padx=10)
        
        


        ttk.Button(lado_esquerdo, text="Cadastrar Livro", width=25, command=self._abrir_cadastro_livro).pack(pady=6, padx=10)
        ttk.Button(lado_esquerdo, text="Excluir Livro (Selecionado)", width=25, command=self._excluir_livro).pack(pady=6, padx=10)
        ttk.Separator(lado_esquerdo, orient='horizontal').pack(fill='x', padx=10)
        ttk.Button(lado_esquerdo, text="Cadastrar Usuário", width=25, command=self._abrir_cadastro_usuario).pack(pady=6, padx=10)
        ttk.Button(lado_esquerdo, text="Excluir Usuário", width=25, command=self._excluir_usuario).pack(pady=6, padx=10)
        ttk.Button(lado_esquerdo, text="Visualizar Usuários", width=25, command=self._mostrar_usuarios).pack(pady=6, padx=10)
        ttk.Separator(lado_esquerdo, orient='horizontal').pack(fill='x', padx=10)
        ttk.Button(lado_esquerdo, text="Emprestar Livro (Selecionado)", width=25, command=self._abrir_emprestimo).pack(pady=6, padx=10)
        ttk.Button(lado_esquerdo, text="Devolver Livro (Selecionado)", width=25, command=self._abrir_devolucao).pack(pady=6, padx=10)
        ttk.Separator(lado_esquerdo, orient='horizontal').pack(fill='x', padx=10)
        ttk.Button(lado_esquerdo, text="Histórico de Empréstimos", width=25, command=self._mostrar_historico).pack(pady=6, padx=10)

        lado_direito = ttk.Frame(quadro_principal)
        lado_direito.pack(side="right", fill="both", expand=True)

        quadro_busca = ttk.LabelFrame(lado_direito, text="Busca Rápida por Título ou Autor")
        quadro_busca.pack(fill="x", pady=(0, 5))
        ttk.Entry(quadro_busca, textvariable=self.filtro_var, width=50).pack(padx=5, pady=5, fill='x')

        colunas = ("id", "titulo", "autor", "ano", "status")
        self.tabela = ttk.Treeview(lado_direito, columns=colunas, show="headings", style="Treeview")
        
        self.tabela.column("id", width=80, anchor="center")
        self.tabela.column("titulo", width=250, anchor="w")
        self.tabela.column("autor", width=180, anchor="w")
        self.tabela.column("ano", width=60, anchor="center")
        self.tabela.column("status", width=100, anchor="center")

        self.tabela.heading("id", text="ID")
        self.tabela.heading("titulo", text="Título")
        self.tabela.heading("autor", text="Autor")
        self.tabela.heading("ano", text="Ano")
        self.tabela.heading("status", text="Status")
        
        self.tabela.pack(fill="both", expand=True)

        self.tabela.tag_configure("Disponível", background="#d4edda", foreground="#155724")
        self.tabela.tag_configure("Emprestado", background="#f8d7da", foreground="#721c24")

    def atualizar_tabela(self):
        for i in self.tabela.get_children():
            self.tabela.delete(i)
            
        termo_busca = self.filtro_var.get().strip().lower()
        
        livros_filtrados = self.modelo.listar_livros()
        
        if termo_busca:
            livros_filtrados = [
                livro for livro in livros_filtrados
                if termo_busca in livro["titulo"].lower() or termo_busca in livro["autor"].lower()
            ]

        for livro in livros_filtrados:
            status = livro["status"]
            tag_status = status.replace(" ", "")
            
            self.tabela.insert(
                "", 
                "end", 
                values=(livro["id"], livro["titulo"], livro["autor"], livro["ano"], status),
                tags=(tag_status,)
            )

    def _on_tabela_select(self, event):
        pass

    
    def _livro_selecionado(self):
        sel = self.tabela.selection()
        if not sel:
            return None
        
        valores = self.tabela.item(sel[0])['values']
        if not valores:
            return None
            
        id_livro = valores[0]
        return self.modelo.buscar_livro_por_id(id_livro) 

    def _abrir_cadastro_livro(self):
        janela = tk.Toplevel(self)
        janela.title("Cadastrar Livro")
        janela.transient(self)

        ttk.Label(janela, text="Título:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entrada_titulo = ttk.Entry(janela, width=40)
        entrada_titulo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(janela, text="Autor:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entrada_autor = ttk.Entry(janela, width=40)
        entrada_autor.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(janela, text="Ano:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        entrada_ano = ttk.Entry(janela, width=10)
        entrada_ano.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        def salvar():
            titulo = entrada_titulo.get().strip()
            autor = entrada_autor.get().strip()
            ano_str = entrada_ano.get().strip()

            if not titulo or not autor or not ano_str:
                messagebox.showerror("Erro de Validação", "Preencha todos os campos obrigatórios.")
                return
            
            try:
                ano = int(ano_str)
                ano_atual = datetime.now().year
                if ano < 1500 or ano > ano_atual:
                    messagebox.showerror("Erro de Validação", f"Ano inválido. Digite um ano entre 1500 e {ano_atual}.")
                    return
            except ValueError:
                messagebox.showerror("Erro de Validação", "O campo 'Ano' deve conter apenas números inteiros.")
                return

            try:
                self.modelo.cadastrar_livro(titulo, autor, str(ano))
                messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!")
                self.atualizar_tabela()
                janela.destroy()
            except ValueError as e:
                messagebox.showerror("Erro de Cadastro", str(e))


        ttk.Button(janela, text="Salvar Livro", command=salvar).grid(row=3, column=0, columnspan=2, pady=15)

    def _abrir_cadastro_usuario(self):
        janela = tk.Toplevel(self)
        janela.title("Cadastrar Usuário")
        janela.transient(self)

        ttk.Label(janela, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entrada_nome = ttk.Entry(janela, width=30)
        entrada_nome.grid(row=0, column=1, padx=5, pady=5)

        def salvar():
            nome = entrada_nome.get().strip()
            
            if not nome:
                 messagebox.showerror("Erro", "Preencha o nome do usuário.")
                 return
                 
            try:
                id_novo = self.modelo.cadastrar_usuario(nome)
                messagebox.showinfo("Sucesso", f"Usuário cadastrado!\nID: {id_novo}")
                janela.destroy()
            except ValueError as e:
                messagebox.showerror("Erro de Cadastro", str(e))

        ttk.Button(janela, text="Salvar Usuário", command=salvar).grid(row=1, column=0, columnspan=2, pady=10)

    def _abrir_emprestimo(self):
        livro = self._livro_selecionado()
        if not livro:
            messagebox.showwarning("Aviso", "Selecione um livro na tabela para emprestar.")
            return
        
        if livro["status"] != "Disponível":
            messagebox.showwarning("Aviso", f"O livro '{livro['titulo']}' já está emprestado.")
            return

        janela = tk.Toplevel(self)
        janela.title("Emprestar Livro")
        janela.transient(self)

        ttk.Label(janela, text=f"Livro Selecionado:").pack(padx=6, pady=(10, 0))
        ttk.Label(janela, text=f"'{livro['titulo']}' ({livro['id']})", font=("", 10, "bold")).pack(padx=6, pady=(0, 10))
        
        ttk.Label(janela, text="Selecione o Usuário:").pack(padx=6, pady=(5, 0))
        
        usuarios = self.modelo.listar_usuarios()
        nome_para_id = {u["nome"]: u["id"] for u in usuarios}
        nomes_usuarios = sorted(list(nome_para_id.keys()))

        combo_usuario = ttk.Combobox(janela, values=nomes_usuarios, state="readonly", width=40)
        combo_usuario.pack(padx=6, pady=(0, 10))

        def confirmar():
            nome_selecionado = combo_usuario.get()
            if not nome_selecionado or nome_selecionado not in nome_para_id:
                messagebox.showerror("Erro", "Selecione um usuário válido.")
                return
            
            id_usuario = nome_para_id[nome_selecionado]
            
            try:
                self.modelo.emprestar_livro(livro["id"], id_usuario)
                messagebox.showinfo("Sucesso", f"Livro '{livro['titulo']}' emprestado para {nome_selecionado}!")
                self.atualizar_tabela()
                janela.destroy()
            except ValueError as erro:
                messagebox.showerror("Erro", str(erro))
            except Exception as erro:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {erro}")

        ttk.Button(janela, text="Confirmar Empréstimo", command=confirmar).pack(pady=10)

    def _abrir_devolucao(self):
        livro = self._livro_selecionado()
        if not livro:
            messagebox.showwarning("Aviso", "Selecione um livro na tabela para devolver.")
            return
        
        if livro["status"] != "Emprestado":
            messagebox.showwarning("Aviso", f"O livro '{livro['titulo']}' não está emprestado no momento.")
            return
            
        janela = tk.Toplevel(self)
        janela.title("Devolver Livro")
        janela.transient(self)

        ttk.Label(janela, text=f"Livro Selecionado:").pack(padx=6, pady=(10, 0))
        ttk.Label(janela, text=f"'{livro['titulo']}' ({livro['id']})", font=("", 10, "bold")).pack(padx=6, pady=(0, 10))

        ttk.Label(janela, text="Selecione o Usuário que está devolvendo:").pack(padx=6, pady=(5, 0))
        
        usuarios = self.modelo.listar_usuarios()
        nome_para_id = {u["nome"]: u["id"] for u in usuarios}
        nomes_usuarios = sorted(list(nome_para_id.keys()))

        combo_usuario = ttk.Combobox(janela, values=nomes_usuarios, state="readonly", width=40)
        combo_usuario.pack(padx=6, pady=(0, 10))

        def confirmar():
            nome_selecionado = combo_usuario.get()
            if not nome_selecionado or nome_selecionado not in nome_para_id:
                messagebox.showerror("Erro", "Selecione um usuário válido.")
                return
            
            id_usuario = nome_para_id[nome_selecionado]
            
            try:
                self.modelo.devolver_livro(livro["id"], id_usuario)
                messagebox.showinfo("Sucesso", f"Livro '{livro['titulo']}' devolvido com sucesso!")
                self.atualizar_tabela()
                janela.destroy()
            except ValueError as erro:
                messagebox.showerror("Erro", str(erro))
            except Exception as erro:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {erro}")

        ttk.Button(janela, text="Confirmar Devolução", command=confirmar).pack(pady=10)

    def _mostrar_historico(self):
        historico = self.modelo.listar_emprestimos()
        
        janela = tk.Toplevel(self)
        janela.title("Histórico de Empréstimos")
        janela.transient(self)
        
        colunas = ("data", "usuario", "acao", "livro")
        tabela_hist = ttk.Treeview(janela, columns=colunas, show="headings")
        tabela_hist.heading("data", text="Data/Hora")
        tabela_hist.heading("usuario", text="Usuário")
        tabela_hist.heading("acao", text="Ação")
        tabela_hist.heading("livro", text="Livro")
        
        tabela_hist.column("data", width=150, anchor="center")
        tabela_hist.column("usuario", width=150, anchor="w")
        tabela_hist.column("acao", width=100, anchor="center")
        tabela_hist.column("livro", width=250, anchor="w")
        
        if not historico:
            tabela_hist.insert("", "end", values=("", "Nenhum registro encontrado.", "", ""))
        else:
            for reg in historico:
                tabela_hist.insert("", "end", values=(
                    reg['data'], reg['usuario'], reg['acao'].capitalize(), reg['livro']
                ))

        tabela_hist.pack(fill="both", expand=True, padx=10, pady=10)

    def _mostrar_usuarios(self):
        usuarios = self.modelo.listar_usuarios()
        
        janela = tk.Toplevel(self)
        janela.title("Lista de Usuários Cadastrados")
        janela.transient(self)
        
        colunas = ("id", "nome")
        tabela_usr = ttk.Treeview(janela, columns=colunas, show="headings")
        tabela_usr.heading("id", text="ID Usuário")
        tabela_usr.heading("nome", text="Nome Completo")
        
        tabela_usr.column("id", width=100, anchor="center")
        tabela_usr.column("nome", width=300, anchor="w")
        
        for usr in usuarios:
            tabela_usr.insert("", "end", values=(usr['id'], usr['nome']))

        tabela_usr.pack(fill="both", expand=True, padx=10, pady=10)

    def _excluir_livro(self):
        livro = self._livro_selecionado()
        if not livro:
            messagebox.showwarning("Aviso", "Selecione um livro na tabela para excluir.")
            return

        confirmar = messagebox.askyesno("Confirmação", f"Deseja realmente excluir o livro '{livro['titulo']}'?")
        if not confirmar:
            return

        try:
            self.modelo.excluir_livro(livro["id"])
            messagebox.showinfo("Sucesso", f"Livro '{livro['titulo']}' excluído com sucesso.")
            self.atualizar_tabela()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def _excluir_usuario(self):
        usuarios = self.modelo.listar_usuarios()
        if not usuarios:
            messagebox.showinfo("Aviso", "Não há usuários cadastrados para excluir.")
            return

        janela = tk.Toplevel(self)
        janela.title("Excluir Usuário")
        janela.transient(self)

        ttk.Label(janela, text="Selecione o usuário para excluir:").pack(padx=10, pady=10)

        nome_para_id = {u["nome"]: u["id"] for u in usuarios}
        nomes_usuarios = sorted(list(nome_para_id.keys()))

        combo_usuario = ttk.Combobox(janela, values=nomes_usuarios, state="readonly", width=40)
        combo_usuario.pack(padx=10, pady=10)

        def confirmar():
            nome_selecionado = combo_usuario.get()
            if not nome_selecionado:
                messagebox.showerror("Erro", "Selecione um usuário.")
                return

            confirmar_exclusao = messagebox.askyesno("Confirmação", f"Deseja realmente excluir o usuário '{nome_selecionado}'?")
            if not confirmar_exclusao:
                return

            try:
                self.modelo.excluir_usuario(nome_para_id[nome_selecionado])
                messagebox.showinfo("Sucesso", f"Usuário '{nome_selecionado}' excluído com sucesso.")
                janela.destroy()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        ttk.Button(janela, text="Excluir Usuário", command=confirmar).pack(pady=10)



if __name__ == "__main__":
    login = LoginAdmin()
    login.mainloop()
    
    if hasattr(login, "resultado") and login.resultado:
        modelo = BibliotecaModelo()
        app = BibliotecaApp(modelo)
        app.mainloop()

