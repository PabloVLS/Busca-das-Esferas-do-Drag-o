from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Dict, Iterable, List, Set, Tuple

from mapa_config import mapa


# Type alias para tornar o código mais legível
Posicao = Tuple[int, int]


# ====================================================================================
# DEFINIÇÃO DE CUSTOS DE TERRENO
# ====================================================================================
# Quanto MAIOR o custo, mais o agente EVITA andar naquele terreno.
# Você pode ajustar estes valores para influenciar o comportamento do agente.
# ====================================================================================

CUSTOS_TERRENO = {
    0: 10,  # água     - caro, o agente tenta evitar
    1: 1,   # grama    - barato, preferido
    2: 60,  # montanha - muito caro, o agente tenta evitar muito
    3: 1,   # início   - tratamos como grama
}


# ====================================================================================
# CLASSE PARA ARMAZENAR O RESULTADO DA BUSCA
# ====================================================================================

@dataclass(frozen=True)
class ResultadoCaminho:
    """
    Armazena o resultado de uma busca de caminho.
    
    Atributos:
        caminho: Sequência de posições do início até o objetivo
        custo: Custo total do caminho (soma dos custos de cada célula)
    """
    caminho: Tuple[Posicao, ...]
    custo: int


# ====================================================================================
# CLASSE PRINCIPAL DO ALGORITMO A*
# ====================================================================================

