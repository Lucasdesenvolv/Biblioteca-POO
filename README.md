Projeto POO - Sistema de Biblioteca

Descrição do Projeto

Este projeto implementa um sistema de gerenciamento de biblioteca utilizando Programação Orientada a Objetos (POO) e interface gráfica com tkinter. O sistema permite o gerenciamento de livros, usuários e empréstimos, com persistência de dados em um arquivo JSON.

Funcionalidades

O sistema oferece as seguintes funcionalidades principais:
Login de Administrador: Acesso restrito ao sistema através de um login de administrador (usuário e senha configuráveis para teste).
Gerenciamento de Livros:

Cadastro de novos livros com título, autor e ano.
Listagem de todos os livros com seus respectivos IDs, títulos, autores, anos e status (Disponível/Emprestado).
Exclusão de livros (apenas se não estiverem emprestados).

Gerenciamento de Usuários:
Cadastro de novos usuários.
Listagem de usuários cadastrados.
Exclusão de usuários (apenas se não possuírem livros emprestados).

Gerenciamento de Empréstimos:
Empréstimo de livros para usuários cadastrados.
Devolução de livros.
Visualização do histórico de empréstimos e devoluções.
Persistência de Dados: Todos os dados (livros, usuários, empréstimos) são salvos e carregados de um arquivo JSON (biblioteca_dados.json).

Estrutura de Arquivos

A estrutura do projeto é a seguinte:
Projeto POO/
├── biblioteca_dados.json
└── codigofonte.py

codigofonte.py: Contém todo o código-fonte da aplicação, incluindo as classes LoginAdmin, BibliotecaModelo e BibliotecaApp.
biblioteca_dados.json: Arquivo JSON utilizado para armazenar os dados da biblioteca (livros, usuários, empréstimos).

Tecnologias Utilizadas:
Python 3: Linguagem de programação principal.
tkinter: Biblioteca padrão do Python para criação de interfaces gráficas de usuário (GUI).
json: Módulo para manipulação de dados em formato JSON, utilizado para persistência.
uuid: Módulo para geração de IDs únicos para livros e usuários.
datetime: Módulo para manipulação de datas e horas.

Como Executar
1.
Certifique-se de ter o Python 3 instalado em seu sistema.
2.
Navegue até o diretório Projeto POO/.
3.
Execute o script principal:
4.
Uma janela de login será exibida. As credenciais de teste são usuário: admin e senha: 123.
5.
Após o login, a interface principal do sistema de biblioteca será carregada, permitindo interagir com as funcionalidades.

