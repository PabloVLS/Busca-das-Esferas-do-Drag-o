import itertools
import random
import pygame
import os
from datetime import timedelta
from typing import Tuple

from mapa_config import mapa, TAMANHO_MAPA
import a_star
from hud import HUD

# constants
TAMANHO_CELULA = 15
RADAR_ALCANCE = 3
QUANTIDADE_ESFERAS = 7
PAINEL_LARGURA = 320
MARGEM_TELA = 18
MOVIMENTO_FPS = 4
MOVIMENTO_FPS_MIN = 1
MOVIMENTO_FPS_MAX = 12
# Se quiser fixar algumas esferas manualmente, adicione aqui uma lista de tuplas (x, y).
# Exemplo: MANUAL_ESFERAS = [(5,3), (10,8)]
# Deixe vazia para usar apenas seleção aleatória.
MANUAL_ESFERAS: list[tuple[int, int]] = [(1,1), (2,1), (1,5), (1, 6), (3, 4), (4, 17), (5, 5)]


class Simulacao:
    def __init__(self, tela, fonte, fonte_pequena, fonte_titulo, relogio):
        self.tela = tela
        self.fonte = fonte
        self.fonte_pequena = fonte_pequena
        self.fonte_titulo = fonte_titulo
        self.relogio = relogio

        largura_tela, altura_tela = self.tela.get_size()
        global TAMANHO_CELULA
        # largura disponível agora ignora o painel lateral (usar toda a largura)
        tamanho_celula_horizontal = max(12, (largura_tela - (MARGEM_TELA * 3)) // TAMANHO_MAPA)
        tamanho_celula_vertical = max(12, (altura_tela - (MARGEM_TELA * 2)) // TAMANHO_MAPA)
        # fator para reduzir o tamanho visual do mapa (0 < fator <= 1). Ajuste conforme desejar.
        self._map_scale_factor = 0.85
        TAMANHO_CELULA = max(8, int(max(12, min(tamanho_celula_horizontal, tamanho_celula_vertical)) * self._map_scale_factor))

        self.tamanho_mapa_px = TAMANHO_MAPA * TAMANHO_CELULA
        # centraliza o mapa na tela (reserva espaço inferior para a HUD)
        self.sidebar_largura = 0
        bar_height = 72
        self.mapa_offset_x = max(MARGEM_TELA, (largura_tela - self.tamanho_mapa_px) // 2)
        # centraliza verticalmente considerando a barra inferior
        self.mapa_offset_y = max(MARGEM_TELA, (altura_tela - bar_height - self.tamanho_mapa_px) // 2)
        self.quantidade_esferas = QUANTIDADE_ESFERAS
        self.radar_alcance = RADAR_ALCANCE

        self.inicio = self.localizar_inicio()
        self.posicao = self.inicio
        self.rng = random.Random()
        self.esferas_ocultas = self.gerar_esferas(self.rng, self.inicio)
        self.esferas_detectadas: set[Tuple[int, int]] = set()
        self.esferas_coletadas: set[Tuple[int, int]] = set()
        self.caminho_percorrido: list[Tuple[int, int]] = [self.inicio]
        self.custo_acumulado = 0
        self.waypoints = self.gerar_waypoints()
        self.waypoint_cursor = 0
        self.movimento_fps = MOVIMENTO_FPS
        self.rodando = True
        self.concluida = False
        self.mensagem_final = ""
        self.pausado = False
        self._pausa_inicio_ms = None
        self._tempo_inicial_ms = pygame.time.get_ticks()
        self._tempo_pausado_ms = 0
        self.botoes_hud = {}

        self.hud = HUD(self.tela, self.fonte, self.fonte_pequena, self.fonte_titulo, PAINEL_LARGURA, MARGEM_TELA)

        # carregar imagem de fundo (fallback para gradiente)
        self._fundo_original = None
        self._fundo_scaled = None
        # ajuste: fator relativo ao tamanho da janela (1.0 = preencher totalmente)
        self._fundo_scale_factor = 1.0
        try:
            caminho_fundo = r"C:\Users\Pichau\Desktop\Outros\Inteligencia Artificial\EsferasDragao\img\goku3geminiMelhorada.jpg"
            if os.path.exists(caminho_fundo):
                self._fundo_original = pygame.image.load(caminho_fundo).convert()
            ow, oh = self._fundo_original.get_size()
            sw, sh = self.tela.get_size()
            # usar 'cover' — escala mínima que cobre a tela inteira mantendo proporção
            scale = max((sw * self._fundo_scale_factor) / ow, (sh * self._fundo_scale_factor) / oh)
            new_w = max(1, int(ow * scale))
            new_h = max(1, int(oh * scale))
            self._fundo_scaled = pygame.transform.smoothscale(self._fundo_original, (new_w, new_h))
        except Exception:
            self._fundo_original = None
            self._fundo_scaled = None

    def fase_atual(self) -> str:
        if self.concluida:
            return "Concluída"
        if len(self.esferas_coletadas) >= self.quantidade_esferas:
            return "Voltando para casa"
        if self.esferas_detectadas:
            return "Coletando"
        return "Explorando"

    def localizar_inicio(self) -> Tuple[int, int]:
        for y in range(TAMANHO_MAPA):
            for x in range(TAMANHO_MAPA):
                if mapa[y][x] == 3:
                    return x, y
        raise ValueError("Não foi possível localizar a Ilha do Mestre Kame no mapa.")

    def gerar_esferas(self, rng: random.Random, inicio: Tuple[int, int]) -> set[Tuple[int, int]]:
        # usa posições manuais definidas em MANUAL_ESFERAS (se houver) e completa o resto aleatoriamente
        manual_validas: list[Tuple[int, int]] = []
        for p in MANUAL_ESFERAS:
            try:
                x, y = int(p[0]), int(p[1])
            except Exception:
                continue
            if 0 <= x < TAMANHO_MAPA and 0 <= y < TAMANHO_MAPA and (x, y) != inicio:
                if (x, y) not in manual_validas:
                    manual_validas.append((x, y))
        # Se o usuário forneceu posições manuais, use somente elas (cortando se houver mais que o desejado)
        if manual_validas:
            return set(manual_validas[: self.quantidade_esferas])

        # Senão, gera tudo aleatoriamente como antes
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

    def distancia_chebyshev(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def gerar_waypoints(self) -> list[Tuple[int, int]]:
        centros = list(range(RADAR_ALCANCE, TAMANHO_MAPA, RADAR_ALCANCE * 2 + 1))
        waypoints: list[Tuple[int, int]] = []
        for indice_y, y in enumerate(centros):
            linha = [(x, y) for x in centros]
            if indice_y % 2 == 1:
                linha.reverse()
            waypoints.extend(linha)
        return waypoints

    def tempo_decorrido_ms(self) -> int:
        agora = pygame.time.get_ticks()
        acumulado = agora - self._tempo_inicial_ms - self._tempo_pausado_ms
        if self.pausado and self._pausa_inicio_ms is not None:
            acumulado -= agora - self._pausa_inicio_ms
        return max(0, acumulado)

    def formatar_tempo(self, milissegundos: int) -> str:
        duracao = timedelta(milliseconds=milissegundos)
        total_segundos = int(duracao.total_seconds())
        minutos, segundos = divmod(total_segundos, 60)
        return f"{minutos:02d}:{segundos:02d}"

    def alternar_pausa(self) -> None:
        if self.concluida:
            return

        if not self.pausado:
            self.pausado = True
            self._pausa_inicio_ms = pygame.time.get_ticks()
            self.mensagem_final = "Simulação pausada. Pressione P ou ESPAÇO para continuar."
        else:
            if self._pausa_inicio_ms is not None:
                self._tempo_pausado_ms += pygame.time.get_ticks() - self._pausa_inicio_ms
            self._pausa_inicio_ms = None
            self.pausado = False
            self.mensagem_final = ""

    def tratar_eventos(self) -> None:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.rodando = False
                    return
                if evento.key in (pygame.K_p, pygame.K_SPACE):
                    self.alternar_pausa()
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                self.processar_clique(evento.pos)

    def processar_clique(self, posicao: Tuple[int, int]) -> None:
        if self.botoes_hud.get("mais_devagar") and self.botoes_hud["mais_devagar"].collidepoint(posicao):
            self.desacelerar_movimento()
        elif self.botoes_hud.get("mais_rapido") and self.botoes_hud["mais_rapido"].collidepoint(posicao):
            self.acelerar_movimento()

    def acelerar_movimento(self) -> None:
        self.movimento_fps = min(MOVIMENTO_FPS_MAX, self.movimento_fps + 1)

    def desacelerar_movimento(self) -> None:
        self.movimento_fps = max(MOVIMENTO_FPS_MIN, self.movimento_fps - 1)

    def sondar_radar(self) -> set[Tuple[int, int]]:
        novos = {
            esfera
            for esfera in self.esferas_ocultas
            if esfera not in self.esferas_detectadas
            and esfera not in self.esferas_coletadas
            and self.distancia_chebyshev(self.posicao, esfera) <= RADAR_ALCANCE
        }
        if novos:
            self.esferas_detectadas.update(novos)
        return novos

    def mover_por_caminho(self, caminho: a_star.ResultadoCaminho) -> bool:
        detectou_nova_esfera = False
        for proxima_posicao in caminho.caminho[1:]:
            self.tratar_eventos()
            if not self.rodando:
                return detectou_nova_esfera

            while self.pausado and self.rodando:
                self.desenhar()
                pygame.display.flip()
                self.tratar_eventos()
                self.relogio.tick(15)
            if not self.rodando:
                return detectou_nova_esfera

            self.posicao = proxima_posicao
            self.custo_acumulado += a_star.planejador.custo_da_celula(proxima_posicao)
            self.caminho_percorrido.append(proxima_posicao)
            self.desenhar()
            pygame.display.flip()
            self.relogio.tick(self.movimento_fps)
            if self.sondar_radar():
                detectou_nova_esfera = True
                break

        return detectou_nova_esfera

    def explorar_mapa(self) -> bool:
        detectou_esfera = False
        total = len(self.waypoints)
        while self.waypoint_cursor < total:
            waypoint = self.waypoints[self.waypoint_cursor]
            if waypoint == self.posicao:
                if self.sondar_radar():
                    detectou_esfera = True
                    break
                self.waypoint_cursor += 1
                continue

            caminho = a_star.caminho_entre(self.posicao, waypoint)
            if self.mover_por_caminho(caminho):
                detectou_esfera = True
                break
            if not self.rodando:
                break
            if self.sondar_radar():
                detectou_esfera = True
                break

            self.waypoint_cursor += 1

        if self.waypoint_cursor >= total:
            self.waypoint_cursor = 0

        return detectou_esfera

    def coletar_esferas(self) -> None:
        while self.rodando and len(self.esferas_coletadas) < self.quantidade_esferas:
            pendentes = tuple(sorted(self.esferas_detectadas - self.esferas_coletadas))
            if not pendentes:
                break

            ordem = None
            menor_custo = 10 ** 9
            for ordem_cand in itertools.permutations(pendentes):
                custo_total = 0
                atual = self.posicao
                for alvo in ordem_cand:
                    custo_total += a_star.caminho_entre(atual, alvo).custo
                    atual = alvo
                if custo_total < menor_custo:
                    menor_custo = custo_total
                    ordem = ordem_cand

            if not ordem:
                break

            houve_nova_deteccao = False
            for destino in ordem:
                if destino in self.esferas_coletadas:
                    continue
                caminho = a_star.caminho_entre(self.posicao, destino)
                interrompeu = self.mover_por_caminho(caminho)
                if not self.rodando:
                    return
                if interrompeu or self.posicao != destino:
                    continue
                self.esferas_coletadas.add(destino)
                novos = self.sondar_radar()
                houve_nova_deteccao = houve_nova_deteccao or bool(novos)
                self.desenhar()
                pygame.display.flip()
                self.relogio.tick(self.movimento_fps)

            if houve_nova_deteccao:
                continue

    def desenhar(self) -> None:
        # fundo: imagem redimensionada e centralizada se disponível, senão gradiente
        if self._fundo_original:
            # recalcular escala 'cover' se necessário (tamanho da tela pode ter mudado)
            try:
                ow, oh = self._fundo_original.get_size()
                sw, sh = self.tela.get_size()
                scale = max((sw * self._fundo_scale_factor) / ow, (sh * self._fundo_scale_factor) / oh)
                new_w = max(1, int(ow * scale))
                new_h = max(1, int(oh * scale))
                if self._fundo_scaled is None or self._fundo_scaled.get_size() != (new_w, new_h):
                    self._fundo_scaled = pygame.transform.smoothscale(self._fundo_original, (new_w, new_h))
            except Exception:
                self._fundo_scaled = None

            if self._fundo_scaled:
                sw, sh = self.tela.get_size()
                iw, ih = self._fundo_scaled.get_size()
                x = (sw - iw) // 2
                y = (sh - ih) // 2
                # desenha gradiente e sobrepõe a imagem centralizada (preenchendo a tela)
                fundo = pygame.Surface((sw, sh))
                self.hud.desenhar_gradiente_vertical(fundo, (8, 12, 24), (24, 34, 54))
                self.tela.blit(fundo, (0, 0))
                self.tela.blit(self._fundo_scaled, (x, y))
        else:
            fundo = pygame.Surface((self.tela.get_width(), self.tela.get_height()))
            self.hud.desenhar_gradiente_vertical(fundo, (8, 12, 24), (24, 34, 54))
            self.tela.blit(fundo, (0, 0))

        # mapa
        for y in range(TAMANHO_MAPA):
            for x in range(TAMANHO_MAPA):
                terreno = mapa[y][x]
                cor = {1: (0, 170, 0), 0: (25, 90, 210), 2: (125, 80, 30), 3: (255, 60, 60)}[terreno]
                rect = pygame.Rect(
                    self.mapa_offset_x + x * TAMANHO_CELULA,
                    self.mapa_offset_y + y * TAMANHO_CELULA,
                    TAMANHO_CELULA,
                    TAMANHO_CELULA,
                )
                pygame.draw.rect(self.tela, cor, rect)
                pygame.draw.rect(self.tela, (55, 55, 55), rect, 1)

        # esferas detectadas
        for posicao in self.esferas_detectadas:
            cor = (180, 180, 180) if posicao in self.esferas_coletadas else (255, 195, 0)
            cx = self.mapa_offset_x + posicao[0] * TAMANHO_CELULA + TAMANHO_CELULA // 2
            cy = self.mapa_offset_y + posicao[1] * TAMANHO_CELULA + TAMANHO_CELULA // 2
            pygame.draw.circle(self.tela, cor, (cx, cy), max(3, TAMANHO_CELULA // 3))

        # alcance radar
        x = self.mapa_offset_x + max(0, self.posicao[0] - RADAR_ALCANCE) * TAMANHO_CELULA
        y = self.mapa_offset_y + max(0, self.posicao[1] - RADAR_ALCANCE) * TAMANHO_CELULA
        largura = (min(TAMANHO_MAPA - 1, self.posicao[0] + RADAR_ALCANCE) - max(0, self.posicao[0] - RADAR_ALCANCE) + 1) * TAMANHO_CELULA
        altura = (min(TAMANHO_MAPA - 1, self.posicao[1] + RADAR_ALCANCE) - max(0, self.posicao[1] - RADAR_ALCANCE) + 1) * TAMANHO_CELULA
        alcance = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(alcance, (255, 255, 0, 50), pygame.Rect(0, 0, largura, altura), 0)
        self.tela.blit(alcance, (x, y))

        # caminho percorrido
        for posicao in self.caminho_percorrido:
            rect = pygame.Rect(
                self.mapa_offset_x + posicao[0] * TAMANHO_CELULA + 4,
                self.mapa_offset_y + posicao[1] * TAMANHO_CELULA + 4,
                TAMANHO_CELULA - 8,
                TAMANHO_CELULA - 8,
            )
            pygame.draw.rect(self.tela, (30, 30, 30), rect, 1)

        # agente
        px = self.mapa_offset_x + self.posicao[0] * TAMANHO_CELULA + TAMANHO_CELULA // 2
        py = self.mapa_offset_y + self.posicao[1] * TAMANHO_CELULA + TAMANHO_CELULA // 2
        pygame.draw.circle(self.tela, (255, 255, 255), (px, py), max(4, TAMANHO_CELULA // 2))
        pygame.draw.circle(self.tela, (255, 0, 0), (px, py), max(2, TAMANHO_CELULA // 3))

        # HUD
        self.botoes_hud = self.hud.draw_panel(self)
        if self.mensagem_final:
            faixa = pygame.Surface((self.tela.get_width(), 36), pygame.SRCALPHA)
            faixa.fill((0, 0, 0, 160))
            self.tela.blit(faixa, (0, self.tela.get_height() - 36))
            self.desenhar_texto(self.mensagem_final, (10, self.tela.get_height() - 28), pequena=True)

    def desenhar_texto(self, texto: str, posicao: tuple[int, int], cor: tuple[int, int, int] = (255, 255, 255), pequena: bool = False) -> None:
        fonte = self.fonte_pequena if pequena else self.fonte
        superficie = fonte.render(texto, True, cor)
        self.tela.blit(superficie, posicao)

    def executar(self) -> None:
        self.sondar_radar()
        self.desenhar()
        pygame.display.flip()

        while self.rodando and len(self.esferas_coletadas) < self.quantidade_esferas:
            self.tratar_eventos()
            if not self.rodando:
                break

            self.explorar_mapa()
            if not self.rodando:
                break

            if self.esferas_detectadas - self.esferas_coletadas:
                self.coletar_esferas()
            if not self.rodando:
                break
            if len(self.esferas_coletadas) >= self.quantidade_esferas:
                break

            self.desenhar()
            pygame.display.flip()

        if self.rodando and len(self.esferas_coletadas) >= self.quantidade_esferas:
            caminho_retorno = a_star.caminho_entre(self.posicao, self.inicio)
            self.mover_por_caminho(caminho_retorno)
            if self.rodando:
                self.concluida = True
                self.mensagem_final = "Missão concluída: Goku reuniu todas as esferas e voltou para casa."

        self.desenhar()
        pygame.display.flip()

        if self.concluida and self.rodando:
            if not self.mensagem_final:
                tempo_final = self.formatar_tempo(self.tempo_decorrido_ms())
                self.mensagem_final = f"Missão concluída em {tempo_final}. Pressione ESC para fechar."
            while self.rodando:
                self.tratar_eventos()
                for evento in pygame.event.get(pygame.KEYDOWN):
                    if evento.key == pygame.K_ESCAPE:
                        self.rodando = False
                self.relogio.tick(30)
