import json
import os
from datetime import datetime, timedelta

class CentralHorasEstagio:
    def __init__(self, arquivo_dados: str = "horas_estagio.json"):
        self.arquivo_dados = arquivo_dados
        self.usuarios = ["Márcio", "Samuel", "Caio", "Robson"]
        self.dados = self._inicializar_dados()
        self.carregar_dados()

    def _inicializar_dados(self):
        """Inicializa a estrutura de dados com os usuários padrão"""
        return {
            "usuarios": {user: {"registros": []} for user in self.usuarios},
            "ultima_atualizacao": None
        }

    def carregar_dados(self):
        """Carrega os dados do arquivo JSON se existir"""
        if os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                dados_carregados = json.load(f)
                
                # Garante que todos os usuários padrão existam
                for user in self.usuarios:
                    if user not in dados_carregados["usuarios"]:
                        dados_carregados["usuarios"][user] = {"registros": []}
                
                self.dados = dados_carregados

    def salvar_dados(self):
        """Salva os dados no arquivo JSON"""
        self.dados["ultima_atualizacao"] = datetime.now().isoformat()
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(self.dados, f, indent=4, ensure_ascii=False)

    def registrar_horas(self, nome: str, entrada: str, saida: str):
        """
        Registra as horas trabalhadas para um usuário (formato HH:MM)
        
        Args:
            nome (str): Nome do usuário
            entrada (str): Horário de entrada (HH:MM)
            saida (str): Horário de saída (HH:MM)
        """
        if nome not in self.dados["usuarios"]:
            raise ValueError(f"Usuário {nome} não encontrado")
        
        try:
            hora_entrada = datetime.strptime(entrada, "%H:%M")
            hora_saida = datetime.strptime(saida, "%H:%M")
            
            if hora_saida <= hora_entrada:
                raise ValueError("Horário de saída deve ser após o horário de entrada")
            
            minutos_trabalhados = int((hora_saida - hora_entrada).total_seconds() / 60)
            return self._registrar_minutos(nome, datetime.now().strftime("%d/%m/%Y"), minutos_trabalhados)
            
        except ValueError as e:
            raise ValueError(f"Formato de hora inválido. Use HH:MM - {str(e)}")

    def registrar_minutos(self, nome: str, data: str, minutos: int, descricao: str = ""):
        """
        Registra horas de estágio usando minutos totais do dia
        
        Args:
            nome (str): Nome do estagiário
            data (str): Data no formato DD/MM/AAAA
            minutos (int): Minutos trabalhados no dia
            descricao (str): Descrição das atividades (opcional)
            
        Returns:
            dict: Registro criado
        """
        try:
            datetime.strptime(data, "%d/%m/%Y")  # Valida formato da data
            if minutos <= 0:
                raise ValueError("Minutos devem ser positivos")
                
            return self._registrar_minutos(nome, data, minutos, descricao)
            
        except ValueError as e:
            raise ValueError(f"Dados inválidos: {str(e)}")

    def _registrar_minutos(self, nome: str, data: str, minutos: int, descricao: str = ""):
        """Método interno para registro por minutos"""
        registro = {
            "data": data,
            "minutos": minutos,
            "horas": round(minutos / 60, 2),  # Mantém ambas as representações
            "descricao": descricao,
            "timestamp": datetime.now().isoformat()
        }
        
        self.dados["usuarios"][nome]["registros"].append(registro)
        self.salvar_dados()
        return registro

    def calcular_minutos_dia(self, nome: str, data: str = None):
        """Calcula minutos trabalhados em um dia específico"""
        if data is None:
            data = datetime.now().strftime("%d/%m/%Y")
            
        registros_dia = [
            reg for reg in self.dados["usuarios"][nome]["registros"] 
            if reg["data"] == data
        ]
        
        return sum(reg.get("minutos", reg["horas"] * 60) for reg in registros_dia)

    def calcular_minutos_mes(self, nome: str, mes: int = None, ano: int = None):
        """Calcula minutos trabalhados no mês"""
        hoje = datetime.now()
        mes = mes if mes is not None else hoje.month
        ano = ano if ano is not None else hoje.year
        
        registros_mes = [
            reg for reg in self.dados["usuarios"][nome]["registros"]
            if datetime.strptime(reg["data"], "%d/%m/%Y").month == mes
            and datetime.strptime(reg["data"], "%d/%m/%Y").year == ano
        ]
        
        return sum(reg.get("minutos", reg["horas"] * 60) for reg in registros_mes)

    def calcular_horas_dia(self, nome: str, data: str = None):
        """Calcula horas trabalhadas em um dia (compatibilidade)"""
        minutos = self.calcular_minutos_dia(nome, data)
        return round(minutos / 60, 2)

    def calcular_horas_mes(self, nome: str, mes: int = None, ano: int = None):
        """Calcula horas trabalhadas no mês (compatibilidade)"""
        minutos = self.calcular_minutos_mes(nome, mes, ano)
        return round(minutos / 60, 2)

    def adicionar_registro_manual(self, nome: str, data: str, entrada: str, saida: str, descricao: str = ""):
        """
        Adiciona um registro manual com horários de entrada e saída
        
        Args:
            nome (str): Nome do estagiário
            data (str): Data no formato DD/MM/AAAA
            entrada (str): Horário de entrada no formato HH:MM
            saida (str): Horário de saída no formato HH:MM
            descricao (str): Descrição das atividades (opcional)
        
        Returns:
            dict: O registro criado
        """
        try:
            # Verifica se o usuário existe
            if nome not in self.usuarios:
                raise ValueError(f"Usuário {nome} não é válido. Use: {', '.join(self.usuarios)}")
            
            # Valida a data
            datetime.strptime(data, "%d/%m/%Y")
            
            # Valida os horários
            entrada_min = self.converter_horario_para_minutos(entrada)
            saida_min = self.converter_horario_para_minutos(saida)
            
            if saida_min <= entrada_min:
                raise ValueError("Horário de saída deve ser após o horário de entrada")
                
            # Calcula os minutos trabalhados
            minutos_trabalhados = saida_min - entrada_min
            
            # Cria e retorna o registro
            return self._registrar_minutos(nome, data, minutos_trabalhados, descricao)
            
        except ValueError as e:
            raise ValueError(f"Dados inválidos: {str(e)}")

    def adicionar_minutos_passados(self, nome: str, data: str, minutos: int, descricao: str = ""):
        """
        Adiciona minutos trabalhados manualmente para uma data passada
        
        Args:
            nome (str): Nome do estagiário
            data (str): Data no formato DD/MM/AAAA
            minutos (int): Minutos trabalhados
            descricao (str): Descrição das atividades (opcional)
            
        Returns:
            dict: Registro criado
        """
        try:
            # Validação básica
            if nome not in self.usuarios:
                raise ValueError(f"Usuário {nome} não é válido. Use: {', '.join(self.usuarios)}")
            
            if minutos <= 0:
                raise ValueError("Minutos devem ser positivos")
                
            datetime.strptime(data, "%d/%m/%Y")  # Valida formato da data
            
            return self._registrar_minutos(nome, data, minutos, descricao)
            
        except ValueError as e:
            raise ValueError(f"Dados inválidos: {str(e)}")

    def gerar_relatorio_mensal(self, mes: int = None, ano: int = None):
        """Gera relatório mensal com conversão precisa de minutos para horas"""
        hoje = datetime.now()
        mes = mes if mes is not None else hoje.month
        ano = ano if ano is not None else hoje.year
        
        relatorio = {
            "mes": mes,
            "ano": ano,
            "usuarios": {},
            "total_minutos": 0,
            "total_horas": 0.0  # Alterado para float para maior precisão
        }
        
        for usuario in self.usuarios:
            # Obtém todos os registros do mês
            registros_mes = [
                reg for reg in self.dados["usuarios"][usuario]["registros"]
                if datetime.strptime(reg["data"], "%d/%m/%Y").month == mes
                and datetime.strptime(reg["data"], "%d/%m/%Y").year == ano
            ]
            
            # Calcula minutos totais de forma robusta
            minutos_totais = sum(
                reg.get("minutos", int(reg["horas"] * 60))  # Converte horas para minutos se necessário
                for reg in registros_mes
            )
            
            # Calcula horas com precisão decimal
            horas_totais = round(minutos_totais / 60, 2)
            
            relatorio["usuarios"][usuario] = {
                "minutos": minutos_totais,
                "horas": horas_totais
            }
            relatorio["total_minutos"] += minutos_totais
            relatorio["total_horas"] = round(relatorio["total_minutos"] / 60, 2)
        
        return relatorio

    def get_registros_usuario(self, nome: str):
        """Retorna todos os registros de um usuário"""
        return self.dados["usuarios"][nome]["registros"]

    @staticmethod
    def converter_horario_para_minutos(horario: str) -> int:
        """Converte formato HH:MM para minutos totais"""
        try:
            horas, minutos = map(int, horario.split(':'))
            return horas * 60 + minutos
        except:
            raise ValueError("Formato inválido. Use HH:MM")
        
    def gerar_relatorio_anual(self, ano: int = None):
        """Gera relatório anual com horas e minutos trabalhados"""
        hoje = datetime.now()
        ano = ano if ano is not None else hoje.year
        
        relatorio = {
            "ano": ano,
            "usuarios": {},
            "total_minutos": 0,
            "total_horas": 0.0,
            "meses": {mes: {"total_minutos": 0, "total_horas": 0.0} for mes in range(1, 13)}
        }
        
        for usuario in self.usuarios:
            # Inicializa os dados do usuário
            relatorio["usuarios"][usuario] = {
                "minutos": 0,
                "horas": 0.0,
                "meses": {mes: {"minutos": 0, "horas": 0.0} for mes in range(1, 13)}
            }
            
            # Obtém todos os registros do ano
            registros_ano = [
                reg for reg in self.dados["usuarios"][usuario]["registros"]
                if datetime.strptime(reg["data"], "%d/%m/%Y").year == ano
            ]
            
            # Calcula totais por mês
            for mes in range(1, 13):
                registros_mes = [
                    reg for reg in registros_ano
                    if datetime.strptime(reg["data"], "%d/%m/%Y").month == mes
                ]
                
                minutos_mes = sum(
                    reg.get("minutos", int(reg["horas"] * 60))
                    for reg in registros_mes
                )
                horas_mes = round(minutos_mes / 60, 2)
                
                relatorio["usuarios"][usuario]["meses"][mes] = {
                    "minutos": minutos_mes,
                    "horas": horas_mes
                }
                
                # Atualiza totais do usuário
                relatorio["usuarios"][usuario]["minutos"] += minutos_mes
                relatorio["usuarios"][usuario]["horas"] = round(
                    relatorio["usuarios"][usuario]["minutos"] / 60, 2)
                
                # Atualiza totais gerais
                relatorio["meses"][mes]["total_minutos"] += minutos_mes
                relatorio["meses"][mes]["total_horas"] = round(
                    relatorio["meses"][mes]["total_minutos"] / 60, 2)
                
                relatorio["total_minutos"] += minutos_mes
                relatorio["total_horas"] = round(relatorio["total_minutos"] / 60, 2)
        
        return relatorio

# Instância global para ser usada no seu código
central_horas = CentralHorasEstagio()
