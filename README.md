# 📊 Crypto EDA Dashboard — Proyecto Dash

## 🎯 Objetivo del Proyecto

Construir un dashboard interactivo en R/Shiny que realice un **Análisis Exploratorio de Datos (EDA)** completo sobre el mercado de criptomonedas, consumiendo datos en tiempo real desde la API de CryptoCompare. El dashboard permite a analistas e inversores explorar el comportamiento histórico de los precios, los patrones de retornos y las relaciones entre activos digitales de forma visual e interactiva.

---

## 🔍 Problema que Resuelve

El mercado de criptomonedas es altamente volátil y difícil de interpretar sin herramientas adecuadas. Los inversores y analistas necesitan:

1. **Visualizar tendencias** de precios con indicadores técnicos (medias móviles, Bandas de Bollinger).
2. **Cuantificar el riesgo** a través de métricas estadísticas (VaR, Sharpe, volatilidad).
3. **Entender las correlaciones** entre distintos activos para tomar decisiones de portafolio.
4. **Comparar el rendimiento** acumulado entre criptomonedas en el mismo horizonte temporal.
5. **Actualización constante cada 5 minutos de los datos.

---

## 🗂️ Estructura del Proyecto

```
employee_attrition/
├── .vscode #Activación del ambiente
├── assets  #Diseño de la página     
├── data    #Datos usados
├── app.py  #Inicialización de la app
├── requirements.txt  #Librerias usadas
└── pages/ #Contenido


```

---



---

## 🚀 Cómo Ejecutar

```python
# En Visual Studio Code, desde el directorio del proyecto:
Ejecutar app.py
```

---

## 🖥️ Pestañas del Dashboard

| Pestaña | Descripción |
|---|---|
| **Mercado** | Se da un resumen de lo que veremos en el análisis |
| **Histórico** | Muestra el panorama global del mercado de cryptos en tiempo real |
| **Eda** | Planteamos el problema a resolver |
| **Arima** | Metas y justificación del análisis |

---

## Como instalar
1. **Descargar el archivo**
2. Abrir Anaconda Powershell y entra hasta al archivo usando cd
3. Crea el ambiente dash_project en python 3.9 : conda create --name dash_project python=3.9
4. Ingresa hasta la carpeta y descarga los requirements: pip install -r requirements-copia.txt
5. Abre Visual Studio Code y ingresa el kernel creado
6. Ya puedes empezar a usar el proyecto






*Desarrollado como proyecto de EDA con Dash · API: CryptoCompare*
