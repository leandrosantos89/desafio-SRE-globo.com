# Desafio-SRE-globo.com

## TODO
- melhorar documentação
- adicionar dashboard no grafana + print
- adicionar pelo menos um teste unitário
- subir imagens para o dockerhub


### prepare.sh
curl
ansible

### o que é necessário para subir o projeto localmente
    - docker em modo swarm
        - curl -Ss https://get.docker.com | bash
        - `docker swarm init`
    - netdata (para monitoramento em tempo)
        - `bash <(curl -Ss https://my-netdata.io/kickstart.sh)`
    - portainer (para ajudar na visualização dos containers)[opcional]
        - `curl -L https://downloads.portainer.io/portainer-agent-stack.yml -o portainer-agent-stack.yml`
        - `docker stack deploy -c portainer-agent-stack.yml portainer`

### DEPLOY
    - testado em ubuntu 21.04
    - instalar ansible (fazer um run.sh)
    - git clone do projeto
    - setar a variável app_dir (full git clone dir) em ansible/group_vars/all
    - entre no diretório `ansible` e execute `ansible-playbook -i hosts main.yml --ask-become-pass -v`
        - vai instalar e fazer o deploy da aplicação, monitoramento e logging
    

### projeto básico... frontend + backend + monitoramento(prometheus + grafana)
    - execute o seguinte comando na raiz do projeto: `docker stack deploy -c stack.yml paredao`
        - vai subir os seguintes serviços:
            - proxy reverso + frontend -> nginx
            - exportar métricas e visualização -> nginx-exporter, prometheus, grafana
            - api flask 
            - mensageria (fila de requisições) -> rabbitMQ
            - backend -> python
            - banco de dados e visualização -> mongoDB e mongo-express
    - endpoints
        - localhost/ -> home do projeto
        - localhost/resultado -> mostra o resultado parcial do paredão
        - localhost/admin-producao -> painel que mostra o total de votos e votos/hora
        - localhost/total -> endpoint da API que retorna o total de votos de cada participante
            - retorna um json `{"voto_1": 21021, "voto_2": 38264}`
            - retorna 200
        - localhost/votar/{1|2} -> endpoint responsável por realizar a votação
            - retorna 200
            - recebe a votação direto no endpoint 
                - `/votar/1 -> vota em 1`
                - `/votar/2 -> vota em 2`

### Testes de carga
    - ab e wrk
