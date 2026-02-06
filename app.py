import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

class PDFGenerator(FPDF):
    def header(self):
        # Intentamos usar una fuente segura para el título
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Reporte General de Datos', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 11)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 8, str(title).upper(), 0, 1, 'L', fill=True)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('helvetica', '', 10)
        # Multi_cell maneja automáticamente los saltos de línea
        self.multi_cell(0, 6, str(body))
        self.ln(4)

def create_pdf(df):
    # 'P' = Portrait (Vertical), 'mm' = milímetros, 'A4' = tamaño papel
    pdf = PDFGenerator(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Si tienes el archivo DejaVuSans.ttf en la carpeta, descomenta estas líneas:
    # pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    # pdf.set_font('DejaVu', '', 10)

    for index, row in df.iterrows():
        pdf.add_page()
        
        # Indicador de registro
        pdf.set_font('helvetica', 'I', 8)
        pdf.cell(0, 5, f"Registro {index + 1} de {len(df)}", 0, 1, 'R')
        
        for column in df.columns:
            pdf.chapter_title(column)
            # Reemplazamos caracteres que suelen dar problemas en latin-1 si no usamos fuentes Unicode
            texto_limpio = str(row[column]).encode('latin-1', 'replace').decode('latin-1')
            pdf.chapter_body(texto_limpio)
            
    return pdf.output()

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Convertidor Excel a PDF", page_icon="📄")

# Estilo personalizado con CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 Generador de PDF Corporativo")
st.info("Sube tu archivo Excel o CSV. Cada fila se convertirá en una página nueva con sus apartados correspondientes.")

uploaded_file = st.file_uploader("Arrastra aquí tu archivo", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # Carga de datos
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Archivo cargado: {len(df)} registros detectados.")
        
        # Mostrar vista previa
        with st.expander("Ver vista previa de los datos"):
            st.dataframe(df.head())

        if st.button("🚀 Crear y Descargar PDF"):
            with st.spinner('Procesando documento...'):
                pdf_output = create_pdf(df)
                
                # Manejo de la salida de datos para evitar el error de NoneType o bytearray
                if pdf_output:
                    st.download_button(
                        label="⬇️ Descargar Archivo PDF",
                        data=bytes(pdf_output),
                        file_name="reporte_final.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("El generador no devolvió datos.")
                    
    except Exception as e:
        st.error(f"❌ Error crítico: {e}")

st.divider()
st.caption("Desarrollado con Python, Streamlit y FPDF2")
