import argparse
import re
from datetime import datetime, timezone

def freq_a_banda(freq_mhz):
    f = float(freq_mhz)
    if 1.8 <= f <= 2.0: return "160M"
    if 3.5 <= f <= 4.0: return "80M"
    if 5.2 <= f <= 5.5: return "60M"
    if 7.0 <= f <= 7.3: return "40M"
    if 10.1 <= f <= 10.15: return "30M"
    if 14.0 <= f <= 14.35: return "20M"
    if 18.068 <= f <= 18.168: return "17M"
    if 21.0 <= f <= 21.45: return "15M"
    if 24.89 <= f <= 24.99: return "12M"
    if 28.0 <= f <= 29.7: return "10M"
    if 50.0 <= f <= 54.0: return "6M"
    return None

def limpiar_call(token):
    # Quita < y > de indicativos compuestos en FT8 (ej. <PF40EUDXF> -> PF40EUDXF)
    return token.strip("<>")

def es_indicativo_valido(call):
    if not isinstance(call, str):
        return False
    c = limpiar_call(call)
    if c in ("CQ", "DE", "QRZ", "RR73", "RRR", "73", "...", "TNX", "THANKS", "GL", "QSO", "WRONG", "INCORRECT"):
        return False
    return bool(re.match(r'^[A-Z0-9]{1,4}/?[A-Z0-9]{1,5}[0-9][A-Z0-9]{1,5}(/[A-Z0-9]+)?$', c))

def es_grid_valido(grid):
    if not isinstance(grid, str) or grid == "RR73":
        return False
    return bool(re.match(r'^[A-R]{2}[0-9]{2}$', grid))

def es_reporte_qso(token):
    if not isinstance(token, str):
        return False
    return bool(re.match(r'^R?[+-]\d{2}$', token))

def etiqueta_adif(nombre, valor):
    val_str = str(valor)
    return f"<{nombre}:{len(val_str)}>{val_str}"

