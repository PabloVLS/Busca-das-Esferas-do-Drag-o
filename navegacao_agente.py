import itertools

import heuristica


class NavegacaoAgente:
    def __init__(self, simulacao):
        self.sim = simulacao

    def coletar_esfera_na_posicao_atual(self) -> bool:
        if self.sim.posicao in self.sim.esferas_ocultas and self.sim.posicao not in self.sim.esferas_coletadas:
            self.sim.esferas_detectadas.add(self.sim.posicao)
            self.sim.esferas_coletadas.add(self.sim.posicao)
            return True
        return False

    def iniciar_rota(self, caminho: heuristica.ResultadoCaminho) -> None:
        self.sim.passos_rota_em_andamento = max(0, len(caminho.caminho) - 1)

    def finalizar_rota(self) -> None:
        self.sim.passos_rota_em_andamento = 0

    def aplicar_passo(self, proxima_posicao: tuple[int, int]) -> bool:
        self.sim.posicao = proxima_posicao
        self.sim.custo_acumulado += heuristica.planejador.custo_da_celula(proxima_posicao)
        self.sim.caminho_percorrido.append(proxima_posicao)
        self.sim.passos_rota_em_andamento = max(0, self.sim.passos_rota_em_andamento - 1)

        self.coletar_esfera_na_posicao_atual()

        novos_radar = self.sim.mundo.sondar_radar(
            posicao_atual=self.sim.posicao,
            esferas_ocultas=self.sim.esferas_ocultas,
            esferas_detectadas=self.sim.esferas_detectadas,
            esferas_coletadas=self.sim.esferas_coletadas,
        )
        return bool(novos_radar)

    def explorar_mapa(self) -> bool:
        while self.sim.rodando:
            escolha_fronteira = self.sim.estrategia_exploracao.selecionar_melhor_fronteira(self.sim.posicao)
            if escolha_fronteira is None:
                return False

            _, caminho = escolha_fronteira
            if self.sim.mover_por_caminho(caminho):
                return True
            if not self.sim.rodando:
                return False

            if self.sim.mundo.sondar_radar(
                posicao_atual=self.sim.posicao,
                esferas_ocultas=self.sim.esferas_ocultas,
                esferas_detectadas=self.sim.esferas_detectadas,
                esferas_coletadas=self.sim.esferas_coletadas,
            ):
                return True

            if self.sim.esferas_detectadas - self.sim.esferas_coletadas:
                return True

        return False

    def coletar_esferas(self) -> None:
        while self.sim.rodando and len(self.sim.esferas_coletadas) < self.sim.quantidade_esferas:
            pendentes = tuple(sorted(self.sim.esferas_detectadas - self.sim.esferas_coletadas))
            if not pendentes:
                break

            ordem = None
            menor_custo = 10 ** 9
            for ordem_candidata in itertools.permutations(pendentes):# gera todas ordens-canditas pra coletar as esferas pendentes
                custo_total = 0
                atual = self.sim.posicao
                for alvo in ordem_candidata:
                    custo_total += heuristica.planejador.buscar(atual, alvo).custo
                    atual = alvo
                if custo_total < menor_custo:
                    menor_custo = custo_total
                    ordem = ordem_candidata

            if not ordem:
                break

            houve_nova_deteccao = False
            for destino in ordem:
                if destino in self.sim.esferas_coletadas:
                    continue

                caminho = heuristica.planejador.buscar(self.sim.posicao, destino)
                interrompeu = self.sim.mover_por_caminho(caminho)
                if not self.sim.rodando:
                    return
                if interrompeu or self.sim.posicao != destino:
                    continue

                self.sim.esferas_coletadas.add(destino)
                novos = self.sim.mundo.sondar_radar(
                    posicao_atual=self.sim.posicao,
                    esferas_ocultas=self.sim.esferas_ocultas,
                    esferas_detectadas=self.sim.esferas_detectadas,
                    esferas_coletadas=self.sim.esferas_coletadas,
                )
                houve_nova_deteccao = houve_nova_deteccao or bool(novos)

            if houve_nova_deteccao:
                continue
