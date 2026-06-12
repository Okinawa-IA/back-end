# Relatório e documentação — Okinawa IA

## 1 - Arquitetura e divisão por arquivo

O projeto foi feito anteriormente sem orientação a objetos. Porém, achamos que a arquitetura desenvolvida pelo professor ficou muito mais organizada, portanto refatoramos nosso projeto para Programação Orientada a Objetos (OOP).

* **`app/main.py`:** Atua como ponto de entrada da aplicação HTTP (FastAPI). Instancia o agente principal. Recebe o payload da partida e delega a decisão para o agente com base na fase do turno, retornando a resposta imediatamente para a API do professor.
* **`app/schemas.py`:** Arquivo feito durante a aula com o professor. Centraliza todos os Data Transfer Objects (DTOs) utilizando Pydantic. 
* **`app/logic/state.py`:** Contém a classe `BoardState` composta por métodos estáticos (se não fosse estático precisariamos ficar instanciando a classe). Cuida das regras físicas do tabuleiro: calcula limites de adjacência, mapeia professores vivos, extrai a "Visão Local 3x3" e levanta os movimentos matematicamente válidos. Contém um filtro anti-suicida, que impede de mentorar um aluno pro um Nível 3 caso haja um inimigo em posição perigosa ao lado.
* **`app/logic/qtable.py`:** Contém a classe `QLearningManager`. Gerencia a tabela Q via `.pickle` e a lógica do Q-Learning. Contém a função de recompensa e executa a simulação do estado futuro (Equação de Bellman) via cópias do tabuleiro com a biblioteca copy.
* **`app/logic/agent.py`:** Contém a classe `OkinawaAgent`. Contém a parte estratégica para acionar estratégias emergenciais (vitória imediata ou bloqueio de vitória inimiga). Caso não haja alguma emergência, identifica professores sob ameaça e delega a jogada ao Q-Learning.
* **`treinar_offline.py`:** Script executável local para rodar partidas onde a IA joga contra outro agente idêntico. Gerencia o decaimento do Epsilon e salva arquivos acumulativos a cada 50k partidas na pasta storage.

## 2 - Jogador Inteligente - Estratégia

### 2.1 - Tomada de decisão e algoritmos
A tomada de decisão foi separada em duas camadas para otimizar tempo e memória:

* **Heurísticas emergenciais (Visão Global):** Implementada no `agent.py`, analisa o tabuleiro inteiro. Se encontrar um caminho aberto para vitória imediata ou notar que o inimigo vai ganhar no próximo turno em uma casa de Nível 3 vazia, o bot age por heurística (construindo um teto Nível 4, por exemplo) e ignora o aprendizado de máquina.
* **Q-Learning de alcance reduzido (Visão Local):** Focada apenas no combate posicional. Ficamos preocupados principalmente com a questão do armazenamento, com o tempo de treino e com a explosão combinatória do mapeamento de estados de um modelo 5x5. Por conta disso, o algoritmo de Q-Learning só "enxerga" um espaço 3x3 onde o professor ativo é o centro. O algoritmo foi treinado especificamente para lutar e otimizar o posicionamento nesse espaço restrito.

### 2.2 - Algoritmos e Treinamento
A base tática do bot utiliza o algoritmo **Q-Learning**, sustentado pela Aprendizagem por **Diferença Temporal (TD)**, atualizando as notas através da Equação de Bellman:

