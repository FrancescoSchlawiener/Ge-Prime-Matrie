# Deployment auf Hostinger VPS (schlawiener.space)

Branch: `cursor/hostinger-vps-live-pipe-95cf`

Der VPS nutzt **Traefik** (aus dem Catpocalypse-Stack), nicht Nginx. GPM und die Landing Page joinen das Netzwerk `traefik-public`.

## URLs

| Pfad | Dienst |
|------|--------|
| `/` | Statische Landing Page (nginx-Container) |
| `/profil.html` | Profil-Vorlage |
| `/GPM/` | Ge-Prime-Matrix (Flask) |
| `/protosarche/` | Protos Arché (bestehend) |
| `/catpocalypse/` | Catpocalypse (nach Routing-Patch) |

## Lokale Vorbereitung

```bash
cp deploy/ssh.config.example deploy/ssh.config.local
cp deploy/.env.deploy.example deploy/.env.deploy
chmod +x deploy/scripts/*.sh
```

SSH testen:

```bash
ssh -F deploy/ssh.config.local schlawiener
```

## Erstinstallation auf dem VPS

Voraussetzung: Traefik läuft (`docker ps` zeigt `traefik`).

```bash
cd /opt
git clone https://github.com/FrancescoSchlawiener/Ge-Prime-Matrie.git ge-prime-matrix
cd ge-prime-matrix
git checkout cursor/hostinger-vps-live-pipe-95cf
bash deploy/scripts/setup-vps.sh
```

`setup-vps.sh` patcht Catpocalypse von `/` auf `/catpocalypse/` und startet Site + GPM.

## Deploy aus dem Repo

```bash
./deploy/scripts/deploy.sh
```

## Manuell auf dem VPS

```bash
cd /opt/ge-prime-matrix
docker compose -f deploy/docker-compose.yml up -d --build
docker exec gpm python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/api/health').read())"
```

## Nginx-Config

[`deploy/nginx/schlawiener.space.conf`](nginx/schlawiener.space.conf) ist eine optionale Alternative, falls Traefik nicht genutzt wird. Auf dem aktuellen VPS ist Traefik aktiv.

## Catpocalypse-Routing

[`deploy/scripts/patch-catpocalypse-routing.sh`](scripts/patch-catpocalypse-routing.sh) verschiebt Catpocalypse unter `/catpocalypse/`, damit `/` frei für die Landing Page ist.
