import os

import pygame


class EstiloGoku:
    def __init__(self, tela: pygame.Surface, caminho_fundo: str, caminho_agente: str) -> None:
        self.tela = tela
        self.caminho_fundo = caminho_fundo
        self.caminho_agente = caminho_agente

        self._fundo_original: pygame.Surface | None = None
        self._fundo_scaled: pygame.Surface | None = None
        self._fundo_scale_factor = 1.0

        self._agente_sprite_original: pygame.Surface | None = None
        self._agente_sprite_escalado: pygame.Surface | None = None
        self._agente_sprite_tamanho_px = 0

        self._carregar_fundo()
        self._carregar_sprite_agente()

    def _carregar_fundo(self) -> None:
        try:
            if os.path.exists(self.caminho_fundo):
                self._fundo_original = pygame.image.load(self.caminho_fundo).convert()
            if self._fundo_original is None:
                return
            ow, oh = self._fundo_original.get_size()
            sw, sh = self.tela.get_size()
            scale = max((sw * self._fundo_scale_factor) / ow, (sh * self._fundo_scale_factor) / oh)
            new_w = max(1, int(ow * scale))
            new_h = max(1, int(oh * scale))
            self._fundo_scaled = pygame.transform.smoothscale(self._fundo_original, (new_w, new_h))
        except Exception:
            self._fundo_original = None
            self._fundo_scaled = None

    def _carregar_sprite_agente(self) -> None:
        try:
            caminho_agente = self.caminho_agente
            if not os.path.exists(caminho_agente):
                caminho_agente = os.path.join(os.path.dirname(__file__), "img", "GokuPixel.png")
            if os.path.exists(caminho_agente):
                self._agente_sprite_original = pygame.image.load(caminho_agente).convert_alpha()
        except Exception:
            self._agente_sprite_original = None

    def desenhar_fundo(self, hud, tela_destino: pygame.Surface) -> None:
        if self._fundo_original:
            try:
                ow, oh = self._fundo_original.get_size()
                sw, sh = tela_destino.get_size()
                scale = max((sw * self._fundo_scale_factor) / ow, (sh * self._fundo_scale_factor) / oh)
                new_w = max(1, int(ow * scale))
                new_h = max(1, int(oh * scale))
                if self._fundo_scaled is None or self._fundo_scaled.get_size() != (new_w, new_h):
                    self._fundo_scaled = pygame.transform.smoothscale(self._fundo_original, (new_w, new_h))
            except Exception:
                self._fundo_scaled = None

            if self._fundo_scaled:
                sw, sh = tela_destino.get_size()
                iw, ih = self._fundo_scaled.get_size()
                x = (sw - iw) // 2
                y = (sh - ih) // 2
                fundo = pygame.Surface((sw, sh))
                hud.desenhar_gradiente_vertical(fundo, (8, 12, 24), (24, 34, 54))
                tela_destino.blit(fundo, (0, 0))
                tela_destino.blit(self._fundo_scaled, (x, y))
                return

        fundo = pygame.Surface((tela_destino.get_width(), tela_destino.get_height()))
        hud.desenhar_gradiente_vertical(fundo, (8, 12, 24), (24, 34, 54))
        tela_destino.blit(fundo, (0, 0))

    def obter_sprite_agente(self, tamanho_celula: int) -> pygame.Surface | None:
        if self._agente_sprite_original is None:
            return None

        tamanho_alvo = max(8, int(tamanho_celula * 1.95))
        if self._agente_sprite_escalado is None or self._agente_sprite_tamanho_px != tamanho_alvo:
            self._agente_sprite_escalado = pygame.transform.smoothscale(
                self._agente_sprite_original,
                (tamanho_alvo, tamanho_alvo),
            )
            self._agente_sprite_tamanho_px = tamanho_alvo

        return self._agente_sprite_escalado
