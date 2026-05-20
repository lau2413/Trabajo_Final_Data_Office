# Dashboard Cine Los Andes

Dashboard interactivo construido con Dash y Plotly sobre `data/processed/cine_en_cifras_validado.csv`.

## Ejecutar localmente

Desde la raiz del proyecto:

```powershell
.\venv\Scripts\python.exe dashboard\app.py
```

Luego abre:

```text
http://127.0.0.1:8051
```

Si ese puerto ya esta ocupado, puedes usar otro:

```powershell
$env:PORT=8052
.\venv\Scripts\python.exe dashboard\app.py
```

## Compartirlo con otras personas

Opcion simple para clase o entrega local:

1. Entrega la carpeta del proyecto completa.
2. La otra persona instala dependencias con `pip install -r requirements.txt`.
3. Ejecuta `python dashboard/app.py`.
4. Abre `http://127.0.0.1:8051`.

Opcion publica:

1. Sube el proyecto a GitHub.
2. Crea una app en Render, Railway o PythonAnywhere.
3. Configura el comando de inicio como `python dashboard/app.py`.
4. Comparte la URL publica que te da la plataforma.
