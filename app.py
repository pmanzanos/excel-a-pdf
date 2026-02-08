import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime

class PDFParte(FPDF):
    def header(self):
        # 1. INSERTAR IMAGEN DE ENCABEZADO
        # 'encabezado.png' debe estar en la misma carpeta que el script. 
        # El 10, 8 es la posición (x, y) y el 190 es el ancho en mm.
        try:
            self.image('encabezado.png', 10, 8, 190)
            self.ln(30) # Espacio para que el texto no pise la imagen
        except:
            # Si no encuentra la imagen, pone el título en texto para no dar error
            self.set_font('helvetica', 'B', 16)
            self.cell(0, 10, 'PARTE DE INCIDENCIAS', 0, 1, 'C')
            self.ln(5)

    def seccion(self, titulo):
        self.set_font('helvetica', 'B', 11)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, f" {titulo}", 0, 1, 'L', fill=True)
        self.ln(2)

    def campo(self, etiqueta, valor):
        self.set_font('helvetica', 'B', 10)
        self.write(6, f"{etiqueta}: ")
        self.set_font('helvetica', '', 10)
        
        # Limpieza de fechas para quitar la hora 00:00:00
        if isinstance(valor, (datetime.datetime, pd.Timestamp)):
            val_str = valor.strftime('%d/%m/%Y')
        else:
            val_str = str(valor) if pd.notna(valor) else "---"
            
        self.multi_cell(0, 6, val_str.encode('latin-1', 'replace').decode('latin-1'))
        self.ln(2)

def generar_pdf(datos_fila):
    pdf = PDFParte()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.seccion("DATOS GENERALES")
    pdf.campo("ID DEL PARTE", datos_fila.get('ID', 'N/A'))
    pdf.campo("ALUMN@/O", datos_fila.get('ALUMNO OBJETO DEL PARTE', 'N/A'))
    pdf.campo("CURSO / GRUPO / TUTOR", datos_fila.get('CURSO / GRUPO / TUTOR', 'N/A'))
    
    # 2. TRATAMIENTO ESPECÍFICO DE LA FECHA
    fecha_raw = datos_fila.get('FECHA DEL INCIDENTE', 'N/A')
    pdf.campo("FECHA DEL INCIDENTE", fecha_raw)
    
    pdf.campo("TRAMO HORARIO", datos_fila.get('TRAMO HORARIO EN QUE SE PRODUCE EL INCIDENTE', 'N/A'))
    pdf.campo("LUGAR", datos_fila.get('LUGAR EN QUE SE PRODUCE EL INCIDENTE', 'N/A'))
    pdf.campo("DOCENTE", datos_fila.get('DOCENTE / ED. SOCIAL QUE IMPONE EL PARTE', 'N/A'))

    pdf.ln(5)
    pdf.seccion("TIPO DE INCIDENCIA")
    pdf.campo("CATEGORÍA", datos_fila.get('TIPO DE INCIDENCIA', 'N/A'))
    
    leve = datos_fila.get('DEFINICIÓN DE LA CONDUCTA O CONDUCTAS CONTRARIAS A LA NORMA', '')
    grave = datos_fila.get('DEFINICIÓN DE LA CONDUCTA O CONDUCTAS  GRAVEMENTE PERJUDICIALES PARA LA CONVIVENCIA.', '')
    
    if pd.notna(leve) and str(leve).strip() != "":
        pdf.campo("CONDUCTA LEVE", leve)
    if pd.notna(grave) and str(grave).strip() != "":
        pdf.campo("CONDUCTA GRAVE", grave)

    pdf.ln(5)
    pdf.seccion("DESCRIPCIÓN DE LOS HECHOS")
    hechos = datos_fila.get('DESCRIBE LOS HECHOS QUE MOTIVAN EL APERCIBIMIENTO POR ESCRITO', 'Sin descripción.')
    pdf.multi_cell(0, 6, str(hechos).encode('latin-1', 'replace').decode('latin-1'))

    return pdf.output()

# --- INTERFAZ ---
st.set_page_config(page_title="Generador de Partes Pro", page_icon="📝")
st.title("📝 Buscador de Partes con Encabezado")

archivo = st.file_uploader("Sube el archivo Excel", type=['xlsx'])

if archivo:
    try:
        # Cargamos RPTS y forzamos que la columna de fecha sea tratada como tal
        df = pd.read_excel(archivo, sheet_name='RPTS')
        if 'FECHA DEL INCIDENTE' in df.columns:
            df['FECHA DEL INCIDENTE'] = pd.to_datetime(df['FECHA DEL INCIDENTE'], errors='coerce')
        
        df = df[df['ID'].notna()] 
        df['ID_STR'] = df['ID'].astype(str).str.replace('.0', '', regex=False).str.strip()
        
        st.success("Base de datos cargada.")

        id_buscada = st.text_input("ID del parte:").strip()

        if id_buscada:
            resultado = df[df['ID_STR'] == id_buscada]
            if not resultado.empty:
                fila = resultado.iloc[0]
                st.info(f"Seleccionado: {fila['ALUMNO OBJETO DEL PARTE']}")
                
                if st.button("🚀 Generar PDF con Logo"):
                    pdf_bytes = generar_pdf(fila)
                    st.download_button(
                        label="⬇️ Descargar PDF",
                        data=bytes(pdf_bytes),
                        file_name=f"Parte_{id_buscada}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error("ID no encontrada.")

    except Exception as e:
        st.error(f"Error: {e}")
