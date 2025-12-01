"""
Funciones de visualización para el módulo de Ósmosis.

Contiene funciones para graficar resultados de comparación de osmolaridades
y dinámica de volumen celular.
"""

import numpy as np
from typing import List, Dict, Optional, Any
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from core.solvers.osmosis import (
    VolumeDynamicsSimulator,
    VolumeDynamicsParams,
    VolumeDynamicsResult,
    simulate_volume_dynamics,
    simulate_lysis_dynamics,
)


def plot_osmolarity_comparison(
    fig: Figure,
    result: Any,  # OsmolarityComparisonResult
) -> None:
    """
    Grafica la comparación de osmolaridades.
    
    Args:
        fig: Figura de matplotlib
        result: Resultado de OsmolarityComparisonSolver
    """
    fig.clear()
    
    # Subplot 1: Barras de osmolaridad
    ax1 = fig.add_subplot(1, 2, 1)
    
    x = [0, 1]
    width = 0.35
    
    # Barras de osmolaridad total
    ax1.bar(
        [i - width/2 for i in x],
        [result.internal_osmolarity, result.external_osmolarity],
        width,
        label='Total',
        color=['#4a90d9', '#5cb85c'],
        alpha=0.8
    )
    
    # Barras de presión osmótica real
    ax1.bar(
        [i + width/2 for i in x],
        [result.internal_effective_osmolarity, result.external_effective_osmolarity],
        width,
        label='π Real',
        color=['#2a6099', '#3c783c'],
        alpha=0.8
    )
    
    ax1.set_ylabel('Osmolaridad (mOsm/L)')
    ax1.set_title('Comparación de Osmolaridades')
    ax1.set_xticks(x)
    ax1.set_xticklabels(['Intracelular', 'Extracelular'])
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Indicador de coeficiente
    ax2 = fig.add_subplot(1, 2, 2)
    coef = result.effective_osmolarity_ratio
    
    # Determinar color según clasificación
    if result.tonic_classification == "Hipertónica":
        color = '#d9534f'
        status = "< 1\nHipertónica"
    elif result.tonic_classification == "Hipotónica":
        color = '#5cb85c'
        status = "> 1\nHipotónica"
    else:
        color = '#5bc0de'
        status = "≈ 1\nIsotónica"
    
    ax2.barh([0], [coef], height=0.5, color=color, alpha=0.7)
    ax2.axvline(x=1, color='black', linestyle='--', linewidth=2, label='Equilibrio (1.0)')
    ax2.text(coef, 0, f' {coef:.3f}', va='center', ha='left', fontsize=12, fontweight='bold')
    
    ax2.set_xlim(0, max(2, coef * 1.2))
    ax2.set_ylim(-0.5, 0.5)
    ax2.set_xlabel('Coeficiente de Presión Osmótica Real')
    ax2.set_title(f'Coef = π_int_real / π_ext_real\n{status}')
    ax2.set_yticks([])
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3, axis='x')
    
    fig.tight_layout()


def plot_lysis_comparison(
    fig: Figure,
    result: Any,  # OsmolarityComparisonResult
    critical_volume: float
) -> None:
    """
    Grafica la comparación cuando hay lisis.
    
    Args:
        fig: Figura de matplotlib
        result: Resultado de OsmolarityComparisonSolver
        critical_volume: Volumen crítico para lisis (V/V0)
    """
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    
    coef = result.effective_osmolarity_ratio
    
    # Barras
    bars = ax.bar(
        ['Coef. π Real', 'Volumen Crítico'],
        [coef, critical_volume],
        color=['#d9534f', '#5bc0de'],
        alpha=0.8,
        edgecolor='black',
        linewidth=2
    )
    
    # Línea de volumen crítico
    ax.axhline(
        y=critical_volume, color='#d9534f', linestyle='--',
        linewidth=2, label=f'Límite lisis ({critical_volume:.1f})'
    )
    
    # Zona de lisis
    ax.axhspan(
        critical_volume, max(coef * 1.2, critical_volume * 1.5),
        alpha=0.2, color='red', label='Zona de lisis'
    )
    
    ax.set_ylabel('Razón de Volumen (V/V₀)')
    ax.set_title(
        '[!] LISIS CELULAR DETECTADA\nEl volumen excedería el límite crítico',
        fontsize=12, color='#d9534f'
    )
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # Valores sobre las barras
    for bar, val in zip(bars, [coef, critical_volume]):
        ax.text(
            bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold'
        )
    
    fig.tight_layout()


