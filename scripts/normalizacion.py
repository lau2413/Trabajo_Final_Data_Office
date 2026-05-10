"""
Módulo de normalización de datos.

Proporciona múltiples métodos de normalización con:
- Normalización Min-Max
- Estandarización Z-Score
- Normalización Robusta (resistente a outliers)
- Normalización Decimal
- Parámetros guardados para reversión
- Validaciones de entrada
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Literal, Tuple
from datetime import datetime
import json
import pickle
from pathlib import Path


class NormalizadorDatos:
    """
    Clase para normalizar datos con múltiples métodos y capacidad de reversión.
    """
    
    def __init__(self, log_level: str = "INFO"):
        """
        Inicializa el normalizador de datos.
        
        Args:
            log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        """
        self.parametros = {}
        self.historial = []
        self._configurar_logging(log_level)
        
    def _configurar_logging(self, log_level: str):
        """Configura el sistema de logging."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _validar_datos_numericos(self, df: pd.DataFrame, columnas: List[str]) -> None:
        """
        Valida que las columnas sean numéricas.
        
        Args:
            df: DataFrame a validar
            columnas: Lista de columnas a verificar
            
        Raises:
            ValueError: Si alguna columna no es numérica
        """
        columnas_no_numericas = []
        for col in columnas:
            if col not in df.columns:
                raise ValueError(f"Columna '{col}' no existe en el DataFrame")
            if not pd.api.types.is_numeric_dtype(df[col]):
                columnas_no_numericas.append(col)
        
        if columnas_no_numericas:
            raise ValueError(f"Las siguientes columnas no son numéricas: {columnas_no_numericas}")
            
    def _registrar_operacion(self, metodo: str, columnas: List[str], parametros: Dict):
        """Registra una operación de normalización en el historial."""
        self.historial.append({
            "metodo": metodo,
            "columnas": columnas,
            "parametros": parametros,
            "timestamp": datetime.now().isoformat()
        })
        
    def normalizar_minmax(
        self, 
        df: pd.DataFrame, 
        columnas: Optional[List[str]] = None,
        rango: Tuple[float, float] = (0, 1),
        guardar_parametros: bool = True
    ) -> pd.DataFrame:
        """
        Normalización Min-Max: escala los valores a un rango específico.
        
        Fórmula: X_norm = (X - X_min) / (X_max - X_min) * (max - min) + min
        
        Args:
            df: DataFrame a normalizar
            columnas: Columnas a normalizar (None = todas las numéricas)
            rango: Tupla (min, max) del rango deseado
            guardar_parametros: Si True, guarda parámetros para reversión
            
        Returns:
            DataFrame normalizado
        """
        df = df.copy()
        
        if columnas is None:
            columnas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        self._validar_datos_numericos(df, columnas)
        
        min_deseado, max_deseado = rango
        
        if min_deseado >= max_deseado:
            raise ValueError(f"El rango debe ser (min, max) con min < max. Recibido: {rango}")
        
        parametros_cols = {}
        
        for col in columnas:
            col_min = df[col].min()
            col_max = df[col].max()
            
            # Evitar división por cero
            if col_max == col_min:
                self.logger.warning(f"Columna '{col}' tiene valores constantes, no se normalizará")
                continue
            
            # Aplicar normalización
            df[col] = ((df[col] - col_min) / (col_max - col_min)) * (max_deseado - min_deseado) + min_deseado
            
            # Guardar parámetros para reversión
            if guardar_parametros:
                parametros_cols[col] = {
                    "min_original": float(col_min),
                    "max_original": float(col_max),
                    "min_deseado": float(min_deseado),
                    "max_deseado": float(max_deseado)
                }
            
            self.logger.info(f"Columna '{col}': normalizada MinMax a rango {rango}")
        
        if guardar_parametros:
            self.parametros["minmax"] = parametros_cols
            self._registrar_operacion("minmax", columnas, {"rango": rango})
        
        return df
        
    def desnormalizar_minmax(self, df: pd.DataFrame, columnas: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Revierte la normalización Min-Max usando parámetros guardados.
        
        Args:
            df: DataFrame normalizado
            columnas: Columnas a desnormalizar (None = todas las guardadas)
            
        Returns:
            DataFrame con valores originales
        """
        if "minmax" not in self.parametros:
            raise ValueError("No hay parámetros de normalización MinMax guardados")
        
        df = df.copy()
        parametros_minmax = self.parametros["minmax"]
        
        if columnas is None:
            columnas = list(parametros_minmax.keys())
        
        for col in columnas:
            if col not in parametros_minmax:
                self.logger.warning(f"No hay parámetros guardados para columna '{col}'")
                continue
            
            params = parametros_minmax[col]
            min_orig = params["min_original"]
            max_orig = params["max_original"]
            min_des = params["min_deseado"]
            max_des = params["max_deseado"]
            
            # Revertir normalización
            df[col] = ((df[col] - min_des) / (max_des - min_des)) * (max_orig - min_orig) + min_orig
            
            self.logger.info(f"Columna '{col}': desnormalizada MinMax")
        
        return df
        
    def estandarizar_zscore(
        self, 
        df: pd.DataFrame, 
        columnas: Optional[List[str]] = None,
        guardar_parametros: bool = True
    ) -> pd.DataFrame:
        """
        Estandarización Z-Score: centra los datos con media 0 y desviación estándar 1.
        
        Formula: Z = (X - μ) / σ
        
        Args:
            df: DataFrame a estandarizar
            columnas: Columnas a estandarizar (None = todas las numéricas)
            guardar_parametros: Si True, guarda parámetros para reversión
            
        Returns:
            DataFrame estandarizado
        """
        df = df.copy()
        
        if columnas is None:
            columnas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        self._validar_datos_numericos(df, columnas)
        
        parametros_cols = {}
        
        for col in columnas:
            media = df[col].mean()
            desv_std = df[col].std()
            
            # Evitar división por cero
            if desv_std == 0:
                self.logger.warning(f"Columna '{col}' tiene desviación estándar 0, no se estandarizará")
                continue
            
            # Aplicar estandarización
            df[col] = (df[col] - media) / desv_std
            
            # Guardar parámetros
            if guardar_parametros:
                parametros_cols[col] = {
                    "media": float(media),
                    "desv_std": float(desv_std)
                }
            
            self.logger.info(f"Columna '{col}': estandarizada Z-Score (μ={media:.2f}, σ={desv_std:.2f})")
        
        if guardar_parametros:
            self.parametros["zscore"] = parametros_cols
            self._registrar_operacion("zscore", columnas, {})
        
        return df
        
    def desestendar_zscore(self, df: pd.DataFrame, columnas: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Revierte la estandarización Z-Score usando parámetros guardados.
        
        Args:
            df: DataFrame estandarizado
            columnas: Columnas a revertir (None = todas las guardadas)
            
        Returns:
            DataFrame con valores originales
        """
        if "zscore" not in self.parametros:
            raise ValueError("No hay parámetros de estandarización Z-Score guardados")
        
        df = df.copy()
        parametros_zscore = self.parametros["zscore"]
        
        if columnas is None:
            columnas = list(parametros_zscore.keys())
        
        for col in columnas:
            if col not in parametros_zscore:
                self.logger.warning(f"No hay parámetros guardados para columna '{col}'")
                continue
            
            params = parametros_zscore[col]
            media = params["media"]
            desv_std = params["desv_std"]
            
            # Revertir estandarización
            df[col] = df[col] * desv_std + media
            
            self.logger.info(f"Columna '{col}': revertida estandarización Z-Score")
        
        return df
        
    def normalizar_robusta(
        self, 
        df: pd.DataFrame, 
        columnas: Optional[List[str]] = None,
        guardar_parametros: bool = True
    ) -> pd.DataFrame:
        """
        Normalización Robusta: usa mediana y rango intercuartílico (resistente a outliers).
        
        Fórmula: X_norm = (X - mediana) / IQR
        
        Args:
            df: DataFrame a normalizar
            columnas: Columnas a normalizar (None = todas las numéricas)
            guardar_parametros: Si True, guarda parámetros para reversión
            
        Returns:
            DataFrame normalizado
        """
        df = df.copy()
        
        if columnas is None:
            columnas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        self._validar_datos_numericos(df, columnas)
        
        parametros_cols = {}
        
        for col in columnas:
            mediana = df[col].median()
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            # Evitar división por cero
            if IQR == 0:
                self.logger.warning(f"Columna '{col}' tiene IQR = 0, no se normalizará")
                continue
            
            # Aplicar normalización robusta
            df[col] = (df[col] - mediana) / IQR
            
            # Guardar parámetros
            if guardar_parametros:
                parametros_cols[col] = {
                    "mediana": float(mediana),
                    "Q1": float(Q1),
                    "Q3": float(Q3),
                    "IQR": float(IQR)
                }
            
            self.logger.info(f"Columna '{col}': normalizada Robusta (mediana={mediana:.2f}, IQR={IQR:.2f})")
        
        if guardar_parametros:
            self.parametros["robusta"] = parametros_cols
            self._registrar_operacion("robusta", columnas, {})
        
        return df
        
    def desnormalizar_robusta(self, df: pd.DataFrame, columnas: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Revierte la normalización Robusta usando parámetros guardados.
        
        Args:
            df: DataFrame normalizado
            columnas: Columnas a revertir (None = todas las guardadas)
            
        Returns:
            DataFrame con valores originales
        """
        if "robusta" not in self.parametros:
            raise ValueError("No hay parámetros de normalización Robusta guardados")
        
        df = df.copy()
        parametros_robusta = self.parametros["robusta"]
        
        if columnas is None:
            columnas = list(parametros_robusta.keys())
        
        for col in columnas:
            if col not in parametros_robusta:
                self.logger.warning(f"No hay parámetros guardados para columna '{col}'")
                continue
            
            params = parametros_robusta[col]
            mediana = params["mediana"]
            IQR = params["IQR"]
            
            # Revertir normalización
            df[col] = df[col] * IQR + mediana
            
            self.logger.info(f"Columna '{col}': revertida normalización Robusta")
        
        return df
        
    def normalizar_decimal(
        self, 
        df: pd.DataFrame, 
        columnas: Optional[List[str]] = None,
        guardar_parametros: bool = True
    ) -> pd.DataFrame:
        """
        Normalización Decimal: divide por potencia de 10 para que valores estén en [-1, 1].
        
        Fórmula: X_norm = X / 10^d, donde d es el número de dígitos del valor máximo
        
        Args:
            df: DataFrame a normalizar
            columnas: Columnas a normalizar (None = todas las numéricas)
            guardar_parametros: Si True, guarda parámetros para reversión
            
        Returns:
            DataFrame normalizado
        """
        df = df.copy()
        
        if columnas is None:
            columnas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        self._validar_datos_numericos(df, columnas)
        
        parametros_cols = {}
        
        for col in columnas:
            max_abs = df[col].abs().max()
            
            if max_abs == 0:
                self.logger.warning(f"Columna '{col}' tiene solo ceros, no se normalizará")
                continue
            
            # Calcular potencia de 10
            d = int(np.ceil(np.log10(max_abs + 1)))
            divisor = 10 ** d
            
            # Aplicar normalización
            df[col] = df[col] / divisor
            
            # Guardar parámetros
            if guardar_parametros:
                parametros_cols[col] = {
                    "divisor": float(divisor),
                    "d": int(d)
                }
            
            self.logger.info(f"Columna '{col}': normalizada Decimal (divisor=10^{d})")
        
        if guardar_parametros:
            self.parametros["decimal"] = parametros_cols
            self._registrar_operacion("decimal", columnas, {})
        
        return df
        
    def desnormalizar_decimal(self, df: pd.DataFrame, columnas: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Revierte la normalización Decimal usando parámetros guardados.
        
        Args:
            df: DataFrame normalizado
            columnas: Columnas a revertir (None = todas las guardadas)
            
        Returns:
            DataFrame con valores originales
        """
        if "decimal" not in self.parametros:
            raise ValueError("No hay parámetros de normalización Decimal guardados")
        
        df = df.copy()
        parametros_decimal = self.parametros["decimal"]
        
        if columnas is None:
            columnas = list(parametros_decimal.keys())
        
        for col in columnas:
            if col not in parametros_decimal:
                self.logger.warning(f"No hay parámetros guardados para columna '{col}'")
                continue
            
            params = parametros_decimal[col]
            divisor = params["divisor"]
            
            # Revertir normalización
            df[col] = df[col] * divisor
            
            self.logger.info(f"Columna '{col}': revertida normalización Decimal")
        
        return df
        
    def guardar_parametros(self, ruta: str):
        """
        Guarda los parámetros de normalización en un archivo.
        
        Args:
            ruta: Ruta del archivo donde guardar (JSON o pickle)
        """
        ruta_path = Path(ruta)
        
        if ruta_path.suffix == '.json':
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(self.parametros, f, indent=2, ensure_ascii=False)
        elif ruta_path.suffix in ['.pkl', '.pickle']:
            with open(ruta, 'wb') as f:
                pickle.dump(self.parametros, f)
        else:
            raise ValueError("El archivo debe tener extensión .json, .pkl o .pickle")
        
        self.logger.info(f"Parámetros guardados en: {ruta}")
        
    def cargar_parametros(self, ruta: str):
        """
        Carga parámetros de normalización desde un archivo.
        
        Args:
            ruta: Ruta del archivo de parámetros
        """
        ruta_path = Path(ruta)
        
        if ruta_path.suffix == '.json':
            with open(ruta, 'r', encoding='utf-8') as f:
                self.parametros = json.load(f)
        elif ruta_path.suffix in ['.pkl', '.pickle']:
            with open(ruta, 'rb') as f:
                self.parametros = pickle.load(f)
        else:
            raise ValueError("El archivo debe tener extensión .json, .pkl o .pickle")
        
        self.logger.info(f"Parámetros cargados desde: {ruta}")
        
    def generar_reporte(self) -> Dict:
        """
        Genera un reporte de las operaciones de normalización.
        
        Returns:
            Diccionario con el reporte
        """
        return {
            "total_operaciones": len(self.historial),
            "metodos_utilizados": list(set([op["metodo"] for op in self.historial])),
            "historial": self.historial,
            "parametros_disponibles": list(self.parametros.keys()),
            "generado_en": datetime.now().isoformat()
        }
        
    def guardar_reporte(self, ruta: str):
        """Guarda el reporte en un archivo JSON."""
        reporte = self.generar_reporte()
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Reporte guardado en: {ruta}")