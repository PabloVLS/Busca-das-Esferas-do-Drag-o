import pygame

from mapa_config import mapa


class RenderizadorCenario:
    def __init__(
        self,
        fator_escurecer_nao_percorrido: float,
        fator_escurecer_detectado_radar: float,
        radar_alcance: int,
        caminho_casa_mestre_kame: str,
    ):
        self.fator_escurecer_nao_percorrido = fator_escurecer_nao_percorrido
        self.fator_escurecer_detectado_radar = fator_escurecer_detectado_radar
        self.radar_alcance = radar_alcance
        self.caminho_casa_mestre_kame = caminho_casa_mestre_kame

        self._casa_mestre_kame_original: pygame.Surface | None = None
        self._casa_mestre_kame_escalada: pygame.Surface | None = None
        self._casa_mestre_kame_tamanho_px = 0
        try:
            self._casa_mestre_kame_original = pygame.image.load(self.caminho_casa_mestre_kame).convert_alpha()
        except Exception:
            self._casa_mestre_kame_original = None

    def obter_sprite_casa_mestre_kame(self, tamanho_celula: int) -> pygame.Surface | None:
        if self._casa_mestre_kame_original is None:
            return None

        tamanho_alvo = max(8, int(tamanho_celula * 1.6))
        if (
            self._casa_mestre_kame_escalada is None
            or self._casa_mestre_kame_tamanho_px != tamanho_alvo
        ):
            self._casa_mestre_kame_escalada = pygame.transform.smoothscale(
                self._casa_mestre_kame_original,
                (tamanho_alvo, tamanho_alvo),
            )
            self._casa_mestre_kame_tamanho_px = tamanho_alvo

        return self._casa_mestre_kame_escalada

    def desenhar(self, simulacao, tamanho_celula: int, tamanho_mapa: int) -> None:
        percorridas = set(simulacao.caminho_percorrido)
        for y in range(tamanho_mapa):
            for x in range(tamanho_mapa):
                terreno = mapa[y][x]
                cor = {1: (0, 170, 0), 0: (25, 90, 210), 2: (125, 80, 30), 3: (255, 60, 60)}[terreno]
                posicao = (x, y)
                if posicao not in percorridas:
                    if posicao in simulacao.celulas_conhecidas:
                        cor = tuple(max(0, int(canal * self.fator_escurecer_detectado_radar)) for canal in cor)
                    else:
                        cor = tuple(max(0, int(canal * self.fator_escurecer_nao_percorrido)) for canal in cor)

                rect = pygame.Rect(
                    simulacao.mapa_offset_x + x * tamanho_celula,
                    simulacao.mapa_offset_y + y * tamanho_celula,
                    tamanho_celula,
                    tamanho_celula,
                )
                pygame.draw.rect(simulacao.tela, cor, rect)
                pygame.draw.rect(simulacao.tela, (55, 55, 55), rect, 1)

                if terreno == 3:
                    sprite_casa = self.obter_sprite_casa_mestre_kame(tamanho_celula)
                    if sprite_casa is not None:
                        rect_casa = sprite_casa.get_rect(center=rect.center)
                        simulacao.tela.blit(sprite_casa, rect_casa)

        for posicao in simulacao.esferas_detectadas:
            cor = (180, 180, 180) if posicao in simulacao.esferas_coletadas else (255, 195, 0)
            cx = simulacao.mapa_offset_x + posicao[0] * tamanho_celula + tamanho_celula // 2
            cy = simulacao.mapa_offset_y + posicao[1] * tamanho_celula + tamanho_celula // 2
            pygame.draw.circle(simulacao.tela, cor, (cx, cy), max(3, tamanho_celula // 3))

        if simulacao.mostrar_esferas_ocultas:
            esferas_ocultas_visiveis = simulacao.esferas_ocultas - simulacao.esferas_detectadas - simulacao.esferas_coletadas
            for posicao in esferas_ocultas_visiveis:
                cx = simulacao.mapa_offset_x + posicao[0] * tamanho_celula + tamanho_celula // 2
                cy = simulacao.mapa_offset_y + posicao[1] * tamanho_celula + tamanho_celula // 2
                raio = max(3, tamanho_celula // 3)
                pygame.draw.circle(simulacao.tela, (255, 255, 0), (cx, cy), raio)

        x = simulacao.mapa_offset_x + max(0, simulacao.posicao[0] - self.radar_alcance) * tamanho_celula
        y = simulacao.mapa_offset_y + max(0, simulacao.posicao[1] - self.radar_alcance) * tamanho_celula
        largura = (min(tamanho_mapa - 1, simulacao.posicao[0] + self.radar_alcance) - max(0, simulacao.posicao[0] - self.radar_alcance) + 1) * tamanho_celula
        altura = (min(tamanho_mapa - 1, simulacao.posicao[1] + self.radar_alcance) - max(0, simulacao.posicao[1] - self.radar_alcance) + 1) * tamanho_celula
        alcance = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(alcance, (255, 255, 0, 50), pygame.Rect(0, 0, largura, altura), 0)
        simulacao.tela.blit(alcance, (x, y))

        for posicao in simulacao.caminho_percorrido:
            rect = pygame.Rect(
                simulacao.mapa_offset_x + posicao[0] * tamanho_celula + 4,
                simulacao.mapa_offset_y + posicao[1] * tamanho_celula + 4,
                tamanho_celula - 8,
                tamanho_celula - 8,
            )
            pygame.draw.rect(simulacao.tela, (30, 30, 30), rect, 1)

        px = simulacao.mapa_offset_x + simulacao.posicao[0] * tamanho_celula + tamanho_celula // 2
        py = simulacao.mapa_offset_y + simulacao.posicao[1] * tamanho_celula + tamanho_celula // 2
        sprite_agente = simulacao.estilo_goku.obter_sprite_agente(tamanho_celula)
        if sprite_agente is not None:
            rect_sprite = sprite_agente.get_rect(center=(px, py))
            simulacao.tela.blit(sprite_agente, rect_sprite)
        else:
            pygame.draw.circle(simulacao.tela, (255, 255, 255), (px, py), max(4, tamanho_celula // 2))
            pygame.draw.circle(simulacao.tela, (255, 0, 0), (px, py), max(2, tamanho_celula // 3))
