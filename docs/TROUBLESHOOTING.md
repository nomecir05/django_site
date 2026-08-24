# Troubleshooting Record

This document records the issues encountered during the Windows Server deployment, how they were diagnosed, and the lesson learned from each one.

## 1. `requirements.txt` not found

**Symptom**

```text
ERROR: Could not open requirements file: No such file or directory
```

**Cause:** PowerShell was opened in the wrong directory.

**Resolution**

```powershell
Set-Location C:\BuildCore\django_site
Test-Path .\requirements.txt
python -m pip install -r requirements.txt
```

**Lesson:** Confirm the working directory and file path before installing dependencies.

## 2. `python` command not recognized

**Symptom:** `python` was not available even though Python was installed.

**Investigation**

```powershell
py --version
```

**Resolution:** Use the Python launcher to create the virtual environment, then use the venv executable.

```powershell
py -m venv C:\BuildCore\venv
C:\BuildCore\venv\Scripts\Activate.ps1
```

## 3. Permission denied while creating the venv

**Symptom**

```text
Permission denied: ...\venv\Scripts\python.exe
```

**Cause:** A partial, copied, or locked virtual environment already existed inside the project.

**Resolution:** Remove only the broken project venv and create a clean environment outside the application directory.

```powershell
Remove-Item -LiteralPath 'C:\BuildCore\django_site\venv' -Recurse -Force -ErrorAction SilentlyContinue
py -m venv C:\BuildCore\venv
```

## 4. `createsuperuser` appears to hang

**Symptom:** The cursor blinked with no visible password prompt in PowerShell ISE.

**Cause:** Interactive hidden-password input does not behave reliably in PowerShell ISE.

**Resolution:** Use regular Windows PowerShell or Windows Terminal, not PowerShell ISE.

```powershell
Set-Location C:\BuildCore\django_site
C:\BuildCore\venv\Scripts\Activate.ps1
python manage.py createsuperuser
```

**Lesson:** A long-running server or hidden password prompt may occupy the terminal without being frozen.

## 5. `manage.py` not found

**Symptom**

```text
can't open file 'C:\Users\Administrator\manage.py'
```

**Cause:** The command was executed from the Administrator profile rather than the project directory.

**Resolution**

```powershell
Set-Location C:\BuildCore\django_site
python manage.py createsuperuser
```

## 6. IIS reverse-proxy modules not listed

**Symptom:** `Get-WebGlobalModule` returned no Rewrite or Routing modules.

**Cause:** URL Rewrite and ARR were not installed or IIS had not loaded them.

**Resolution:** Install the official x64 URL Rewrite 2 and ARR 3 packages, then verify:

```powershell
Import-Module WebAdministration
Get-WebGlobalModule | Where-Object { $_.Name -match 'Rewrite|Routing' } | Select-Object Name
```

## 7. IIS `502 Bad Gateway`

**Likely causes**

- Waitress is stopped.
- Waitress is listening on a different port.
- The scheduled task has failed.
- The IIS rewrite target is incorrect.

**Checks**

```powershell
Get-ScheduledTask -TaskName 'BuildCoreWaitress' | Select-Object TaskName,State
Get-NetTCPConnection -LocalPort 8080 -State Listen
Invoke-WebRequest http://127.0.0.1:8080 -UseBasicParsing
```

## 8. `DisallowedHost`

**Cause:** The public hostname is missing from `DJANGO_ALLOWED_HOSTS`.

**Resolution**

```env
DJANGO_ALLOWED_HOSTS=construction.crysmon.online,127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=https://construction.crysmon.online
```

Restart the Waitress scheduled task after changing `.env`.

## 9. Static files or CSS missing

```powershell
Set-Location C:\BuildCore\django_site
C:\BuildCore\venv\Scripts\python.exe manage.py collectstatic --noinput
C:\BuildCore\venv\Scripts\python.exe manage.py check
```

Confirm that WhiteNoise is installed and `DJANGO_DEBUG=False` is loaded from `.env`.

## 10. Site opens on desktop but not immediately on a phone

**Likely cause:** DNS or negative-cache propagation on the mobile carrier or device.

**Checks**

- Enter the complete `https://` URL.
- Toggle Airplane Mode to refresh the mobile connection.
- Test both mobile data and Wi-Fi.
- Temporarily disable VPN or iCloud Private Relay.
- Verify DNS using a public resolver.

## 11. Form saves but no email arrives

**Cause:** The current production environment intentionally uses Django's console email backend until a dedicated mailbox is created.

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

The form record is still saved in the database and visible in Django Admin. SMTP credentials must remain outside GitHub and should be added only after the dedicated company mailbox is ready.

## Operational checklist

```powershell
Get-Website -Name 'BuildCoreConstruction' | Select-Object Name,State,PhysicalPath,ApplicationPool
Get-WebBinding -Name 'BuildCoreConstruction' | Select-Object protocol,bindingInformation
Get-WebAppPoolState -Name 'BuildCoreProxyPool'
Get-ScheduledTask -TaskName 'BuildCoreWaitress' | Select-Object TaskName,State
Get-NetTCPConnection -LocalPort 8080 -State Listen
```

