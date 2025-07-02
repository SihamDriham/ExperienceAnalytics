# Script PowerShell pour configurer Spark sur Windows
# Exécuter dans PowerShell en tant qu'administrateur

Write-Host "=== Configuration Spark pour Windows ===" -ForegroundColor Green

# Créer le répertoire config s'il n'existe pas
if (!(Test-Path "config")) {
    New-Item -ItemType Directory -Path "config"
    Write-Host "Répertoire config créé" -ForegroundColor Yellow
}

# Créer le fichier passwd pour résoudre le problème d'authentification Unix
$passwdContent = @"
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
spark:x:1001:1001:Spark User:/opt/bitnami/spark:/bin/bash
"@

$passwdContent | Out-File -FilePath "config\passwd" -Encoding UTF8 -Force

Write-Host "Fichier passwd créé dans config\passwd" -ForegroundColor Green

# Créer le répertoire spark s'il n'existe pas
if (!(Test-Path "config\spark")) {
    New-Item -ItemType Directory -Path "config\spark"
    Write-Host "Répertoire config\spark créé" -ForegroundColor Yellow
}

# Créer les autres répertoires nécessaires
$directories = @("scripts", "data", "logs", "data\checkpoints")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "Répertoire $dir créé" -ForegroundColor Yellow
    }
}

Write-Host "=== Configuration terminée ===" -ForegroundColor Green
Write-Host "Vous pouvez maintenant lancer: docker-compose down && docker-compose up -d" -ForegroundColor Cyan