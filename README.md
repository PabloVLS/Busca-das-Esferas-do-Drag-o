# Esferas do Dragao

Simulacao em 2D do trabalho de busca heuristica com A*, radar de alcance limitado e coleta das 7 Esferas do Dragao.

## Requisitos

- Python 3.8+
- `pygame`

## Como executar

No terminal, dentro da pasta do projeto:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Se o seu ambiente Python exigir um executavel especifico, use o caminho configurado no seu sistema.

## Como funciona

- O mapa fica em `mapa_config.py`.
- Parâmetros da simulação (radar, penalidades, assets e esferas manuais) ficam em `config.py`.
- O algoritmo de caminho A* fica em `a_star.py`.
- A escolha de fronteiras para exploracao fica em `estrategia_exploracao.py`.
- O ponto vermelho indica a Ilha do Mestre Kame.
- As esferas sao geradas aleatoriamente ao iniciar a simulacao.
- O agente explora o mapa usando pontos estrategicos para cobrir toda a area com o radar.
- Quando as esferas sao detectadas, o agente usa A* para planejar o menor custo de deslocamento.
- O custo acumulado aparece na tela durante toda a execucao.

## Editando o mapa

Altere a matriz `mapa` em `mapa_config.py` para mudar o terreno em qualquer posicao.

Valores usados:

- `0` = agua
- `1` = grama
- `2` = montanha
- `3` = Ilha do Mestre Kame
