"""
================================================================================
ALGORITMO A* (A-ESTRELA) - VERSÃO DIDÁTICA
================================================================================

Objetivo: Encontrar um caminho de menor custo entre dois pontos no mapa.

Ideia principal do A*:
    Para cada posição, calculamos uma pontuação total:
    
        f(posição) = g(posição) + h(posição)
    
    Onde:
        g(posição) = custo REAL acumulado para chegar até aqui
        h(posição) = ESTIMATIVA de custo restante até o objetivo (heurística)

    O A* sempre escolhe a posição com menor f(posição) para explorar próximo.

Terrenos no mapa (mapa_config.py):
    - 0 = água (custo: 10 - caro, o agente evita)
    - 1 = grama (custo: 1 - barato, preferido)
    - 2 = montanha (custo: 60 - muito caro, o agente evita muito)
    - 3 = Ilha do Mestre Kame (início, custo: 1)

================================================================================
"""

from dataclasses import dataclass
from functools import lru_cache
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
        """
        Inicializa o planejador com um mapa.
        
        Args:
            mapa_terreno: Matriz 2D onde cada elemento é um tipo de terreno
        """
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
        """
        Verifica se uma posição está dentro dos limites do mapa.
        
        Importante: Usamos isto para NÃO sair do mapa durante a busca.
        
        Args:
            posicao: Coordenada (x, y) a verificar
            
        Returns:
            True se está dentro do mapa, False caso contrário
        """
        x, y = posicao
        
        # Verifica se x está entre 0 e largura-1
        if x < 0 or x >= self.largura:
            return False
        
        # Verifica se y está entre 0 e altura-1
        if y < 0 or y >= self.altura:
            return False
        
        return True

    # ==================================================================================
    # MÉTODO 2: Obter o custo de entrada em uma célula
    # ==================================================================================

    def custo_da_celula(self, posicao: Posicao) -> int:
        """
        Retorna o custo para ENTRAR em uma célula.
        
        Exemplo:
            - Pisar em grama custa 1
            - Pisar em água custa 10
            - Pisar em montanha custa 60
        
        Args:
            posicao: Coordenada (x, y) da célula
            
        Returns:
            Custo (número inteiro) para entrar nessa célula
        """
        x, y = posicao
        tipo_de_terreno = self.mapa[y][x]

        if tipo_de_terreno not in CUSTOS_TERRENO:
            raise ValueError(f"Terreno desconhecido: {tipo_de_terreno}")

        return CUSTOS_TERRENO[tipo_de_terreno]

    # ==================================================================================
    # MÉTODO 3: HEURÍSTICA - Estimar custo até o objetivo
    # ==================================================================================

    def calcular_heuristica(self, posicao_atual: Posicao, posicao_objetivo: Posicao) -> int:
        """
        Calcula uma ESTIMATIVA de custo até o objetivo (heurística).
        
        Usamos distância Manhattan (também chamada de "distância de táxi"):
            - Soma a distância em X com a distância em Y
            - Válida quando você só pode se mover em 4 direções (cima, baixo, esquerda, direita)
        
        IMPORTANTE:
            A heurística deve NUNCA superestimar o custo real!
            Isso garante que o A* encontre o caminho ótimo.
        
        Args:
            posicao_atual: Onde estamos agora
            posicao_objetivo: Onde queremos chegar
            
        Returns:
            Estimativa de custo restante
        """
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
        """
        Gera as 4 posições vizinhas (cima, baixo, esquerda, direita).
        
        Importante: Só retorna vizinhos que estão DENTRO do mapa.
        
        Args:
            posicao: Posição atual (x, y)
            
        Yields:
            Cada vizinho válido (dentro do mapa)
        """
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

    def reconstruir_caminho(
        self,
        posicao_final: Posicao,
        posicao_anterior_by_posicao: Dict[Posicao, Posicao],
    ) -> Tuple[Posicao, ...]:
        """
        Reconstrói o caminho completo saindo do final e voltando para o início.
        
        Como funciona:
            1. Começamos na posição final
            2. Consultamos de onde viemos (posicao_anterior_by_posicao)
            3. Vamos voltando até chegar no início
            4. Invertemos a ordem para ter: início -> ... -> final
        
        Args:
            posicao_final: Posição de chegada
            posicao_anterior_by_posicao: Dicionário que diz de onde viemos
            
        Returns:
            Tupla ordenada com o caminho completo
        """
        caminho_invertido: List[Posicao] = []

        # Começar no final
        posicao_atual = posicao_final
        caminho_invertido.append(posicao_atual)

        # Voltar até chegar no início (início não tem "anterior")
        while posicao_atual in posicao_anterior_by_posicao:
            posicao_anterior = posicao_anterior_by_posicao[posicao_atual]
            caminho_invertido.append(posicao_anterior)
            posicao_atual = posicao_anterior

        # Inverter para ficar: início -> ... -> fim
        caminho_invertido.reverse()
        
        return tuple(caminho_invertido)

    # ==================================================================================
    # MÉTODO PRINCIPAL: ALGORITMO A*
    # ==================================================================================

    def buscar(self, posicao_inicial: Posicao, posicao_objetivo: Posicao) -> ResultadoCaminho:
        """
        Implementa o algoritmo A* completo.
        
        Fluxo geral:
            1. Validação de entrada
            2. Inicialização (fila, estruturas de dados)
            3. Loop principal: mientras haya posições para explorar
                a. Pegar melhor posição da fila
                b. Se for o objetivo: encontramos!
                c. Explorar vizinhos e adicionar à fila
            4. Se sair do loop: não há caminho
        
        Args:
            posicao_inicial: Ponto de partida (x, y)
            posicao_objetivo: Ponto de chegada (x, y)
            
        Returns:
            ResultadoCaminho com o caminho e que custo total
        """

        # -----------------------------------
        # FASE 1: Validação de entrada
        # -----------------------------------

        if not self.posicao_esta_dentro_do_mapa(posicao_inicial):
            raise ValueError(f"Posição inicial fora do mapa: {posicao_inicial}")

        if not self.posicao_esta_dentro_do_mapa(posicao_objetivo):
            raise ValueError(f"Posição objetivo fora do mapa: {posicao_objetivo}")

        # Caso especial: já estamos no objetivo
        if posicao_inicial == posicao_objetivo:
            return ResultadoCaminho(caminho=(posicao_inicial,), custo=0)

        # -----------------------------------
        # FASE 2: Inicialização da busca
        # -----------------------------------

        # ESTRUTURA 1: Fila de prioridade
        # - Sempre retorna o item com MENOR prioridade (f)
        # - Cada item é: (prioridade_f, custo_real_g, posicao)
        # - Usamos heapq (heap/fila de prioridade mínima)
        fila_aberta: List[Tuple[int, int, Posicao]] = []

        # Inicializar com a posição inicial
        custo_real_inicial = 0  # g(inicial) = 0
        heuristica_inicial = self.calcular_heuristica(posicao_inicial, posicao_objetivo)
        prioridade_inicial = custo_real_inicial + heuristica_inicial  # f = g + h

        heappush(fila_aberta, (prioridade_inicial, custo_real_inicial, posicao_inicial))

        # ESTRUTURA 2: Dicionário para rastrear De onde viemos
        # - Usado para reconstruir o caminho no final
        # - Exemplo: posicao_anterior[(2, 3)] = (1, 3)  (viemos de (1,3) para (2,3))
        posicao_anterior_by_posicao: Dict[Posicao, Posicao] = {}

        # ESTRUTURA 3: Menor custo encontrado para cada posição
        # - Guardar o MELHOR custo que conseguimos para chegar em cada posição
        # - Se encontramos um caminho mais barato, atualizamos
        melhor_custo_real_para_posicao: Dict[Posicao, int] = {posicao_inicial: 0}

        # ESTRUTURA 4: Posições que já foram processadas
        # - Uma vez que processamos uma posição, não processamos novamente
        # - Isso garante eficiência (evita explorar o mesmo nó duas vezes)
        posicoes_fechadas: Set[Posicao] = set()

        # -----------------------------------
        # FASE 3: Loop principal do A*
        # -----------------------------------

        while len(fila_aberta) > 0:

            # Pega a posição com MENOR pontuação f
            prioridade_atual, custo_real_atual, posicao_atual = heappop(fila_aberta)

            # Se já processamos esta posição, pular (não fazer nada)
            if posicao_atual in posicoes_fechadas:
                continue

            # Marcar como processada
            posicoes_fechadas.add(posicao_atual)

            # VERIFICAÇÃO: Chegamos no objetivo?
            if posicao_atual == posicao_objetivo:
                caminho_completo = self.reconstruir_caminho(
                    posicao_atual,
                    posicao_anterior_by_posicao,
                )
                return ResultadoCaminho(caminho=caminho_completo, custo=custo_real_atual)

            # -----------------------------------
            # Explorar vizinhos
            # -----------------------------------

            for posicao_vizinha in self.obter_posicoes_vizinhas(posicao_atual):

                # Pular vizinhos já processados
                if posicao_vizinha in posicoes_fechadas:
                    continue

                # Calcular custo real para chegar neste vizinho
                custo_para_entrar_vizinha = self.custo_da_celula(posicao_vizinha)
                novo_custo_real = custo_real_atual + custo_para_entrar_vizinha

                # Verificar se encontramos um caminho MELHOR para este vizinho
                melhor_custo_anterior = melhor_custo_real_para_posicao.get(posicao_vizinha)

                # Encontramos caminho melhor se:
                # - Primeira vez que vemos este vizinho, OU
                # - Novo caminho é mais barato que o anterior
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

                    # Adicionar na fila
                    heappush(fila_aberta, (prioridade_vizinha, novo_custo_real, posicao_vizinha))

        # Se saiu do loop: não encontrou caminho
        raise RuntimeError(
            f"Não foi possível encontrar caminho de {posicao_inicial} até {posicao_objetivo}."
        )


# ====================================================================================
# INSTÂNCIA GLOBAL DO PLANEJADOR
# ====================================================================================

planejador = PlanejadorAEstrela(mapa)


# ====================================================================================
# FUNÇÃO PÚBLICA PARA BUSCAR CAMINHO (com cache)
# ====================================================================================

@lru_cache(maxsize=None)
def caminho_entre(posicao_inicial: Posicao, posicao_objetivo: Posicao) -> ResultadoCaminho:
    """
    Função pública para encontrar caminho entre duas posições.
    
    Esta função usa CACHE (lru_cache) para evitar recalcular caminhos
    que já foram calculados antes. Isto melhora MUITO a performance!
    
    Args:
        posicao_inicial: Ponto de saída (x, y)
        posicao_objetivo: Ponto de chegada (x, y)
        
    Returns:
        ResultadoCaminho com o melhor caminho encontrado
    """
    resultado = planejador.buscar(posicao_inicial, posicao_objetivo)
    return resultado
