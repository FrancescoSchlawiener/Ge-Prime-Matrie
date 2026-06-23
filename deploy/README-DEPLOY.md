# Deployment auf Hostinger VPS (schlawiener.space)

Branch: `cursor/hostinger-vps-live-pipe-95cf`

## URLs

| Pfad | Dienst |
|------|--------|
| `/` | Statische Landing Page |
| `/profil.html` | Profil-Vorlage |
| `/GPM/` | Ge-Prime-Matrix (Docker) |
| `/protosarche/` | Bestehende Docker-Instanz |
| `/catpocalypse/` | Bestehende Docker-Instanz |

## Lokale Vorbereitung

```bash
cp deploy/ssh.config.example deploy/ssh.config.local
cp deploy/.env.deploy.example deploy/.env.deploy
chmod +x deploy/scripts/*.sh
```

`deploy/ssh.config.local` und `deploy/.env.deploy` sind gitignored.

SSH-Verbindung testen:

```bash
ssh -F deploy/ssh.config.local schlawiener
```

## Erstinstallation auf dem VPS

Auf dem VPS als root:

```bash
cd /opt
git clone https://github.com/francescoschlawiener/ge-prime-matrie.git ge-prime-matrix
cd ge-prime-matrix
git checkout cursor/hostinger-vps-live-pipe-95cf
bash deploy/scripts/setup-vps.sh
```

## Ports für bestehende Docker-Apps

Vor dem Nginx-Reload prüfen:

```bash
docker ps
```

In [`deploy/nginx/schlawiener.space.conf`](nginx/schlawiener.space.conf) die Upstreams `protosarche_backend` und `catpocalypse_backend` auf die tatsächlichen Host-Ports setzen (Standard in der Config: 8081, 8082).

## Deploy aus dem Repo

```bash
./deploy/scripts/deploy.sh
```

Das Script synct die statische Site, pullt den Branch auf dem VPS, baut GPM neu und reloadet Nginx.

## GPM manuell auf dem VPS

```bash
cd /opt/ge-prime-matrix
docker compose -f deploy/docker-compose.yml up -d --build
curl -s http://127.0.0.1:5000/api/health
```

## SSL

Certbot wird in `setup-vps.sh` angestoßen. Erneuerung:

```bash
certbot renew --dry-run
```
