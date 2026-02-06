import streamlit as st
import pandas as pd
from fpdf import FPDF

class PDFGenerator(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Informe Individual de Registro', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('helvetica', 'B', 11)
        self.set_fill_color(230, 230, 230)
        self.multi_cell(0, 8, str(title).upper(), 0, 'L', fill=True)
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('helvetica', '', 10)
        # multi_cell es clave para que el texto largo no se corte y fluya a la siguiente página
        self.multi_cell(0, 6, str(body))
        self.ln(4)

def create_single_pdf(row_data, columns):
    pdf = PDFGenerator(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    for col_name in columns:
        valor = row_data[col_name]
        # Evitar imprimir apartados vacíos si lo deseas, o poner "N/A"
        if pd.isna(valor): valor = "Sin información"
        
        pdf.chapter_title(col_name)
        # Limpieza de caracteres para evitar errores de encoding
        texto_limpio = str(valor).encode('latin-1', 'replace').decode('latin-1')
        pdf.chapter_body(texto_limpio)
            
    return pdf.output()

# --- INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Generador de Informes Pro", page_icon="📄")

st.title("📄 Generador de Informes Individuales")
st.markdown("Carga tu archivo y genera un PDF único para un registro específico.")

uploaded_file = st.file_uploader("Sube tu Excel o CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # 1. LEER EL ARCHIVO COMPLETO PRIMERO PARA LAS ETIQUETAS
        # La primera fila (índice 0) serán las columnas
        header_df = pd.read_excel(uploaded_file, nrows=0) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file, nrows=0)
        etiquetas = header_df.columns.tolist()

        # 2. LEER DATOS DESDE LA FILA 4 (skiprows=3)
        # Nota: skiprows=3 salta las filas 1, 2 y 3. La fila 4 se convierte en el primer dato.
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=3, names=etiquetas)
        else:
            df = pd.read_excel(uploaded_file, skiprows=3, names=etiquetas)
        
        st.success(f"Base de datos cargada. {len(df)} registros disponibles (empezando desde la fila 4).")

        # 3. SELECTOR DE FILA
        # Usamos una columna identificadora (por ejemplo la primera) para el selector
        opciones = [f"Fila {i + 4}: {str(row[0])[:30]}..." for i, row in df.iterrows()]
        seleccion = st.selectbox("Selecciona el registro que deseas convertir a PDF:", range(len(opciones)), format_func=lambda x: opciones[x])

        # 4. BOTÓN DE GENERACIÓN
        if st.button("🚀 Generar PDF de este registro"):
            fila_seleccionada = df.iloc[seleccion]
            
            with st.spinner('Construyendo documento...'):
                pdf_output = create_single_pdf(fila_seleccionada, etiquetas)
                
                if pdf_output:
                    st.download_button(
                        label="⬇️ Descargar Informe PDF",
                        data=bytes(pdf_output),
                        file_name=f"Informe_Fila_{seleccion + 4}.pdf",
                        mime="application/pdf"
                    )

    except Exception as e:
        st.error(f"❌ Error al procesar: {e}")

st.divider()
st.caption("Configuración: Etiquetas en Fila 1 | Datos desde Fila 4")
