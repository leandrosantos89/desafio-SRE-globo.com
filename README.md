# Desafio-SRE-globo.com

## TODO
- melhorar documentação
- adicionar dashboard no grafana + print
- subir imagens para o dockerhub


### o que é necessário para subir o projeto localmente
    - docker em modo swarm
        - curl -Ss https://get.docker.com | bash
        - `docker swarm init`
    - portainer (para ajudar na visualização dos containers)[opcional]
        - `curl -L https://downloads.portainer.io/portainer-agent-stack.yml -o portainer-agent-stack.yml`
        - `docker stack deploy -c portainer-agent-stack.yml portainer`

### DEPLOY
    - testado em ubuntu 20.04
    - git clone do projeto
    - executar o script preflight.sh
    - entre no diretório `ansible` e execute `ansible-playbook -i hosts main.yml -v`
        - utilize --ask-become-pass se o sudo precisa de senha
        - vai instalar e fazer o deploy da aplicação, monitoramento e logging
    
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
        - localhost:5000/
        - localhost:5000/total -> endpoint da API que retorna o total de votos de cada participante
            - retorna um json `{"voto_1": 2, "voto_2": 0, "votos_ultima_hora": 0}`
            - retorna 200
        - localhost:5000/votar/{1|2} -> endpoint responsável por realizar a votação
            - retorna 200
            - recebe a votação direto no endpoint 
                - `/votar/1 -> vota em 1`
                - `/votar/2 -> vota em 2`

### Testes de carga
    - ab e wrk
