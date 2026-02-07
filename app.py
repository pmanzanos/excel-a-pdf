import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

class PDFParte(FPDF):
    def header(self):
        try:
            self.image('encabezado.png', 10, 8, 190)
            self.ln(30) 
        except:
            self.set_font('helvetica', 'B', 16)
            self.cell(0, 10, 'PARTE DE INCIDENCIAS', 0, 1, 'C')
            self.ln(5)

    def seccion(self, titulo):
        self.set_font('helvetica', 'B', 11)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, f" {titulo}", 0, 1, 'L', fill=True)
        self.ln(2)

    def campo(self, etiqueta, valor):
        self.set_font('helvetica', 'B', 10)
        self.write(6, f"{etiqueta}: ")
        self.set_font('helvetica', '', 10)
        
        # Limpiar valor para el PDF
        if pd.isna(valor) or str(valor).lower() == "nan" or str(valor) == "#VALUE!":
            val_str = "---"
        elif isinstance(valor, (datetime.datetime, pd.Timestamp)):
            val_str = valor.strftime('%d/%m/%Y')
        else:
            val_str = str(valor)
            
        self.multi_cell(0, 6, val_str.encode('latin-1', 'replace').decode('latin-1'))
        self.ln(1)

    def casilla_conforme(self, texto):
        self.set_font('helvetica', 'B', 10)
        x_pos, y_pos = self.get_x(), self.get_y()
        self.rect(x_pos, y_pos, 4, 4) 
        self.set_font('helvetica', 'B', 8)
        self.text(x_pos + 1, y_pos + 3.2, "X")
        self.set_xy(x_pos + 6, y_pos - 1)
        self.set_font('helvetica', '', 10)
        self.cell(0, 6, texto, 0, 1)
        self.ln(2)

def generar_pdf(datos_fila, nombre_jefatura):
    pdf = PDFParte()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # --- DATOS GENERALES ---
    pdf.seccion("DATOS GENERALES")
    pdf.campo("ID DEL PARTE", datos_fila.get('ID', '---'))
    pdf.campo("ALUMN@/O", datos_fila.get('ALUMNO OBJETO DEL PARTE', '---'))
    pdf.campo("CURSO / GRUPO / TUTOR", datos_fila.get('CURSO / GRUPO / TUTOR', '---'))
    pdf.campo("FECHA DEL INCIDENTE", datos_fila.get('FECHA DEL INCIDENTE', '---'))
    pdf.campo("TRAMO HORARIO", datos_fila.get('TRAMO HORARIO EN QUE SE PRODUCE EL INCIDENTE', '---'))
    pdf.campo("LUGAR", datos_fila.get('LUGAR EN QUE SE PRODUCE EL INCIDENTE', '---'))
    
    docente_nombre = datos_fila.get('DOCENTE / ED. SOCIAL QUE IMPONE EL PARTE', '---')
    pdf.campo("DOCENTE", docente_nombre)

    pdf.ln(3); pdf.seccion("TIPO DE INCIDENCIA")
    pdf.campo("CATEGORÍA", datos_fila.get('TIPO DE INCIDENCIA', '---'))
    
    leve = datos_fila.get('DEFINICIÓN DE LA CONDUCTA O CONDUCTAS CONTRARIAS A LA NORMA', '')
    grave = datos_fila.get('DEFINICIÓN DE LA CONDUCTA O CONDUCTAS  GRAVEMENTE PERJUDICIALES PARA LA CONVIVENCIA.', '')
    
    if pd.notna(leve) and str(leve).strip() != "": pdf.campo("CONDUCTA LEVE", leve)
    if pd.notna(grave) and str(grave).strip() != "": pdf.campo("CONDUCTA GRAVE", grave)

    pdf.ln(3); pdf.seccion("DESCRIPCIÓN DE LOS HECHOS")
    hechos = datos_fila.get('DESCRIBE LOS HECHOS QUE MOTIVAN EL APERCIBIMIENTO POR ESCRITO', 'Sin descripción.')
    pdf.multi_cell(0, 5, str(hechos).encode('latin-1', 'replace').decode('latin-1'))

    pdf.ln(10)
    pdf.casilla_conforme("Conforme del Docente / Ed. Social")
    pdf.casilla_conforme("Conforme de la Jefatura de Estudios")

    pdf.ln(10); y_actual = pdf.get_y()
    pdf.set_xy(10, y_actual)
    pdf.set_font('helvetica', 'B', 10); pdf.cell(90, 6, "V.º B.º El Docente / Ed. Social", 0, 1, 'L')
    pdf.set_font('helvetica', 'I', 9); pdf.cell(90, 6, f"Fdo: {docente_nombre}".encode('latin-1', 'replace').decode('latin-1'), 0, 0, 'L')

    pdf.set_xy(110, y_actual)
    pdf.set_font('helvetica', 'B', 10); pdf.cell(90, 6, "V.º B.º Jefatura de Estudios", 0, 1, 'L')
    pdf.set_font('helvetica', 'I', 9); pdf.set_x(110); pdf.cell(90, 6, f"Fdo: {nombre_jefatura}".encode('latin-1', 'replace').decode('latin-1'), 0, 0, 'L')

    return pdf.output()

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Generador de Partes", page_icon="📝")
st.title("📝 Generador de Partes de Incidencias")

archivo = st.file_uploader("Sube el archivo Excel (PARTES.RESPUESTAS.xlsx)", type=['xlsx'])

if archivo:
    try:
        # Cargar hojas
        df = pd.read_excel(archivo, sheet_name='RPTS')
        df_parte_raw = pd.read_excel(archivo, sheet_name='PARTE', header=None)
        
        # Jefatura
        try:
            nombre_jefatura = df_parte_raw.iloc[48, 3]
            if pd.isna(nombre_jefatura): nombre_jefatura = "Jefatura de Estudios"
        except:
            nombre_jefatura = "Jefatura de Estudios"

        # TRATAMIENTO SIMPLE DE IDs (Como en las versiones que funcionaban)
        # Convertimos la columna ID a texto, quitando el ".0" si existe
        df['ID_TEXTO'] = df['ID'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        if 'FECHA DEL INCIDENTE' in df.columns:
            df['FECHA DEL INCIDENTE'] = pd.to_datetime(df['FECHA DEL INCIDENTE'], errors='coerce')
        
        st.success(f"✅ Archivo cargado correctamente. Jefatura: {nombre_jefatura}")

        # Buscador
        id_buscada = st.text_input("Introduce la ID del parte (ej. 5801):").strip()

        if id_buscada:
            # Buscamos coincidencia exacta en texto
            resultado = df[df['ID_TEXTO'] == id_buscada]

            if not resultado.empty:
                fila = resultado.iloc[0]
                st.info(f"🔎 Encontrado: {fila['ALUMNO OBJETO DEL PARTE']}")
                
                if st.button("🚀 Crear PDF"):
                    pdf_bytes = generar_pdf(fila, nombre_jefatura)
                    st.download_button(
                        label="⬇️ Descargar PDF",
                        data=bytes(pdf_bytes),
                        file_name=f"Parte_{id_buscada}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error(f"❌ La ID '{id_buscada}' no existe en el archivo.")
                # Ayuda: mostramos algunas IDs para verificar el formato
                with st.expander("Ver IDs disponibles en el archivo"):
                    st.write(df['ID_TEXTO'].unique().tolist()[:50])

    except Exception as e:
        st.error(f"⚠️ Error al procesar el archivo: {e}")
else:
    st.info("👋 Por favor, sube el archivo Excel para empezar.")
