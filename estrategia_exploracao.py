from typing import Tuple

from heuristica import PlanejadorAEstrela, ResultadoCaminho
from mundo import Mapa


Posicao = Tuple[int, int]


class EstrategiaExploracao:
    """
    Estratégia de exploração baseada em fronteiras.

    Responsabilidades deste módulo:
    - escolher a melhor fronteira para explorar;
    - calcular score de exploração usando custo de rota + ganho de informação.

    O algoritmo A* em si fica no módulo heuristica.py.
    """

    def __init__(self,mundo: Mapa,terreno_desconhecido_padrao: int,penalidade_agua_passo: int,penalidade_montanha_passo: int,penalidade_agua_destino: int,penalidade_montanha_destino: int,) -> None:
        self.mundo = mundo
        self.terreno_desconhecido_padrao = terreno_desconhecido_padrao
        self.penalidade_agua_passo = penalidade_agua_passo
        self.penalidade_montanha_passo = penalidade_montanha_passo
        self.penalidade_agua_destino = penalidade_agua_destino
        self.penalidade_montanha_destino = penalidade_montanha_destino

    def penalidade_terreno(self, terreno: int, destino: bool = False) -> int:
        if terreno == 2:
            return self.penalidade_montanha_destino if destino else self.penalidade_montanha_passo
        if terreno == 0:
            return self.penalidade_agua_destino if destino else self.penalidade_agua_passo
        return 0

    def calcular_penalidade_trajeto(self, caminho: ResultadoCaminho) -> int:
        penalidade = 0
        for posicao in caminho.caminho[1:]:
            terreno = self.mundo.terreno_conhecido.get(posicao)
            if terreno is None:
                continue
            penalidade += self.penalidade_terreno(terreno, destino=False)
        return penalidade

    def selecionar_melhor_fronteira(self, posicao_atual: Posicao) -> tuple[Posicao, ResultadoCaminho] | None:
        fronteiras = self.mundo.detectar_fronteiras()
        if not fronteiras:
            return None

        planejador_estimado = PlanejadorAEstrela(
            self.mundo.construir_mapa_planejamento(self.terreno_desconhecido_padrao)
        )

        melhor_fronteira: Posicao | None = None
        melhor_caminho: ResultadoCaminho | None = None
        melhor_score: float | None = None

        for frontier in fronteiras:
            if frontier == posicao_atual:
                continue

            try:
                caminho = planejador_estimado.buscar(posicao_atual, frontier)
            except RuntimeError:
                continue

            ganho = self.mundo.calcular_ganho_informacao(frontier)#qts celulas o radar vai revelar
            penalidade_trajeto = self.calcular_penalidade_trajeto(caminho)
            terreno_destino = self.mundo.terreno_conhecido.get(frontier)
            penalidade_destino = self.penalidade_terreno(terreno_destino, destino=True) if terreno_destino is not None else 0
            score = caminho.custo - ganho + penalidade_trajeto + penalidade_destino

            if melhor_score is None or score < melhor_score:#score menor fronteira melhor
                melhor_score = score
                melhor_fronteira = frontier
                melhor_caminho = caminho
            elif score == melhor_score and melhor_caminho is not None and caminho.custo < melhor_caminho.custo:
                melhor_fronteira = frontier
                melhor_caminho = caminho

        if melhor_fronteira is None or melhor_caminho is None:
            return None

        return melhor_fronteira, melhor_caminho
