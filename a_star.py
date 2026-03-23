import sys
from dataclasses import dataclass
from functools import lru_cache
from heapq import heappop, heappush

from mapa_config import mapa, TAMANHO_MAPA
from typing import Tuple

CUSTOS_TERRENO = {
    0: 10,
    1: 1,
    2: 60,
    3: 1,
}


@dataclass(frozen=True)
class ResultadoCaminho:
    caminho: Tuple[Tuple[int, int], ...]
    custo: int


class PlanejadorAEstrela:
    def __init__(self, mapa_terreno):
        self.mapa = mapa_terreno

    def custo_da_celula(self, posicao: Tuple[int, int]) -> int:
        x, y = posicao
        return CUSTOS_TERRENO[self.mapa[y][x]]

    def heuristica(self, origem: Tuple[int, int], destino: Tuple[int, int]) -> int:
        return (abs(origem[0] - destino[0]) + abs(origem[1] - destino[1])) * 1

    def vizinhos(self, posicao: Tuple[int, int]):
        x, y = posicao
        for proximo in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            px, py = proximo
            if 0 <= px < TAMANHO_MAPA and 0 <= py < TAMANHO_MAPA:
                yield proximo

    def buscar(self, inicio: Tuple[int, int], objetivo: Tuple[int, int]) -> ResultadoCaminho:
        if inicio == objetivo:
            return ResultadoCaminho((inicio,), 0)

        fila_prioridade = []
        heappush(fila_prioridade, (self.heuristica(inicio, objetivo), 0, inicio))

        veio_de = {}
        custo_g = {inicio: 0}
        visitados = set()

        while fila_prioridade:
            _, custo_atual, atual = heappop(fila_prioridade)

            if atual in visitados:
                continue
            visitados.add(atual)

            if atual == objetivo:
                caminho = [atual]
                while atual in veio_de:
                    atual = veio_de[atual]
                    caminho.append(atual)
                caminho.reverse()
                return ResultadoCaminho(tuple(caminho), custo_atual)

            for proximo in self.vizinhos(atual):
                novo_custo = custo_atual + self.custo_da_celula(proximo)
                if novo_custo < custo_g.get(proximo, sys.maxsize):
                    custo_g[proximo] = novo_custo
                    veio_de[proximo] = atual
                    prioridade = novo_custo + self.heuristica(proximo, objetivo)
                    heappush(fila_prioridade, (prioridade, novo_custo, proximo))

        raise RuntimeError(f"Não foi possível encontrar caminho de {inicio} até {objetivo}.")


planejador = PlanejadorAEstrela(mapa)


@lru_cache(maxsize=None)
def caminho_entre(inicio: Tuple[int, int], objetivo: Tuple[int, int]) -> ResultadoCaminho:
    return planejador.buscar(inicio, objetivo)