def procesar_log(args):
    mejores_recepciones = {}
    lineas_leidas = 0
    tramas_validas = 0

    patron_linea = re.compile(
        r'^(\d{6})_(\d{6})\s+(\d+\.\d+)\s+(?:Rx|~)\s+([A-Z0-9]+)\s+([+-]?\d+)\s+[+-]?\d+\.\d+\s+\d+\s+(.+)$'
    )

    try:
        with open(args.input, "r", encoding="utf-8", errors="ignore") as f:
            for linea in f:
                lineas_leidas += 1
                linea = linea.strip()
                match = patron_linea.match(linea)
                if not match:
                    continue

                tramas_validas += 1
                fecha_raw, hora_raw, freq_str, modo, snr_str, mensaje = match.groups()
                
                fecha_adif = "20" + fecha_raw
                if args.date and fecha_adif != args.date:
                    continue

                banda = freq_a_banda(freq_str)
                if not banda:
                    continue

                mi_snr = int(snr_str)

                # Quitar marcadores finales de decodificación de WSJT-X ("? a1", "a9", "?")
                mensaje = re.sub(r'\s+(?:\?\s*)?a\d+\s*$', '', mensaje)
                mensaje = re.sub(r'\s+\?\s*$', '', mensaje)

                # Si es mensaje compuesto con ';', nos quedamos con la segunda parte (quien transmite)
                if ";" in mensaje:
                    partes_compuestas = mensaje.split(";")
                    mensaje = partes_compuestas.pop().strip()

                tokens = mensaje.split()
                if len(tokens) < 2:
                    continue

                emisor = None
                grid_emisor = None
                corresponsal = None
                qso_snr = None

                primero = tokens.pop(0)

                if primero == "CQ":
                    siguiente = tokens.pop(0)
                    if es_indicativo_valido(siguiente):
                        emisor = limpiar_call(siguiente)
                        if tokens:
                            posible_grid = tokens.pop(0)
                            if es_grid_valido(posible_grid):
                                grid_emisor = posible_grid
                    elif tokens:
                        # Caso CQ DX / CQ NA / CQ AS / CQ SA / CQ ID + INDICATIVO + GRID
                        tercero = tokens.pop(0)
                        if es_indicativo_valido(tercero):
                            emisor = limpiar_call(tercero)
                            if tokens:
                                posible_grid = tokens.pop(0)
                                if es_grid_valido(posible_grid):
                                    grid_emisor = posible_grid
                else:
                    segundo = tokens.pop(0)
                    if es_indicativo_valido(segundo):
                        emisor = limpiar_call(segundo)
                        if es_indicativo_valido(primero):
                            corresponsal = limpiar_call(primero)
                        if tokens:
                            tercero = tokens.pop(0)
                            if es_grid_valido(tercero):
                                grid_emisor = tercero
                            elif es_reporte_qso(tercero):
                                qso_snr = tercero

                if not emisor:
                    continue

                clave = (fecha_adif, banda, emisor)
                
                if clave not in mejores_recepciones:
                    mejores_recepciones[clave] = {
                        "call": emisor,
                        "date": fecha_adif,
                        "time": hora_raw,
                        "freq": freq_str,
                        "band": banda,
                        "mode": modo,
                        "mi_snr": mi_snr,
                        "grid": grid_emisor,
                        "wkd_call": corresponsal,
                        "qso_snr": qso_snr
                    }
                else:
                    reg = mejores_recepciones[clave]
                    if mi_snr > reg["mi_snr"]:
                        reg["mi_snr"] = mi_snr
                        reg["time"] = hora_raw
                    if not reg["grid"] and grid_emisor:
                        reg["grid"] = grid_emisor
                    if not reg["wkd_call"] and corresponsal:
                        reg["wkd_call"] = corresponsal
                    if not reg["qso_snr"] and qso_snr:
                        reg["qso_snr"] = qso_snr

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{args.input}'.")
        return

    registros_ordenados = sorted(mejores_recepciones.values(), key=lambda x: (x["date"], x["time"]))

    with open(args.output, "w", encoding="utf-8") as out:
        out.write("Generated by WSJT-X_TO_EQSL_SWL Clean Parser\n")
        out.write(etiqueta_adif("ADIF_VER", "3.1.4") + "\n")
        out.write(etiqueta_adif("PROGRAMID", "WSJTX_SWL_CLEAN") + "\n")
        out.write(etiqueta_adif("CREATED_TIMESTAMP", datetime.now(timezone.utc).strftime("%Y%m%d %H%M%S")) + "\n")
        out.write("<EOH>\n\n")

        for r in registros_ordenados:
            mi_snr_fmt = f"{r['mi_snr']:+d}" if r['mi_snr'] != 0 else "+00"
            
            if r["wkd_call"] and r["qso_snr"]:
                detalle_qso = f" (QSO w/ {r['wkd_call']}, QSO SNR: {r['qso_snr']} dB)"
            elif r["wkd_call"]:
                detalle_qso = f" (QSO w/ {r['wkd_call']})"
            else:
                detalle_qso = " (CQ call)"

            comentario = f"SWL report from {args.city}. Copied at {mi_snr_fmt} dB{detalle_qso} using {args.rig}. 73!"

            campos = [
                etiqueta_adif("CALL", r["call"]),
                etiqueta_adif("QSO_DATE", r["date"]),
                etiqueta_adif("TIME_ON", r["time"]),
                etiqueta_adif("FREQ", r["freq"]),
                etiqueta_adif("BAND", r["band"]),
                etiqueta_adif("MODE", r["mode"]),
                etiqueta_adif("RST_RCVD", mi_snr_fmt),
                etiqueta_adif("SWL", "Y"),
                etiqueta_adif("OWNER_CALLSIGN", args.call.upper()),
                etiqueta_adif("MY_GRIDSQUARE", args.grid.upper()),
            ]

            if r["grid"]:
                campos.append(etiqueta_adif("GRIDSQUARE", r["grid"]))
            if r["wkd_call"]:
                campos.append(etiqueta_adif("APP_EQSL_SWL", r["wkd_call"]))

            campos.append(etiqueta_adif("COMMENT", comentario))
            out.write("".join(campos) + "<EOR>\n")

    print(f"Líneas leídas: {lineas_leidas} | Tramas válidas detectadas: {tramas_validas}")
    print(f"¡Listo! Se han exportado {len(registros_ordenados)} recepciones limpias a '{args.output}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convierte ALL.TXT de WSJT-X a ADIF limpio para eQSL SWL.")
    
    parser.add_argument("-i", "--input", required=True, help="Ruta del archivo ALL.TXT de entrada")
    parser.add_argument("-c", "--call", required=True, help="Tu indicativo SWL (ej. EA40365FD)")
    parser.add_argument("-g", "--grid", required=True, help="Tu cuadrícula Maidenhead (ej. IN80EK)")
    
    parser.add_argument("-o", "--output", default="SWL_eQSL.adi", help="Ruta del archivo ADIF de salida")
    parser.add_argument("-d", "--date", default=None, help="Filtrar por fecha exacta YYYYMMDD (ej. 20261127)")
    parser.add_argument("--city", default="Madrid", help="Ciudad o ubicación para el comentario")
    parser.add_argument("--rig", default="RTL-SDR v4 & 12.5m Long Wire + Balun", help="Descripción de equipo y antena")

    args = parser.parse_args()
    procesar_log(args)