def plot_volume_dynamics(
    fig: Figure,
    result: Any,  # OsmolarityComparisonResult
    internal_solutes: List[Dict],
    external_solutes: List[Dict]
) -> None:
    """
    Grafica la dinámica del volumen celular.
    
    Args:
        fig: Figura de matplotlib
        result: Resultado de OsmolarityComparisonSolver
        internal_solutes: Lista de solutos intracelulares
        external_solutes: Lista de solutos extracelulares
    """
    fig.clear()
    
    # Simular dinámica
    sim_result = simulate_volume_dynamics(internal_solutes, external_solutes)
    
    ax = fig.add_subplot(1, 1, 1)
    
    t = sim_result.time
    V_percent = sim_result.volume_percent
    t_max = t[-1]
    
    # Determinar color según tonicidad
    if result.tonic_classification == "Hipertónica":
        color = '#d9534f'
        fill_color = '#f2dede'
    elif result.tonic_classification == "Hipotónica":
        color = '#5cb85c'
        fill_color = '#dff0d8'
    else:
        color = '#5bc0de'
        fill_color = '#d9edf7'
    
    # Graficar volumen vs tiempo
    ax.plot(t, V_percent, color=color, linewidth=2.5, label='Volumen celular')
    ax.fill_between(t, 100, V_percent, alpha=0.3, color=fill_color)
    
    # Línea de referencia
    ax.axhline(y=100, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='V₀ (100%)')
    
    # Volumen final
    V_final = sim_result.final_volume_percent
    ax.axhline(y=V_final, color=color, linestyle=':', linewidth=1.5, alpha=0.7)
    ax.text(
        t_max * 0.95, V_final, f'{V_final:.1f}%',
        va='bottom' if V_final < 100 else 'top', ha='right',
        fontsize=10, fontweight='bold', color=color
    )
    
    ax.set_xlabel('Tiempo (s)', fontsize=11)
    ax.set_ylabel('Volumen celular (%)', fontsize=11)
    ax.set_title(f'Dinámica del Volumen Celular\n{result.tonic_classification}', fontsize=12)
    
    # Límites
    y_min = min(V_percent.min() * 0.9, 95)
    y_max = max(V_percent.max() * 1.1, 105)
    ax.set_ylim(y_min, y_max)
    ax.set_xlim(0, t_max)
    
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    
    # Anotación
    if result.tonic_classification == "Hipertónica":
        annotation = "El agua sale de la célula\n(crenación)"
    elif result.tonic_classification == "Hipotónica":
        annotation = "El agua entra en la célula\n(posible lisis)"
    else:
        annotation = "Sin cambio neto de volumen"
    
    ax.annotate(
        annotation, xy=(t_max * 0.5, V_percent[len(V_percent)//2]),
        xytext=(t_max * 0.7, 100),
        fontsize=9, ha='center',
        arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5)
    )
    
    fig.tight_layout()


def plot_volume_dynamics_lysis(
    fig: Figure,
    result: Any,  # OsmolarityComparisonResult
    internal_solutes: List[Dict],
    external_solutes: List[Dict],
    critical_volume: float
) -> None:
    """
    Grafica la dinámica del volumen hasta el punto de lisis.
    
    Args:
        fig: Figura de matplotlib
        result: Resultado de OsmolarityComparisonSolver
        internal_solutes: Lista de solutos intracelulares
        external_solutes: Lista de solutos extracelulares
        critical_volume: Volumen crítico para lisis (V/V0)
    """
    fig.clear()
    
    # Simular dinámica de lisis
    sim_result = simulate_lysis_dynamics(
        internal_solutes, external_solutes, critical_volume
    )
    
    ax = fig.add_subplot(1, 1, 1)
    
    t = sim_result.time
    V_percent = sim_result.volume_percent
    t_max = t[-1]
    critical_percent = critical_volume * 100
    
    # Encontrar punto de lisis
    lysis_idx = np.where(V_percent >= critical_percent)[0]
    
    if len(lysis_idx) > 0:
        lysis_time = float(t[lysis_idx[0]])
        lysis_vol = float(V_percent[lysis_idx[0]])
        
        # Antes de lisis
        ax.plot(
            t[:lysis_idx[0]+1], V_percent[:lysis_idx[0]+1],
            color='#5cb85c', linewidth=2.5, label='Volumen celular'
        )
        ax.fill_between(
            t[:lysis_idx[0]+1], 100, V_percent[:lysis_idx[0]+1],
            alpha=0.3, color='#dff0d8'
        )
        
        # Después de lisis
        ax.plot(
            t[lysis_idx[0]:], V_percent[lysis_idx[0]:],
            color='#d9534f', linewidth=2, linestyle='--', alpha=0.5
        )
        
        # Marcar punto de lisis
        ax.scatter(
            [lysis_time], [lysis_vol], color='#d9534f', s=150,
            zorder=5, marker='X', label=f'LISIS (t={lysis_time:.1f}s)'
        )
        ax.annotate(
            '[X] LISIS', xy=(lysis_time, lysis_vol),
            xytext=(lysis_time + 5, lysis_vol + 10),
            fontsize=11, fontweight='bold', color='#d9534f',
            arrowprops=dict(arrowstyle='->', color='#d9534f')
        )
    else:
        ax.plot(t, V_percent, color='#5cb85c', linewidth=2.5, label='Volumen celular')
    
    # Líneas de referencia
    ax.axhline(y=100, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='V₀ (100%)')
    ax.axhline(
        y=critical_percent, color='#d9534f', linestyle='-',
        linewidth=2, alpha=0.8, label=f'V crítico ({critical_percent:.0f}%)'
    )
    
    # Zona de lisis
    y_max = max(V_percent.max() * 1.1, critical_percent * 1.2)
    ax.axhspan(critical_percent, y_max, alpha=0.15, color='red', label='Zona de lisis')
    
    ax.set_xlabel('Tiempo (s)', fontsize=11)
    ax.set_ylabel('Volumen celular (%)', fontsize=11)
    ax.set_title('[!] Dinámica hasta Lisis Celular', fontsize=12, color='#d9534f')
    
    ax.set_xlim(0, t_max)
    ax.set_ylim(min(V_percent.min() * 0.9, 95), y_max)
    
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=9)
    
    fig.tight_layout()
