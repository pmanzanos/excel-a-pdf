import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Documento Generado desde Hoja de Cálculo', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, str(title).upper(), 0, 1, 'L', fill=True)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, str(body))
        self.ln(4)

def create_pdf(df):
    pdf = PDFGenerator()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for index, row in df.iterrows():
        pdf.add_page()
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 5, f"Registro {index + 1} de {len(df)}", 0, 1, 'R')
        
        for column in df.columns:
            pdf.chapter_title(column)
            # Usamos str(row[column]) para asegurar que datos numéricos no den error
            pdf.chapter_body(str(row[column]))

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Excel a PDF Converter", page_icon="📄")

st.title("📄 Convertidor de Excel a PDF")
st.write("Sube tu archivo y generaremos un único PDF organizado por apartados.")

uploaded_file = st.file_uploader("Elige un archivo Excel o CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # Leer datos
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"Archivo cargado con éxito: {len(df)} registros encontrados.")
        st.dataframe(df.head()) # Vista previa

        if st.button("🚀 Generar PDF"):
            with st.spinner('Creando documento...'):
                pdf_bytes = create_pdf(df)
                
                st.download_button(
                    label="⬇️ Descargar PDF Final",
                    data=pdf_bytes,
                    file_name="archivo_convertido.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Hubo un error al procesar el archivo: {e}")
