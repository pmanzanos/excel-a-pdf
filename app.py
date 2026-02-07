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
        val_str = str(valor) if pd.notna(valor) else "---"
        self.multi_cell(0, 6, val_str.encode('latin-1', 'replace').decode('latin-1'))
        self.ln(2)

def generar_pdf(datos_fila):
    pdf = PDFParte()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Mapeo exacto basado en tus columnas de "RPTS"
    pdf.seccion("DATOS GENERALES")
    pdf.campo("ID DEL PARTE", datos_fila.get('ID', 'N/A'))
    pdf.campo("ALUMN@/O", datos_fila.get('ALUMNO OBJETO DEL PARTE', 'N/A'))
    pdf.campo("CURSO / GRUPO / TUTOR", datos_fila.get('CURSO / GRUPO / TUTOR', 'N/A'))
    pdf.campo("FECHA DEL INCIDENTE", datos_fila.get('FECHA DEL INCIDENTE', 'N/A'))
    pdf.campo("TRAMO HORARIO", datos_fila.get('TRAMO HORARIO EN QUE SE PRODUCE EL INCIDENTE', 'N/A'))
    pdf.campo("LUGAR", datos_fila.get('LUGAR EN QUE SE PRODUCE EL INCIDENTE', 'N/A'))
    pdf.campo("DOCENTE", datos_fila.get('DOCENTE / ED. SOCIAL QUE IMPONE EL PARTE', 'N/A'))

    pdf.ln(5)
    pdf.seccion("TIPO DE INCIDENCIA")
    pdf.campo("CATEGORÍA", datos_fila.get('TIPO DE INCIDENCIA', 'N/A'))
    
    # Comprobamos categorías leve/grave
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
st.set_page_config(page_title="Generador de Partes", page_icon="📝")
st.title("📝 Buscador de Partes por ID")

archivo = st.file_uploader("Sube el archivo Excel", type=['xlsx'])

if archivo:
    try:
        # Cargamos la pestaña RPTS
        df = pd.read_excel(archivo, sheet_name='RPTS')
        
        # LIMPIEZA CRÍTICA: Convertimos la columna ID a String y quitamos espacios o errores
        df = df[df['ID'].notna()] # Quitar filas vacías
        df['ID_STR'] = df['ID'].astype(str).str.replace('.0', '', regex=False).str.strip()
        
        st.success(f"Base de datos cargada. {len(df)} registros listos.")

        # Usamos text_input para evitar problemas de formato numérico
        id_buscada = st.text_input("Escribe la ID del parte (ejemplo: 5801):").strip()

        if id_buscada:
            # Buscamos en la columna de texto que hemos creado
            resultado = df[df['ID_STR'] == id_buscada]

            if not resultado.empty:
                fila = resultado.iloc[0]
                st.info(f"✅ Encontrado: {fila['ALUMNO OBJETO DEL PARTE']}")
                
                if st.button("🚀 Descargar PDF de este Parte"):
                    pdf_bytes = generar_pdf(fila)
                    st.download_button(
                        label="⬇️ Guardar Archivo",
                        data=bytes(pdf_bytes),
                        file_name=f"Parte_{id_buscada}.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error(f"❌ La ID '{id_buscada}' no aparece en la hoja RPTS. Revisa que sea correcta.")
                # Opcional: mostrar IDs disponibles para ayudar al usuario
                with st.expander("Ver IDs disponibles"):
                    st.write(", ".join(df['ID_STR'].unique()[:20]) + "...")

    except Exception as e:
        st.error(f"Hubo un problema: {e}")
