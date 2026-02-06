import streamlit as st
import pandas as pd
from fpdf import FPDF

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Informe de Registro Específico', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 11)
        self.set_fill_color(240, 240, 240)
        self.multi_cell(0, 8, str(title).upper(), 0, 'L', fill=True)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 6, str(body))
        self.ln(4)

def create_single_pdf(row_data):
    pdf = PDFGenerator(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # row_data ya viene filtrado desde el DataFrame, 
    # así que aquí solo iteramos lo que queda.
    for col_name, valor in row_data.items():
        if pd.isna(valor): valor = "---"
        
        pdf.chapter_title(col_name)
        texto_limpio = str(valor).encode('latin-1', 'replace').decode('latin-1')
        pdf.chapter_body(texto_limpio)
            
    return pdf.output()

# --- INTERFAZ ---
st.set_page_config(page_title="Excel a PDF", page_icon="📑")

st.title("📑 Generador de Informes Filtrados")

uploaded_file = st.file_uploader("Sube tu Excel o CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # 1. Leemos los nombres de las columnas (Fila 1)
        header_df = pd.read_excel(uploaded_file, nrows=0) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file, nrows=0)
        columnas_originales = header_df.columns.tolist()

        # 2. Leemos datos desde la Fila 4 (salta las primeras 3 filas de datos)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=3, names=columnas_originales)
        else:
            df = pd.read_excel(uploaded_file, skiprows=3, names=columnas_originales)

        # --- CORRECCIÓN: FILTRO DE COLUMNAS (HORIZONTAL) ---
        st.sidebar.header("Configuración de Columnas")
        cols_a_omitir = st.sidebar.number_input("¿Cuántas columnas iniciales omitir en el PDF?", 
                                               min_value=0, 
                                               max_value=len(columnas_originales)-1, 
                                               value=3) # Por defecto omitimos 3 (A, B, C)
        
        # Seleccionamos solo desde la columna 'n' en adelante para todo el DataFrame
        df_final = df.iloc[:, cols_a_omitir:]

        # --- SELECTOR DE FILA ---
        opciones = [f"Fila Excel {i + 4}" for i in range(len(df_final))]
        seleccion_idx = st.selectbox("Selecciona el número de fila (según Excel):", 
                                     range(len(opciones)), 
                                     format_func=lambda x: opciones[x])

        if st.button("🚀 Generar PDF"):
            # Extraemos la fila seleccionada ya recortada
            fila_recortada = df_final.iloc[seleccion_idx]
            
            with st.spinner('Generando PDF sin las columnas omitidas...'):
                pdf_output = create_single_pdf(fila_recortada)
                
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=bytes(pdf_output),
                    file_name=f"Informe_Fila_{seleccion_idx + 4}.pdf",
                    mime="application/pdf"
                )

        st.write("### Vista previa de lo que irá al PDF:")
        st.dataframe(df_final.head(1))

    except Exception as e:
        st.error(f"Error: {e}")
