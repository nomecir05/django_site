# Windows Server Deployment — Django, Waitress, IIS, and HTTPS

This document records the production deployment of BuildCore Construction on Windows Server. Values that could expose credentials are represented by placeholders.

## 1. Deployment design

```text
Client -> DNS -> IIS :80/:443 -> ARR/URL Rewrite -> Waitress 127.0.0.1:8080 -> Django
```

IIS terminates HTTPS and redirects HTTP to HTTPS. Waitress listens only on loopback, so port `8080` does not need a public firewall rule.

## 2. Prerequisites

- Windows Server with IIS installed
- Python 3.12 x64
- IIS URL Rewrite Module 2
- Microsoft Application Request Routing (ARR) 3
- Administrator Windows PowerShell
- A DNS hostname pointing to the server

Project paths used in this deployment:

```text
C:\BuildCore\django_site
C:\BuildCore\venv
C:\BuildCore\iis-proxy
```

## 3. Python environment

Verify Python:

```powershell
py --version
```

Create the virtual environment outside the application directory. This avoids conflicts from copied or locked `venv` files.

```powershell
py -m venv C:\BuildCore\venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
C:\BuildCore\venv\Scripts\Activate.ps1
Set-Location C:\BuildCore\django_site
python -m pip install -r requirements.txt
```

Gunicorn may be present for Linux deployments, but Windows production uses Waitress.

## 4. Production environment file

Generate a unique key:

```powershell
$secret = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Create `C:\BuildCore\django_site\.env` with values similar to the following. Never commit the real file.

```env
DJANGO_SECRET_KEY=GENERATED_SECRET_HERE
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=construction.crysmon.online,127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=https://construction.crysmon.online

# IIS performs the HTTP-to-HTTPS redirect.
SECURE_SSL_REDIRECT=False

# Temporary until a dedicated mailbox is configured.
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=BuildCore Construction <noreply@example.com>
COMPANY_EMAIL=estimates@example.com
```

Remove the PowerShell variable after writing the file:

```powershell
Remove-Variable secret
```

## 5. Database and static files

```powershell
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py check
python manage.py test
```

The demo seed is optional in a real customer deployment.

## 6. Test Waitress locally

```powershell
Set-Location C:\BuildCore\django_site
C:\BuildCore\venv\Scripts\waitress-serve.exe --listen=127.0.0.1:8080 buildcore.wsgi:application
```

Test `http://127.0.0.1:8080/`. A terminal that remains occupied while the server is running is normal. Stop the manual test with `Ctrl+C` before starting the background task.

## 7. Enable IIS reverse proxy

```powershell
Import-Module WebAdministration
Set-WebConfigurationProperty -PSPath 'MACHINE/WEBROOT/APPHOST' -Filter 'system.webServer/proxy' -Name 'enabled' -Value 'True'
Set-WebConfigurationProperty -PSPath 'MACHINE/WEBROOT/APPHOST' -Filter 'system.webServer/proxy' -Name 'preserveHostHeader' -Value 'True'
```

Verify the modules:

```powershell
Get-WebGlobalModule | Where-Object { $_.Name -match 'Rewrite|Routing' } | Select-Object Name
```

Expected modules:

```text
RewriteModule
ApplicationRequestRouting
```

## 8. IIS proxy site

Create the physical directory and copy [`deployment/iis/web.config.example`](../deployment/iis/web.config.example) to `C:\BuildCore\iis-proxy\web.config`.

```powershell
New-Item -ItemType Directory -Path C:\BuildCore\iis-proxy -Force
New-WebAppPool -Name 'BuildCoreProxyPool'
Set-ItemProperty 'IIS:\AppPools\BuildCoreProxyPool' -Name managedRuntimeVersion -Value ''
New-Website -Name 'BuildCoreConstruction' -PhysicalPath 'C:\BuildCore\iis-proxy' -Port 80 -HostHeader 'construction.crysmon.online' -ApplicationPool 'BuildCoreProxyPool'
```

Verify:

```powershell
Get-WebAppPoolState -Name 'BuildCoreProxyPool'
Get-WebBinding -Name 'BuildCoreConstruction' | Select-Object protocol,bindingInformation
```

## 9. Run Waitress automatically

Create a startup task that runs as `SYSTEM` and restarts after failure:

```powershell
$action = New-ScheduledTaskAction -Execute 'C:\BuildCore\venv\Scripts\waitress-serve.exe' -Argument '--listen=127.0.0.1:8080 buildcore.wsgi:application' -WorkingDirectory 'C:\BuildCore\django_site'
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName 'BuildCoreWaitress' -Action $action -Trigger $trigger -Settings $settings -User 'SYSTEM' -RunLevel Highest -Force
Start-ScheduledTask -TaskName 'BuildCoreWaitress'
```

Verify:

```powershell
Get-ScheduledTask -TaskName 'BuildCoreWaitress' | Select-Object TaskName,State
Get-NetTCPConnection -LocalPort 8080 -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess
```

## 10. DNS

The deployed hostname is:

```text
construction.crysmon.online
```

It was configured as a CNAME to the server's established hostname. Verify public resolution:

```powershell
nslookup construction.crysmon.online 8.8.8.8
```

The server IP is intentionally omitted from this public document.

## 11. HTTPS with win-acme

1. Download the recommended x64 trimmed release from [win-acme](https://www.win-acme.com/).
2. Extract it to `C:\Program Files\win-acme`.
3. Run `wacs.exe` as Administrator.
4. Choose `N` for default IIS settings.
5. Select only the `construction.crysmon.online` binding.
6. Complete the Let's Encrypt registration.

win-acme creates the IIS HTTPS binding and a scheduled renewal task.

Verify the binding:

```powershell
Get-WebBinding -Name 'BuildCoreConstruction' | Select-Object protocol,bindingInformation
```

## 12. Production verification

```powershell
curl.exe -I http://construction.crysmon.online
curl.exe -I https://construction.crysmon.online
```

Expected results:

- HTTP returns `301 Moved Permanently` to HTTPS.
- HTTPS returns `200 OK`.
- IIS reports the correct hostname on ports 80 and 443.
- Waitress listens only on `127.0.0.1:8080`.
- The main site and `/admin/` load over HTTPS.
- Contact and quote records are saved in Django Admin.

## 13. Updating the application

```powershell
Stop-ScheduledTask -TaskName 'BuildCoreWaitress'
Set-Location C:\BuildCore\django_site
C:\BuildCore\venv\Scripts\python.exe -m pip install -r requirements.txt
C:\BuildCore\venv\Scripts\python.exe manage.py migrate
C:\BuildCore\venv\Scripts\python.exe manage.py collectstatic --noinput
C:\BuildCore\venv\Scripts\python.exe manage.py check
Start-ScheduledTask -TaskName 'BuildCoreWaitress'
```

Back up the application files, `.env`, and database before production updates. Do not publish those backups to GitHub.

