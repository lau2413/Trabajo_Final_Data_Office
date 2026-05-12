"""
Módulo de limpieza de datos.

Proporciona funcionalidades avanzadas para:
- Manejo configurable de valores nulos
- Detección y tratamiento de outliers
- Validación de tipos de datos
- Logging detallado de operaciones
- Backup automático de datos
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Literal
from datetime import datetime
import json
from pathlib import Path


class LimpiadorDatos:
    """
    Clase para realizar limpieza avanzada de datos con logging y validaciones.
    """
    
    def __init__(self, log_level: str = "INFO", backup_dir: Optional[str] = None):
        """
        Inicializa el limpiador de datos.
        
        Args:
            log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
            backup_dir: Directorio para guardar backups (opcional)
        """
        self.backup_dir = Path(backup_dir) if backup_dir else None
        self.operaciones_log = []
        self._configurar_logging(log_level)
        
    def _configurar_logging(self, log_level: str):
        """Configura el sistema de logging."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def crear_backup(self, df: pd.DataFrame, nombre: str = "backup") -> Optional[str]:
        """
        Crea un backup del DataFrame antes de modificarlo.
        
        Args:
            df: DataFrame a respaldar
            nombre: Nombre base para el archivo de backup
            
        Returns:
            Ruta del archivo de backup o None si no hay directorio configurado
        """
        if self.backup_dir is None:
            return None
            
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{nombre}_{timestamp}.csv"
        
        df.to_csv(backup_path, index=False)
        self.logger.info(f"Backup creado en: {backup_path}")
        return str(backup_path)
        
    def validar_esquema(self, df: pd.DataFrame, esquema_esperado: Dict[str, type]) -> bool:
        """
        Valida que el DataFrame tenga las columnas y tipos esperados.
        
        Args:
            df: DataFrame a validar
            esquema_esperado: Dict con {columna: tipo_esperado}
            
        Returns:
            True si el esquema es válido
            
        Raises:
            ValueError: Si el esquema no es válido
        """
        errores = []
        
        # Verificar columnas faltantes
        columnas_faltantes = set(esquema_esperado.keys()) - set(df.columns)
        if columnas_faltantes:
            errores.append(f"Columnas faltantes: {columnas_faltantes}")
            
        # Verificar tipos de datos
        for col, tipo_esperado in esquema_esperado.items():
            if col in df.columns:
                tipo_actual = df[col].dtype
                # Convertir tipos de numpy a tipos de Python para comparación
                if not self._tipos_compatibles(tipo_actual, tipo_esperado):
                    errores.append(f"Columna '{col}': tipo {tipo_actual} no compatible con {tipo_esperado}")
        
        if errores:
            mensaje_error = "Errores de validación de esquema:\n" + "\n".join(errores)
            self.logger.error(mensaje_error)
            raise ValueError(mensaje_error)
            
        self.logger.info("Validación de esquema exitosa")
        return True
        
    def _tipos_compatibles(self, tipo_actual, tipo_esperado) -> bool:
        """Verifica si dos tipos son compatibles."""
        # Mapeo de tipos numpy a tipos Python
        mapeo = {
            np.int64: int,
            np.int32: int,
            np.float64: float,
            np.float32: float,
            np.object_: str,
            'object': str,
        }
        
        tipo_actual_normalizado = mapeo.get(tipo_actual, tipo_actual)
        return tipo_actual_normalizado == tipo_esperado or str(tipo_actual).startswith(tipo_esperado.__name__)
        
    def manejar_nulos(
        self, 
        df: pd.DataFrame, 
        estrategia: Literal["eliminar", "media", "mediana", "moda", "ffill", "bfill", "constante"] = "media",
        columnas: Optional[List[str]] = None,
        valor_constante: Optional[Union[int, float, str]] = None,
        umbral_eliminar: float = 0.5
    ) -> pd.DataFrame:
        """
        Maneja valores nulos según diferentes estrategias.
        
        Args:
            df: DataFrame a procesar
            estrategia: Estrategia para manejar nulos
            columnas: Lista de columnas a procesar (None = todas)
            valor_constante: Valor para usar si estrategia="constante"
            umbral_eliminar: Proporción de nulos para eliminar columna (solo con estrategia="eliminar")
            
        Returns:
            DataFrame con nulos manejados
        """
        df = df.copy()
        columnas = columnas or df.columns.tolist()
        
        # Registrar estado inicial
        nulos_inicial = df[columnas].isnull().sum()
        self.logger.info(f"Nulos iniciales:\n{nulos_inicial[nulos_inicial > 0]}")
        
        for col in columnas:
            if col not in df.columns:
                self.logger.warning(f"Columna '{col}' no encontrada")
                continue
                
            proporcion_nulos = df[col].isnull().sum() / len(df)
            
            if estrategia == "eliminar":
                if proporcion_nulos > umbral_eliminar:
                    df = df.drop(columns=[col])
                    self.logger.info(f"Columna '{col}' eliminada ({proporcion_nulos:.1%} nulos)")
                else:
                    df = df.dropna(subset=[col])
                    self.logger.info(f"Filas con nulos en '{col}' eliminadas")
                    
            elif estrategia == "media":
                if pd.api.types.is_numeric_dtype(df[col]):
                    valor = df[col].mean()
                    df[col] = df[col].fillna(valor)
                    self.logger.info(f"Columna '{col}': nulos rellenados con media ({valor:.2f})")
                else:
                    self.logger.warning(f"Columna '{col}' no es numérica, saltando media")
                    
            elif estrategia == "mediana":
                if pd.api.types.is_numeric_dtype(df[col]):
                    valor = df[col].median()
                    df[col] = df[col].fillna(valor)
                    self.logger.info(f"Columna '{col}': nulos rellenados con mediana ({valor:.2f})")
                else:
                    self.logger.warning(f"Columna '{col}' no es numérica, saltando mediana")
                    
            elif estrategia == "moda":
                moda = df[col].mode()
                if len(moda) > 0:
                    valor = moda[0]
                    df[col] = df[col].fillna(valor)
                    self.logger.info(f"Columna '{col}': nulos rellenados con moda ({valor})")
                    
            elif estrategia == "ffill":
                df[col] = df[col].ffill()
                self.logger.info(f"Columna '{col}': nulos rellenados con forward fill")
                
            elif estrategia == "bfill":
                df[col] = df[col].bfill()
                self.logger.info(f"Columna '{col}': nulos rellenados con backward fill")
                
            elif estrategia == "constante":
                if valor_constante is None:
                    raise ValueError("Debe proporcionar valor_constante para estrategia 'constante'")
                df[col] = df[col].fillna(valor_constante)
                self.logger.info(f"Columna '{col}': nulos rellenados con valor constante ({valor_constante})")
        
        # Registrar operación
        self.operaciones_log.append({
            "operacion": "manejar_nulos",
            "estrategia": estrategia,
            "columnas": columnas,
            "timestamp": datetime.now().isoformat()
        })
        
        return df
        
    def detectar_outliers(
        self, 
        df: pd.DataFrame, 
        columnas: Optional[List[str]] = None,
        metodo: Literal["iqr", "zscore"] = "iqr",
        umbral_zscore: float = 3.0,
        multiplicador_iqr: float = 1.5
    ) -> Dict[str, pd.Series]:
        """
        Detecta outliers en columnas numéricas.
        
        Args:
            df: DataFrame a analizar
            columnas: Columnas a analizar (None = todas las numéricas)
            metodo: Método de detección ("iqr" o "zscore")
            umbral_zscore: Umbral para método z-score
            multiplicador_iqr: Multiplicador para método IQR
            
        Returns:
            Diccionario con Series booleanas indicando outliers por columna
        """
        if columnas is None:
            columnas = df.select_dtypes(include=[np.number]).columns.tolist()
        
        outliers = {}
        
        for col in columnas:
            if col not in df.columns:
                continue
                
            if not pd.api.types.is_numeric_dtype(df[col]):
                self.logger.warning(f"Columna '{col}' no es numérica, saltando detección de outliers")
                continue
            
            if metodo == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                limite_inferior = Q1 - multiplicador_iqr * IQR
                limite_superior = Q3 + multiplicador_iqr * IQR
                outliers[col] = (df[col] < limite_inferior) | (df[col] > limite_superior)
                
            elif metodo == "zscore":
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers[col] = z_scores > umbral_zscore
            
            num_outliers = outliers[col].sum()
            if num_outliers > 0:
                self.logger.info(f"Columna '{col}': {num_outliers} outliers detectados ({num_outliers/len(df):.1%})")
        
        return outliers
        
    def tratar_outliers(
        self, 
        df: pd.DataFrame,
        outliers: Dict[str, pd.Series],
        tratamiento: Literal["eliminar", "winsorizar", "clip", "nulo"] = "winsorizar",
        percentiles: tuple = (5, 95)
    ) -> pd.DataFrame:
        """
        Trata los outliers detectados.
        
        Args:
            df: DataFrame a procesar
            outliers: Diccionario con máscaras de outliers (resultado de detectar_outliers)
            tratamiento: Método de tratamiento
            percentiles: Percentiles para winsorización (solo si tratamiento="winsorizar")
            
        Returns:
            DataFrame con outliers tratados
        """
        df = df.copy()
        
        for col, mascara_outliers in outliers.items():
            num_outliers = mascara_outliers.sum()
            
            if num_outliers == 0:
                continue
            
            if tratamiento == "eliminar":
                df = df[~mascara_outliers]
                self.logger.info(f"Columna '{col}': {num_outliers} filas con outliers eliminadas")
                
            elif tratamiento == "winsorizar":
                limite_inferior = df[col].quantile(percentiles[0] / 100)
                limite_superior = df[col].quantile(percentiles[1] / 100)
                df.loc[mascara_outliers, col] = df.loc[mascara_outliers, col].clip(limite_inferior, limite_superior)
                self.logger.info(f"Columna '{col}': outliers winsorizados a percentiles {percentiles}")
                
            elif tratamiento == "clip":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                limite_inferior = Q1 - 1.5 * IQR
                limite_superior = Q3 + 1.5 * IQR
                df[col] = df[col].clip(limite_inferior, limite_superior)
                self.logger.info(f"Columna '{col}': outliers clipados a límites IQR")
                
            elif tratamiento == "nulo":
                df.loc[mascara_outliers, col] = np.nan
                self.logger.info(f"Columna '{col}': {num_outliers} outliers convertidos a nulos")
        
        # Registrar operación
        self.operaciones_log.append({
            "operacion": "tratar_outliers",
            "tratamiento": tratamiento,
            "columnas": list(outliers.keys()),
            "timestamp": datetime.now().isoformat()
        })
        
        return df
        
    def limpiar_duplicados(self, df: pd.DataFrame, subset: Optional[List[str]] = None, keep: str = "first") -> pd.DataFrame:
        """
        Elimina filas duplicadas.
        
        Args:
            df: DataFrame a procesar
            subset: Columnas a considerar para detectar duplicados
            keep: Qué duplicado mantener ('first', 'last', False para eliminar todos)
            
        Returns:
            DataFrame sin duplicados
        """
        df = df.copy()
        duplicados_antes = df.duplicated(subset=subset, keep=keep).sum()
        
        if duplicados_antes > 0:
            df = df.drop_duplicates(subset=subset, keep=keep)
            self.logger.info(f"{duplicados_antes} filas duplicadas eliminadas")
            
            self.operaciones_log.append({
                "operacion": "limpiar_duplicados",
                "duplicados_eliminados": int(duplicados_antes),
                "subset": subset,
                "timestamp": datetime.now().isoformat()
            })
        else:
            self.logger.info("No se encontraron duplicados")
        
        return df
        
    def estandarizar_texto(
        self, 
        df: pd.DataFrame, 
        columnas: Optional[List[str]] = None,
        minusculas: bool = True,
        quitar_espacios: bool = True,
        quitar_acentos: bool = False
    ) -> pd.DataFrame:
        """
        Estandariza columnas de texto.
        
        Args:
            df: DataFrame a procesar
            columnas: Columnas de texto a estandarizar
            minusculas: Convertir a minúsculas
            quitar_espacios: Eliminar espacios extras
            quitar_acentos: Eliminar acentos
            
        Returns:
            DataFrame con texto estandarizado
        """
        df = df.copy()
        
        if columnas is None:
            columnas = df.select_dtypes(include=['object']).columns.tolist()
        
        for col in columnas:
            if col not in df.columns:
                continue
                
            if minusculas:
                df[col] = df[col].str.lower()
                
            if quitar_espacios:
                df[col] = df[col].str.strip()
                df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
                
            if quitar_acentos:
                df[col] = df[col].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
            
            self.logger.info(f"Columna '{col}': texto estandarizado")
        
        return df
        
    def generar_reporte_limpieza(self) -> Dict:
        """
        Genera un reporte de todas las operaciones de limpieza realizadas.
        
        Returns:
            Diccionario con el reporte de operaciones
        """
        reporte = {
            "total_operaciones": len(self.operaciones_log),
            "operaciones": self.operaciones_log,
            "generado_en": datetime.now().isoformat()
        }
        
        return reporte
        
    def guardar_reporte(self, ruta: str):
        """Guarda el reporte de limpieza en un archivo JSON."""
        reporte = self.generar_reporte_limpieza()
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Reporte guardado en: {ruta}")
