"""
Módulo de validación de datos.

Proporciona un framework completo de validación con:
- Validaciones de tipos de datos
- Validaciones de rangos y dominios
- Validaciones de patrones (regex)
- Validaciones de integridad referencial
- Validaciones de unicidad
- Reportes detallados con estadísticas
- Reglas de validación configurables
"""

import pandas as pd
import numpy as np
import re
import logging
from typing import Dict, List, Optional, Callable, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json


class SeveridadError(Enum):
    """Niveles de severidad para errores de validación."""
    CRITICO = "CRITICO"
    ALTO = "ALTO"
    MEDIO = "MEDIO"
    BAJO = "BAJO"
    ADVERTENCIA = "ADVERTENCIA"


@dataclass
class ResultadoValidacion:
    """Resultado de una validación individual."""
    nombre_regla: str
    columna: str
    paso: bool
    errores_encontrados: int
    indices_error: List[int] = field(default_factory=list)
    severidad: SeveridadError = SeveridadError.MEDIO
    mensaje: str = ""
    detalles: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReglaValidacion:
    """Definición de una regla de validación."""
    nombre: str
    columna: str
    funcion_validacion: Callable
    severidad: SeveridadError = SeveridadError.MEDIO
    mensaje_error: str = ""
    parametros: Dict[str, Any] = field(default_factory=dict)


