# Alliance Auth BBS
A simple forum for Alliance Auth. Emphasis on simple.

## Installation

`pip install git+https://github.com/basraah/allianceauth-bbs.git`

Add to your `INSTALLED_APPS`
```
    'allianceauth_bbs.bbs',
    'martor',
```

Collect staticfiles `python manage.py collectstatic`

Run migrations `python manage.py migrate`

Restart your WSGI workers.
