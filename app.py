import streamlit as st
import pandas as pd
from fpdf import FPDF

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Informe Detallado de Registro', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 11)
        self.set_fill_color(240, 240, 240)
        # multi_cell por si el título de la columna es muy largo
        self.multi_cell(0, 8, str(title).upper(), 0, 'L', fill=True)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('helvetica', '', 10)
        self.multi_cell(0, 6, str(body))
        self.ln(4)

def create_single_pdf(row_data, columns_to_show):
    pdf = PDFGenerator(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    for col_name in columns_to_show:
        valor = row_data[col_name]
        if pd.isna(valor): valor = "---"
        
        pdf.chapter_title(col_name)
        # Limpieza para evitar errores de símbolos no soportados
        texto_limpio = str(valor).encode('latin-1', 'replace').decode('latin-1')
        pdf.chapter_body(texto_limpio)
            
    return pdf.output()

# --- INTERFAZ ---
st.set_page_config(page_title="Generador de Informes", page_icon="📑")

st.title("📑 Generador de Informes a la Carta")
st.markdown("""
**Reglas de procesamiento:**
1. Etiquetas tomadas de la **Fila 1**.
2. Datos procesados desde la **Fila 4**.
3. Puedes elegir **qué columnas omitir**.
""")

uploaded_file = st.file_uploader("Sube tu archivo (XLSX o CSV)", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # Obtener nombres de columnas (Fila 1)
        header_df = pd.read_excel(uploaded_file, nrows=0) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file, nrows=0)
        todas_las_etiquetas = header_df.columns.tolist()

        # Leer datos desde la Fila 4
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=3, names=todas_las_etiquetas)
        else:
            df = pd.read_excel(uploaded_file, skiprows=3, names=todas_las_etiquetas)
        
        st.sidebar.header("Configuración de Columnas")
        # Selector para omitir columnas iniciales
        num_omitir = st.sidebar.number_input("¿Cuántas columnas iniciales quieres OMITIR?", min_value=0, max_value=len(todas_las_etiquetas)-1, value=0)
        
        columnas_finales = todas_las_etiquetas[num_omitir:]
        
        st.sidebar.write("Columnas que aparecerán en el PDF:")
        st.sidebar.info(", ".join(columnas_finales))

        # Selector de Fila
        opciones = [f"Fila {i + 4}: {str(row.iloc[0])[:20]}..." for i, row in df.iterrows()]
        seleccion = st.selectbox("Selecciona el registro:", range(len(opciones)), format_func=lambda x: opciones[x])

        if st.button("🚀 Generar PDF"):
            fila_seleccionada = df.iloc[seleccion]
            
            with st.spinner('Generando documento...'):
                pdf_output = create_single_pdf(fila_seleccionada, columnas_finales)
                
                if pdf_output:
                    st.download_button(
                        label="⬇️ Descargar PDF",
                        data=bytes(pdf_output),
                        file_name=f"Informe_Fila_{seleccion + 4}.pdf",
                        mime="application/pdf"
                    )

    except Exception as e:
        st.error(f"Error: {e}")
