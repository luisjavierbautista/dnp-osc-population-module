"""Visualization Agent for creating data visualizations."""
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic import BaseModel
from typing import Dict, List, Any, Optional, Literal
from app.services.llm_provider import LLMProvider
from app.core.config import settings
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json


class VisualizationRequest(BaseModel):
    """Visualization request schema."""
    data: List[Dict[str, Any]]
    query_context: str
    visualization_types: List[Literal["table", "chart", "text"]]


class VisualizationResponse(BaseModel):
    """Visualization response schema."""
    visualizations: List[Dict[str, Any]]
    summary: str


class VisualizationAgent:
    """Agent for creating data visualizations for population data."""

    def __init__(self, model_name: str = "openai:gpt-4", provider: Optional[LLMProvider] = None):
        """
        Initialize the Visualization Agent.

        Args:
            model_name: Model identifier for pydantic-ai
            provider: LLM provider to use (Claude or Azure OpenAI)
        """
        self.provider = provider

        system_prompt_text = """You are an expert data visualization specialist for the DNP Population Module.
            Your task is to analyze query results and determine the best way to visualize population and demographic data.
            Consider:
            - Tables for detailed data inspection
            - Charts (bar, line, scatter, pie, population pyramids) for numerical comparisons and trends
            - Text summaries for insights and key findings

            Always provide clear, informative visualizations that help understand population dynamics and demographic patterns.
            Focus on Colombian population data and demographic trends.
            """

        # For Azure OpenAI, use OpenAIChatModel with provider='azure'
        if provider == LLMProvider.AZURE_OPENAI:
            # Set required environment variables for Azure
            import os
            os.environ["OPENAI_API_VERSION"] = settings.AZURE_OPENAI_API_VERSION
            os.environ["AZURE_OPENAI_ENDPOINT"] = settings.AZURE_OPENAI_ENDPOINT
            os.environ["AZURE_OPENAI_API_KEY"] = settings.AZURE_OPENAI_API_KEY

            # Create Azure OpenAI model
            azure_model = OpenAIChatModel(
                model_name=settings.AZURE_OPENAI_DEPLOYMENT,
                provider='azure'
            )

            # Create agent with Azure model
            self.agent = Agent(
                azure_model,
                system_prompt=system_prompt_text
            )
        else:
            # Default Claude or standard OpenAI
            self.agent = Agent(
                model_name,
                system_prompt=system_prompt_text
            )

    async def create_visualizations(self, data: List[Dict[str, Any]], query_context: str) -> VisualizationResponse:
        """Create appropriate visualizations based on the data and context."""
        if not data:
            return VisualizationResponse(
                visualizations=[{
                    "type": "text",
                    "content": "No se encontraron datos para la consulta proporcionada."
                }],
                summary="No se obtuvieron resultados de la base de datos."
            )

        df = pd.DataFrame(data)
        visualizations = []

        # Determine visualization types based on data
        viz_types = await self._determine_visualization_types(df, query_context)

        for viz_type in viz_types:
            if viz_type == "table":
                viz = self._create_table(df)
            elif viz_type == "chart":
                viz = await self._create_chart(df, query_context)
            elif viz_type == "text":
                viz = await self._create_text_summary(df, query_context)

            if viz:
                visualizations.append(viz)

        summary = await self._generate_summary(df, query_context)

        return VisualizationResponse(
            visualizations=visualizations,
            summary=summary
        )

    async def _determine_visualization_types(self, df: pd.DataFrame, context: str) -> List[str]:
        """Determine appropriate visualization types based on data characteristics."""
        viz_types = []

        # Always include table for raw data
        viz_types.append("table")

        # Check for numerical data suitable for charts
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_columns:
            viz_types.append("chart")

        # Always provide a text summary
        viz_types.append("text")

        return viz_types

    def _create_table(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create a table visualization."""
        # Limit table to first 100 rows for performance
        display_df = df.head(100)

        return {
            "type": "table",
            "data": display_df.to_dict('records'),
            "columns": list(display_df.columns),
            "title": "Resultados de la Consulta",
            "total_rows": len(df)
        }

    async def _create_chart(self, df: pd.DataFrame, context: str) -> Optional[Dict[str, Any]]:
        """Create appropriate chart based on data."""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        if not numeric_cols:
            return None

        # Detect population pyramid pattern (edad + sexo columns)
        if self._is_population_pyramid(df):
            return self._create_population_pyramid(df)

        # Prioritize specific value columns
        priority_keywords = ['poblacion', 'pob_total', 'pob_hombres', 'pob_mujeres', 'total', 'count', 'sum', 'avg']
        y_col = None

        for keyword in priority_keywords:
            matching = [col for col in numeric_cols if keyword in col.lower()]
            if matching:
                y_col = matching[0]
                break

        # Fallback to first numeric column
        if not y_col:
            y_col = numeric_cols[0]

        # Determine chart type based on data
        if 'anio' in [col.lower() for col in df.columns] or 'año' in [col.lower() for col in df.columns]:
            # Time series chart
            year_col = next((col for col in df.columns if col.lower() in ['anio', 'año']), None)
            if year_col and len(df) > 1:
                fig = px.line(df, x=year_col, y=y_col, title=f"Evolución de {y_col}")
                chart_type = "line"
        elif len(categorical_cols) > 0 and len(df) <= 50:
            # Bar chart for categorical data
            x_col = categorical_cols[0]
            fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} por {x_col}")
            chart_type = "bar"
        else:
            # Default to bar chart
            if len(df) > 20:
                df = df.head(20)  # Limit for readability
            fig = px.bar(df, x=df.columns[0], y=y_col, title=f"Distribución de {y_col}")
            chart_type = "bar"

        return {
            "type": "chart",
            "chart_type": chart_type,
            "data": json.loads(fig.to_json()),
            "title": fig.layout.title.text
        }

    def _is_population_pyramid(self, df: pd.DataFrame) -> bool:
        """Check if data is suitable for a population pyramid."""
        required_cols = {'edad', 'sexo', 'poblacion'}
        df_cols_lower = {col.lower() for col in df.columns}

        # Check if we have the required columns
        if not required_cols.issubset(df_cols_lower):
            return False

        # Check if we have H and M in sexo
        sexo_col = next((col for col in df.columns if col.lower() == 'sexo'), None)
        if sexo_col:
            sexo_values = set(df[sexo_col].unique())
            return 'H' in sexo_values and 'M' in sexo_values

        return False

    def _create_population_pyramid(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create a population pyramid visualization."""
        # Get column names (case-insensitive)
        edad_col = next((col for col in df.columns if col.lower() == 'edad'), 'edad')
        sexo_col = next((col for col in df.columns if col.lower() == 'sexo'), 'sexo')
        pob_col = next((col for col in df.columns if col.lower() == 'poblacion'), 'poblacion')

        # Separate male and female data
        male_data = df[df[sexo_col] == 'H'].copy()
        female_data = df[df[sexo_col] == 'M'].copy()

        # Sort by age
        male_data = male_data.sort_values(edad_col)
        female_data = female_data.sort_values(edad_col)

        # Create pyramid (male values negative for left side)
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=male_data[edad_col],
            x=-male_data[pob_col],  # Negative for left side
            name='Hombres',
            orientation='h',
            marker=dict(color='#3b82f6')
        ))

        fig.add_trace(go.Bar(
            y=female_data[edad_col],
            x=female_data[pob_col],
            name='Mujeres',
            orientation='h',
            marker=dict(color='#ec4899')
        ))

        fig.update_layout(
            title='Pirámide Poblacional',
            barmode='overlay',
            bargap=0.1,
            xaxis=dict(
                title='Población',
                tickformat=',d'
            ),
            yaxis=dict(title='Edad'),
            legend=dict(x=0.1, y=1.1, orientation='h')
        )

        return {
            "type": "chart",
            "chart_type": "pyramid",
            "data": json.loads(fig.to_json()),
            "title": "Pirámide Poblacional"
        }

    async def _create_text_summary(self, df: pd.DataFrame, context: str) -> Dict[str, Any]:
        """Generate a text summary of the data."""
        prompt = f"""
        Analiza estos datos en el contexto de: {context}

        Forma de los datos: {df.shape[0]} filas, {df.shape[1]} columnas
        Columnas: {list(df.columns)}

        Primeras 5 filas:
        {df.head().to_string()}

        Proporciona 3-5 puntos concisos con hallazgos clave sobre la demografía y población basados en estos datos.

        IMPORTANTE:
        - NO incluyas código Python ni sugerencias de código
        - NO sugieras visualizaciones (ya están creadas)
        - Enfócate SOLO en insights y patrones de los datos
        - Mantén cada punto en 1-2 oraciones
        - Usa español para los insights
        - Formatea como bullet points en markdown
        - Si hay datos de población, menciona cifras relevantes
        - Si hay tendencias temporales, descríbelas
        - Si hay comparaciones territoriales, resáltalas
        """

        result = await self.agent.run(prompt)

        return {
            "type": "text",
            "content": result.output if hasattr(result, 'output') else str(result),
            "title": "Análisis de Datos"
        }

    async def _generate_summary(self, df: pd.DataFrame, context: str) -> str:
        """Generate overall summary of the visualization."""
        stats = {
            "rows": len(df),
            "columns": len(df.columns),
            "numeric_columns": len(df.select_dtypes(include=['number']).columns)
        }

        return f"Se generaron {stats['rows']} resultados con {stats['columns']} columnas. Análisis completado para: {context}"
