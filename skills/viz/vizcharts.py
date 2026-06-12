#!/usr/bin/env python3
"""
VizCharts — Professional chart generator with Northwind branding.
Built on Edward Tufte's principles: maximize data-ink, minimize chartjunk.

Usage:
    python3 Tools/vizcharts.py <chart_type> <data_json_or_file> <output_path> [options_json]

Chart types:
    timeline    — Line/area chart for time series (ARR, MRR, growth curves)
    multi_line  — Multiple line series on one chart (compare trends)
    quadrant    — 2-axis scatter with quadrant labels (offense vs defense, etc.)
    scatter     — Simple scatter with optional color grouping and trend line
    rankings    — Horizontal bar / lollipop for ranked metrics
    comparison  — Side-by-side bar comparison (two entities)
    stacked_bar — Stacked bar chart (revenue by segment, etc.)
    donut       — Donut/pie chart for composition breakdowns
    waterfall   — Waterfall chart for showing changes (MRR movements, etc.)
    hex_shot    — Basketball hex bin shot chart on half-court (FG% or volume)

Themes:
    light       — Northwind Light (white bg, presentations/decks)
    dark        — Northwind Dark (dark bg, dashboards/social)
"""

import json
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patheffects as pe
import matplotlib.font_manager as fm
import numpy as np
from datetime import datetime
from adjustText import adjust_text

# ─── Font registration ───────────────────────────────────────────────────────
#
# Resolution order:
#   1. Inter (preferred — see skills/viz/SKILL.md § Setup for install)
#   2. Helvetica Neue (preinstalled on macOS)
#   3. matplotlib's default (DejaVu Sans)
#
# The chosen font name is stored in DEFAULT_FONT_FAMILY for setup_style() to use.

import glob

def _register_fonts_from_dir(directory, name_filter):
    """Register all matching font files in a directory; return count registered."""
    count = 0
    for ext in ('*.otf', '*.ttf'):
        for path in glob.glob(os.path.join(directory, ext)):
            base = os.path.basename(path).lower()
            if name_filter.lower() in base:
                fm.fontManager.addfont(path)
                count += 1
    return count


def _detect_default_font():
    """Pick the best available font family. Returns the matplotlib family name."""
    user_fonts = os.path.expanduser('~/Library/Fonts')

    # 1. Inter — preferred
    if _register_fonts_from_dir(user_fonts, 'Inter-') > 0:
        return 'Inter'

    # 2. Helvetica Neue — preinstalled on macOS
    if any('helveticaneue' in f.fname.lower() for f in fm.fontManager.ttflist):
        return 'Helvetica Neue'

    # 3. matplotlib default
    return 'DejaVu Sans'


# Register Roobert if it happens to be present (back-compat for Northwind machines)
for p in [
    '/Users/seanoconnor/Library/Fonts/Roobert-Regular.ttf',
    '/Users/seanoconnor/Library/Fonts/Roobert-Bold.ttf',
    '/Users/seanoconnor/Library/Fonts/Roobert-SemiBold.ttf',
    os.path.expanduser('~/Library/Fonts/Roobert-Regular.ttf'),
    os.path.expanduser('~/Library/Fonts/Roobert-Bold.ttf'),
    os.path.expanduser('~/Library/Fonts/Roobert-SemiBold.ttf'),
]:
    if os.path.exists(p):
        fm.fontManager.addfont(p)

# Register tabular-numerics font (JetBrains Mono) if present — for chart numeric labels
_register_fonts_from_dir(os.path.expanduser('~/Library/Fonts'), 'JetBrainsMono')

DEFAULT_FONT_FAMILY = _detect_default_font()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NORTHWIND BRANDED THEMES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Two branded templates following Tufte principles:
# - High data-ink ratio: data elements are the most prominent
# - Minimal chartjunk: no top/right spines, subtle grids, no bordered legends
# - Smallest effective difference: thin lines, muted supporting elements
# - Direct labeling over legends where possible

THEMES = {
    # Northwind Light — for presentations, decks, Substack, print
    'light': {
        'bg':           '#FFFFFF',
        'panel':        '#FFFFFF',    # Tufte: no panel fill distinct from background
        'grid':         '#EBEBEB',    # Very light — Tufte: gridlines should barely exist
        'spine':        '#D0D0D0',    # Subtle left/bottom spine only
        'text':         '#1B1F23',
        'text_secondary': '#4A5568',  # Axis labels, secondary info
        'dim':          '#9CA3AF',    # Tick labels, footnotes
        'accent':       '#FF4C57',    # Northwind red
        'blue':         '#0969DA',
        'green':        '#2DA44E',
        'orange':       '#E16F24',
        'purple':       '#8250DF',
        'yellow':       '#BF8700',
        'cyan':         '#1B7C83',
        'data_line_weight': 2.5,      # Data lines prominent
        'grid_weight':      0.4,      # Tufte: grid barely visible
        'grid_alpha':       0.5,
        'spine_weight':     0.6,
    },
    # Northwind Dark — for dashboards, social media, analytics content
    'dark': {
        'bg':           '#0F1318',
        'panel':        '#0F1318',    # Same as bg — no distinct panel
        'grid':         '#1E2430',
        'spine':        '#2D3544',
        'text':         '#E6EDF3',
        'text_secondary': '#A0AEC0',
        'dim':          '#636E7B',
        'accent':       '#FF4C57',
        'blue':         '#58A6FF',
        'green':        '#3FB950',
        'orange':       '#F0883E',
        'purple':       '#BC8CFF',
        'yellow':       '#D29922',
        'cyan':         '#39D2C0',
        'data_line_weight': 2.5,
        'grid_weight':      0.4,
        'grid_alpha':       0.4,
        'spine_weight':     0.6,
    },
    # Neutral — brand-free, suitable for any audience (default for new general-purpose use)
    'neutral': {
        'bg':           '#FFFFFF',
        'panel':        '#FFFFFF',
        'grid':         '#EBEBEB',
        'spine':        '#D0D0D0',
        'text':         '#1B1F23',
        'text_secondary': '#4A5568',
        'dim':          '#9CA3AF',
        'accent':       '#1E40AF',    # Deep blue (replaces Northwind red)
        'blue':         '#0969DA',
        'green':        '#2DA44E',
        'orange':       '#E16F24',
        'purple':       '#8250DF',
        'yellow':       '#BF8700',
        'cyan':         '#1B7C83',
        'data_line_weight': 2.5,
        'grid_weight':      0.4,
        'grid_alpha':       0.5,
        'spine_weight':     0.6,
    },
}

