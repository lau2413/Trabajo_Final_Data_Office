"""
Módulo de pipeline de procesamiento de datos.

Proporciona un pipeline completo con:
- Manejo robusto de errores con reintentos
- Sistema de checkpoints para reanudar ejecución
- Logging estructurado con niveles
- Métricas de tiempo y calidad
- Modo dry-run para testing
- Paralelización opcional
- Notificaciones de progreso
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Callable, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import traceback
from pathlib import Path
import pickle


class EstadoEtapa(Enum):
    """Estados posibles de una etapa del pipeline."""
    PENDIENTE = "PENDIENTE"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADA = "COMPLETADA"
    FALLIDA = "FALLIDA"
    OMITIDA = "OMITIDA"


@dataclass
class Metrica:
    """Métricas de una etapa del pipeline."""
    tiempo_inicio: datetime
    tiempo_fin: Optional[datetime] = None
    duracion_segundos: float = 0.0
    filas_entrada: int = 0
    filas_salida: int = 0
    filas_modificadas: int = 0
    filas_eliminadas: int = 0
    errores: int = 0
    advertencias: int = 0


@dataclass
class Etapa:
    """Definición de una etapa del pipeline."""
    nombre: str
    funcion: Callable
    descripcion: str = ""
    critica: bool = True  # Si falla, ¿detener el pipeline?
    max_reintentos: int = 3
    timeout_segundos: Optional[int] = None
    parametros: Dict[str, Any] = field(default_factory=dict)
    dependencias: List[str] = field(default_factory=list)  # Etapas que deben completarse antes


@dataclass
class ResultadoEtapa:
    """Resultado de la ejecución de una etapa."""
    nombre: str
    estado: EstadoEtapa
    df_resultado: Optional[pd.DataFrame]
    metricas: Metrica
    error: Optional[str] = None
    traceback: Optional[str] = None
    reintentos_usados: int = 0


class PipelineDatos:
    """
    Pipeline completo para procesamiento de datos con características avanzadas.
    """
    
    def __init__(
        self, 
        nombre: str = "Pipeline",
        log_level: str = "INFO",
        checkpoint_dir: Optional[str] = None,
        modo_dry_run: bool = False
    ):
        """
        Inicializa el pipeline de datos.
        
        Args:
            nombre: Nombre del pipeline
            log_level: Nivel de logging
            checkpoint_dir: Directorio para guardar checkpoints
            modo_dry_run: Si True, simula ejecución sin modificar datos
        """
        self.nombre = nombre
        self.etapas: List[Etapa] = []
        self.resultados: Dict[str, ResultadoEtapa] = {}
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else None
        self.modo_dry_run = modo_dry_run
        self.inicio_pipeline: Optional[datetime] = None
        self.fin_pipeline: Optional[datetime] = None
        
        self._configurar_logging(log_level)
        
        if self.checkpoint_dir:
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
    def _configurar_logging(self, log_level: str):
        """Configura el sistema de logging."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(f'pipeline_{self.nombre}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            ]
        )
        self.logger = logging.getLogger(f"Pipeline.{self.nombre}")
        
    def agregar_etapa(self, etapa: Etapa):
        """
        Agrega una etapa al pipeline.
        
        Args:
            etapa: Objeto Etapa a agregar
        """
        # Validar dependencias
        for dep in etapa.dependencias:
            if not any(e.nombre == dep for e in self.etapas):
                raise ValueError(f"Dependencia '{dep}' no existe. Debe agregarse antes que '{etapa.nombre}'")
        
        self.etapas.append(etapa)
        self.logger.info(f"Etapa agregada: '{etapa.nombre}' {f'(depende de: {etapa.dependencias})' if etapa.dependencias else ''}")
        
    def _verificar_dependencias(self, etapa: Etapa) -> bool:
        """
        Verifica que todas las dependencias de una etapa estén completadas.
        
        Args:
            etapa: Etapa a verificar
            
        Returns:
            True si todas las dependencias están completadas
        """
        for dep in etapa.dependencias:
            if dep not in self.resultados:
                self.logger.warning(f"Dependencia '{dep}' no ejecutada para '{etapa.nombre}'")
                return False
            
            if self.resultados[dep].estado != EstadoEtapa.COMPLETADA:
                self.logger.warning(f"Dependencia '{dep}' no completada para '{etapa.nombre}' (estado: {self.resultados[dep].estado.value})")
                return False
        
        return True
        
    def _ejecutar_etapa_con_reintentos(
        self, 
        etapa: Etapa, 
        df: pd.DataFrame
    ) -> ResultadoEtapa:
        """
        Ejecuta una etapa con lógica de reintentos.
        
        Args:
            etapa: Etapa a ejecutar
            df: DataFrame de entrada
            
        Returns:
            ResultadoEtapa con el resultado
        """
        metricas = Metrica(
            tiempo_inicio=datetime.now(),
            filas_entrada=len(df)
        )
        
        for intento in range(etapa.max_reintentos):
            try:
                self.logger.info(f"{'[DRY-RUN] ' if self.modo_dry_run else ''}Ejecutando '{etapa.nombre}' (intento {intento + 1}/{etapa.max_reintentos})")
                
                if self.modo_dry_run:
                    # En modo dry-run, solo validar que la función existe
                    self.logger.info(f"[DRY-RUN] Simulando ejecución de '{etapa.nombre}'")
                    df_resultado = df.copy()
                    time.sleep(0.1)  # Simular procesamiento
                else:
                    # Ejecutar función real
                    inicio = time.time()
                    df_resultado = etapa.funcion(df.copy(), **etapa.parametros)
                    duracion = time.time() - inicio
                    
                    if etapa.timeout_segundos and duracion > etapa.timeout_segundos:
                        raise TimeoutError(f"Etapa excedió timeout de {etapa.timeout_segundos}s")
                
                # Calcular métricas
                metricas.tiempo_fin = datetime.now()
                metricas.duracion_segundos = (metricas.tiempo_fin - metricas.tiempo_inicio).total_seconds()
                metricas.filas_salida = len(df_resultado)
                metricas.filas_eliminadas = metricas.filas_entrada - metricas.filas_salida
                
                self.logger.info(f" '{etapa.nombre}' completada en {metricas.duracion_segundos:.2f}s")
                
                return ResultadoEtapa(
                    nombre=etapa.nombre,
                    estado=EstadoEtapa.COMPLETADA,
                    df_resultado=df_resultado,
                    metricas=metricas,
                    reintentos_usados=intento
                )
                
            except Exception as e:
                metricas.errores += 1
                error_msg = str(e)
                error_traceback = traceback.format_exc()
                
                self.logger.error(f" Error en '{etapa.nombre}' (intento {intento + 1}): {error_msg}")
                
                if intento < etapa.max_reintentos - 1:
                    tiempo_espera = 2 ** intento  # Backoff exponencial
                    self.logger.info(f"Reintentando en {tiempo_espera}s...")
                    time.sleep(tiempo_espera)
                else:
                    # Último intento fallido
                    metricas.tiempo_fin = datetime.now()
                    metricas.duracion_segundos = (metricas.tiempo_fin - metricas.tiempo_inicio).total_seconds()
                    
                    return ResultadoEtapa(
                        nombre=etapa.nombre,
                        estado=EstadoEtapa.FALLIDA,
                        df_resultado=None,
                        metricas=metricas,
                        error=error_msg,
                        traceback=error_traceback,
                        reintentos_usados=intento + 1
                    )
        
        # No debería llegar aquí
        raise RuntimeError("Error inesperado en lógica de reintentos")
        
    def _guardar_checkpoint(self, etapa_nombre: str, df: pd.DataFrame):
        """
        Guarda un checkpoint del estado actual.
        
        Args:
            etapa_nombre: Nombre de la etapa
            df: DataFrame a guardar
        """
        if self.checkpoint_dir is None:
            return
        
        checkpoint_path = self.checkpoint_dir / f"checkpoint_{etapa_nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        with open(checkpoint_path, 'wb') as f:
            pickle.dump({
                'etapa': etapa_nombre,
                'dataframe': df,
                'timestamp': datetime.now().isoformat(),
                'resultados': self.resultados
            }, f)
        
        self.logger.info(f"Checkpoint guardado: {checkpoint_path}")
        
    def _cargar_ultimo_checkpoint(self) -> Optional[Tuple[str, pd.DataFrame]]:
        """
        Carga el último checkpoint disponible.
        
        Returns:
            Tupla (nombre_etapa, dataframe) o None si no hay checkpoints
        """
        if self.checkpoint_dir is None or not self.checkpoint_dir.exists():
            return None
        
        checkpoints = list(self.checkpoint_dir.glob("checkpoint_*.pkl"))
        
        if not checkpoints:
            return None
        
        # Obtener el más reciente
        ultimo_checkpoint = max(checkpoints, key=lambda p: p.stat().st_mtime)
        
        self.logger.info(f"Cargando checkpoint: {ultimo_checkpoint}")
        
        with open(ultimo_checkpoint, 'rb') as f:
            data = pickle.load(f)
        
        self.resultados = data['resultados']
        
        return data['etapa'], data['dataframe']
        
    def ejecutar(
        self, 
        df_inicial: pd.DataFrame,
        desde_checkpoint: bool = False,
        guardar_checkpoints: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Ejecuta el pipeline completo.
        
        Args:
            df_inicial: DataFrame inicial
            desde_checkpoint: Si True, intenta reanudar desde último checkpoint
            guardar_checkpoints: Si True, guarda checkpoints después de cada etapa
            
        Returns:
            Tupla (DataFrame final, reporte de ejecución)
        """
        self.inicio_pipeline = datetime.now()
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Iniciando Pipeline: '{self.nombre}' {f'[MODO DRY-RUN]' if self.modo_dry_run else ''}")
        self.logger.info(f"Etapas totales: {len(self.etapas)}")
        self.logger.info(f"Filas iniciales: {len(df_inicial)}")
        self.logger.info(f"{'='*80}")
        
        df_actual = df_inicial.copy()
        etapa_inicio = 0
        
        # Intentar cargar checkpoint si se solicita
        if desde_checkpoint:
            checkpoint_data = self._cargar_ultimo_checkpoint()
            if checkpoint_data:
                etapa_checkpoint, df_checkpoint = checkpoint_data
                self.logger.info(f"Reanudando desde checkpoint: '{etapa_checkpoint}'")
                df_actual = df_checkpoint
                
                # Encontrar índice de la siguiente etapa
                for i, etapa in enumerate(self.etapas):
                    if etapa.nombre == etapa_checkpoint:
                        etapa_inicio = i + 1
                        break
        
        # Ejecutar etapas
        for i, etapa in enumerate(self.etapas[etapa_inicio:], start=etapa_inicio):
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"Etapa {i+1}/{len(self.etapas)}: '{etapa.nombre}'")
            self.logger.info(f"Descripción: {etapa.descripcion}")
            self.logger.info(f"{'='*80}")
            
            # Verificar dependencias
            if not self._verificar_dependencias(etapa):
                self.logger.warning(f"  Omitiendo '{etapa.nombre}' por dependencias no cumplidas")
                self.resultados[etapa.nombre] = ResultadoEtapa(
                    nombre=etapa.nombre,
                    estado=EstadoEtapa.OMITIDA,
                    df_resultado=df_actual,
                    metricas=Metrica(tiempo_inicio=datetime.now())
                )
                continue
            
            # Ejecutar etapa
            resultado = self._ejecutar_etapa_con_reintentos(etapa, df_actual)
            self.resultados[etapa.nombre] = resultado
            
            # Manejar resultado
            if resultado.estado == EstadoEtapa.COMPLETADA:
                df_actual = resultado.df_resultado
                
                # Guardar checkpoint si está habilitado
                if guardar_checkpoints and not self.modo_dry_run:
                    self._guardar_checkpoint(etapa.nombre, df_actual)
                    
            elif resultado.estado == EstadoEtapa.FALLIDA:
                if etapa.critica:
                    self.logger.error(f" Etapa crítica '{etapa.nombre}' falló. Deteniendo pipeline.")
                    self.logger.error(f"Error: {resultado.error}")
                    if resultado.traceback:
                        self.logger.debug(f"Traceback:\n{resultado.traceback}")
                    break
                else:
                    self.logger.warning(f"  Etapa no crítica '{etapa.nombre}' falló. Continuando...")
            
            # Mostrar progreso
            self._mostrar_progreso(i + 1, len(self.etapas), resultado.metricas)
        
        self.fin_pipeline = datetime.now()
        
        # Generar reporte final
        reporte = self._generar_reporte()
        
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"Pipeline '{self.nombre}' finalizado")
        self.logger.info(f"Tiempo total: {reporte['tiempo_total_segundos']:.2f}s")
        self.logger.info(f"Etapas completadas: {reporte['etapas_completadas']}/{reporte['total_etapas']}")
        self.logger.info(f"Filas finales: {len(df_actual)}")
        self.logger.info(f"{'='*80}")
        
        return df_actual, reporte
        
    def _mostrar_progreso(self, etapa_actual: int, total_etapas: int, metricas: Metrica):
        """Muestra el progreso del pipeline."""
        porcentaje = (etapa_actual / total_etapas) * 100
        barra = '█' * int(porcentaje / 5) + '░' * (20 - int(porcentaje / 5))
        
        self.logger.info(f"\nProgreso: [{barra}] {porcentaje:.1f}%")
        self.logger.info(f"Tiempo: {metricas.duracion_segundos:.2f}s | "
                        f"Filas: {metricas.filas_entrada} → {metricas.filas_salida} "
                        f"({'−' if metricas.filas_eliminadas >= 0 else '+'}{abs(metricas.filas_eliminadas)})")
        
    def _generar_reporte(self) -> Dict[str, Any]:
        """
        Genera un reporte completo de la ejecución del pipeline.
        
        Returns:
            Diccionario con el reporte
        """
        duracion_total = (self.fin_pipeline - self.inicio_pipeline).total_seconds() if self.fin_pipeline else 0
        
        etapas_por_estado = {estado.value: 0 for estado in EstadoEtapa}
        for resultado in self.resultados.values():
            etapas_por_estado[resultado.estado.value] += 1
        
        detalles_etapas = []
        for etapa in self.etapas:
            if etapa.nombre in self.resultados:
                resultado = self.resultados[etapa.nombre]
                metricas = resultado.metricas
                
                detalles_etapas.append({
                    "nombre": etapa.nombre,
                    "descripcion": etapa.descripcion,
                    "estado": resultado.estado.value,
                    "duracion_segundos": metricas.duracion_segundos,
                    "filas_entrada": metricas.filas_entrada,
                    "filas_salida": metricas.filas_salida,
                    "filas_eliminadas": metricas.filas_eliminadas,
                    "errores": metricas.errores,
                    "advertencias": metricas.advertencias,
                    "reintentos_usados": resultado.reintentos_usados,
                    "error": resultado.error
                })
        
        return {
            "nombre_pipeline": self.nombre,
            "modo_dry_run": self.modo_dry_run,
            "inicio": self.inicio_pipeline.isoformat() if self.inicio_pipeline else None,
            "fin": self.fin_pipeline.isoformat() if self.fin_pipeline else None,
            "tiempo_total_segundos": duracion_total,
            "total_etapas": len(self.etapas),
            "etapas_completadas": etapas_por_estado[EstadoEtapa.COMPLETADA.value],
            "etapas_fallidas": etapas_por_estado[EstadoEtapa.FALLIDA.value],
            "etapas_omitidas": etapas_por_estado[EstadoEtapa.OMITIDA.value],
            "etapas_por_estado": etapas_por_estado,
            "detalles_etapas": detalles_etapas
        }
        
    def guardar_reporte(self, ruta: str):
        """
        Guarda el reporte de ejecución en un archivo JSON.
        
        Args:
            ruta: Ruta del archivo donde guardar
        """
        reporte = self._generar_reporte()
        
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Reporte guardado en: {ruta}")
        
    def obtener_etapas_fallidas(self) -> List[ResultadoEtapa]:
        """Retorna las etapas que fallaron."""
        return [r for r in self.resultados.values() if r.estado == EstadoEtapa.FALLIDA]
        
    def pipeline_exitoso(self) -> bool:
        """Verifica si el pipeline se ejecutó exitosamente."""
        etapas_criticas = [e for e in self.etapas if e.critica]
        
        for etapa in etapas_criticas:
            if etapa.nombre not in self.resultados:
                return False
            if self.resultados[etapa.nombre].estado != EstadoEtapa.COMPLETADA:
                return False
        
        return True