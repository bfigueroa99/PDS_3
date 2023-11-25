# PDS_3

## Para Local:
``` bash
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

## Para Server:
```bash
ssh root@161.35.0.111
```

``` bash
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
rm db.sqlite3
python3 manage.py makemigrations
python3 manage.py migrate
python3 load_fake_data.py
python3 manage.py runserver 0.0.0.0:8000
```
