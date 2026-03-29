import random
from typing import Tuple

from mapa_config import mapa, TAMANHO_MAPA


Posicao = Tuple[int, int]


class Mapa:
    def __init__(self, radar_alcance: int, quantidade_esferas: int, manual_esferas: list[tuple[int, int]]) -> None:
        self.radar_alcance = radar_alcance
        self.quantidade_esferas = quantidade_esferas
        self.manual_esferas = manual_esferas
        self.celulas_conhecidas: set[Posicao] = set()
        self.terreno_conhecido: dict[Posicao, int] = {}
        self.inicio = self.localizar_inicio()

    def localizar_inicio(self) -> Posicao:
        for y in range(TAMANHO_MAPA):
            for x in range(TAMANHO_MAPA):
                if mapa[y][x] == 3:
                    return x, y
        raise ValueError("Nao foi possivel localizar a Ilha do Mestre Kame no mapa.")

    def gerar_esferas(self, rng: random.Random, inicio: Posicao) -> set[Posicao]:
        manual_validas: list[Posicao] = []
        for p in self.manual_esferas:
            try:
                x, y = int(p[0]), int(p[1])
            except Exception:
                continue
            if 0 <= x < TAMANHO_MAPA and 0 <= y < TAMANHO_MAPA and (x, y) != inicio:
                if (x, y) not in manual_validas:
                    manual_validas.append((x, y))

        if manual_validas:
            return set(manual_validas[: self.quantidade_esferas])

        candidatas = [
            (x, y)
            for y in range(TAMANHO_MAPA)
            for x in range(TAMANHO_MAPA)
            if (x, y) != inicio
        ]
        restantes = max(0, self.quantidade_esferas)
        if restantes > len(candidatas):
            restantes = len(candidatas)

        aleatorias = rng.sample(candidatas, restantes) if restantes else []
        return set(aleatorias)

    @staticmethod
    def distancia_chebyshev(a: Posicao, b: Posicao) -> int:
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def obter_posicoes_vizinhas(self, posicao: Posicao) -> list[Posicao]:
        x, y = posicao
        vizinhas: list[Posicao] = []
        candidatas = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        for vx, vy in candidatas:
            if 0 <= vx < TAMANHO_MAPA and 0 <= vy < TAMANHO_MAPA:
                vizinhas.append((vx, vy))
        return vizinhas

    def celulas_no_alcance_do_radar(self, centro: Posicao) -> list[Posicao]:
        celulas: list[Posicao] = []
        for y in range(max(0, centro[1] - self.radar_alcance), min(TAMANHO_MAPA, centro[1] + self.radar_alcance + 1)):
            for x in range(max(0, centro[0] - self.radar_alcance), min(TAMANHO_MAPA, centro[0] + self.radar_alcance + 1)):
                if self.distancia_chebyshev(centro, (x, y)) <= self.radar_alcance:
                    celulas.append((x, y))
        return celulas

    def atualizar_mapa_conhecido(self, posicao_atual: Posicao) -> set[Posicao]:
        novas_celulas: set[Posicao] = set()
        for posicao in self.celulas_no_alcance_do_radar(posicao_atual):
            if posicao not in self.celulas_conhecidas:
                novas_celulas.add(posicao)
            self.celulas_conhecidas.add(posicao)
            self.terreno_conhecido[posicao] = mapa[posicao[1]][posicao[0]]
        return novas_celulas

    def detectar_fronteiras(self) -> set[Posicao]:
        fronteiras: set[Posicao] = set()
        for posicao in self.celulas_conhecidas:
            for vizinha in self.obter_posicoes_vizinhas(posicao):
                if vizinha not in self.celulas_conhecidas:
                    fronteiras.add(posicao)
                    break
        return fronteiras

    def calcular_ganho_informacao(self, frontier: Posicao) -> int:
        ganho = 0
        for posicao in self.celulas_no_alcance_do_radar(frontier):
            if posicao not in self.celulas_conhecidas:
                ganho += 1
        return ganho

    def construir_mapa_planejamento(self, terreno_desconhecido_padrao: int) -> list[list[int]]:
        mapa_estimado: list[list[int]] = []
        for y in range(TAMANHO_MAPA):
            linha: list[int] = []
            for x in range(TAMANHO_MAPA):
                posicao = (x, y)
                if posicao in self.terreno_conhecido:
                    linha.append(self.terreno_conhecido[posicao])
                else:
                    linha.append(terreno_desconhecido_padrao)
            mapa_estimado.append(linha)
        return mapa_estimado

    def sondar_radar(self,posicao_atual: Posicao,esferas_ocultas: set[Posicao],esferas_detectadas: set[Posicao],esferas_coletadas: set[Posicao],) -> set[Posicao]:
        self.atualizar_mapa_conhecido(posicao_atual)
        novos = {
            esfera
            for esfera in esferas_ocultas
            if esfera not in esferas_detectadas
            and esfera not in esferas_coletadas
            and self.distancia_chebyshev(posicao_atual, esfera) <= self.radar_alcance
        }
        if novos:
            esferas_detectadas.update(novos)
        return novos
