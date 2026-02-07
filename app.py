import streamlit as st
import pandas as pd
from fpdf import FPDF

class PDFParte(FPDF):
    def header(self):
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
        self.multi_cell(0, 6, str(valor))
        self.ln(2)

def generar_pdf_por_id(datos_fila):
    pdf = PDFParte()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Mapeo según tu hoja "PARTE"
    pdf.seccion("DATOS GENERALES")
    pdf.campo("ID", datos_fila.get('ID', 'N/A'))
    pdf.campo("ALUMN@/O", datos_fila.get('ALUMNO OBJETO DEL PARTE', 'N/A'))
    pdf.campo("CURSO / GRUPO / TUTOR", datos_fila.get('CURSO / GRUPO / TUTOR', 'N/A'))
    pdf.campo("FECHA", datos_fila.get('FECHA DEL INCIDENTE', 'N/A'))
    pdf.campo("TRAMO HORARIO", datos_fila.get('TRAMO HORARIO EN QUE SE PRODUCE EL INCIDENTE', 'N/A'))
    pdf.campo("LUGAR", datos_fila.get('LUGAR EN QUE SE PRODUCE EL INCIDENTE', 'N/A'))
    pdf.campo("DOCENTE QUE IMPONE EL PARTE", datos_fila.get('DOCENTE / ED. SOCIAL QUE IMPONE EL PARTE', 'N/A'))

    pdf.ln(5)
    pdf.seccion("TIPO DE INCIDENCIA")
    pdf.campo("CATEGORÍA", datos_fila.get('TIPO DE INCIDENCIA', 'N/A'))
    
    # Verificamos si es leve o grave según tus columnas
    desc_leve = datos_fila.get('DEFINICIÓN DE LA CONDUCTA O CONDUCTAS CONTRARIAS A LA NORMA', '')
    desc_grave = datos_fila.get('DEFINICIÓN DE LA CONDUCTA O CONDUCTAS  GRAVEMENTE PERJUDICIALES PARA LA CONVIVENCIA.', '')
    
    if pd.notna(desc_leve) and desc_leve != "":
        pdf.campo("CONDUCTA CONTRARIA", desc_leve)
    if pd.notna(desc_grave) and desc_grave != "":
        pdf.campo("CONDUCTA GRAVE", desc_grave)

    pdf.ln(5)
    pdf.seccion("DESCRIPCIÓN DE LOS HECHOS")
    hechos = datos_fila.get('DESCRIBE LOS HECHOS QUE MOTIVAN EL APERCIBIMIENTO POR ESCRITO', 'Sin descripción.')
    pdf.multi_cell(0, 6, str(hechos).encode('latin-1', 'replace').decode('latin-1'))

    return pdf.output()

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Generador de Partes", page_icon="📝")
st.title("📝 Sistema de Generación de Partes")

# En una app real, podrías subir el archivo una sola vez
archivo = st.file_uploader("Sube el archivo 'PARTES.RESPUESTAS.xlsx'", type=['xlsx', 'csv'])

if archivo:
    # Cargamos la hoja de datos (RPTS)
    # Si es CSV usamos el que me pasaste, si es XLSX buscamos la pestaña "RPTS"
    try:
        if archivo.name.endswith('.csv'):
            df = pd.read_csv(archivo)
        else:
            df = pd.read_excel(archivo, sheet_name='RPTS')
        
        st.success("Base de datos cargada correctamente.")

        # BUSCADOR POR ID
        id_buscar = st.number_input("Introduce la ID del parte:", min_value=0, step=1)

        if id_buscar:
            # Buscamos la fila que coincide con la ID
            resultado = df[df['ID'] == id_buscar]

            if not resultado.empty:
                fila = resultado.iloc[0]
                st.info(f"Parte encontrado: {fila['ALUMNO OBJETO DEL PARTE']}")
                
                # Vista previa rápida
                with st.expander("Ver datos del parte"):
                    st.write(fila)

                if st.button("🚀 Generar PDF del Parte"):
                    pdf_bytes = generar_pdf_por_id(fila)
                    st.download_button(
                        label="⬇️ Descargar Parte en PDF",
                        data=bytes(pdf_bytes),
                        file_name=f"Parte_{id_buscar}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.warning(f"No se ha encontrado ningún parte con la ID {id_buscar}")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
