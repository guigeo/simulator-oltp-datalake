# VPS Runbook

## Layout

Projeto na VPS:

```text
/home/gramos/projects/simulator-oltp-datalake
```

Configuracao oficial:

```text
config/.env
```

## Dashboard Full Time

O dashboard e o simulador rodam via Docker Compose, com portas presas em
`127.0.0.1` para evitar exposicao direta na internet.

```bash
cd /home/gramos/projects/simulator-oltp-datalake
DASHBOARD_PORT=8502 docker compose --profile dashboard --profile simulator up -d dashboard simulator
docker compose --profile dashboard --profile simulator ps
```

Servicos esperados:

```text
postgres    127.0.0.1:5432->5432
dashboard   127.0.0.1:8502->8501
simulator   sem porta publicada
```

Os servicos principais usam `restart: unless-stopped`, entao voltam junto com o
Docker apos reinicio da VPS, desde que tenham sido iniciados pelo Compose.

## Caddy

Publicar acesso externo somente pelo Caddy:

```caddyfile
hospital-dashboard.averisen.com {
    reverse_proxy 127.0.0.1:8502
}
```

Validacao:

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
curl -I https://hospital-dashboard.averisen.com
```

## Operacao

Ver status:

```bash
cd /home/gramos/projects/simulator-oltp-datalake
docker compose --profile dashboard --profile simulator ps
```

Ver logs:

```bash
docker compose logs -f dashboard
docker compose logs -f simulator
docker compose logs -f postgres
```

Ver contagens:

```bash
docker compose run --rm simulator python -m scripts.cli counts
```

Parar a operacao continua:

```bash
docker compose --profile dashboard --profile simulator stop simulator dashboard
```
