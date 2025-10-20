from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # Configura el logo o título si quieres
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Plan Nutricional para Ganar Masa Muscular', 0, 1, 'C')
        self.ln(10) # Añade un pequeño espacio

    def chapter_title(self, title):
        # Título de capítulo
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        # Cuerpo del texto
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 7, body)
        self.ln()

    def add_recipe(self, title, ingredients, steps):
        # Función para añadir una receta formateada
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        
        self.set_font('Arial', 'I', 11)
        self.multi_cell(0, 7, "Ingredientes:\n" + ingredients)
        self.ln(2)
        
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 7, "Preparación:\n" + steps)
        self.ln(5)

# --- Contenido del PDF ---

lista_compra_texto = """
🛒 Proteínas
    - Pechugas de pollo o pavo
    - Carne picada de ternera (+5% grasa)
    - Huevos
    - Salmón fresco o congelado
    - Latas de atún
    - Yogur griego natural
    - Queso fresco batido / Requesón
    - Lentejas o garbanzos

🥑 Grasas Saludables
    - Aguacates
    - Frutos secos al natural (nueces, almendras)
    - Crema de cacahuete 100%
    - Aceite de Oliva Virgen Extra
    - Semillas de chía o lino

🍚 Carbohidratos
    - Avena en copos
    - Arroz (basmati o integral)
    - Patatas y Boniato
    - Pan integral
    - Pasta integral

🍓 Frutas y Verduras
    - Plátanos
    - Frutos rojos (frescos o congelados)
    - Espinacas, brócoli, pimientos, cebolla
"""

# --- Creación del PDF ---

pdf = PDF()
pdf.add_page()

# Añadir la lista de la compra
pdf.chapter_title('Lista de la Compra Detallada')
pdf.chapter_body(lista_compra_texto)

# Añadir las recetas
pdf.add_page()
pdf.chapter_title('Recetas Fáciles y Nutritivas')

pdf.add_recipe(
    "1. Batido 'Bomba' de Desayuno o Post-Entreno",
    """- 1 plátano maduro
- 30g de proteína en polvo
- 1 cucharada sopera de crema de cacahuete
- 40g de avena en copos
- 250 ml de leche entera
- Un puñadito de espinacas frescas
- Opcional: 5g de creatina""",
    """1. Añade todos los ingredientes a la batidora.
2. Bate todo durante 1 minuto hasta obtener una mezcla homogénea.
3. Servir y disfrutar."""
)

pdf.add_recipe(
    "2. Bowl de Arroz, Pollo Teriyaki y Aguacate",
    """- 150g de pechuga de pollo en dados
- 80g de arroz (peso en crudo)
- Medio aguacate
- Un puñado de edamame o brócoli al vapor
- Salsa Teriyaki: 2 cucharadas de soja, 1 de miel, jengibre.""",
    """1. Cocina el arroz.
2. Saltea el pollo en una sartén. Cuando esté dorado, añade la salsa y remueve 1-2 min.
3. Monta el bowl: base de arroz, pollo, aguacate en láminas y el brócoli."""
)

pdf.add_recipe(
    "3. Salmón al Horno con Boniato Asado",
    """- 1 lomo de salmón (150-200g)
- 1 boniato mediano
- 1 ramillete de brócoli
- Aceite de oliva, sal, pimienta y eneldo.""",
    """1. Precalienta el horno a 200°C.
2. Corta el boniato y hornéalo con aceite y sal durante 20 minutos.
3. Añade el brócoli y el salmón aliñado a la bandeja.
4. Hornea todo junto durante 12-15 minutos más."""
)


# Guardar el PDF
pdf.output('C:\Users\PC1\Carpeta DIGI storage\MIS COSAS\plan_nutricional.pdf')

print("¡PDF 'plan_nutricional.pdf' generado con éxito!")