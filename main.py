import pygame
from mapa_config import TAMANHO_MAPA
from simulation import Simulacao, TAMANHO_CELULA, PAINEL_LARGURA, MARGEM_TELA


def main() -> None:
    pygame.init()
    tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Busca das Esferas do Dragão - A*")
    fonte = pygame.font.SysFont("arial", 18, bold=True)
    fonte_pequena = pygame.font.SysFont("arial", 15)
    fonte_titulo = pygame.font.SysFont("arial", 22, bold=True)
    relogio = pygame.time.Clock()

    simulacao = Simulacao(tela, fonte, fonte_pequena, fonte_titulo, relogio)
    try:
        simulacao.executar()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()