GROUP_COLORS_MAP = {
    'Strong': 'green', 'Elite': 'green', 'Good': 'cyan', 'Least Streaky': 'blue',
    'Average': 'yellow', 'Streaky': 'orange', 'Below Avg': 'orange',
    'Suspect': 'accent', 'Weak': 'accent', 'Highlight': 'accent', 'Default': 'blue',
}

SERIES_COLOR_ORDER = ['blue', 'accent', 'green', 'orange', 'purple', 'cyan', 'yellow']


def get_theme(options):
    return THEMES[options.get('theme', 'light')]


def group_color(group, theme):
    key = GROUP_COLORS_MAP.get(group, 'blue')
    return theme[key]


def setup_style(theme, options):
    """Apply Tufte-informed style: maximize data prominence, minimize chrome."""
    font_size = options.get('font_size', 13)
    bg = 'none' if options.get('transparent') else theme['bg']
    panel = 'none' if options.get('transparent') else theme['panel']
    plt.rcParams.update({
        'figure.facecolor':   bg,
        'axes.facecolor':     panel,
        'axes.edgecolor':     theme['spine'],
        'axes.labelcolor':    theme['text_secondary'],
        'axes.grid':          True,
        'axes.linewidth':     theme['spine_weight'],
        'grid.color':         theme['grid'],
        'grid.alpha':         theme['grid_alpha'],
        'grid.linewidth':     theme['grid_weight'],
        'text.color':         theme['text'],
        'xtick.color':        options.get('tick_color', theme['dim']),
        'ytick.color':        options.get('tick_color', theme['dim']),
        'xtick.major.width':  0.4,
        'ytick.major.width':  0.4,
        'xtick.major.size':   3,
        'ytick.major.size':   3,
        'xtick.minor.size':   0,     # Tufte: no minor ticks
        'ytick.minor.size':   0,
        'font.family':        options.get('font_family', DEFAULT_FONT_FAMILY),
        'font.size':          font_size,
        'figure.dpi':         150,
        'savefig.dpi':        options.get('dpi', 200),
        'savefig.bbox':       'tight',
        'savefig.pad_inches': 0.5,
        'savefig.facecolor':  bg,
    })


