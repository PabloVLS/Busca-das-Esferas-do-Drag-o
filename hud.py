import pygame

class HUD:
    def __init__(self, tela, fonte, fonte_pequena, fonte_titulo, painel_largura, margem):
        self.tela = tela
        self.fonte = fonte
        self.fonte_pequena = fonte_pequena
        self.fonte_titulo = fonte_titulo
        self.painel_largura = painel_largura
        self.margem = margem

    def desenhar_texto(self, superficie_destino: pygame.Surface, texto: str, posicao: tuple[int, int], cor: tuple[int, int, int] = (255, 255, 255), pequena: bool = False) -> None:
        fonte = self.fonte_pequena if pequena else self.fonte
        superficie_texto = fonte.render(texto, True, cor)
        superficie_destino.blit(superficie_texto, posicao)

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

    def desenhar_borda_elegante(self, superficie: pygame.Surface) -> None:
        rect = superficie.get_rect()
        pygame.draw.rect(superficie, (150, 165, 185, 200), rect, 1, border_radius=16)

    def desenhar_label_valor(self, superficie: pygame.Surface, titulo: str, valor: str, posicao: tuple[int, int], cor: tuple[int, int, int]) -> None:
        x, y = posicao
        fonte = self.fonte_pequena
        superficie_texto_titulo = fonte.render(titulo, True, (215, 215, 230))
        superficie_texto_valor = self.fonte.render(valor, True, cor)
        superficie.blit(superficie_texto_titulo, (x, y))
        superficie.blit(superficie_texto_valor, (x, y + 16))

    def desenhar_metrica(self, superficie: pygame.Surface, rect: pygame.Rect, titulo: str, valor: str, cor: tuple[int, int, int]) -> None:
        cartao = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        self.desenhar_gradiente_vertical(cartao, (45, 55, 70), (35, 42, 55), alpha=160)
        pygame.draw.rect(cartao, (100, 115, 135, 180), cartao.get_rect(), 1, border_radius=12)
        pygame.draw.rect(cartao, (255, 255, 255, 25), cartao.get_rect().inflate(-3, -3), 1, border_radius=11)

        titulo_surface = self.fonte_pequena.render(titulo, True, (180, 190, 205))
        valor_surface = self.fonte.render(valor, True, cor)
        cartao.blit(titulo_surface, (14, 10))
        cartao.blit(valor_surface, (14, 25))
        superficie.blit(cartao, rect.topleft)

    def desenhar_botao(self, superficie: pygame.Surface, rect: pygame.Rect, titulo: str, subtitulo: str, cor_base: tuple[int, int, int], cor_borda: tuple[int, int, int]) -> None:
        fundo = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        cor_top = tuple(min(255, int(c * 1.15)) for c in cor_base)
        cor_bot = tuple(max(0, int(c * 0.85)) for c in cor_base)
        self.desenhar_gradiente_vertical(fundo, cor_top, cor_bot, alpha=200)
        pygame.draw.rect(fundo, (*cor_borda, 150), fundo.get_rect(), 2, border_radius=11)
        pygame.draw.rect(fundo, (255, 255, 255, 40), fundo.get_rect().inflate(-4, -4), 1, border_radius=10)
        superficie.blit(fundo, rect.topleft)

        titulo_surface = self.fonte_pequena.render(titulo, True, (245, 248, 250))
        subtitulo_surface = self.fonte_pequena.render(subtitulo, True, (220, 225, 230))
        titulo_x = rect.x + 10
        titulo_y = rect.y + 6
        superficie.blit(titulo_surface, (titulo_x, titulo_y))
        superficie.blit(subtitulo_surface, (titulo_x, titulo_y + 16))

    def desenhar_separador(self, superficie: pygame.Surface, y: int, largura: int) -> None:
        pygame.draw.line(superficie, (120, 135, 155, 80), (18, y), (largura - 18, y), 1)

    def draw_panel(self, simulacao):
        painel_largura = self.painel_largura
        painel_altura = self.tela.get_height() - (self.margem * 2)
        painel_x = self.margem
        painel_y = self.margem

        sombra = pygame.Surface((painel_largura, painel_altura), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 100))
        self.tela.blit(sombra, (painel_x + 4, painel_y + 4))

        painel = pygame.Surface((painel_largura, painel_altura), pygame.SRCALPHA)
        # Fundo elegante com gradiente suave
        self.desenhar_gradiente_vertical(painel, (35, 45, 60), (25, 32, 45), alpha=190)

        # Borda elegante
        self.desenhar_borda_elegante(painel)

        self.desenhar_texto(painel, "Missão Dragon Ball", (18, 16), (200, 215, 235), pequena=False)
        self.desenhar_texto(painel, "Status da Missão", (18, 36), (155, 170, 190), pequena=True)
        self.desenhar_separador(painel, 50, painel_largura)

        margem_interna = 18
        espacamento_vertical = 13
        cartao_largura = painel_largura - (margem_interna * 2)
        cartao_altura = 56
        linha_y = 60

        cartoes = [
            ("Custo", str(simulacao.custo_acumulado), (170, 190, 215)),
            ("Tempo", simulacao.formatar_tempo(simulacao.tempo_decorrido_ms()), (180, 200, 220)),
            ("Detectadas", str(len(simulacao.esferas_detectadas)), (210, 190, 160)),
            ("Coletadas", f"{len(simulacao.esferas_coletadas)} / {simulacao.quantidade_esferas}", (170, 210, 180)),
            ("Faltam", str(simulacao.quantidade_esferas - len(simulacao.esferas_coletadas)), (200, 180, 160)),
            ("Velocidade", f"{simulacao.movimento_fps} fps", (190, 200, 220)),
            ("Fase", simulacao.fase_atual(), (180, 200, 225)),
            ("Alcance", f"{simulacao.radar_alcance} células", (175, 200, 225)),
        ]

        # Empilha métricas verticalmente com espaçamento maior para melhorar leitura
        for indice, (titulo, valor, cor) in enumerate(cartoes):
            rect = pygame.Rect(
                margem_interna,
                linha_y + indice * (cartao_altura + espacamento_vertical),
                cartao_largura,
                cartao_altura,
            )
            self.desenhar_metrica(painel, rect, titulo, valor, cor)

        separador_y = linha_y + len(cartoes) * (cartao_altura + espacamento_vertical) + 8
        self.desenhar_separador(painel, separador_y, painel_largura)

        # Botões elegantes lado a lado
        botao_width = (cartao_largura - 18) // 2
        botao_height = 44
        botao_x_left = margem_interna
        botao_x_right = margem_interna + botao_width + 18
        botao_y = separador_y + 18

        botao_mais_devagar = pygame.Rect(botao_x_left, botao_y, botao_width, botao_height)
        botao_mais_rapido = pygame.Rect(botao_x_right, botao_y, botao_width, botao_height)
        self.desenhar_botao(painel, botao_mais_devagar, "Mais Lento", "reduzir velocidade", (140, 110, 80), (160, 130, 100))
        self.desenhar_botao(painel, botao_mais_rapido, "Mais Rápido", "aumentar velocidade", (80, 140, 110), (110, 160, 135))

        # Barra de progresso elegante
        barra_x = margem_interna
        barra_y = botao_y + botao_height + 18
        barra_largura = cartao_largura
        barra_altura = 18
        
        # Fundo da barra
        pygame.draw.rect(painel, (50, 60, 75, 200), (barra_x, barra_y, barra_largura, barra_altura), border_radius=9)
        pygame.draw.rect(painel, (100, 120, 145, 150), (barra_x, barra_y, barra_largura, barra_altura), 1, border_radius=9)
        
        # Barra preenchida com gradiente suave
        progresso = len(simulacao.esferas_coletadas) / simulacao.quantidade_esferas if simulacao.quantidade_esferas else 0
        barra_preenchida = int(barra_largura * progresso)
        if barra_preenchida > 0:
            barra_surf = pygame.Surface((barra_preenchida, barra_altura), pygame.SRCALPHA)
            self.desenhar_gradiente_vertical(barra_surf, (160, 180, 210), (140, 160, 190), alpha=220)
            painel.blit(barra_surf, (barra_x, barra_y))

        # Instruções com estilo elegante
        instr_y = barra_y + barra_altura + 14
        self.desenhar_texto(painel, "[P / ESPAÇO] pausar · [ESC] sair", (margem_interna, instr_y), (150, 165, 185), pequena=True)
        self.tela.blit(painel, (painel_x, painel_y))

        return {
            "mais_devagar": botao_mais_devagar.move(painel_x, painel_y),
            "mais_rapido": botao_mais_rapido.move(painel_x, painel_y),
        }