class PlanejadorAEstrela:
    """
    Implementa o algoritmo A* para encontrar caminhos ótimos em um mapa.
    
    Este é um algoritmo de busca informada que combina:
        1. Busca de menor custo (Dijkstra)
        2. Heurística para guiar a busca (algoritmo guloso)
    
    Resultado: Combina o melhor dos dois abordagens!
    """

    def __init__(self, mapa_terreno):
        if mapa_terreno is None:
            raise ValueError("O mapa de terreno não pode ser None.")

        if len(mapa_terreno) == 0:
            raise ValueError("O mapa de terreno não pode ser vazio.")

        if len(mapa_terreno[0]) == 0:
            raise ValueError("O mapa de terreno não pode ter linhas vazias.")

        self.mapa = mapa_terreno
        self.altura = len(mapa_terreno)
        self.largura = len(mapa_terreno[0])

    # ==================================================================================
    # MÉTODO 1: Verificar se uma posição está dentro dos limites do mapa
    # ==================================================================================

    def posicao_esta_dentro_do_mapa(self, posicao: Posicao) -> bool:
        x, y = posicao
        
        if x < 0 or x >= self.largura:
            return False
        
        if y < 0 or y >= self.altura:
            return False
        
        return True

    # ==================================================================================
    # MÉTODO 2: Obter o custo de entrada em uma célula
    # ==================================================================================

    def custo_da_celula(self, posicao: Posicao) -> int:
        x, y = posicao
        tipo_de_terreno = self.mapa[y][x]

        if tipo_de_terreno not in CUSTOS_TERRENO:
            raise ValueError(f"Terreno desconhecido: {tipo_de_terreno}")

        return CUSTOS_TERRENO[tipo_de_terreno]

    # ==================================================================================
    # MÉTODO 3: HEURÍSTICA - Estimar custo até o objetivo
    # ==================================================================================

    def calcular_heuristica(self, posicao_atual: Posicao, posicao_objetivo: Posicao) -> int:
        x_atual, y_atual = posicao_atual
        x_objetivo, y_objetivo = posicao_objetivo

        # Distância em X (quantas casas para esquerda/direita)
        diferenca_x = abs(x_atual - x_objetivo)
        
        # Distância em Y (quantas casas para cima/baixo)
        diferenca_y = abs(y_atual - y_objetivo)

        # Distância Manhattan = andar primeiro em X, depois em Y
        distancia_manhattan = diferenca_x + diferenca_y
        
        return distancia_manhattan

    # ==================================================================================
    # MÉTODO 4: Gerar vizinhos - Quais são as próximas células que o agente pode pisa?
    # ==================================================================================

    def obter_posicoes_vizinhas(self, posicao: Posicao) -> Iterable[Posicao]:
        x, y = posicao

        # Define os 4 vizinhos possíveis (4 direções)
        vizinto_direita = (x + 1, y)
        vizinto_esquerda = (x - 1, y)
        vizinto_baixo = (x, y + 1)
        vizinto_cima = (x, y - 1)

        # Retorna apenas os vizinhos que estão dentro do mapa
        if self.posicao_esta_dentro_do_mapa(vizinto_direita):
            yield vizinto_direita

        if self.posicao_esta_dentro_do_mapa(vizinto_esquerda):
            yield vizinto_esquerda

        if self.posicao_esta_dentro_do_mapa(vizinto_baixo):
            yield vizinto_baixo

        if self.posicao_esta_dentro_do_mapa(vizinto_cima):
            yield vizinto_cima

    # ==================================================================================
    # MÉTODO 5: Reconstruir o caminho (voltar do final até o início)
    # ==================================================================================

    def reconstruir_caminho(self,posicao_final: Posicao,posicao_anterior_by_posicao: Dict[Posicao, Posicao],) -> Tuple[Posicao, ...]:
        caminho_invertido: List[Posicao] = []

        # Começar no final
        posicao_atual = posicao_final
        caminho_invertido.append(posicao_atual)

        # Voltar até chegar no início (início não tem "anterior")
        while posicao_atual in posicao_anterior_by_posicao:
            posicao_anterior = posicao_anterior_by_posicao[posicao_atual]
            caminho_invertido.append(posicao_anterior)
            posicao_atual = posicao_anterior

        caminho_invertido.reverse()
        
        return tuple(caminho_invertido)

    # ==================================================================================
    # MÉTODO PRINCIPAL: ALGORITMO A*
    # ==================================================================================

    def  buscar(self, posicao_inicial: Posicao, posicao_objetivo: Posicao) -> ResultadoCaminho:
        if not self.posicao_esta_dentro_do_mapa(posicao_inicial):
            raise ValueError(f"Posição inicial fora do mapa: {posicao_inicial}")

        if not self.posicao_esta_dentro_do_mapa(posicao_objetivo):
            raise ValueError(f"Posição objetivo fora do mapa: {posicao_objetivo}")

        if posicao_inicial == posicao_objetivo:
            return ResultadoCaminho(caminho=(posicao_inicial,), custo=0)

        fila_aberta: List[Tuple[int, int, Posicao]] = []
        custo_real_inicial = 0  # g(inicial) = 0
        heuristica_inicial = self.calcular_heuristica(posicao_inicial, posicao_objetivo)
        prioridade_inicial = custo_real_inicial + heuristica_inicial  # f = g + h
        heappush(fila_aberta, (prioridade_inicial, custo_real_inicial, posicao_inicial)) 
        # Coloca o nó inicial na fila de exploração.

        posicao_anterior_by_posicao: Dict[Posicao, Posicao] = {}
        melhor_custo_real_para_posicao: Dict[Posicao, int] = {posicao_inicial: 0}
        posicoes_fechadas: Set[Posicao] = set()

        while len(fila_aberta) > 0:

            prioridade_atual, custo_real_atual, posicao_atual = heappop(fila_aberta)
            if posicao_atual in posicoes_fechadas:
                continue

            posicoes_fechadas.add(posicao_atual)

            #se a posicao atual que saiu da fila for o objetivo, monta o caminho final usando o dicionário de "posicao_anterior_by_posicao" e retorna o resultado 
            if posicao_atual == posicao_objetivo:
                caminho_completo = self.reconstruir_caminho(posicao_atual,posicao_anterior_by_posicao)
                return ResultadoCaminho(caminho=caminho_completo, custo=custo_real_atual)

            for posicao_vizinha in self.obter_posicoes_vizinhas(posicao_atual):

                if posicao_vizinha in posicoes_fechadas:
                    continue

                custo_para_entrar_vizinha = self.custo_da_celula(posicao_vizinha)
                novo_custo_real = custo_real_atual + custo_para_entrar_vizinha

                # Verificar se encontramos um caminho MELHOR para este vizinho
                melhor_custo_anterior = melhor_custo_real_para_posicao.get(posicao_vizinha)

                encontramos_caminho_melhor = (
                    melhor_custo_anterior is None or novo_custo_real < melhor_custo_anterior
                )

                if encontramos_caminho_melhor:
                    # Atualizar dados do vizinho
                    melhor_custo_real_para_posicao[posicao_vizinha] = novo_custo_real
                    posicao_anterior_by_posicao[posicao_vizinha] = posicao_atual
                    # Calcular prioridade para este vizinho
                    heuristica_vizinha = self.calcular_heuristica(posicao_vizinha, posicao_objetivo)
                    prioridade_vizinha = novo_custo_real + heuristica_vizinha
                    heappush(fila_aberta, (prioridade_vizinha, novo_custo_real, posicao_vizinha))

        # Se saiu do loop: não encontrou caminho
        raise RuntimeError(
            f"Não foi possível encontrar caminho de {posicao_inicial} até {posicao_objetivo}."
        )


# ====================================================================================
# INSTÂNCIA GLOBAL DO PLANEJADOR
# ====================================================================================

planejador = PlanejadorAEstrela(mapa)