$$Q(s, a) \leftarrow Q(s, a) + \alpha \left( R(s, a) + \gamma \max_{a'} Q(s', a') - Q(s, a) \right)$$

* **Parâmetros utilizados:** Taxa de aprendizado $\alpha = 0.5$ e Fator de desconto $\gamma = 0.9$ (para priorizar estratégias de longo prazo e não apenas ganhos imediatos).
* **Recompensas:** $+1000$ pontos para a vitória, $+10$ para subir de nível, $-5$ para descidas (evitando passividade) e $+1$ para construir blocos aliados.

Para o treinamento, com auxílio de IA gerativa para a elaboração do script, implementamos o modelo de **Self-Play** (a IA jogando contra ela mesma) em vez de jogar contra oponentes aleatórios. O raciocínio por trás disso é promover o co-aprendizado: quando um agente usa uma estratégia muito agressiva e ganha, o outro agente é penalizado e, nas partidas seguintes, aprende a se defender contra aquele movimento. 
No total, simulamos mais de 150 mil partidas. O treinamento precisou ser interrompido por restrições de arquitetura do GitHub, pois o arquivo binário gerado pela Tabela Q estava atingindo o limite de 100MB imposto pela plataforma para versionamento de arquivos.

### 2.3 - Tabela Q e mapeamento dos dados
O cérebro do bot é armazenado em uma estrutura de Dicionário Aninhado, o que permite consultas de alta velocidade (tempo constante) através de Hash Tables.

    {
       "0,1,0,P,X,2,-1,3,4": {
          "M1,2_B1,3": 45.3,
          "M0,1_B1,1": -5.0
       }
    }

#### Explicação do mapeamento:
* **Chave principal:** Estado atual, representando os 9 blocos ao redor.
    * **X**: Posição do professor a ser controlado, sempre no meio do 3x3.
    * **Números de 0-4**: Nível das casas ao redor.
    * **P**: Professor (aliado ou inimigo) ocupando a casa.
    * **-1**: Fora do mapa ou paredes.
* **Chaves internas:**
    * **Mx,y**: Mover para a coordenada (x,y).
    * **Bx,y**: Mentorar o aluno na coordenada (x,y).
    * **Valor associado à chave**: É o **Q-Value** (a utilidade/nota de longo prazo daquela ação), e não apenas a recompensa imediata.

Anteriormente, salvávamos a Tabela Q em JSON. Contudo, ao conversarmos com o professor Celso, fomos orientados a salvar a matriz em um arquivo binário `.pickle`. Essa mudança arquitetural garantiu que a leitura no servidor e o carregamento para a memória RAM fossem mais eficientes.

---

## 3 - Limitações e melhorias
Após pesquisas e conversas com os professores do curso, ficaram claras algumas limitações no projeto que geram oportunidades de melhorias futuras.

### Tempo e Retrabalho
Dada a data de estruturação do backend e do agente, tivemos pouco tempo de sobra para a fase de treinamento. Além disso, embora a orientação de trocar o formato de JSON para `.pickle` ajudasse bastante, isso exigiu que refizéssemos o treinamento, consumindo horas importantes na reta final do projeto. Um melhor planejamento e uma validação antecipada do formato de armazenamento dos dados evitariam esse problema.

### Limite de Armazenamento
Tivemos um sério problema de estrutura, onde não conseguimos prolongar o treinamento da IA para 200 mil partidas ou mais porque a Tabela Q ficou grande demais para o limite de commit do GitHub (100MB). Uma melhoria arquitetural envolveria modelar o armazenamento utilizando bibliotecas numéricas mais compactas (como matrizes do NumPy) ou realizar a compressão e otimização dos tipos de dados (tipos numéricos menores em vez de strings longas) para que menos bytes fossem consumidos. Talvez dessa forma conseguíssemos até mapear o tabuleiro inteiro no treinamento com Q-learning.

## 4. O processo de construção e principais desafios

A construção do nosso agente foi um processo de evolução contínua. Implementar o Q-Learning foi um grande desafio. Foram necessários realizar chamadas em grupo para traduzir a matemática para o código e definir como o agente iria de fato "enxergar" o jogo na Tabela Q.

Fazer a equação de Bellman funcionar

O primeiro grande desafio foi estrutural: abandonamos um rascunho procedural confuso e refatoramos tudo para o paradigma de Orientação a Objetos (OOP). Fazer o fluxo de dados se encaixar perfeitamente — com o Pydantic blindando a entrada, o motor físico (`state.py`) validando as regras, e o Agente decidindo quando usar a IA — exigiu muito planejamento arquitetural.

Contudo, 

Para a Equação de Bellman funcionar corretamente, o algoritmo precisa prever a melhor jogada do próximo estado. Para resolver isso, implementamos um mecanismo utilizando a biblioteca `copy`. O bot tira uma cópia profunda (`deepcopy`) do tabuleiro na memória RAM, simula a sua jogada nesse tabuleiro imaginário, avalia a nova posição e descarta a matriz.