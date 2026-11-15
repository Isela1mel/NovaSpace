# Vita Orbital · Aplicación de escritorio (Python + PySide6)

Una sola aplicación con **menú principal**. Del menú se entra a:

| Opción del menú | Para quién | Carpeta | Qué es |
|---|---|---|---|
| **Astronautas** | el astronauta | `astronautas/` | «Mi cuerpo»: cuerpo interactivo, latidos en vivo con ECG, asistente por voz y botón de EMERGENCIA |
| **Médicos** | el médico de vuelo | `medicos/` | Panel de monitoreo: resumen, indicadores, bienestar psicológico, predicción, alertas, contexto de misión y reportes en PDF |

Cada app es **independiente**: vive en su carpeta, con su propio código, datos simulados, configuración, estilo e imagen del cuerpo. El menú solo las abre.

## Ejecutar (VS Code)
```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py                  # o F5 → «▶ Vita Orbital · Menú principal»
```
También puedes abrir una app sola, sin menú: `python -m astronautas` o `python -m medicos` (hay una configuración de F5 para cada una).

## Cómo funciona el menú
1. `python main.py` muestra el menú con la imagen del planeta. Elige con el **clic**, con **Tab + Enter**, o con las teclas **1** (Astronautas) y **2** (Médicos).
2. La app elegida se abre y el menú se oculta.
3. Para volver: botón **«← Menú principal»** (arriba a la izquierda de cada app) o cerrar la ventana. El menú reaparece.
4. Cerrar el menú cierra todo.

El menú es responsivo: con la ventana ancha pone una tarjeta a cada lado del planeta; en tamaño medio, las dos abajo lado a lado; en ventanas angostas, apiladas. La imagen siempre cubre toda la ventana sin deformarse.

## Estructura (cada parte tiene su carpeta)
```
main.py                     ← ARRANQUE: abre el menú
requirements.txt
.vscode/launch.json         ← F5: menú · astronautas solo · médicos solo

menu/                       ══ MENÚ PRINCIPAL ══
  registry.py                 LISTA DE APPS del menú (aquí se agrega o quita una opción)
  window.py                   ventana y distribución responsiva
  role_card.py                tarjeta de cada opción
  background.py               fondo con la imagen
  icons.py                    iconos dibujados (casco, cruz médica)
  launcher.py                 abre la app elegida y regresa al menú
  theme.py                    colores y fuentes del menú
  assets/menu_bg.jpg          ← imagen de fondo del menú (cámbiala por otra del mismo nombre)

astronautas/                ══ APP DE ASTRONAUTAS · «Mi cuerpo» ══
  app.py                      composición: repositorio → servicio → controlador → ventana
  config.py                   tiempos, imagen del cuerpo y build_repository()  ← AQUÍ SE CONECTA SU BACKEND
  domain/                     enums y modelos (sin Qt ni backend)
  data/                       repository.py (contrato) · mock_repository.py (simulado) · api_repository.py (plantilla)
  services/body_service.py    lógica: zona prioritaria, estado general
  controllers/                estado y señales; llamadas al back en segundo plano
  ui/                         tema (theme.py), columnas, cuerpo, SOS, emergencia, vistas, widgets
  assets/body.png

medicos/                    ══ APP DE MÉDICOS · Panel de monitoreo ══
  app.py                      composición: repositorio → servicio → controlador → ventana
  config.py                   secciones visibles, sección inicial y build_repository()  ← AQUÍ SE CONECTA SU BACKEND
  domain/                     enums y modelos (sin Qt ni backend)
  data/                       repository.py (contrato) · mock_repository.py (simulado) · api_repository.py (plantilla)
  services/                   z-score, tendencias, ventanas, alertas, constructor de reportes
  controllers/main_controller.py
  ui/                         tema, menú lateral, cuerpo, tarjeta, panel
  ui/sections/                una clase por opción del panel (resumen, indicadores, ...)
  assets/body.png
```

## Conectar el backend (cada app por separado)
1. Rellena el `api_repository.py` de la app (`astronautas/data/` o `medicos/data/`) devolviendo los modelos de su `domain/models.py`.
2. En el `config.py` de esa app, dentro de `build_repository()`, devuelve el repositorio real en vez del simulado.

Nada más cambia. Las llamadas al back corren en segundo plano, así que una API lenta no congela la ventana.

## Personalizar
- **Menú:** textos, puntos y orden de las tarjetas en `menu/registry.py`; imagen en `menu/assets/menu_bg.jpg`; colores en `menu/theme.py`.
- **Colores y tipografía de cada app:** `astronautas/ui/theme.py` y `medicos/ui/theme.py` (paleta de la guía de marca: #0A3D91, #1E6BFF, #7A869A, #D7DEE8). Si instalas la fuente *Aerospace*, los títulos la usan solos.
- **Qué secciones ve el médico:** `ENABLED_SECTIONS` y `DEFAULT_SECTION` en `medicos/config.py`.
- **Agregar otra app al menú:** crea su carpeta con una función `build_window(allow_back=True)` (como `astronautas/app.py`) y añade una entrada en `menu/registry.py`.

## Notas técnicas
- Cada ventana lleva su **propio estilo (QSS)**, aplicado solo a ella y no a toda la aplicación, por eso los dos diseños no se mezclan.
- Al cerrar una app se detienen sus temporizadores y llamadas en curso, para que abrirla y cerrarla muchas veces no deje nada trabajando de fondo.
- Datos simulados: las dos apps vienen con repositorios de ejemplo hasta que se conecte el backend.