class ValidadorDatos:
    """
    Clase para validar datos con múltiples reglas y generar reportes detallados.
    """
    
    def __init__(self, log_level: str = "INFO"):
        """
        Inicializa el validador de datos.
        
        Args:
            log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        """
        self.reglas: List[ReglaValidacion] = []
        self.resultados: List[ResultadoValidacion] = []
        self._configurar_logging(log_level)
        
    def _configurar_logging(self, log_level: str):
        """Configura el sistema de logging."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def agregar_regla(self, regla: ReglaValidacion):
        """
        Agrega una regla de validación.
        
        Args:
            regla: Objeto ReglaValidacion a agregar
        """
        self.reglas.append(regla)
        self.logger.info(f"Regla agregada: {regla.nombre} para columna '{regla.columna}'")
        
    def validar_tipo_dato(
        self, 
        df: pd.DataFrame, 
        columna: str, 
        tipo_esperado: type,
        severidad: SeveridadError = SeveridadError.ALTO
    ) -> ResultadoValidacion:
        """
        Valida que una columna tenga el tipo de dato esperado.
        
        Args:
            df: DataFrame a validar
            columna: Nombre de la columna
            tipo_esperado: Tipo de dato esperado (int, float, str, etc.)
            severidad: Nivel de severidad del error
            
        Returns:
            ResultadoValidacion con el resultado
        """
        if columna not in df.columns:
            return ResultadoValidacion(
                nombre_regla="validar_tipo_dato",
                columna=columna,
                paso=False,
                errores_encontrados=1,
                severidad=SeveridadError.CRITICO,
                mensaje=f"Columna '{columna}' no existe en el DataFrame"
            )
        
        # Mapeo de tipos de Python a tipos de pandas/numpy
        mapeo_tipos = {
            int: ['int64', 'int32', 'int16', 'int8'],
            float: ['float64', 'float32', 'float16'],
            str: ['object', 'string'],
            bool: ['bool']
        }
        
        tipo_actual = str(df[columna].dtype)
        tipos_validos = mapeo_tipos.get(tipo_esperado, [tipo_esperado.__name__])
        
        paso = any(tipo_actual.startswith(tv) for tv in tipos_validos)
        
        return ResultadoValidacion(
            nombre_regla="validar_tipo_dato",
            columna=columna,
            paso=paso,
            errores_encontrados=0 if paso else 1,
            severidad=severidad,
            mensaje=f"Tipo esperado: {tipo_esperado.__name__}, tipo actual: {tipo_actual}",
            detalles={"tipo_esperado": tipo_esperado.__name__, "tipo_actual": tipo_actual}
        )
        
    def validar_no_nulos(
        self, 
        df: pd.DataFrame, 
        columna: str,
        severidad: SeveridadError = SeveridadError.ALTO
    ) -> ResultadoValidacion:
        """
        Valida que una columna no tenga valores nulos.
        
        Args:
            df: DataFrame a validar
            columna: Nombre de la columna
            severidad: Nivel de severidad del error
            
        Returns:
            ResultadoValidacion con el resultado
        """
        if columna not in df.columns:
            return ResultadoValidacion(
                nombre_regla="validar_no_nulos",
                columna=columna,
                paso=False,
                errores_encontrados=1,
                severidad=SeveridadError.CRITICO,
                mensaje=f"Columna '{columna}' no existe"
            )
        
        mascara_nulos = df[columna].isnull()
        num_nulos = mascara_nulos.sum()
        indices_nulos = df[mascara_nulos].index.tolist()
        
        return ResultadoValidacion(
            nombre_regla="validar_no_nulos",
            columna=columna,
            paso=num_nulos == 0,
            errores_encontrados=num_nulos,
            indices_error=indices_nulos,
            severidad=severidad,
            mensaje=f"Se encontraron {num_nulos} valores nulos ({num_nulos/len(df)*100:.2f}%)",
            detalles={"total_nulos": int(num_nulos), "porcentaje": float(num_nulos/len(df)*100)}
        )
        
    def validar_rango(
        self, 
        df: pd.DataFrame, 
        columna: str,
        minimo: Optional[float] = None,
        maximo: Optional[float] = None,
        severidad: SeveridadError = SeveridadError.MEDIO
    ) -> ResultadoValidacion:
        """
        Valida que los valores estén dentro de un rango.
        
        Args:
            df: DataFrame a validar
            columna: Nombre de la columna
            minimo: Valor mínimo permitido (None = sin límite inferior)
            maximo: Valor máximo permitido (None = sin límite superior)
            severidad: Nivel de severidad del error
            
        Returns:
            ResultadoValidacion con el resultado
        """
        if columna not in df.columns:
            return ResultadoValidacion(
                nombre_regla="validar_rango",
                columna=columna,
                paso=False,
                errores_encontrados=1,
                severidad=SeveridadError.CRITICO,
                mensaje=f"Columna '{columna}' no existe"
            )
        
        # Excluir nulos de la validación
        valores_no_nulos = df[columna].dropna()
        
        if len(valores_no_nulos) == 0:
            return ResultadoValidacion(
                nombre_regla="validar_rango",
                columna=columna,
                paso=True,
                errores_encontrados=0,
                severidad=SeveridadError.ADVERTENCIA,
                mensaje="Todos los valores son nulos, no se puede validar rango"
            )
        
        mascara_error = pd.Series([False] * len(df), index=df.index)
        
        if minimo is not None:
            mascara_error |= (df[columna] < minimo) & df[columna].notna()
        
        if maximo is not None:
            mascara_error |= (df[columna] > maximo) & df[columna].notna()
        
        num_errores = mascara_error.sum()
        indices_error = df[mascara_error].index.tolist()
        
        mensaje_rango = []
        if minimo is not None:
            mensaje_rango.append(f"mínimo: {minimo}")
        if maximo is not None:
            mensaje_rango.append(f"máximo: {maximo}")
        
        return ResultadoValidacion(
            nombre_regla="validar_rango",
            columna=columna,
            paso=num_errores == 0,
            errores_encontrados=num_errores,
            indices_error=indices_error,
            severidad=severidad,
            mensaje=f"{num_errores} valores fuera de rango ({', '.join(mensaje_rango)})",
            detalles={
                "minimo": minimo,
                "maximo": maximo,
                "valor_min_encontrado": float(valores_no_nulos.min()),
                "valor_max_encontrado": float(valores_no_nulos.max())
            }
        )
        
    def validar_patron(
        self, 
        df: pd.DataFrame, 
        columna: str,
        patron: str,
        severidad: SeveridadError = SeveridadError.MEDIO
    ) -> ResultadoValidacion:
        """
        Valida que los valores cumplan con un patrón regex.
        
        Args:
            df: DataFrame a validar
            columna: Nombre de la columna
            patron: Expresión regular a validar
            severidad: Nivel de severidad del error
            
        Returns:
            ResultadoValidacion con el resultado
        """
        if columna not in df.columns:
            return ResultadoValidacion(
                nombre_regla="validar_patron",
                columna=columna,
                paso=False,
                errores_encontrados=1,
                severidad=SeveridadError.CRITICO,
                mensaje=f"Columna '{columna}' no existe"
            )
        
        # Convertir a string y validar patrón
        valores_str = df[columna].astype(str)
        mascara_cumple = valores_str.str.match(patron, na=False)
        mascara_error = ~mascara_cumple & df[columna].notna()
        
        num_errores = mascara_error.sum()
        indices_error = df[mascara_error].index.tolist()
        
        return ResultadoValidacion(
            nombre_regla="validar_patron",
            columna=columna,
            paso=num_errores == 0,
            errores_encontrados=num_errores,
            indices_error=indices_error,
            severidad=severidad,
            mensaje=f"{num_errores} valores no cumplen el patrón '{patron}'",
            detalles={"patron": patron}
        )
        
    def validar_unicidad(
        self, 
        df: pd.DataFrame, 
        columna: str,
        severidad: SeveridadError = SeveridadError.ALTO
    ) -> ResultadoValidacion:
        """
        Valida que todos los valores sean únicos (sin duplicados).
        
        Args:
            df: DataFrame a validar
            columna: Nombre de la columna
            severidad: Nivel de severidad del error
            
        Returns:
            ResultadoValidacion con el resultado
        """
        if columna not in df.columns:
            return ResultadoValidacion(
                nombre_regla="validar_unicidad",
                columna=columna,
                paso=False,
                errores_encontrados=1,
                severidad=SeveridadError.CRITICO,
                mensaje=f"Columna '{columna}' no existe"
            )
        
        duplicados = df[columna].duplicated(keep=False)
        num_duplicados = duplicados.sum()
        indices_duplicados = df[duplicados].index.tolist()
        
        valores_duplicados = df[duplicados][columna].unique().tolist()
        
        return ResultadoValidacion(
            nombre_regla="validar_unicidad",
            columna=columna,
            paso=num_duplicados == 0,
            errores_encontrados=num_duplicados,
            indices_error=indices_duplicados,
            severidad=severidad,
            mensaje=f"Se encontraron {num_duplicados} valores duplicados",
            detalles={
                "total_duplicados": int(num_duplicados),
                "valores_duplicados": [str(v) for v in valores_duplicados[:10]]  # Primeros 10
            }
        )
        
    def validar_dominio(
        self, 
        df: pd.DataFrame, 
        columna: str,
        valores_validos: List[Any],
        severidad: SeveridadError = SeveridadError.MEDIO
    ) -> ResultadoValidacion:
        """
        Valida que los valores pertenezcan a un dominio específico.
        
        Args:
            df: DataFrame a validar
            columna: Nombre de la columna
            valores_validos: Lista de valores permitidos
            severidad: Nivel de severidad del error
            
        Returns:
            ResultadoValidacion con el resultado
        """
        if columna not in df.columns:
            return ResultadoValidacion(
                nombre_regla="validar_dominio",
                columna=columna,
                paso=False,
                errores_encontrados=1,
                severidad=SeveridadError.CRITICO,
                mensaje=f"Columna '{columna}' no existe"
            )
        
        mascara_valido = df[columna].isin(valores_validos) | df[columna].isnull()
        mascara_error = ~mascara_valido
        
        num_errores = mascara_error.sum()
        indices_error = df[mascara_error].index.tolist()
        
        valores_invalidos = df[mascara_error][columna].unique().tolist()
        
        return ResultadoValidacion(
            nombre_regla="validar_dominio",
            columna=columna,
            paso=num_errores == 0,
            errores_encontrados=num_errores,
            indices_error=indices_error,
            severidad=severidad,
            mensaje=f"{num_errores} valores no pertenecen al dominio válido",
            detalles={
                "valores_validos": valores_validos,
                "valores_invalidos": [str(v) for v in valores_invalidos[:10]]
            }
        )
        
    def validar_integridad_referencial(
        self, 
        df: pd.DataFrame,
        columna_fk: str,
        df_referencia: pd.DataFrame,
        columna_pk: str,
        severidad: SeveridadError = SeveridadError.ALTO
    ) -> ResultadoValidacion:
        """
        Valida integridad referencial (clave foránea).
        
        Args:
            df: DataFrame a validar
            columna_fk: Columna con clave foránea
            df_referencia: DataFrame de referencia
            columna_pk: Columna con clave primaria en DataFrame de referencia
            severidad: Nivel de severidad del error
            
        Returns:
            ResultadoValidacion con el resultado
        """
        if columna_fk not in df.columns:
            return ResultadoValidacion(
                nombre_regla="validar_integridad_referencial",
                columna=columna_fk,
                paso=False,
                errores_encontrados=1,
                severidad=SeveridadError.CRITICO,
                mensaje=f"Columna '{columna_fk}' no existe en DataFrame principal"
            )
        
        if columna_pk not in df_referencia.columns:
            return ResultadoValidacion(
                nombre_regla="validar_integridad_referencial",
                columna=columna_fk,
                paso=False,
                errores_encontrados=1,
                severidad=SeveridadError.CRITICO,
                mensaje=f"Columna '{columna_pk}' no existe en DataFrame de referencia"
            )
        
        valores_referencia = set(df_referencia[columna_pk].dropna().unique())
        
        # Valores que no están en la referencia (excluir nulos)
        mascara_error = ~df[columna_fk].isin(valores_referencia) & df[columna_fk].notna()
        
        num_errores = mascara_error.sum()
        indices_error = df[mascara_error].index.tolist()
        valores_huerfanos = df[mascara_error][columna_fk].unique().tolist()
        
        return ResultadoValidacion(
            nombre_regla="validar_integridad_referencial",
            columna=columna_fk,
            paso=num_errores == 0,
            errores_encontrados=num_errores,
            indices_error=indices_error,
            severidad=severidad,
            mensaje=f"{num_errores} valores no tienen referencia en '{columna_pk}'",
            detalles={
                "columna_referencia": columna_pk,
                "valores_huerfanos": [str(v) for v in valores_huerfanos[:10]]
            }
        )
        
    def ejecutar_validaciones(self, df: pd.DataFrame) -> List[ResultadoValidacion]:
        """
        Ejecuta todas las reglas de validación agregadas.
        
        Args:
            df: DataFrame a validar
            
        Returns:
            Lista de ResultadoValidacion
        """
        self.resultados = []
        
        self.logger.info(f"Ejecutando {len(self.reglas)} reglas de validación...")
        
        for regla in self.reglas:
            try:
                # Ejecutar función de validación con parámetros
                resultado = regla.funcion_validacion(
                    df, 
                    regla.columna,
                    **regla.parametros
                )
                
                # Si la regla tiene mensaje personalizado, usarlo
                if regla.mensaje_error and not resultado.paso:
                    resultado.mensaje = regla.mensaje_error
                
                # Asegurar que tenga la severidad correcta
                resultado.severidad = regla.severidad
                resultado.nombre_regla = regla.nombre
                
                self.resultados.append(resultado)
                
                if not resultado.paso:
                    self.logger.warning(f" {regla.nombre}: {resultado.mensaje}")
                else:
                    self.logger.info(f" {regla.nombre}: Validación exitosa")
                    
            except Exception as e:
                self.logger.error(f"Error ejecutando regla '{regla.nombre}': {str(e)}")
                self.resultados.append(ResultadoValidacion(
                    nombre_regla=regla.nombre,
                    columna=regla.columna,
                    paso=False,
                    errores_encontrados=1,
                    severidad=SeveridadError.CRITICO,
                    mensaje=f"Error en ejecución: {str(e)}"
                ))
        
        return self.resultados
        
    def generar_reporte(self, mostrar_indices: bool = False) -> Dict:
        """
        Genera un reporte detallado de todas las validaciones.
        
        Args:
            mostrar_indices: Si True, incluye índices de errores en el reporte
            
        Returns:
            Diccionario con el reporte completo
        """
        total_validaciones = len(self.resultados)
        validaciones_exitosas = sum(1 for r in self.resultados if r.paso)
        validaciones_fallidas = total_validaciones - validaciones_exitosas
        
        # Agrupar por severidad
        errores_por_severidad = {}
        for severidad in SeveridadError:
            errores_por_severidad[severidad.value] = sum(
                1 for r in self.resultados if not r.paso and r.severidad == severidad
            )
        
        # Detalles de errores
        detalles_errores = []
        for resultado in self.resultados:
            detalle = {
                "regla": resultado.nombre_regla,
                "columna": resultado.columna,
                "paso": resultado.paso,
                "severidad": resultado.severidad.value,
                "errores_encontrados": resultado.errores_encontrados,
                "mensaje": resultado.mensaje,
                "detalles": resultado.detalles
            }
            
            if mostrar_indices and resultado.indices_error:
                detalle["indices_error"] = resultado.indices_error[:100]  # Limitar a 100
            
            detalles_errores.append(detalle)
        
        return {
            "resumen": {
                "total_validaciones": total_validaciones,
                "validaciones_exitosas": validaciones_exitosas,
                "validaciones_fallidas": validaciones_fallidas,
                "tasa_exito": f"{validaciones_exitosas/total_validaciones*100:.2f}%" if total_validaciones > 0 else "N/A",
                "errores_por_severidad": errores_por_severidad
            },
            "validaciones": detalles_errores,
            "generado_en": datetime.now().isoformat()
        }
        
    def guardar_reporte(self, ruta: str, mostrar_indices: bool = False):
        """
        Guarda el reporte de validación en un archivo JSON.
        
        Args:
            ruta: Ruta del archivo donde guardar
            mostrar_indices: Si True, incluye índices de errores
        """
        reporte = self.generar_reporte(mostrar_indices)
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Reporte guardado en: {ruta}")
        
    def obtener_errores_criticos(self) -> List[ResultadoValidacion]:
        """Retorna solo los errores críticos."""
        return [r for r in self.resultados if not r.paso and r.severidad == SeveridadError.CRITICO]
        
    def todas_validaciones_pasaron(self) -> bool:
        """Verifica si todas las validaciones pasaron."""
        return all(r.paso for r in self.resultados)