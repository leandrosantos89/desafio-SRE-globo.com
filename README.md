# Desafio-SRE-globo.com

## TODO
- [ ] terminar documentação
- [x] adicionar dashboard no grafana + print
- [x] subir imagens para o dockerhub

### DEPLOY

Procurei fazer o deploy o mais simples e automático possível. Para isso utilizei duas formas: shell script e ansible.
O primeiro passo é executar o `preflight.sh (shell|ansible)`. Esse script vai instalar as dependências necessárias e também vai preparar o ambiente para subir a aplicação.
O segundo passo é executar o `run.sh (subir_app|subir_logging|subir_monitoring|full_stack_shell|full_stack_ansible)`. Esse script vai subir todo o projeto. Você pode escolher subir apenas a aplicação (frontend + api + banco). Caso queira, pode subir toda a pilha utilizando shell ou ansible.
O deploy foi testado em um ambiente com Ubuntu 20.04.

```bash
git clone git@github.com:leandrosantos89/desafio-SRE-globo.com.git
cd desafio-SRE-globo.com
# escolha a forma de subir o projeto, shell ou ansible
./preflight.sh (shell|ansible)
# run.sh possui algumas opções para subir a pilha:
## OBS.: a pilha de logging precisa de arquivos adicionais
./run.sh (subir_app|subir_logging|subir_monitoring|full_stack_shell|full_stack_ansible)
```
Extra:
- portainer (para ajudar na visualização dos containers)
    - `curl -L https://downloads.portainer.io/portainer-agent-stack.yml -o portainer-agent-stack.yml`
    - Alter a porta que o portainer expôe, pois a porta 9000 já é utilizada no graylog
    - `docker stack deploy -c portainer-agent-stack.yml portainer`

#### dockerhub
- leandrorfsantos/paredao-proxy
- leandrorfsantos/paredao-api
- leandrorfsantos/paredao-consumer
- leandrorfsantos/logging-collector

### projeto básico... frontend + backend + monitoramento(prometheus + grafana)
    - proxy reverso + frontend -> nginx
    - exportar métricas e visualização -> nginx-exporter, prometheus, grafana
    - api flask 
    - mensageria (fila de requisições) -> rabbitMQ
    - backend -> python + pymongo
    - banco de dados e visualização -> mongoDB e mongo-express
    - endpoints
        - localhost/index.html -> home, interface para votação
        - localhost/resultado.html -> mostra o resultado parcial do paredão
        - localhost/painel.html -> painel que mostra o total de votos e votos/hora
        - localhost:5000/ -> apenas retorna 'OK'
        - localhost:5000/total -> endpoint da API que retorna o total de votos de cada participante
            - retorna um json `{"voto_1": 10000, "voto_2": 8500, "votos_ultima_hora": 5000}`
        - localhost:5000/votar/{1|2} -> endpoint responsável por realizar a votação
            - `/votar/1 -> vota em 1`
            - `/votar/2 -> vota em 2`

### Testes de carga
    - ab e wrk
