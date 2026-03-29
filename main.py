import pygame
from simulation import Simulacao


def main() -> None:
    pygame.init()
    tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Busca das Esferas do Dragão - A*")
    fonte = pygame.font.SysFont("arial", 24, bold=True)
    fonte_pequena = pygame.font.SysFont("arial", 20)
    relogio = pygame.time.Clock()

    simulacao = Simulacao(tela, fonte, fonte_pequena, relogio)
    try:
        simulacao.executar()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()