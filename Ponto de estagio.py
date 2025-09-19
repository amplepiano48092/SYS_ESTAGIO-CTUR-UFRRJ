import customtkinter as ctk
from central_horas import CentralHorasEstagio
central_horas = CentralHorasEstagio()
from datetime import datetime

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme("blue")

APP = ctk.CTk()
APP.title('Ponto Estágio')
APP.geometry('500x600')

# Função para o botão Enviar
def enviar_dados():
    nome = Nome.get()
    entrada = HORARIO_ENTRADA.get()
    saida = HORARIO_Saida.get()
    
    try:
        registro = central_horas.registrar_horas(nome, entrada, saida)
        # Limpa os campos após o envio
        Nome.delete(0, 'end')
        HORARIO_ENTRADA.delete(0, 'end')
        HORARIO_Saida.delete(0, 'end')
        
        # Mostra mensagem de sucesso
        resultado.configure(text=f"Registro salvo: {entrada}-{saida} ({registro['horas']}h)", text_color="green")
        
        # Exibe no console também
        print(f"Registro salvo para {nome}: {registro}")
        
    except ValueError as e:
        resultado.configure(text=f"Erro: {str(e)}", text_color="red")
        print(f"Erro: {str(e)}")

# Função para mostrar o ranking Mensal
def mostrar_ranking():
    relatorio = central_horas.gerar_relatorio_mensal()
    
    # Ordena os usuários pelo total de minutos (maior primeiro)
    usuarios_ordenados = sorted(
        [(usuario, dados['minutos'], dados['horas']) for usuario, dados in relatorio['usuarios'].items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    janela_ranking = ctk.CTkToplevel(APP)
    janela_ranking.title("Ranking Mensal")
    janela_ranking.geometry("500x400")  # Aumentei o tamanho para acomodar mais informações
    
    # Frame para organização
    frame = ctk.CTkFrame(janela_ranking)
    frame.pack(pady=20, padx=20, fill="both", expand=True)
    
    # Título
    ctk.CTkLabel(frame, 
                text="🏆 Ranking de Horas Trabalhadas 🏆", 
                font=("Times New Roman", 16, "bold")).pack(pady=(0, 10))
    
    # Cabeçalho da tabela
    cabecalho = ctk.CTkFrame(frame)
    cabecalho.pack(fill="x", pady=5)
    
    ctk.CTkLabel(cabecalho, text="Posição", width=50, anchor="w", font=("Times New Roman", 12, "bold")).pack(side="left")
    ctk.CTkLabel(cabecalho, text="Nome", width=150, anchor="w", font=("Times New Roman", 12, "bold")).pack(side="left")
    ctk.CTkLabel(cabecalho, text="Horas", width=80, anchor="center", font=("Times New Roman", 12, "bold")).pack(side="left")
    ctk.CTkLabel(cabecalho, text="Minutos", width=80, anchor="center", font=("Times New Roman", 12, "bold")).pack(side="left")
    
    # Lista de usuários
    for i, (usuario, minutos, horas) in enumerate(usuarios_ordenados, 1):
        # Frame para cada linha do ranking
        linha = ctk.CTkFrame(frame)
        linha.pack(fill="x", pady=2)
        
        ctk.CTkLabel(linha, text=f"{i}º", width=50, anchor="w").pack(side="left")
        ctk.CTkLabel(linha, text=usuario, width=150, anchor="w").pack(side="left")
        ctk.CTkLabel(linha, text=f"{horas:.2f}h", width=80, anchor="center").pack(side="left")
        ctk.CTkLabel(linha, text=f"{minutos}m", width=80, anchor="center").pack(side="left")
    
    # Rodapé com totais
    rodape = ctk.CTkFrame(frame)
    rodape.pack(fill="x", pady=(10, 0))
    
    ctk.CTkLabel(rodape, text="Total Geral:", width=200, anchor="e", font=("Times New Roman", 12, "bold")).pack(side="left")
    ctk.CTkLabel(rodape, text=f"{relatorio['total_horas']:.2f}h", width=80, anchor="center", font=("Times New Roman", 12, "bold")).pack(side="left")
    ctk.CTkLabel(rodape, text=f"{relatorio['total_minutos']}m", width=80, anchor="center", font=("Times New Roman", 12, "bold")).pack(side="left")
    
    # Botão de fechar
    ctk.CTkButton(janela_ranking, text="Fechar", command=janela_ranking.destroy, fg_color="#e74c3c").pack(pady=10)

def abrir_janela_registro_manual():
    janela = ctk.CTkToplevel(APP)
    janela.title("Adicionar Horas Passadas")
    janela.geometry("400x550")
    
    frame = ctk.CTkFrame(janela)
    frame.pack(pady=20, padx=20, fill="both", expand=True)
    
    mensagem_label = ctk.CTkLabel(frame, text="", font=("Times New Roman", 12))
    mensagem_label.pack(pady=10)
    
    # Campos do formulário
    campos = [
        ("Data (DD/MM/AAAA):", "Ex: 15/03/2023"),
        ("Nome:", "Márcio, Samuel, Caio ou Robson"),
        ("Horário Entrada (HH:MM):", "Ex: 08:30"),
        ("Horário Saída (HH:MM):", "Ex: 17:45"),
        ("Descrição (opcional):", "Atividades realizadas")
    ]
    
    entries = []
    for label, placeholder in campos:
        ctk.CTkLabel(frame, text=label, font=("Times New Roman", 12)).pack(pady=5)
        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, font=("Times New Roman", 12))
        entry.pack(pady=5)
        entries.append(entry)
    
    def submeter():
        try:
            registro = central_horas.adicionar_registro_manual(
                nome=entries[1].get(),
                data=entries[0].get(),
                entrada=entries[2].get(),
                saida=entries[3].get(),
                descricao=entries[4].get()
            )
            
            mensagem_label.configure(text="✅ Registro adicionado com sucesso!", text_color="green")
            
            # Limpa os campos
            for entry in entries:
                entry.delete(0, 'end')
                
        except Exception as e:
            mensagem_label.configure(text=f"❌ Erro: {str(e)}", text_color="red")
    
    ctk.CTkButton(frame, text="Adicionar Registro", command=submeter, fg_color="#3498db",font=("Times New Roman", 14)).pack(pady=15)

def abrir_janela_minutos_passados():
    janela = ctk.CTkToplevel(APP)
    janela.title("Adicionar Minutos Passados")
    janela.geometry("400x450")
    
    frame = ctk.CTkFrame(janela)
    frame.pack(pady=20, padx=20, fill="both", expand=True)
    
    mensagem = ctk.CTkLabel(frame, text="", font=("Times New Roman", 12))
    mensagem.pack(pady=10)
    
    # Campos
    ctk.CTkLabel(frame, text="Data (DD/MM/AAAA):").pack(pady=5)
    entrada_data = ctk.CTkEntry(frame, placeholder_text="Ex: 15/03/2023")
    entrada_data.pack(pady=5)
    
    ctk.CTkLabel(frame, text="Nome:").pack(pady=5)
    entrada_nome = ctk.CTkEntry(frame, placeholder_text="Márcio, Samuel, Caio ou Robson")
    entrada_nome.pack(pady=5)
    
    ctk.CTkLabel(frame, text="Minutos trabalhados:").pack(pady=5)
    entrada_minutos = ctk.CTkEntry(frame, placeholder_text="Ex: 480 (para 8 horas)")
    entrada_minutos.pack(pady=5)
    
    ctk.CTkLabel(frame, text="Descrição (opcional):").pack(pady=5)
    entrada_desc = ctk.CTkEntry(frame, placeholder_text="Atividades realizadas")
    entrada_desc.pack(pady=5)
    
    def submeter():
        try:
            central_horas.adicionar_minutos_passados(
                nome=entrada_nome.get(),
                data=entrada_data.get(),
                minutos=int(entrada_minutos.get()),
                descricao=entrada_desc.get()
            )
            mensagem.configure(text="✅ Minutos adicionados com sucesso!", text_color="green")
            # Limpa os campos
            entrada_data.delete(0, 'end')
            entrada_nome.delete(0, 'end')
            entrada_minutos.delete(0, 'end')
            entrada_desc.delete(0, 'end')
        except Exception as e:
            mensagem.configure(text=f"❌ Erro: {str(e)}", text_color="red")
    
    ctk.CTkButton(frame, text="Adicionar", command=submeter).pack(pady=15)

def mostrar_ranking_anual():
    # Cria uma janela de seleção de ano
    janela_ano = ctk.CTkToplevel(APP)
    janela_ano.title("Selecionar Ano")
    janela_ano.geometry("300x150")
    
    frame = ctk.CTkFrame(janela_ano)
    frame.pack(pady=20, padx=20, fill="both", expand=True)
    
    ctk.CTkLabel(frame, text="Selecione o ano:", font=("Times New Roman", 14)).pack(pady=5)
    
    # Pega o ano atual para usar como padrão
    ano_atual = datetime.now().year
    entrada_ano = ctk.CTkEntry(frame, placeholder_text=str(ano_atual))
    entrada_ano.pack(pady=10)
    
    def gerar_ranking():
        try:
            ano = int(entrada_ano.get() or ano_atual)
            janela_ano.destroy()
            exibir_ranking_anual(ano)
        except ValueError:
            ctk.CTkLabel(frame, text="Ano inválido!", text_color="red").pack()
    
    ctk.CTkButton(frame, text="Gerar Ranking", command=gerar_ranking).pack()

def exibir_ranking_anual(ano: int):
    relatorio = central_horas.gerar_relatorio_anual(ano)
    
    # Ordena usuários por minutos trabalhados
    usuarios_ordenados = sorted(
        [(usuario, dados['horas'], dados['minutos']) for usuario, dados in relatorio['usuarios'].items()],
        key=lambda x: x[2],  # Ordena por minutos
        reverse=True
    )
    
    janela_ranking = ctk.CTkToplevel(APP)
    janela_ranking.title(f"Ranking Anual - {ano}")
    janela_ranking.geometry("800x600")
    
    # Frame principal com scrollbar
    main_frame = ctk.CTkFrame(janela_ranking)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Canvas para scroll
    canvas = ctk.CTkCanvas(main_frame)
    scrollbar = ctk.CTkScrollbar(main_frame, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Título
    ctk.CTkLabel(scrollable_frame, 
                text=f"🏆 Ranking Anual {ano} 🏆", 
                font=("Times New Roman", 18, "bold")).pack(pady=(0, 15))
    
    # Resumo geral
    frame_resumo = ctk.CTkFrame(scrollable_frame)
    frame_resumo.pack(fill="x", pady=5, padx=10)
    
    ctk.CTkLabel(frame_resumo, 
                text=f"Total Geral: {relatorio['total_horas']:.2f}h | {relatorio['total_minutos']}m",
                font=("Times New Roman", 14, "bold")).pack()
    
    # Ranking principal
    frame_ranking = ctk.CTkFrame(scrollable_frame)
    frame_ranking.pack(fill="x", pady=10, padx=10)
    
    # Cabeçalho
    cabecalho = ctk.CTkFrame(frame_ranking)
    cabecalho.pack(fill="x", pady=5)
    
    ctk.CTkLabel(cabecalho, text="Pos", width=40, anchor="center", font=("Times New Roman", 12, "bold")).pack(side="left")
    ctk.CTkLabel(cabecalho, text="Nome", width=150, anchor="w", font=("Times New Roman", 12, "bold")).pack(side="left")
    ctk.CTkLabel(cabecalho, text="Horas", width=100, anchor="center", font=("Times New Roman", 12, "bold")).pack(side="left")
    ctk.CTkLabel(cabecalho, text="Minutos", width=100, anchor="center", font=("Times New Roman", 12, "bold")).pack(side="left")
    
    # Lista de usuários
    for i, (usuario, horas, minutos) in enumerate(usuarios_ordenados, 1):
        linha = ctk.CTkFrame(frame_ranking)
        linha.pack(fill="x", pady=2)
        
        ctk.CTkLabel(linha, text=f"{i}º", width=40, anchor="center").pack(side="left")
        ctk.CTkLabel(linha, text=usuario, width=150, anchor="w").pack(side="left")
        ctk.CTkLabel(linha, text=f"{horas:.2f}h", width=100, anchor="center").pack(side="left")
        ctk.CTkLabel(linha, text=f"{minutos}m", width=100, anchor="center").pack(side="left")
    
    # Detalhamento por mês para cada usuário
    for usuario in relatorio['usuarios']:
        frame_usuario = ctk.CTkFrame(scrollable_frame, border_width=1)
        frame_usuario.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(frame_usuario, 
                    text=f"Detalhes de {usuario}:",
                    font=("Times New Roman", 14)).pack(anchor="w", pady=5)
        
        # Cabeçalho meses
        cabecalho_meses = ctk.CTkFrame(frame_usuario)
        cabecalho_meses.pack(fill="x", pady=2)
        
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for mes_num, mes_nome in enumerate(meses, 1):
            if mes_num in relatorio['usuarios'][usuario]['meses']:
                dados = relatorio['usuarios'][usuario]['meses'][mes_num]
                frame_mes = ctk.CTkFrame(frame_usuario)
                frame_mes.pack(fill="x", pady=1)
                
                ctk.CTkLabel(frame_mes, text=mes_nome, width=40, anchor="w").pack(side="left")
                ctk.CTkLabel(frame_mes, text=f"{dados['horas']:.2f}h", width=80, anchor="center").pack(side="left")
                ctk.CTkLabel(frame_mes, text=f"{dados['minutos']}m", width=80, anchor="center").pack(side="left")
    
    # Botão de fechar
    ctk.CTkButton(janela_ranking, 
                 text="Fechar", 
                 command=janela_ranking.destroy,
                 fg_color="#e74c3c",
                 font=("Times New Roman", 12)).pack(pady=10)

# Adicione o botão na interface principal
BOTAO_MINUTOS = ctk.CTkButton(APP,text="Adicionar Minutos Passados",command=abrir_janela_minutos_passados,fg_color="#3498db")

# Adicione o botão na interface principal
BOTAO_REGISTRO_MANUAL = ctk.CTkButton(APP,text="Adicionar Horas Passadas",command=abrir_janela_registro_manual,fg_color="#3498db",font=("Times New Roman", 14))

# Elementos da interface principal
TITLE = ctk.CTkLabel(APP, text="Ponto de Estágio", font=("Times New Roman", 20))
Nome = ctk.CTkEntry(APP, placeholder_text='Nome', font=("Times New Roman", 14))
HORARIO_ENTRADA = ctk.CTkEntry(APP, placeholder_text='Horário de Entrada (HH:MM)', font=("Times New Roman", 14))
X = ctk.CTkLabel(APP, text='X', font=("Times New Roman", 14))
HORARIO_Saida = ctk.CTkEntry(APP, placeholder_text='Horário de Saída (HH:MM)', font=("Times New Roman", 14))
ENVIAR = ctk.CTkButton(APP, text='Registrar Ponto', font=("Times New Roman", 14), command=enviar_dados)
resultado = ctk.CTkLabel(APP, text="", font=("Times New Roman", 12))

# Botão para ver o ranking
BOTAO_RANKING = ctk.CTkButton(APP, text="Ver Ranking Mensal", font=("Times New Roman", 14),command=mostrar_ranking,fg_color="#3498db")

# Botão para ver o ranking anual
BOTAO_RANKING_ANUAL = ctk.CTkButton(APP, text="Ranking Anual", font=("Times New Roman", 14), command=mostrar_ranking_anual, fg_color="#3498db")


# Layout da interface principal
TITLE.pack(pady=15)
resultado.pack(pady=5)
Nome.pack(pady=15)
HORARIO_ENTRADA.pack(pady=5)
X.pack(pady=5)
HORARIO_Saida.pack(pady=5)
ENVIAR.pack(pady=15)
BOTAO_REGISTRO_MANUAL.pack(pady=10)
BOTAO_MINUTOS.pack(pady=10)
BOTAO_RANKING.pack(pady=10)
BOTAO_RANKING_ANUAL.pack(pady=10)


# Mantém a janela aberta
APP.mainloop()
