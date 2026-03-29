import pygame
import math


class HUD:
    def __init__(self, tela, fonte_pequena):
        self.tela = tela
        self.fonte_pequena = fonte_pequena
        self.animacao_tempo = 0

    def desenhar_gradiente_vertical(self, superficie: pygame.Surface, cor_topo: tuple[int, int, int], cor_base: tuple[int, int, int], alpha: int = 255) -> None:
        largura, altura = superficie.get_size()
        for y in range(altura):
            progresso = y / max(1, altura - 1)
            cor_rgb = tuple(
                int(cor_topo[indice] * (1 - progresso) + cor_base[indice] * progresso)
                for indice in range(3)
            )
            cor = (*cor_rgb, alpha) if alpha < 255 else cor_rgb
            pygame.draw.line(superficie, cor, (0, y), (largura, y))

    def desenhar_sombra(self, superficie: pygame.Surface, rect: pygame.Rect, raio: int = 4, alpha: int = 60) -> None:
        """Adiciona efeito de sombra suave."""
        sombra = pygame.Surface((rect.width + raio * 2, rect.height + raio * 2), pygame.SRCALPHA)
        pygame.draw.rect(sombra, (0, 0, 0, alpha), pygame.Rect(raio, raio, rect.width, rect.height), border_radius=12)
        superficie.blit(sombra, (rect.x - raio, rect.y - raio))

    def desenhar_chip_metrica_moderno(self, superficie: pygame.Surface, rect: pygame.Rect, titulo: str, valor: str, hover: bool = False) -> None:
        """Chip de métrica com design limpo e elegante."""
        # Sombra suave para profundidade
        self.desenhar_sombra(superficie, rect, raio=2, alpha=25)

        # Fundo com gradiente sutil
        chip = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        if hover:
            # Efeito de hover sutil
            cor_topo = (60, 70, 85)
            cor_base = (50, 60, 73)
            alpha_fundo = 200
        else:
            cor_topo = (45, 55, 70)
            cor_base = (35, 45, 58)
            alpha_fundo = 170

        self.desenhar_gradiente_vertical(chip, cor_topo, cor_base, alpha=alpha_fundo)

        # Sem bordas externas - design mais limpo
        # Destaque superior sutil para profundidade
        destaque = pygame.Surface((rect.width - 6, 1), pygame.SRCALPHA)
        destaque.fill((255, 255, 255, 15))
        chip.blit(destaque, (3, 3))

        # Texto centralizado sem ícone
        titulo_surface = self.fonte_pequena.render(f"{titulo}: {valor}", True, (240, 245, 252))
        texto_rect = titulo_surface.get_rect(center=(rect.width // 2, rect.height // 2))
        chip.blit(titulo_surface, texto_rect)

        superficie.blit(chip, rect.topleft)

    def desenhar_botao_moderno(self, superficie: pygame.Surface, rect: pygame.Rect, titulo: str, cor_base: tuple[int, int, int], hover: bool, icone_tipo: str = None) -> None:
        """Botão com design limpo e elegante."""
        # Sombra sutil
        sombra_alpha = 35 if hover else 20
        self.desenhar_sombra(superficie, rect, raio=3, alpha=sombra_alpha)

        botao = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        if hover:
            # Gradiente sutil no hover
            intensidade = 1.2
            cor_topo = tuple(min(255, int(c * intensidade)) for c in cor_base)
            cor_base_grad = tuple(min(255, int(c * (intensidade - 0.1))) for c in cor_base)
            alpha_fundo = 220
        else:
            cor_topo = tuple(min(255, int(c * 1.05)) for c in cor_base)
            cor_base_grad = tuple(max(0, int(c * 0.9)) for c in cor_base)
            alpha_fundo = 190

        self.desenhar_gradiente_vertical(botao, cor_topo, cor_base_grad, alpha=alpha_fundo)

        # Sem bordas externas - design mais limpo
        # Destaque superior sutil para profundidade
        destaque = pygame.Surface((rect.width - 6, 1), pygame.SRCALPHA)
        destaque.fill((255, 255, 255, 12))
        botao.blit(destaque, (3, 3))

        # Ícone se especificado
        if icone_tipo:
            if icone_tipo == "menos":
                pygame.draw.line(botao, (255, 255, 255), (rect.width//2 - 10, rect.height//2), (rect.width//2 + 10, rect.height//2), 3)
            elif icone_tipo == "mais":
                pygame.draw.line(botao, (255, 255, 255), (rect.width//2 - 10, rect.height//2), (rect.width//2 + 10, rect.height//2), 3)
                pygame.draw.line(botao, (255, 255, 255), (rect.width//2, rect.height//2 - 10), (rect.width//2, rect.height//2 + 10), 3)

        # Texto limpo sem sombras
        titulo_surface = self.fonte_pequena.render(titulo, True, (255, 255, 255))

        texto_rect = titulo_surface.get_rect(center=(rect.width//2, rect.height//2))
        botao.blit(titulo_surface, texto_rect)

        superficie.blit(botao, rect.topleft)

    def draw_panel(self, simulacao):
        self.animacao_tempo += 1

        largura_tela, altura_tela = self.tela.get_size()
        altura_barra = 90
        y_barra = altura_tela - altura_barra

        # Barra inferior com efeito glass ultra-moderno
        barra = pygame.Surface((largura_tela, altura_barra), pygame.SRCALPHA)

        # Fundo com gradiente complexo
        self.desenhar_gradiente_vertical(barra, (25, 35, 50), (15, 20, 30), alpha=160)

        # Efeito de vidro com reflexo sutil
        for i in range(3):
            alpha_reflexo = 15 - i * 3
            pygame.draw.line(barra, (255, 255, 255, alpha_reflexo), (0, i), (largura_tela, i), 1)

        # Linha de destaque superior com gradiente
        for x in range(largura_tela):
            progress = x / largura_tela
            color = (int(200 + 55 * progress), int(215 + 40 * progress), int(235 + 20 * progress), 60)
            pygame.draw.line(barra, color, (x, 0), (x, 0))

        # Painel de controles à direita com design limpo
        largura_controles = 360
        painel_controles = pygame.Rect(largura_tela - largura_controles - 12, 8, largura_controles, altura_barra - 16)

        # Fundo do painel com gradiente sutil
        painel_fundo = pygame.Surface((painel_controles.width, painel_controles.height), pygame.SRCALPHA)
        self.desenhar_gradiente_vertical(painel_fundo, (40, 50, 65), (30, 37, 50), alpha=160)
        # Sem bordas - design mais limpo
        barra.blit(painel_fundo, painel_controles.topleft)

        # Métricas organizadas em chips modernos - reduzidas para evitar poluição
        metricas = [
            ("Custo", f"{simulacao.custo_acumulado}"),
            ("Tempo", simulacao.formatar_tempo(simulacao.tempo_decorrido_ms())),
            ("Esferas", f"{len(simulacao.esferas_coletadas)}/{simulacao.quantidade_esferas}"),
            ("Rota", simulacao.texto_rota_em_andamento()),
            ("Velocidade", f"{simulacao.movimento_fps} fps"),
            ("Fase", simulacao.fase_atual()),
        ]

        # Layout inteligente das métricas
        limite_direita = painel_controles.left - 12
        x_inicial = 16
        x_atual = x_inicial
        y_linha_1 = 16
        y_linha_2 = 50
        segunda_linha = False

        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_local = (mouse_x, mouse_y - y_barra)

        for titulo, valor in metricas:
            titulo_surface = self.fonte_pequena.render(f"{titulo}: {valor}", True, (240, 245, 252))
            largura_chip = titulo_surface.get_width() + 40
            rect_chip = pygame.Rect(x_atual, y_linha_2 if segunda_linha else y_linha_1, largura_chip, 40)

            if rect_chip.right > limite_direita:
                if segunda_linha:
                    break
                segunda_linha = True
                x_atual = x_inicial
                rect_chip = pygame.Rect(x_atual, y_linha_2, largura_chip, 32)
                if rect_chip.right > limite_direita:
                    continue

            hover = rect_chip.collidepoint(mouse_local)
            self.desenhar_chip_metrica_moderno(barra, rect_chip, titulo, valor, hover)
            x_atual += largura_chip + 14

        # Botões elegantes
        largura_botao = 110
        altura_botao = 42
        espacamento_botoes = 10
        margem_direita = 24

        x_botao_rapido = largura_tela - margem_direita - largura_botao
        x_botao_lento = x_botao_rapido - espacamento_botoes - largura_botao
        x_botao_toggle = x_botao_lento - espacamento_botoes - largura_botao
        y_botao = 10

        botao_mais_devagar = pygame.Rect(x_botao_lento, y_botao, largura_botao, altura_botao)
        botao_mais_rapido = pygame.Rect(x_botao_rapido, y_botao, largura_botao, altura_botao)
        botao_toggle_esferas = pygame.Rect(x_botao_toggle, y_botao, largura_botao, altura_botao)

        hover_lento = botao_mais_devagar.collidepoint(mouse_local)
        hover_rapido = botao_mais_rapido.collidepoint(mouse_local)
        hover_toggle = botao_toggle_esferas.collidepoint(mouse_local)

        self.desenhar_botao_moderno(
            barra,
            botao_mais_devagar,
            "Mais Lento",
            (175, 130, 76),
            hover_lento,
            None,
        )
        self.desenhar_botao_moderno(
            barra,
            botao_mais_rapido,
            "Mais Rápido",
            (102, 174, 133),
            hover_rapido,
            None,
        )
        self.desenhar_botao_moderno(
            barra,
            botao_toggle_esferas,
            "Ocultar" if simulacao.mostrar_esferas_ocultas else "Mostrar",
            (110, 132, 190),
            hover_toggle,
            None,
        )

        # Indicador de status animado
        if simulacao.pausado:
            # Pulsação quando pausado
            alpha_pulse = int(128 + 127 * math.sin(self.animacao_tempo * 0.1))
            pygame.draw.circle(barra, (255, 100, 100, alpha_pulse), (largura_tela - 40, 15), 6)
            pygame.draw.polygon(barra, (255, 255, 255), [(largura_tela - 45, 10), (largura_tela - 35, 15), (largura_tela - 45, 20)])

        # Texto de ajuda com estilo moderno
        texto_ajuda = "[P / ESPAÇO] pausar  |  [ESC] sair"
        ajuda_surface = self.fonte_pequena.render(texto_ajuda, True, (199, 211, 229))
        ajuda_x = largura_tela - margem_direita - ajuda_surface.get_width()
        ajuda_y = altura_barra - ajuda_surface.get_height() - 12
        barra.blit(ajuda_surface, (ajuda_x, ajuda_y))

        self.tela.blit(barra, (0, y_barra))

        return {
            "mais_devagar": botao_mais_devagar.move(0, y_barra),
            "mais_rapido": botao_mais_rapido.move(0, y_barra),
            "toggle_esferas": botao_toggle_esferas.move(0, y_barra),
        }
