import random
from datetime import timedelta

import pygame

import heuristica
from config import (
    AGENTE_IMAGEM_CAMINHO,
    CASA_MESTRE_KAME_IMAGEM_CAMINHO,
    FATOR_ESCURECER_DETECTADO_RADAR,
    FATOR_ESCURECER_NAO_PERCORRIDO,
    FUNDO_IMAGEM_CAMINHO,
    MANUAL_ESFERAS,
    MARGEM_TELA,
    MOVIMENTO_FPS,
    MOVIMENTO_FPS_MAX,
    MOVIMENTO_FPS_MIN,
    PENALIDADE_AGUA_DESTINO,
    PENALIDADE_AGUA_PASSO,
    PENALIDADE_MONTANHA_DESTINO,
    PENALIDADE_MONTANHA_PASSO,
    QUANTIDADE_ESFERAS,
    RADAR_ALCANCE,
    TERRENO_DESCONHECIDO_PADRAO,
)
from estrategia_exploracao import EstrategiaExploracao
from estilo_goku import EstiloGoku
from hud import HUD
from mapa_config import TAMANHO_MAPA
from mundo import Mapa
from navegacao_agente import NavegacaoAgente
from renderizador_cenario import RenderizadorCenario

TAMANHO_CELULA = 15


class Simulacao:
    def __init__(self, tela, fonte, fonte_pequena, relogio):
        self.tela = tela
        self.fonte = fonte
        self.fonte_pequena = fonte_pequena
        self.relogio = relogio

        largura_tela, altura_tela = self.tela.get_size()
        global TAMANHO_CELULA
        tamanho_celula_horizontal = max(12, (largura_tela - (MARGEM_TELA * 3)) // TAMANHO_MAPA)
        tamanho_celula_vertical = max(12, (altura_tela - (MARGEM_TELA * 2)) // TAMANHO_MAPA)
        map_scale_factor = 0.85
        TAMANHO_CELULA = max(8, int(max(12, min(tamanho_celula_horizontal, tamanho_celula_vertical)) * map_scale_factor))

        self.tamanho_mapa_px = TAMANHO_MAPA * TAMANHO_CELULA
        bar_height = 72
        self.mapa_offset_x = max(MARGEM_TELA, (largura_tela - self.tamanho_mapa_px) // 2)
        self.mapa_offset_y = max(MARGEM_TELA, (altura_tela - bar_height - self.tamanho_mapa_px) // 2)

        self.quantidade_esferas = QUANTIDADE_ESFERAS
        self.radar_alcance = RADAR_ALCANCE
        self.rng = random.Random()

        self.mundo = Mapa(radar_alcance=self.radar_alcance,quantidade_esferas=self.quantidade_esferas,manual_esferas=MANUAL_ESFERAS,)
        self.estrategia_exploracao = EstrategiaExploracao(mundo=self.mundo,terreno_desconhecido_padrao=TERRENO_DESCONHECIDO_PADRAO,penalidade_agua_passo=PENALIDADE_AGUA_PASSO,penalidade_montanha_passo=PENALIDADE_MONTANHA_PASSO,penalidade_agua_destino=PENALIDADE_AGUA_DESTINO,penalidade_montanha_destino=PENALIDADE_MONTANHA_DESTINO,)
        self.estilo_goku = EstiloGoku(tela=self.tela,caminho_fundo=FUNDO_IMAGEM_CAMINHO,caminho_agente=AGENTE_IMAGEM_CAMINHO,)
        self.renderizador = RenderizadorCenario(fator_escurecer_nao_percorrido=FATOR_ESCURECER_NAO_PERCORRIDO,fator_escurecer_detectado_radar=FATOR_ESCURECER_DETECTADO_RADAR,radar_alcance=RADAR_ALCANCE,caminho_casa_mestre_kame=CASA_MESTRE_KAME_IMAGEM_CAMINHO,)

        self.inicio = self.mundo.inicio
        self.posicao = self.inicio
        self.esferas_ocultas = self.mundo.gerar_esferas(self.rng, self.inicio)
        self.esferas_detectadas: set[tuple[int, int]] = set()
        self.esferas_coletadas: set[tuple[int, int]] = set()
        self.caminho_percorrido: list[tuple[int, int]] = [self.inicio]
        self.custo_acumulado = 0
        self.celulas_conhecidas = self.mundo.celulas_conhecidas
        self.terreno_conhecido = self.mundo.terreno_conhecido
        self.movimento_fps = MOVIMENTO_FPS
        self.mostrar_esferas_ocultas = False
        self.passos_rota_em_andamento = 0
        self.rodando = True
        self.concluida = False
        self.mensagem_final = ""
        self.pausado = False
        self._pausa_inicio_ms = None
        self._tempo_inicial_ms = pygame.time.get_ticks()
        self._tempo_pausado_ms = 0
        self.botoes_hud = {}

        self.hud = HUD(self.tela, self.fonte_pequena)
        self.navegacao = NavegacaoAgente(self)

        self.mundo.atualizar_mapa_conhecido(self.posicao)

    def fase_atual(self) -> str:
        if self.concluida:
            return "Concluída"
        if len(self.esferas_coletadas) >= self.quantidade_esferas:
            return "Voltando para casa"
        if self.esferas_detectadas:
            return "Coletando"
        return "Explorando"

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

    def processar_clique(self, posicao: tuple[int, int]) -> None:
        if self.botoes_hud.get("mais_devagar") and self.botoes_hud["mais_devagar"].collidepoint(posicao):
            self.desacelerar_movimento()
        elif self.botoes_hud.get("mais_rapido") and self.botoes_hud["mais_rapido"].collidepoint(posicao):
            self.acelerar_movimento()
        elif self.botoes_hud.get("toggle_esferas") and self.botoes_hud["toggle_esferas"].collidepoint(posicao):
            self.alternar_visualizacao_esferas()

    def acelerar_movimento(self) -> None:
        self.movimento_fps = min(MOVIMENTO_FPS_MAX, self.movimento_fps + 1)

    def desacelerar_movimento(self) -> None:
        self.movimento_fps = max(MOVIMENTO_FPS_MIN, self.movimento_fps - 1)

    def alternar_visualizacao_esferas(self) -> None:
        self.mostrar_esferas_ocultas = not self.mostrar_esferas_ocultas

    def texto_rota_em_andamento(self) -> str:
        return f"{self.passos_rota_em_andamento} passos"

    def aguardar_se_pausado(self) -> None:
        while self.pausado and self.rodando:
            self.desenhar()
            pygame.display.flip()
            self.tratar_eventos()
            self.relogio.tick(15)

    def mover_por_caminho(self, caminho: heuristica.ResultadoCaminho) -> bool:
        detectou_nova_esfera = False
        self.navegacao.iniciar_rota(caminho)

        for proxima_posicao in caminho.caminho[1:]:
            self.tratar_eventos()
            if not self.rodando:
                self.navegacao.finalizar_rota()
                return detectou_nova_esfera

            self.aguardar_se_pausado()
            if not self.rodando:
                self.navegacao.finalizar_rota()
                return detectou_nova_esfera

            detectou_nova_esfera = self.navegacao.aplicar_passo(proxima_posicao)
            self.desenhar()
            pygame.display.flip()
            self.relogio.tick(self.movimento_fps)

            if detectou_nova_esfera:
                break

        self.navegacao.finalizar_rota()
        return detectou_nova_esfera

    def desenhar_texto(self,texto: str,posicao: tuple[int, int],cor: tuple[int, int, int] = (255, 255, 255), pequena: bool = False,) -> None:
        fonte = self.fonte_pequena if pequena else self.fonte
        superficie = fonte.render(texto, True, cor)
        self.tela.blit(superficie, posicao)

    def desenhar(self) -> None:
        self.estilo_goku.desenhar_fundo(self.hud, self.tela)
        self.renderizador.desenhar(self, TAMANHO_CELULA, TAMANHO_MAPA)

        self.botoes_hud = self.hud.draw_panel(self)
        if self.mensagem_final:
            faixa = pygame.Surface((self.tela.get_width(), 36), pygame.SRCALPHA)
            faixa.fill((0, 0, 0, 160))
            self.tela.blit(faixa, (0, self.tela.get_height() - 36))
            self.desenhar_texto(self.mensagem_final, (10, self.tela.get_height() - 28), pequena=True)

    def executar(self) -> None:
        self.mundo.sondar_radar(posicao_atual=self.posicao,esferas_ocultas=self.esferas_ocultas, esferas_detectadas=self.esferas_detectadas,esferas_coletadas=self.esferas_coletadas,)
        self.desenhar()
        pygame.display.flip()

        while self.rodando and len(self.esferas_coletadas) < self.quantidade_esferas:
            self.tratar_eventos()
            if not self.rodando:
                break

            if self.esferas_detectadas - self.esferas_coletadas:
                self.navegacao.coletar_esferas()
                if not self.rodando:
                    break
                continue

            self.navegacao.explorar_mapa()
            if not self.rodando:
                break

            if self.esferas_detectadas - self.esferas_coletadas:
                self.navegacao.coletar_esferas()
                if not self.rodando:
                    break
            if len(self.esferas_coletadas) >= self.quantidade_esferas:
                break

            self.desenhar()
            pygame.display.flip()

        if self.rodando and len(self.esferas_coletadas) >= self.quantidade_esferas:
            caminho_retorno = heuristica.planejador.buscar(self.posicao, self.inicio)
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
                self.relogio.tick(30)
