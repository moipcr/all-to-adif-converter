# 📡 WSJT-X `ALL.TXT` to eQSL SWL Converter

[🇪🇸 Español](#-español) | [🇬🇧 English](#-english)

---

## 🇪🇸 Español

Script en Python ligero y sin dependencias externas para convertir los registros de escucha (`ALL.TXT`) generados por **WSJT-X** en un archivo **ADIF (`.adi`)** limpio, sin duplicados y 100% compatible con los reportes **SWL de eQSL.cc**.

### ✨ Características principales

* 📶 **SNR real de recepción:** Extrae exclusivamente los decibelios (`dB`) recibidos por tu antena (`<RST_RCVD>`), sin confundirlos con los reportes internos de los QSOs interceptados.
* 🤝 **Detalle del QSO interceptado:** Identifica la estación corresponsal (`<APP_EQSL_SWL>`) e incluye en el comentario tanto su indicativo como el SNR interno de su contacto.
* 🧹 **Cero duplicados:** Agrupa las recepciones por estación, banda y día, conservando siempre la captura con mayor nivel de señal.
* 🛡️ **Validación automática para eQSL:**
  * Elimina corchetes angulares (`<` `>`) de indicativos compuestos o especiales.
  * Valida cuadrículas Maidenhead (`<GRIDSQUARE>`) para evitar textos erróneos como `RR73`.
  * Añade automáticamente la etiqueta oficial `<SWL:1>Y`.

### 📋 Requisitos

* **Python 3.8** o superior *(usa únicamente librerías estándar)*.

### 🚀 Uso y parámetros

Ejecuta el script desde tu terminal (CMD / PowerShell / Bash):

```bash
python sdrangel_ft8_adif_swl.py -i <RUTA_ALL.TXT> -c <TU_INDICATIVO_SWL> -g <TU_GRID>
```

| Parámetro | Obligatorio | Descripción | Ejemplo |
| :--- | :---: | :--- | :--- |
| `-i`, `--input` | ✅ | Ruta al archivo `ALL.TXT` de WSJT-X | `"C:\Users\...\ALL.TXT"` |
| `-c`, `--call` | ✅ | Tu indicativo registrado en eQSL SWL | `EA40365FD` |
| `-g`, `--grid` | ✅ | Tu cuadrícula Maidenhead (4 o 6 caracteres) | `IN80EK` |
| `-o`, `--output` | ❌ | Archivo ADIF de salida *(por defecto: `SWL_eQSL.adi`)* | `reporte_hoy.adi` |
| `-d`, `--date` | ❌ | Filtra únicamente por una fecha (`YYYYMMDD`) | `20261127` |
| `--city` | ❌ | Ciudad para el comentario *(por defecto: `Madrid`)* | `"Madrid"` |
| `--rig` | ❌ | Descripción de tu receptor y antena | `"RTL-SDR v4 & Long Wire 12.5m + Balun"` |

### 💡 Ejemplos

**1. Exportar solo las escuchas de un día concreto (recomendado para subidas diarias):**
```bash
python sdrangel_ft8_adif_swl.py -i ALL.TXT -o swl_20261127.adi -c EA40365FD -g IN80EK -d 20261127 --city "Madrid" --rig "RTL-SDR v4 & 12.5m Long Wire + 5m counterpoise + Balun"
```

**2. Procesar todo el historial acumulado en `ALL.TXT`:**
```bash
python sdrangel_ft8_adif_swl.py -i ALL.TXT -c EA40365FD -g IN80EK
```

### 📤 Subida a eQSL.cc

1. Inicia sesión en [eQSL.cc](https://eqsl.cc) con tu cuenta SWL.
2. Ve al menú superior **Upload ADIF**.
3. Selecciona el archivo `.adi` generado y haz clic en **Upload**.
4. Verifica tus reportes enviados en la sección **OutBox**.

---

## 🇬🇧 English

Lightweight, zero-dependency Python script to convert **WSJT-X** `ALL.TXT` log files into a clean, deduplicated **ADIF (`.adi`)** file ready for **eQSL.cc SWL** reporting.

### ✨ Key Features

* 📶 **True RX SNR:** Extracts only the actual signal-to-noise ratio (`dB`) received at your antenna (`<RST_RCVD>`), avoiding mix-ups with the internal SNR exchanged between third-party stations.
* 🤝 **Intercepted QSO Details:** Captures the worked station callsign (`<APP_EQSL_SWL>`) and logs both the correspondent callsign and their internal QSO SNR inside `<COMMENT>`.
* 🧹 **Deduplication:** Keeps a single entry per callsign, band, and date, retaining the strongest reception (`max SNR`).
* 🛡️ **eQSL-Safe Formatting:**
  * Strips angle brackets (`<` `>`) from compound or special event callsigns.
  * Strictly validates Maidenhead grid squares (`<GRIDSQUARE>`) so tokens like `RR73` never leak into location fields.
  * Automatically appends the required `<SWL:1>Y` tag.

### 📋 Requirements

* **Python 3.8+** *(uses standard library only, no `pip install` needed)*.

### 🚀 Usage & Arguments

Run the script from your terminal (CMD / PowerShell / Bash):

```bash
python sdrangel_ft8_adif_swl.py -i <PATH_TO_ALL.TXT> -c <YOUR_SWL_CALLSIGN> -g <YOUR_GRID>
```

| Argument | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `-i`, `--input` | ✅ | Path to WSJT-X `ALL.TXT` file | `"C:\Users\...\ALL.TXT"` |
| `-c`, `--call` | ✅ | Your registered eQSL SWL callsign | `EA40365FD` |
| `-g`, `--grid` | ✅ | Your Maidenhead grid locator (4 or 6 chars) | `IN80EK` |
| `-o`, `--output` | ❌ | Output ADIF filename *(default: `SWL_eQSL.adi`)* | `today_swl.adi` |
| `-d`, `--date` | ❌ | Filter logs by a specific date (`YYYYMMDD`) | `20261127` |
| `--city` | ❌ | City/location shown in comment *(default: `Madrid`)* | `"Madrid"` |
| `--rig` | ❌ | Receiver & antenna description | `"RTL-SDR v4 & Long Wire 12.5m + Balun"` |

### 💡 Examples

**1. Export receptions for a single day (recommended for daily uploads):**
```bash
python sdrangel_ft8_adif_swl.py -i ALL.TXT -o swl_20261127.adi -c EA40365FD -g IN80EK -d 20261127 --city "Madrid" --rig "RTL-SDR v4 & 12.5m Long Wire + 5m counterpoise + Balun"
```

**2. Convert the entire `ALL.TXT` history:**
```bash
python sdrangel_ft8_adif_swl.py -i ALL.TXT -c EA40365FD -g IN80EK
```

### 📤 Uploading to eQSL.cc

1. Log in to your SWL account on [eQSL.cc](https://eqsl.cc).
2. Navigate to **Upload ADIF**.
3. Choose the generated `.adi` file and click **Upload**.
4. Check your **OutBox** to verify the uploaded SWL reports.
