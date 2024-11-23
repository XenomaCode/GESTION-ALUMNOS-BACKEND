fastapi-university/
│
├── app/
│   ├── main.py           # Punto de entrada de la aplicación.
│   ├── models/           # Modelos Pydantic para la validación de datos.
│   │   ├── __init__.py
│   │   └── student.py    # Modelos relacionados con alumnos.
│   ├── routers/          # Routers para organizar las rutas.
│   │   ├── __init__.py
│   │   └── student.py    # Endpoints relacionados con alumnos.
│   ├── services/         # Lógica de negocio (opcional).
│   │   ├── __init__.py
│   │   └── student.py    # Lógica de negocio para alumnos.
│   ├── db/               # Configuración de base de datos.
│   │   ├── __init__.py
│   │   └── database.py   # Conexión a la base de datos.
│   └── config/           # Configuración de la aplicación (variables de entorno).
│       ├── __init__.py
│       └── settings.py
│
├── requirements.txt      # Dependencias del proyecto.
└── .gitignore            # Archivos y carpetas a ignorar por git.