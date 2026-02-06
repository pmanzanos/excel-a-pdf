import streamlit as st
import pandas as pd
from fpdf import FPDF

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Informe de Registro', 0, 1, 'C')
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
    
    for col_name, valor in row_data.items():
        if pd.isna(valor): valor = "---"
        
        pdf.chapter_title(col_name)
        # Limpieza para evitar errores de símbolos
        texto_limpio = str(valor).encode('latin-1', 'replace').decode('latin-1')
        pdf.chapter_body(texto_limpio)
            
    return pdf.output()

# --- INTERFAZ ---
st.set_page_config(page_title="Excel a PDF Pro", page_icon="📝")

st.title("📝 Generador de Informes por Fila")

uploaded_file = st.file_uploader("Sube tu archivo Excel o CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # CARGA SIN SALTOS: Leemos desde la fila 1 (donde están las etiquetas)
        # Por defecto, pandas toma la primera fila como nombres de columna (header=0)
        df_original = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
        
        # --- FILTRO DE COLUMNAS (HORIZONTAL) ---
        st.sidebar.header("Configuración")
        cols_a_omitir = st.sidebar.number_input("¿Cuántas columnas iniciales omitir?", 
                                               min_value=0, 
                                               max_value=len(df_original.columns)-1, 
                                               value=3)
        
        # Recortamos columnas
        df_filtrado = df_original.iloc[:, cols_a_omitir:]

        # --- SELECTOR DE FILA (SINCRONIZADO CON EXCEL) ---
        # En Pandas, el índice 0 corresponde a la fila 2 de Excel (porque la 1 son las etiquetas).
        # Queremos que el usuario vea: "Fila 2", "Fila 3", "Fila 4", etc.
        opciones = []
        for i in range(len(df_filtrado)):
            num_excel = i + 2  # i=0 es fila 2 en Excel
            dato_guia = str(df_filtrado.iloc[i, 0])[:15] # Primer dato para ayudar a identificar
            opciones.append(f"Fila {num_excel} ({dato_guia}...)")

        st.write(f"### Selección de datos")
        seleccion_idx = st.selectbox("Elige la fila de Excel de la que quieres el PDF:", 
                                     range(len(opciones)), 
                                     format_func=lambda x: opciones[x])

        if st.button("🚀 Generar PDF"):
            fila_seleccionada = df_filtrado.iloc[seleccion_idx]
            num_fila_excel = seleccion_idx + 2
            
            with st.spinner('Construyendo documento...'):
                pdf_output = create_single_pdf(fila_seleccionada)
                
                st.download_button(
                    label=f"⬇️ Descargar PDF (Fila {num_fila_excel})",
                    data=bytes(pdf_output),
                    file_name=f"Informe_Fila_{num_fila_excel}.pdf",
                    mime="application/pdf"
                )

        st.divider()
        st.write("#### Vista previa del registro seleccionado:")
        st.dataframe(df_filtrado.iloc[[seleccion_idx]])

    except Exception as e:
        st.error(f"Error en el proceso: {e}")
