import streamlit as st
import pandas as pd
from fpdf import FPDF

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Informe Personalizado', 0, 1, 'C')
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
    
    # Recorremos solo las columnas que quedan en el registro
    for col_name, valor in row_data.items():
        if pd.isna(valor): valor = "---"
        
        pdf.chapter_title(col_name)
        # Limpieza para evitar errores de símbolos
        texto_limpio = str(valor).encode('latin-1', 'replace').decode('latin-1')
        pdf.chapter_body(texto_limpio)
            
    return pdf.output()

# --- INTERFAZ ---
st.set_page_config(page_title="Generador PDF Excel", page_icon="📝")

st.title("📝 Generador de PDF por Fila")

uploaded_file = st.file_uploader("Sube tu archivo Excel o CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # 1. Obtener etiquetas de la Fila 1
        header_df = pd.read_excel(uploaded_file, nrows=0) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file, nrows=0)
        etiquetas_originales = header_df.columns.tolist()

        # 2. Cargar datos desde la Fila 4 (skiprows=3)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=3, names=etiquetas_originales)
        else:
            df = pd.read_excel(uploaded_file, skiprows=3, names=etiquetas_originales)

        # --- AJUSTES DE COLUMNAS ---
        st.sidebar.header("Filtro de Columnas")
        cols_a_omitir = st.sidebar.number_input("¿Cuántas columnas iniciales omitir?", min_value=0, max_value=len(etiquetas_originales)-1, value=0)
        
        # Recortamos el DataFrame: quitamos las primeras 'n' columnas
        df_filtrado = df.iloc[:, cols_a_omitir:]

        # --- SELECTOR DE FILA (Sincronizado con Excel) ---
        # Si saltamos 3 filas, la primera fila de datos en nuestro DF es la 4 de Excel.
        # El índice de la fila en el selector será: i + 4
        opciones = []
        for i, row in df_filtrado.iterrows():
            # Mostramos el número de fila real de Excel y el primer dato visible
            primer_dato = str(row.iloc[0])[:20] if not row.empty else "Vacío"
            opciones.append(f"Fila {i + 4} - ({primer_dato})")

        seleccion_idx = st.selectbox("Selecciona el registro (según número de fila en Excel):", 
                                     range(len(opciones)), 
                                     format_func=lambda x: opciones[x])

    
        if st.button("🚀 Generar PDF de esta fila"):
            fila_para_pdf = df_filtrado.iloc[seleccion_idx]
            
            with st.spinner('Generando archivo...'):
                pdf_output = create_single_pdf(fila_para_pdf)
                
                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=bytes(pdf_output),
                    file_name=f"Fila_{seleccion_idx + 4}_Informe.pdf",
                    mime="application/pdf"
                )

    except Exception as e:
        st.error(f"Error en el proceso: {e}")

st.divider()
st.caption("Nota: La fila 1 se usa como encabezado. Los datos empiezan en la fila 4.")
