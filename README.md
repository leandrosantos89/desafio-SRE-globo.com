# Desafio-SRE-globo.com

## TODO
- [ ] terminar documentação
- [x] adicionar dashboard no grafana + print
- [x] subir imagens para o dockerhub


#### dockerhub
- leandrorfsantos/paredao-proxy
- leandrorfsantos/paredao-api
- leandrorfsantos/paredao-consumer
- leandrorfsantos/logging-collector


## O Problema
Você deve desenvolver um sistema de votação para o paredão do BBB, em versão Web com HTML/CSS/Javascript e uma API REST como backend utilizando qualquer linguagem de programação (Java, Python, Go ou Ruby). 

O paredão do BBB consiste em uma votação que confronta dois integrantes do programa BBB. A votação é apresentada em uma interface acessível pela Web, onde os usuários optam por votar em um dos integrantes apresentados. Uma vez realizado o voto, o usuário recebe uma tela com a confirmação do sucesso de seu voto e um panorama percentual dos votos por candidato até aquele momento.

Além do frontend deve existir uma api aonde de fato, será computado os votos.

### Regras

1. Os usuários podem votar quantas vezes quiserem independente da opção escolhida, entretanto, a produção do programa não gostaria de receber votos oriundos de uma máquina e sim votos de pessoas. 
2. A votação é chamada em horário nobre, com isso, é esperado um volume elevado de votos. Para exemplificar, vamos trabalhar com 1000 votos/segundo.
3. A produção do programa gostaria de consultar numa URL, o total geral de votos, o total por participante e o total de votos por hora.
4. Muito importante 1: Utilizando uma ferramenta de logging (exemplos: Elastic Search,Splunk, Graylog ou similar), crie uma query que mostre em tempo real os eventos queacontecem na execução da api , exemplos (Warning, Erro, Debug, Info, etc). Importante ter ao menos uma situação de execução com erro.
5. Muito importante 2: Utilizando uma ferramenta de métricas (exemplos: Prometheus,Zabbix, cloudwatch ou similar), crie 3 dashboards que mostre em tempo real a quantidade de execução, a latência (tempo de execução) e quantidade de erros da api criada no item 6.
Importante ter ao menos uma situação de execução com erro.

## Solução
### Dependências
- docker
- ansible (caso faça o deploy com ansible)

### Como rodar os testes unitários da API
```bash 
docker exec -ti $(docker ps -q --filter 'name=paredao_api.1.*') py.test --cov=api
```

### Como rodar os testes de performance
ab
wrk

## Como fazer o deploy

Procurei fazer o deploy o mais simples e automático possível. Para isso utilizei duas formas: shell script e ansible.
O primeiro passo é executar o `preflight.sh (shell|ansible)`. Esse script vai instalar as dependências necessárias e também vai preparar o ambiente para subir a aplicação.
O segundo passo é executar o `run.sh (subir_app|subir_logging|subir_monitoring|full_stack_shell|full_stack_ansible)`. Esse script vai subir todo o projeto. Você pode escolher subir apenas a aplicação (frontend + api + banco). Caso queira, pode subir toda a pilha utilizando shell ou ansible.
O deploy foi testado em um ambiente com Ubuntu 20.04.

```bash
git clone git@github.com:leandrosantos89/desafio-SRE-globo.com.git
cd desafio-SRE-globo.com
./preflight.sh (shell|ansible)
./run.sh (subir_app|subir_logging|subir_monitoring|full_stack_shell|full_stack_ansible)
```
Extra:
- portainer (para ajudar na visualização dos containers)
    - `curl -L https://downloads.portainer.io/portainer-agent-stack.yml -o portainer-agent-stack.yml`
    - Alter a porta que o portainer expôe, pois a porta 9000 já é utilizada no graylog
    - `docker stack deploy -c portainer-agent-stack.yml portainer`

### Aplicação
- Abra a aplicação no endereço http://localhost em algum browser
- API Rest: http://localhost:5000

### Monitoramento
- Prometheus: http://localhost:9090
- Netdata: http://localhost:19999
- CAdvisor: http://localhost:8080
- Grafana: http://localhost:3000 (admin:admin)
- Node-exporter: http://localhost:9100
- Nginx-exporter: http://localhost:9113
- Mongo-express: http://localhost:8081
- RabbitMQ (Métricas): http://localhost:15672 (guest:guest)

### Logging
- Graylog: http://localhost:9000 (admin:admin)

## Organização, Arquitetura e Frameworks (aplicação)
### Organização 
A aplicação está separada em três aplicações, Frontend e API Rest e um consumidor da fila. O foco do projeto é a escalabidade. Para isso cada parte da aplicação é um container docker isolado. Dessa forma, a aplicação escala de forma independente, tanto o frontend quanto o backend.

O Frontend contém os conteúdos estáticos (html e javascript puro) e é servido por um container NGINX. Esse mesmo container NGINX também provê acesso à API Rest. Assim, todo o processamento das telas fica no cliente e não onera o backend.

A API Rest fica responsável por entregar os dados tanto para o frontend quanto para algum outro cliente, isso é feito por meio de uma fila (RabbitMQ. O processamento dos votos é feito de fato no consumer, que consume os dados que estão na fila.

### Arquitetura
![Arquitetura](./Arquitetura.png?raw=true "Arquitetura")

#### Endpoints
- localhost/index.html -> home, interface para votação
- localhost/resultado.html -> mostra o resultado parcial do paredão
- localhost/painel.html -> painel que mostra o total de votos e votos/hora
- localhost:5000/ -> apenas retorna 'OK'
- localhost:5000/total -> endpoint da API que retorna o total de votos de cada participante
  - retorna um json `{"voto_1": 10000, "voto_2": 8500, "votos_ultima_hora": 5000}`
- localhost:5000/votar/{1|2} -> endpoint responsável por realizar a votação
  - `/votar/1 -> vota em 1`
  - `/votar/2 -> vota em 2`

### Frameworks e Ferramentas
#### API Rest
- Flask: Escolhido por ser um framework leve e simples de implementar.
- Pytest: Testes unitários.
- ab e wrk: Ferramentas para realizar testes de carga.

#### Fila
- RabbitMQ: utilizada por ser escalável (apesar que está com apenas uma instância nesse projeto)

#### DB
- Mongo: Escolhido por ser NoSQL

#### Frontend
- HTML e JavaScript puro: O objeto é ser o mais leve e simples possível.

#### Stack de logging
- Graylog + Elasticsearch + Mongo: Escolhido por já ter familiaridade com a solução.

#### Stack de monitoramento
- Grafana + prometheus + CAdvisor + Node-exporter + nginx-exporter: escolhida por ser muito utilizada. O Prometheus facilita muito a coleta de dados e o Grafana provê dashboards agradáveis e flexíveis.
- Netdata: Solução pronta para monitoramento em tempo real do hospedeiro e de algumas ferramentas. Foi escolhido por entregar muitas métricas (inclusive para o prometheus) e também já possui diversos dashboards prontos.

