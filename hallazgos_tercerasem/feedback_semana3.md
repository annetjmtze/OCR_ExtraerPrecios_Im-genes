# Feedback Semana 3 – Usuarios reales

## Fecha
17 de julio de 2026

## Objetivo
Evaluar las mejoras implementadas en la Semana 3: integración de precios de delivery (Rappi y Uber Eats), respuesta inmediata y formato unificado.

---

## Usuario 1

### Medicamento consultado: Ibuprofeno

### Resultado
El bot mostró opciones de delivery (Rappi) y precios actualizados. Sin embargo, los enlaces no funcionaban correctamente (https://www.rappi.com.mxadd-product-icon), lo que generó confusión. También apareció un precio de $513.63 claramente erróneo (producto Buscapina, no ibuprofeno).

### Observaciones
- **Mejora respecto a la semana pasada**: Ahora se muestran opciones de compra inmediata (delivery).
- **Confuso**: Los enlaces rotos y los precios incorrectos hacen que el usuario desconfíe.
- **No pudo responder**: El usuario preguntó "¿ese precio de $513 es de ibuprofeno?" y el bot no pudo aclarar el error.

---

## Usuario 2 

### Medicamento consultado: Paracetamol

### Resultado
El bot mostró farmacias físicas y delivery (Rappi y Uber Eats) con precios variados. La respuesta fue rápida y bien formateada. Sin embargo, aparecieron duplicados (OXXO, Farmacias Guadalajara varias veces).

### Observaciones
- **Mejora**: La separación entre físicas y delivery es muy útil.
- **Confuso**: Los duplicados hacen que el usuario piense que son farmacias diferentes.
- **No pudo responder**: Preguntó "¿cuánto tarda en llegar el pedido por Rappi?" y el bot no dio un tiempo específico (aunque aparece "25-35 min", el usuario no lo interpretó).

---

## Usuario 3 

### Medicamento: Ácido clavulánico y Amoxicilina

### Resultado
El bot no encontró precios, pero mostró la ficha del medicamento con nombre genérico, uso y si requiere receta. El usuario valoró la información, pero quería saber dónde comprarlo.

### Observaciones
- **Mejora**: La ficha informativa es útil y evita respuestas vacías.
- **Confuso**: El mensaje "Aún no tenemos precios" no indica si es temporal o definitivo.
- **No pudo responder**: Preguntó "¿puedo comprarlo sin receta?" (el bot ya dice que sí requiere receta, pero el usuario no lo leyó bien).

---

## Usuario 4 
### Medicamento: Aspirina

### Resultado
No encontró precios, mostró la ficha. El usuario preguntó si había genéricos más baratos, pero el bot no pudo responder porque no distingue entre marcas y genéricos en la búsqueda.

### Observaciones
- **Mejora**: La ficha de Aspirina fue clara.
- **Confuso**: El usuario no entendió por qué no había precios si "Aspirina es muy común".
- **No pudo responder**: "¿Hay genérico más barato?" – el bot no maneja esa consulta.

---

## Resumen de mejoras vs semana pasada

| Aspecto | Semana pasada | Semana 3 |
|---------|---------------|----------|
| Precios de delivery | No disponibles | Sí, con enlaces (aunque algunos rotos) |
| Tiempo de respuesta | A veces silencios | Menos de 5 segundos siempre |
| Normalización de nombres | Buena | Excelente (reconoce comerciales y genéricos) |
| Formato | Sencillo | Muy claro (físicas vs delivery) |
| Precios duplicados | Ocasionales | Frecuentes |
| Enlaces funcionales | No aplicaba | Algunos rotos |

---

## Conclusiones

**Lo que mejoró**
- El bot ahora ofrece opciones de compra inmediata (delivery) junto a farmacias físicas.
- La respuesta es siempre rápida, incluso sin precios.
- El formato es más claro y visual.

**Lo que sigue siendo confuso**
- Enlaces rotos y precios incorrectos dañan la confianza.
- Duplicados en la lista de precios.
- No se distingue entre marcas y genéricos en la búsqueda.

**Lo que no pudo responder**
- Dosis y presentación (mg, tabletas vs cápsulas).
- Precios en otras ciudades.
- Comparación de precios entre marcas y genéricos.
- Tiempo exacto de entrega por delivery.

---

## Próximos pasos sugeridos

1. Corregir extracción de enlaces en Rappi/Uber Eats para que sean funcionales.
2. Deduplicar resultados en la consulta de la base de datos.
3. Validar precios extremos antes de mostrarlos.
4. Agregar campo "presentación" (tabletas, mg, etc.) en la base de datos.
5. Implementar geolocalización para mostrar farmacias cercanas.