def tufte_spine(ax):
    """Apply Tufte spine treatment: remove top/right, lighten left/bottom."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.6)
    ax.spines['bottom'].set_linewidth(0.6)


def add_title_subtitle(fig, ax, options, theme):
    title = options.get('title', '')
    if title:
        ax.set_title(title, fontsize=options.get('title_size', 20),
                      fontweight='bold', pad=20, color=theme['text'],
                      loc='left')  # Tufte: left-align titles
    subtitle = options.get('subtitle', '')
    if subtitle:
        fig.text(0.12, -0.01, subtitle, ha='left',
                 fontsize=options.get('subtitle_size', 9), color=theme['dim'])


def make_legend(ax, theme, **kwargs):
    """Tufte-style legend: no frame, no background, inside plot area."""
    defaults = dict(
        frameon=False,           # Tufte: no legend border
        fontsize=kwargs.pop('fontsize', 11),
        labelcolor=theme['text_secondary'],
    )
    defaults.update(kwargs)
    leg = ax.legend(**defaults)
    return leg


def direct_label(ax, x, y, text, color, theme, fontsize=10, offset=(5, 0)):
    """Tufte: label data directly instead of using legends where possible."""
    txt = ax.annotate(text, (x, y), textcoords='offset points', xytext=offset,
                      fontsize=fontsize, color=color, fontweight='bold', va='center')
    txt.set_path_effects([pe.withStroke(linewidth=3, foreground=theme['bg'])])
    return txt


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHART: TIMELINE (line / area — time series)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def chart_timeline(data, output, options):
    """
    Time series line/area chart.
    Data: {"labels": ["Jan 2024", ...], "values": [12345, ...]}
    Options: actual_through, y_format, y_divisor, milestones, reference_lines, callouts, fill
    Supports quarter labels: "Q1 2025", "Q2 2026", and year labels: "2027"
    """
    import re as _re

    theme = get_theme(options)
    setup_style(theme, options)
    figsize = options.get('figsize', [16, 8])
    fig, ax = plt.subplots(figsize=figsize)
    tufte_spine(ax)

    labels = data['labels']
    y_divisor = options.get('y_divisor', 1)

    # Parse dates — standard formats first, then quarter/year labels
    date_formats = ['%b %Y', '%B %Y', '%Y-%m-%d', '%Y-%m', '%m/%Y']
    dates = None
    use_original_labels = False

    for fmt in date_formats:
        try:
            dates = [datetime.strptime(l, fmt) for l in labels]
            break
        except ValueError:
            continue

    if dates is None:
        # Try "Q1 2025" / "2027" mixed quarter+year format
        try:
            parsed = []
            for l in labels:
                qm = _re.match(r'Q(\d)\s+(\d{4})$', l.strip())
                ym = _re.match(r'^(\d{4})$', l.strip())
                if qm:
                    q, yr = int(qm.group(1)), int(qm.group(2))
                    parsed.append(datetime(yr, q * 3, 1))
                elif ym:
                    parsed.append(datetime(int(ym.group(1)), 12, 1))
                else:
                    raise ValueError(f"Cannot parse: {l}")
            dates = parsed
            use_original_labels = True
        except ValueError:
            dates = list(range(len(labels)))
            use_original_labels = True

    # Multi-series → delegate
    if 'series' in data:
        plt.close(fig)
        return chart_multi_line(data, output, options)

    values = [v / y_divisor for v in data['values']]
    fill = options.get('fill', True)
    lw = theme['data_line_weight']

    # Split actual vs forecast — try label lookup first, then date parse
    actual_through = options.get('actual_through', data.get('actual_through'))
    if actual_through:
        if actual_through in labels:
            cut_idx = labels.index(actual_through) + 1
        else:
            try:
                cutoff = datetime.strptime(actual_through, '%b %Y')
                cut_idx = next((i for i, d in enumerate(dates)
                                if isinstance(d, datetime) and d > cutoff), len(dates))
            except ValueError:
                cut_idx = len(dates)

        act_dates, act_vals = dates[:cut_idx], values[:cut_idx]
        fcast_dates, fcast_vals = dates[cut_idx-1:], values[cut_idx-1:]

        if fill:
            ax.fill_between(act_dates, act_vals, alpha=0.08, color=theme['blue'], zorder=1)
        ax.plot(act_dates, act_vals, color=theme['blue'], linewidth=lw, zorder=3)

        if fill:
            ax.fill_between(fcast_dates, fcast_vals, alpha=0.04, color=theme['blue'], zorder=1)
        ax.plot(fcast_dates, fcast_vals, color=theme['blue'], linewidth=lw,
                linestyle=':', zorder=3)

        # Tufte: direct label at end of each line instead of legend
        direct_label(ax, act_dates[-1], act_vals[-1], 'Actual', theme['blue'], theme,
                     offset=(-45, -15))
        direct_label(ax, fcast_dates[-1], fcast_vals[-1], 'Forecast', theme['blue'], theme,
                     offset=(-60, 14))
    else:
        if fill:
            ax.fill_between(dates, values, alpha=0.07, color=theme['blue'], zorder=1)
        ax.plot(dates, values, color=theme['blue'], linewidth=lw, zorder=3)

    # Reference lines — horizontal dashed lines at milestone values
    for rl in options.get('reference_lines', []):
        rl_val = rl['value'] / y_divisor
        ax.axhline(y=rl_val, color=theme['dim'], linewidth=0.5,
                   linestyle='--', alpha=0.4, zorder=0)
        ax.text(1.002, rl_val, rl['label'], va='center', ha='left',
                fontsize=rl.get('fontsize', 8), color=theme['accent'],
                fontweight='bold', transform=ax.get_yaxis_transform(), clip_on=False)

    # Milestones — dot on data line at crossing point
    for m in options.get('milestones', []):
        m_val = m['value'] / y_divisor
        offset = m.get('offset', [10, 12])
        for i, v in enumerate(values):
            if v >= m_val:
                ax.scatter(dates[i], v, color=theme['accent'], s=50, zorder=6,
                          edgecolors='white', linewidths=1.5)
                ax.annotate(m['label'], (dates[i], v), textcoords='offset points',
                           xytext=offset, fontsize=m.get('fontsize', 9), fontweight='bold',
                           color=m.get('color', theme['accent']),
                           bbox=dict(boxstyle='round,pad=0.25', facecolor=theme['bg'],
                                     edgecolor='none', alpha=0.9),
                           arrowprops=dict(arrowstyle='-', color=theme['dim'], alpha=0.3, lw=0.5),
                           zorder=7)
                break

    # Callouts
    for c in options.get('callouts', []):
        idx = c.get('index')
        if idx is not None and idx < len(values):
            offset = c.get('offset', [-60, 30])
            color = c.get('color', theme['text'])
            border = c.get('border_color', theme['grid'])
            ha = c.get('ha', 'center' if offset[0] == 0 else 'left')
            va = c.get('va', 'bottom' if offset[1] > 0 else 'top')
            relpos = (0.5, 0.0) if (offset[0] == 0 and offset[1] > 0) else (0.5, 1.0) if (offset[0] == 0 and offset[1] < 0) else (0.0, 0.5)
            ax.annotate(c['label'], (dates[idx], values[idx]),
                       textcoords='offset points', xytext=offset,
                       ha=ha, va=va,
                       fontsize=c.get('fontsize', 12), fontweight='bold', color=color,
                       bbox=dict(boxstyle='round,pad=0.4', facecolor=theme['bg'],
                                 edgecolor=border, alpha=0.95),
                       arrowprops=dict(arrowstyle='->', color=color, lw=1.2, relpos=relpos), zorder=8)

    # Y-axis formatting
    y_format = options.get('y_format', 'currency')
    if y_format == 'currency':
        if y_divisor >= 1_000_000:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda x, p: f'${x:.1f}M' if x >= 1 else f'${x*1000:.0f}K'))
        elif y_divisor >= 1_000:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}K'))
        else:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    elif y_format == 'percent':
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.0f}%'))
    y_suffix = options.get('y_suffix', '')
    if y_suffix and y_format not in ('currency', 'percent'):
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:,.0f}{y_suffix}'))

    # X-axis: only horizontal gridlines (Tufte)
    ax.xaxis.grid(False)

    if isinstance(dates[0], datetime):
        ax.set_xticks(dates)
        if use_original_labels:
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=10)
        else:
            x_tick_format = options.get('x_tick_format')
            if x_tick_format == 'quarter':
                def quarter_label(d):
                    q = (d.month - 1) // 3 + 1
                    return f"Q{q} '{d.strftime('%y')}"
                ax.set_xticklabels([quarter_label(d) for d in dates],
                                   rotation=45, ha='right', fontsize=10)
            else:
                ax.set_xticklabels([d.strftime('%b %y') for d in dates],
                                   rotation=45, ha='right', fontsize=10)

    ax.set_ylabel(options.get('ylabel', ''), fontsize=13, fontweight='bold',
                  color=theme['text_secondary'])
    ax.set_xlabel(options.get('xlabel', ''), fontsize=13, fontweight='bold',
                  color=theme['text_secondary'])
    ax.tick_params(axis='y', labelsize=10)

    add_title_subtitle(fig, ax, options, theme)
    plt.tight_layout()
    fig.savefig(output, transparent=options.get('transparent', False))
    plt.close(fig)
    print(f"Saved: {output}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHART: MULTI-LINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def chart_multi_line(data, output, options):
    """
    Multiple line series.
    Data: {"labels": [...], "series": [{"name": "A", "values": [...]}, ...]}
    """
    theme = get_theme(options)
    setup_style(theme, options)
    figsize = options.get('figsize', [16, 8])
    fig, ax = plt.subplots(figsize=figsize)
    tufte_spine(ax)

    labels = data['labels']
    date_formats = ['%b %Y', '%B %Y', '%Y-%m-%d', '%Y-%m']
    dates = None
    for fmt in date_formats:
        try:
            dates = [datetime.strptime(l, fmt) for l in labels]
            break
        except ValueError:
            continue
    if dates is None:
        dates = list(range(len(labels)))

    y_divisor = options.get('y_divisor', 1)
    lw = theme['data_line_weight']

    for i, series in enumerate(data['series']):
        color_key = SERIES_COLOR_ORDER[i % len(SERIES_COLOR_ORDER)]
        color = series.get('color', theme[color_key])
        raw_vals = series['values']
        # Filter out None values — plot only non-null segments
        valid = [(d, v / y_divisor) for d, v in zip(dates, raw_vals) if v is not None]
        if not valid:
            continue
        s_dates, vals = zip(*valid)
        s_dates, vals = list(s_dates), list(vals)
        style = series.get('style', '-')
        ax.plot(s_dates, vals, color=color, linewidth=lw, linestyle=style, zorder=3+i)
        if options.get('fill', False):
            ax.fill_between(s_dates, vals, alpha=0.04, color=color, zorder=1)

        # Tufte: direct label at end of line
        label = series.get('label', series.get('name', ''))
        if label:
            direct_label(ax, s_dates[-1], vals[-1], label, color, theme, offset=(8, 0))

    # Milestones — search across ALL series to find the crossing point
    all_dates = dates
    for m in options.get('milestones', []):
        m_val = m['value'] / y_divisor
        offset = m.get('offset', [10, 12])
        found = False
        # Build combined (date, value) from all series, sorted by date
        all_points = []
        for series in data['series']:
            for d, v in zip(all_dates, series['values']):
                if v is not None:
                    all_points.append((d, v / y_divisor))
        all_points.sort(key=lambda p: p[0])
        for d, v in all_points:
            if v >= m_val:
                ms_size = m.get('marker_size', 50)
                ax.scatter(d, v, color=theme['accent'], s=ms_size, zorder=6,
                          edgecolors='white', linewidths=1.5)
                ax.annotate(m['label'], (d, v), textcoords='offset points',
                           xytext=offset, fontsize=m.get('fontsize', 9), fontweight='bold',
                           color=m.get('color', theme['accent']),
                           bbox=dict(boxstyle='round,pad=0.25', facecolor=theme['bg'] if not options.get('transparent') else '#1a1a1a',
                                     edgecolor='none', alpha=0.9),
                           arrowprops=dict(arrowstyle='-', color=theme['dim'], alpha=0.3, lw=0.5),
                           zorder=7)
                found = True
                break

    ax.xaxis.grid(False)  # Only horizontal gridlines

    # Y-axis formatting (same as timeline)
    y_format = options.get('y_format', '')
    y_ticks = options.get('y_ticks')  # Custom tick values (in original units, before y_divisor)
    if y_ticks:
        ax.set_yticks([v / y_divisor for v in y_ticks])
    if y_format == 'currency':
        if y_divisor >= 1_000_000:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda x, p: f'${x:.1f}M' if x >= 1 else f'${x*1000:.0f}K'))
        elif y_divisor >= 1_000:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(
                lambda x, p: f'${x/1000:.1f}M' if x >= 1000 else f'${x:.0f}K'))
        else:
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    elif y_format == 'percent':
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'{x:.0f}%'))

    # Hide y-axis entirely
    if options.get('hide_y_axis'):
        ax.yaxis.set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.grid(False)

    if isinstance(dates[0], datetime):
        x_tick_format = options.get('x_tick_format')
        if len(dates) > 12:
            tick_dates = [d for d in dates if d.month in (1, 4, 7, 10)]
            if not tick_dates:
                tick_dates = dates
        else:
            tick_dates = dates
        ax.set_xticks(tick_dates)
        if x_tick_format == 'quarter':
            def quarter_label(d):
                q = (d.month - 1) // 3 + 1
                return f"Q{q} '{d.strftime('%y')}"
            ax.set_xticklabels([quarter_label(d) for d in tick_dates],
                               rotation=45, ha='right', fontsize=10)
        else:
            ax.set_xticklabels([d.strftime('%b %y') for d in tick_dates],
                               rotation=45, ha='right', fontsize=10)

    ax.set_ylabel(options.get('ylabel', ''), fontsize=13, fontweight='bold',
                  color=theme['text_secondary'])
    ax.set_xlabel(options.get('xlabel', ''), fontsize=13, fontweight='bold',
                  color=theme['text_secondary'])

    add_title_subtitle(fig, ax, options, theme)
    plt.tight_layout()
    fig.savefig(output, transparent=options.get('transparent', False))
    plt.close(fig)
    print(f"Saved: {output}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHART: QUADRANT SCATTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def chart_quadrant(data, output, options):
    """
    Quadrant scatter plot.
    Data: [{"label": "Team A", "x": 105.2, "y": 98.1, "group": "Strong"}, ...]
    """
    theme = get_theme(options)
    setup_style(theme, options)
    figsize = options.get('figsize', [12, 9])
    fig, ax = plt.subplots(figsize=figsize)
    tufte_spine(ax)

    xs = [d['x'] for d in data]
    ys = [d['y'] for d in data]
    x_thresh = options.get('x_threshold', np.mean(xs))
    y_thresh = options.get('y_threshold', np.mean(ys))
    highlights = set(options.get('highlight', []))

    # Tufte: quadrant lines should be subtle, not dominant
    ax.axhline(y=y_thresh, color=theme['dim'], linewidth=0.6, linestyle='--', alpha=0.4)
    ax.axvline(x=x_thresh, color=theme['dim'], linewidth=0.6, linestyle='--', alpha=0.4)

    pad = 0.08
    xlim_min = min(xs) - (max(xs) - min(xs)) * pad
    xlim_max = max(xs) + (max(xs) - min(xs)) * pad
    ylim_min = min(ys) - (max(ys) - min(ys)) * pad
    ylim_max = max(ys) + (max(ys) - min(ys)) * pad

    # Tufte: data points should be the most prominent element
    texts = []
    for d in data:
        grp = d.get('group', 'Default')
        hl = d['label'] in highlights
        color = theme['accent'] if hl else group_color(grp, theme)
        sz = 80 if hl else 45
        ec = 'white' if hl else color
        lw = 1.5 if hl else 0.3

        ax.scatter(d['x'], d['y'], c=color, s=sz, zorder=5 if hl else 3,
                   edgecolors=ec, linewidths=lw, alpha=0.9)
        txt = ax.text(d['x'], d['y'], '  ' + d['label'], fontsize=8,
                      color=theme['text'] if hl else theme['text_secondary'],
                      fontweight='bold' if hl else 'normal', zorder=6)
        txt.set_path_effects([pe.withStroke(linewidth=2.5, foreground=theme['bg'])])
        texts.append(txt)

    adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle='-', color=theme['dim'],
                alpha=0.3, lw=0.4), expand=(1.5, 1.5), force_text=(0.8, 0.8))

    # Tufte: quadrant labels as subtle watermarks
    q = options.get('quadrant_labels', {})
    ls = dict(fontsize=13, fontweight='bold', alpha=0.10, ha='center', va='center',
              color=theme['text'])
    ax.set_xlim(xlim_min, xlim_max)
    ax.set_ylim(ylim_min, ylim_max)

    xm_l, xm_r = (xlim_min + x_thresh) / 2, (x_thresh + xlim_max) / 2
    ym_t, ym_b = (y_thresh + ylim_max) / 2, (ylim_min + y_thresh) / 2

    if options.get('invert_y', False):
        ax.invert_yaxis()
        ax.text(xm_r, ym_b, q.get('top_right', ''), **ls)
        ax.text(xm_l, ym_b, q.get('top_left', ''), **ls)
        ax.text(xm_r, ym_t, q.get('bottom_right', ''), **ls)
        ax.text(xm_l, ym_t, q.get('bottom_left', ''), **ls)
    else:
        ax.text(xm_r, ym_t, q.get('top_right', ''), **ls)
        ax.text(xm_l, ym_t, q.get('top_left', ''), **ls)
        ax.text(xm_r, ym_b, q.get('bottom_right', ''), **ls)
        ax.text(xm_l, ym_b, q.get('bottom_left', ''), **ls)

    ax.set_xlabel(options.get('xlabel', 'X'), fontsize=12, fontweight='bold',
                  color=theme['text_secondary'])
    ax.set_ylabel(options.get('ylabel', 'Y'), fontsize=12, fontweight='bold',
                  color=theme['text_secondary'])

    # Tufte: legend without frame, only if groups exist
    groups_in_data = list(dict.fromkeys(d.get('group', 'Default') for d in data))
    if len(groups_in_data) > 1 and groups_in_data != ['Default']:
        handles = [ax.scatter([], [], c=group_color(g, theme), s=35, label=g) for g in groups_in_data]
        make_legend(ax, theme, handles=handles, loc='upper left', fontsize=9)

    add_title_subtitle(fig, ax, options, theme)
    plt.tight_layout()
    fig.savefig(output, transparent=options.get('transparent', False))
    plt.close(fig)
    print(f"Saved: {output}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHART: SCATTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def chart_scatter(data, output, options):
    """Simple scatter with optional trend line and grouping."""
    theme = get_theme(options)
    setup_style(theme, options)
    figsize = options.get('figsize', [12, 8])
    fig, ax = plt.subplots(figsize=figsize)
    tufte_spine(ax)
    highlights = set(options.get('highlight', []))

    texts = []
    for d in data:
        grp = d.get('group', 'Default')
        hl = d['label'] in highlights
        color = theme['accent'] if hl else group_color(grp, theme)
        ax.scatter(d['x'], d['y'], c=color, s=80 if hl else 45,
                   zorder=5 if hl else 3, edgecolors='white' if hl else color,
                   linewidths=1.5 if hl else 0.3, alpha=0.9)
        txt = ax.text(d['x'], d['y'], '  ' + d['label'], fontsize=8,
                      color=theme['text'] if hl else theme['text_secondary'],
                      fontweight='bold' if hl else 'normal', zorder=6)
        txt.set_path_effects([pe.withStroke(linewidth=2.5, foreground=theme['bg'])])
        texts.append(txt)

    adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle='-', color=theme['dim'], alpha=0.3, lw=0.4))

    if options.get('trend_line'):
        xs, ys = [d['x'] for d in data], [d['y'] for d in data]
        z = np.polyfit(xs, ys, 1)
        xr = np.linspace(min(xs), max(xs), 100)
        ax.plot(xr, np.poly1d(z)(xr), color=theme['accent'], linewidth=1.2,
                linestyle='--', alpha=0.4, zorder=1)

    ax.set_xlabel(options.get('xlabel', 'X'), fontsize=12, fontweight='bold',
                  color=theme['text_secondary'])
    ax.set_ylabel(options.get('ylabel', 'Y'), fontsize=12, fontweight='bold',
                  color=theme['text_secondary'])
    if options.get('invert_y'):
        ax.invert_yaxis()

    add_title_subtitle(fig, ax, options, theme)
    plt.tight_layout()
    fig.savefig(output, transparent=options.get('transparent', False))
    plt.close(fig)
    print(f"Saved: {output}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHART: RANKINGS (horizontal bar / lollipop)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def chart_rankings(data, output, options):
    """Horizontal bar chart for ranked metrics."""
    theme = get_theme(options)
    setup_style(theme, options)

    data = sorted(data, key=lambda d: d['value'], reverse=not options.get('ascending', False))
    if options.get('top_n'):
        data = data[:options['top_n']]

    figsize = options.get('figsize', [10, max(4, len(data) * 0.45)])
    fig, ax = plt.subplots(figsize=figsize)

    # Tufte bar chart: remove left spine, use thin white lines across bars
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_linewidth(0.6)

    labels = [d['label'] for d in data]
    values = [d['value'] for d in data]
    highlights = set(options.get('highlight', []))
    colors = [theme['accent'] if d['label'] in highlights else
              group_color(d.get('group', 'Default'), theme) for d in data]

    y_pos = range(len(labels))

    if options.get('lollipop', False):
        ax.hlines(y_pos, 0, values, color=theme['grid'], linewidth=1, zorder=1)
        ax.scatter(values, y_pos, c=colors, s=60, zorder=3, edgecolors='white', linewidths=0.5)
    else:
        ax.barh(y_pos, values, color=colors, height=0.55, alpha=0.9)

    # Tufte: data labels on bars can replace y-axis gridlines
    val_range = max(values) - min(values) if max(values) != min(values) else 1
    fmt = options.get('value_format', '.1f')
    for i, v in enumerate(values):
        ax.text(v + val_range * 0.015, i, f'{v:{fmt}}', va='center', fontsize=10,
                color=theme['text'], fontweight='bold')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=11, color=theme['text_secondary'])
    ax.invert_yaxis()
    ax.xaxis.grid(False)  # Tufte: data labels replace gridlines
    ax.yaxis.grid(False)
    ax.tick_params(axis='y', length=0)  # No tick marks — labels are sufficient

    benchmark = options.get('benchmark')
    if benchmark is not None:
        ax.axvline(x=benchmark, color=theme['dim'], linewidth=0.6, linestyle='--', alpha=0.5)
        ax.text(benchmark, -0.7, f'Avg: {benchmark:.1f}', fontsize=8,
                color=theme['dim'], ha='center')

    ax.set_xlabel(options.get('xlabel', ''), fontsize=12, fontweight='bold',
                  color=theme['text_secondary'])
    add_title_subtitle(fig, ax, options, theme)
    plt.tight_layout()
    fig.savefig(output, transparent=options.get('transparent', False))
    plt.close(fig)
    print(f"Saved: {output}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHART: COMPARISON (side-by-side bars)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def chart_comparison(data, output, options):
    """Side-by-side bar comparison for two entities."""
    theme = get_theme(options)
    setup_style(theme, options)

    labels = data['labels']
    team_a, team_b = data['team_a'], data['team_b']
    figsize = options.get('figsize', [10, max(4, len(labels) * 0.5)])
    fig, ax = plt.subplots(figsize=figsize)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_linewidth(0.6)

    y = np.arange(len(labels))
    bh = 0.32

    bars_a = ax.barh(y - bh/2, team_a['values'], bh, color=theme['blue'], alpha=0.9)
    bars_b = ax.barh(y + bh/2, team_b['values'], bh, color=theme['accent'], alpha=0.9)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=11, color=theme['text_secondary'])
    ax.tick_params(axis='y', length=0)
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)

    # Tufte: inline data labels replace need for x-axis reading
    for bar in list(bars_a):
        w = bar.get_width()
        ax.text(w + 0.2, bar.get_y() + bar.get_height()/2, f'{w:.1f}',
                va='center', fontsize=9, color=theme['blue'], fontweight='bold')
    for bar in list(bars_b):
        w = bar.get_width()
        ax.text(w + 0.2, bar.get_y() + bar.get_height()/2, f'{w:.1f}',
                va='center', fontsize=9, color=theme['accent'], fontweight='bold')

    # Tufte: direct label instead of bordered legend
    direct_label(ax, max(team_a['values']), y[0] - bh/2, team_a['name'],
                 theme['blue'], theme, fontsize=10, offset=(30, 0))
    direct_label(ax, max(team_b['values']), y[0] + bh/2, team_b['name'],
                 theme['accent'], theme, fontsize=10, offset=(30, 0))

    add_title_subtitle(fig, ax, options, theme)
    plt.tight_layout()
    fig.savefig(output, transparent=options.get('transparent', False))
    plt.close(fig)
    print(f"Saved: {output}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHART: STACKED BAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def chart_stacked_bar(data, output, options):
    """
    Stacked bar chart.
    Data: {"labels": [...], "series": [{"name": "Segment A", "values": [...]}, ...]}
    """
    theme = get_theme(options)
    setup_style(theme, options)
    figsize = options.get('figsize', [14, 7])
    fig, ax = plt.subplots(figsize=figsize)
    tufte_spine(ax)

    labels = data['labels']
    series_list = data['series']
    x = np.arange(len(labels))
    width = 0.55
    horizontal = options.get('horizontal', False)
    bottom = np.zeros(len(labels))

    for i, series in enumerate(series_list):
        color_key = SERIES_COLOR_ORDER[i % len(SERIES_COLOR_ORDER)]
        color = theme[color_key]
        vals = np.array(series['values'])
        if horizontal:
            ax.barh(x, vals, width, left=bottom, label=series['name'], color=color, alpha=0.9)
        else:
            ax.bar(x, vals, width, bottom=bottom, label=series['name'], color=color, alpha=0.9)
        bottom += vals

    if horizontal:
        ax.set_yticks(x)
        ax.set_yticklabels(labels, fontsize=11, color=theme['text_secondary'])
        ax.invert_yaxis()
        ax.xaxis.grid(True)
        ax.yaxis.grid(False)
    else:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=11, rotation=45, ha='right',
                           color=theme['text_secondary'])
        ax.yaxis.grid(True)
        ax.xaxis.grid(False)

    ax.tick_params(axis='both', length=0)
    ax.set_xlabel(options.get('xlabel', ''), fontsize=12, fontweight='bold',
                  color=theme['text_secondary'])
    ax.set_ylabel(options.get('ylabel', ''), fontsize=12, fontweight='bold',
                  color=theme['text_secondary'])
    make_legend(ax, theme, loc=options.get('legend_loc', 'upper left'))
    add_title_subtitle(fig, ax, options, theme)
    plt.tight_layout()
    fig.savefig(output, transparent=options.get('transparent', False))
    plt.close(fig)
    print(f"Saved: {output}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHART: DONUT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def chart_donut(data, output, options):
    """
    Donut / pie chart.
    Data: [{"label": "Segment A", "value": 45}, ...]
    """
    theme = get_theme(options)
    setup_style(theme, options)
    figsize = options.get('figsize', [8, 8])
    fig, ax = plt.subplots(figsize=figsize)

    labels = [d['label'] for d in data]
    values = [d['value'] for d in data]
    colors = [theme[SERIES_COLOR_ORDER[i % len(SERIES_COLOR_ORDER)]] for i in range(len(data))]

    show_pct = options.get('show_pct', True)
    autopct = '%1.1f%%' if show_pct else ''

    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors, autopct=autopct,
        startangle=90, pctdistance=0.82,
        wedgeprops=dict(width=0.4, edgecolor=theme['bg'], linewidth=2),
        textprops=dict(color=theme['text_secondary'], fontsize=11))

    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight('bold')
        t.set_color(theme['text'])

    center_text = options.get('center_text', '')
    if center_text:
        ax.text(0, 0, center_text, ha='center', va='center', fontsize=16,
                fontweight='bold', color=theme['text'])

    add_title_subtitle(fig, ax, options, theme)
    plt.tight_layout()
    fig.savefig(output, transparent=options.get('transparent', False))
    plt.close(fig)
    print(f"Saved: {output}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHART: WATERFALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def chart_waterfall(data, output, options):
    """
    Waterfall chart for showing incremental changes.
    Data: [{"label": "Starting", "value": 500000, "type": "total"}, ...]
    """
    theme = get_theme(options)
    setup_style(theme, options)
    figsize = options.get('figsize', [14, 7])
    fig, ax = plt.subplots(figsize=figsize)
    tufte_spine(ax)

    y_divisor = options.get('y_divisor', 1)
    labels = [d['label'] for d in data]
    values = [d['value'] / y_divisor for d in data]
    types = [d.get('type', 'increase') for d in data]

    running = 0
    bottoms, bar_vals, colors = [], [], []

    for v, t in zip(values, types):
        if t == 'total':
            bottoms.append(0)
            bar_vals.append(v)
            colors.append(theme['blue'])
            running = v
        elif t == 'increase':
            bottoms.append(running)
            bar_vals.append(v)
            colors.append(theme['green'])
            running += v
        elif t == 'decrease':
            running += v
            bottoms.append(running)
            bar_vals.append(abs(v))
            colors.append(theme['accent'])

    x = np.arange(len(labels))
    ax.bar(x, bar_vals, bottom=bottoms, color=colors, width=0.55,
           edgecolor=theme['bg'], linewidth=1, alpha=0.9)

    # Tufte: subtle connector lines
    for i in range(len(x) - 1):
        top = bottoms[i] + bar_vals[i]
        ax.plot([x[i] + 0.28, x[i+1] - 0.28], [top, top],
                color=theme['dim'], linewidth=0.5, linestyle='--', alpha=0.4)

    # Inline data labels (Tufte: data on the chart, not in a legend)
    fmt = options.get('value_format', '.0f')
    for i, (b, v, t) in enumerate(zip(bottoms, bar_vals, types)):
        display = v if t != 'decrease' else -v
        prefix = '+' if t == 'increase' else ''
        y_pos = b + v + (max(bar_vals) * 0.02)
        ax.text(x[i], y_pos, f'{prefix}{display:{fmt}}', ha='center',
                fontsize=10, fontweight='bold', color=theme['text'])

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11, rotation=30, ha='right',
                       color=theme['text_secondary'])
    ax.tick_params(axis='x', length=0)
    ax.xaxis.grid(False)
    ax.set_ylabel(options.get('ylabel', ''), fontsize=12, fontweight='bold',
                  color=theme['text_secondary'])
    add_title_subtitle(fig, ax, options, theme)
    plt.tight_layout()
    fig.savefig(output, transparent=options.get('transparent', False))
    plt.close(fig)
    print(f"Saved: {output}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHART: HEX SHOT CHART (basketball court hex bin visualization)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import matplotlib.colors as mcolors
from matplotlib.patches import Arc, Circle

# FG% color scale: cold blue (low) → hot red (high)
_HEX_CMAP = mcolors.LinearSegmentedColormap.from_list(
    'shot_heat', ['#2563EB', '#3B82F6', '#22D3EE', '#A3E635',
                  '#FACC15', '#F97316', '#EF4444'], N=256)


def _draw_half_court(ax, color='#C0C0C0', lw=0.8):
    """Draw NCAA half-court. ESPN coordinate system: basket at ~(25, 2.5)."""
    bx, by = 25, 2.5
    three_r = 22.146

    # Boundary
    ax.plot([0, 50, 50, 0, 0], [0, 0, 47, 47, 0], color=color, lw=lw)
    # Lane
    ax.plot([bx-6, bx-6], [0, 16], color=color, lw=lw)
    ax.plot([bx+6, bx+6], [0, 16], color=color, lw=lw)
    ax.plot([bx-6, bx+6], [16, 16], color=color, lw=lw)
    # FT circle
    ax.add_patch(Arc((bx, 16), 12, 12, angle=0, theta1=0, theta2=180,
                      color=color, lw=lw))
    # Basket + backboard
    ax.add_patch(Circle((bx, by), 0.75, fill=False, color=color, lw=lw))
    ax.plot([bx-3, bx+3], [by-1, by-1], color=color, lw=lw*1.5)
    # 3pt arc + baseline straights
    ax.add_patch(Arc((bx, by), three_r*2, three_r*2, angle=0,
                      theta1=8, theta2=172, color=color, lw=lw))
    ax.plot([bx-three_r+0.5, bx-three_r+0.5], [0, 6], color=color, lw=lw)
    ax.plot([bx+three_r-0.5, bx+three_r-0.5], [0, 6], color=color, lw=lw)
    # Restricted area
    ax.add_patch(Arc((bx, by), 8, 8, angle=0, theta1=0, theta2=180,
                      color=color, lw=lw, ls='--'))
    # Center court
    ax.add_patch(Arc((bx, 47), 12, 12, angle=0, theta1=180, theta2=360,
                      color=color, lw=lw))


def chart_hex_shot(data, output, options):
    """
    Hex bin shot chart on a basketball half-court.

    Data format (list of shots):
        [{"x": 25, "y": 10, "made": true, "points": 2, "team": "Duke"}, ...]

    Or dict with "shots" key:
        {"shots": [...], "title": "...", "subtitle": "..."}

    ESPN coordinate system: x=0-50 (court width), y=0-47 (half court),
    basket at approximately (25, 2.5).

    Options:
        gridsize     — hex grid density (default: 20, higher = smaller hexes)
        mincnt       — minimum shots per hex to display (default: 5)
        color_by     — "fg_pct" (default) or "volume"
        court_color  — color for court lines (default: theme-appropriate)
        show_stats   — show FG%, 3PT% in subtitle (default: true)
        cmap         — custom colormap name, or uses built-in shot_heat
        figsize      — [width, height] (default: [12, 11.5])
    """
    theme = get_theme(options)
    setup_style(theme, options)

    # Accept both list-of-shots and dict wrapper
    if isinstance(data, dict):
        shots = data.get('shots', [])
        title = data.get('title', options.get('title', ''))
        subtitle = data.get('subtitle', options.get('subtitle', ''))
    else:
        shots = data
        title = options.get('title', '')
        subtitle = options.get('subtitle', '')

    xs = np.array([s['x'] for s in shots])
    ys = np.array([s['y'] for s in shots])
    made = np.array([1.0 if s.get('made') else 0.0 for s in shots])

    figsize = options.get('figsize', [12, 11.5])
    fig, ax = plt.subplots(figsize=figsize, facecolor=theme['bg'])
    ax.set_facecolor(theme['bg'])

    # Court lines
    court_color = options.get('court_color',
                               '#D0D0D0' if theme['bg'] == '#FFFFFF' else '#2A3A4A')
    _draw_half_court(ax, color=court_color, lw=0.8)

    # Hex bin
    gridsize = options.get('gridsize', 20)
    mincnt = options.get('mincnt', 5)
    color_by = options.get('color_by', 'fg_pct')
    cmap = _HEX_CMAP

    if color_by == 'volume':
        hb = ax.hexbin(xs, ys, gridsize=gridsize, cmap=cmap,
                        mincnt=mincnt, extent=[0, 50, 0, 47], alpha=0.9,
                        edgecolors=theme['bg'], linewidths=0.5)
        cb_label = 'Shot Volume'
        cb_fmt = lambda x, _: f'{int(x)}'
    else:
        hb = ax.hexbin(xs, ys, C=made, gridsize=gridsize, cmap=cmap,
                        reduce_C_function=np.mean, mincnt=mincnt,
                        extent=[0, 50, 0, 47], alpha=0.9,
                        edgecolors=theme['bg'], linewidths=0.5)
        cb_label = 'Field Goal %'
        cb_fmt = lambda x, _: f'{x:.0%}'

    # Colorbar
    cb = fig.colorbar(hb, ax=ax, shrink=0.5, aspect=20, pad=0.02)
    cb.set_label(cb_label, fontsize=11, color=theme['text_secondary'],
                 fontfamily='Roobert')
    cb.ax.yaxis.set_tick_params(color=theme['dim'])
    cb.ax.tick_params(labelcolor=theme['dim'], labelsize=9)
    cb.outline.set_edgecolor(theme['dim'])
    cb.ax.yaxis.set_major_formatter(plt.FuncFormatter(cb_fmt))

    # Axis cleanup
    ax.set_xlim(-2, 52)
    ax.set_ylim(-2, 49)
    ax.set_aspect('equal')
    ax.axis('off')

    # Title
    if title:
        fig.text(0.08, 0.95, title, fontsize=options.get('title_size', 24),
                 fontweight='bold', color=theme['text'], fontfamily='Roobert')

    # Auto-subtitle with stats
    if not subtitle and options.get('show_stats', True):
        n_games = len(set(s.get('game_id', i) for i, s in enumerate(shots)))
        fg_pct = np.mean(made)
        threes = [m for m, s in zip(made, shots) if s.get('points') == 3]
        three_pct = np.mean(threes) if threes else 0
        subtitle = (f'{len(shots):,} shots from {n_games} games  |  '
                    f'FG%: {fg_pct:.1%}  |  3PT: {three_pct:.1%}')
    if subtitle:
        fig.text(0.08, 0.915, subtitle, fontsize=11,
                 color=theme['text_secondary'], fontfamily='Roobert')

    # Shot volume breakdown
    total_3 = sum(1 for s in shots if s.get('points') == 3)
    total_2 = sum(1 for s in shots if s.get('points') == 2)
    if total_2 + total_3 > 0:
        fig.text(0.08, 0.06, f'2-pointers: {total_2:,}  |  3-pointers: {total_3:,}',
                 fontsize=10, color=theme['dim'], fontfamily='Roobert')

    # Source
    source = options.get('source', '')
    if source:
        fig.text(0.08, 0.03, source, fontsize=8, color=theme['dim'],
                 fontfamily='Roobert')

    fig.savefig(output, dpi=options.get('dpi', 200), bbox_inches='tight',
                facecolor=theme['bg'], pad_inches=0.4)
    plt.close(fig)
    print(f"Saved: {output}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHART_TYPES = {
    'timeline':     chart_timeline,
    'multi_line':   chart_multi_line,
    'quadrant':     chart_quadrant,
    'scatter':      chart_scatter,
    'rankings':     chart_rankings,
    'comparison':   chart_comparison,
    'stacked_bar':  chart_stacked_bar,
    'donut':        chart_donut,
    'waterfall':    chart_waterfall,
    'hex_shot':     chart_hex_shot,
}

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        print(f"\nAvailable: {', '.join(CHART_TYPES.keys())}")
        sys.exit(1)

    chart_type = sys.argv[1]
    data_arg = sys.argv[2]
    output_path = sys.argv[3]
    options = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}

    if chart_type not in CHART_TYPES:
        print(f"Unknown: {chart_type}. Available: {', '.join(CHART_TYPES.keys())}")
        sys.exit(1)

    if os.path.isfile(data_arg):
        with open(data_arg) as f:
            data = json.load(f)
    else:
        data = json.loads(data_arg)

    CHART_TYPES[chart_type](data, output_path, options)

if __name__ == '__main__':
    main()
