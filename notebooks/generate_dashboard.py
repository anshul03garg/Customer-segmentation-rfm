import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
import os

# Load the exported CSVs
rfm = pd.read_csv('../data/rfm_segments.csv')
monthly = pd.read_csv('../data/monthly_revenue.csv')

# ── Colors ──────────────────────────────────────────
COLORS = {
    'Champions':           '#E53935',
    'Loyal Customers':     '#1E88E5',
    'Potential Loyalists': '#43A047',
    'At-Risk Customers':   '#FB8C00'
}
BG       = '#F4F6FA'
CARD_BG  = '#FFFFFF'
TITLE_C  = '#1A237E'
TEXT_C   = '#37474F'
ACCENT   = '#1E88E5'

seg_colors = [COLORS.get(s, '#888') for s in rfm['Segment'].unique()]

# ── Figure setup ────────────────────────────────────
fig = plt.figure(figsize=(20, 13), facecolor=BG)
fig.suptitle('Customer Segmentation & RFM Analysis Dashboard',
             fontsize=22, fontweight='bold', color=TITLE_C, y=0.98)

gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.55, wspace=0.4,
                       left=0.05, right=0.97, top=0.92, bottom=0.06)

# ── KPI Cards ───────────────────────────────────────
kpi_data = [
    ('Total Customers',    f"{rfm.shape[0]:,}",           '#1E88E5'),
    ('Total Transactions', f"{805549:,}",                  '#43A047'),
    ('Total Revenue',      f"${rfm['Monetary'].sum():,.0f}",'#E53935'),
    ('Avg Order Value',    f"${rfm['Monetary'].mean():,.0f}",'#FB8C00'),
]

for i, (label, value, color) in enumerate(kpi_data):
    ax = fig.add_subplot(gs[0, i])
    ax.set_facecolor(CARD_BG)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    for spine in ax.spines.values():
        spine.set_visible(False)
    # Colored top bar
    ax.add_patch(mpatches.FancyBboxPatch((0, 0), 1, 1,
        boxstyle="round,pad=0.02", facecolor=CARD_BG,
        edgecolor=color, linewidth=2.5))
    ax.add_patch(mpatches.Rectangle((0, 0.82), 1, 0.18, color=color, zorder=2))
    ax.text(0.5, 0.91, label, ha='center', va='center',
            fontsize=10, color='white', fontweight='bold', zorder=3)
    ax.text(0.5, 0.42, value, ha='center', va='center',
            fontsize=20, color=color, fontweight='bold')

# ── Pie Chart — Segment Distribution ────────────────
ax_pie = fig.add_subplot(gs[1, 0])
ax_pie.set_facecolor(CARD_BG)
seg_counts = rfm['Segment'].value_counts()
pie_colors = [COLORS.get(s, '#888') for s in seg_counts.index]
wedges, texts, autotexts = ax_pie.pie(
    seg_counts, labels=None, colors=pie_colors,
    autopct='%1.1f%%', startangle=90,
    textprops={'fontsize': 9}, pctdistance=0.75,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2})
for at in autotexts:
    at.set_color('white'); at.set_fontweight('bold')
ax_pie.set_title('Customer Segments', fontsize=12,
                 fontweight='bold', color=TITLE_C, pad=10)
ax_pie.legend(seg_counts.index, loc='lower center',
              bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=8,
              frameon=False)

# ── Bar Chart — Revenue by Segment ──────────────────
ax_rev = fig.add_subplot(gs[1, 1])
ax_rev.set_facecolor(CARD_BG)
rev_by_seg = rfm.groupby('Segment')['Monetary'].sum().sort_values(ascending=True)
bar_colors = [COLORS.get(s, '#888') for s in rev_by_seg.index]
bars = ax_rev.barh(rev_by_seg.index, rev_by_seg.values,
                   color=bar_colors, edgecolor='white', height=0.55)
for bar, val in zip(bars, rev_by_seg.values):
    ax_rev.text(bar.get_width() + rev_by_seg.max()*0.01,
                bar.get_y() + bar.get_height()/2,
                f'${val/1e6:.1f}M', va='center', fontsize=9, fontweight='bold', color=TEXT_C)
ax_rev.set_title('Revenue by Segment', fontsize=12,
                 fontweight='bold', color=TITLE_C)
ax_rev.set_xlabel('Total Revenue ($)', fontsize=9, color=TEXT_C)
ax_rev.tick_params(labelsize=8)
ax_rev.set_facecolor(CARD_BG)
ax_rev.spines['top'].set_visible(False)
ax_rev.spines['right'].set_visible(False)
ax_rev.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1e6:.0f}M'))

# ── Scatter — Recency vs Monetary ───────────────────
ax_sc = fig.add_subplot(gs[1, 2])
ax_sc.set_facecolor(CARD_BG)
for seg, color in COLORS.items():
    mask = rfm['Segment'] == seg
    if mask.sum() > 0:
        ax_sc.scatter(rfm[mask]['Recency'],
                      rfm[mask]['Monetary'].clip(upper=rfm['Monetary'].quantile(0.95)),
                      c=color, label=seg, alpha=0.55, s=18, edgecolors='none')
ax_sc.set_title('Recency vs Monetary', fontsize=12,
                fontweight='bold', color=TITLE_C)
ax_sc.set_xlabel('Recency (days)', fontsize=9, color=TEXT_C)
ax_sc.set_ylabel('Monetary ($)', fontsize=9, color=TEXT_C)
ax_sc.tick_params(labelsize=8)
ax_sc.spines['top'].set_visible(False)
ax_sc.spines['right'].set_visible(False)
ax_sc.set_facecolor(CARD_BG)

# ── Bar — Avg RFM per Segment ───────────────────────
ax_rfm = fig.add_subplot(gs[1, 3])
ax_rfm.set_facecolor(CARD_BG)
seg_profile = rfm.groupby('Segment')[['Recency','Frequency','Monetary']].mean()
seg_profile_norm = (seg_profile - seg_profile.min()) / (seg_profile.max() - seg_profile.min())
seg_profile_norm['Recency'] = 1 - seg_profile_norm['Recency']

x = np.arange(len(seg_profile_norm))
width = 0.25
ax_rfm.bar(x - width, seg_profile_norm['Recency'],   width, label='Recency',   color='#E53935', alpha=0.85)
ax_rfm.bar(x,          seg_profile_norm['Frequency'], width, label='Frequency', color='#1E88E5', alpha=0.85)
ax_rfm.bar(x + width,  seg_profile_norm['Monetary'],  width, label='Monetary',  color='#43A047', alpha=0.85)
ax_rfm.set_xticks(x)
ax_rfm.set_xticklabels([s.replace(' ', '\n') for s in seg_profile_norm.index], fontsize=7)
ax_rfm.set_title('Avg RFM Score by Segment', fontsize=12,
                 fontweight='bold', color=TITLE_C)
ax_rfm.legend(fontsize=8, frameon=False)
ax_rfm.set_ylabel('Normalized Score', fontsize=9, color=TEXT_C)
ax_rfm.tick_params(labelsize=8)
ax_rfm.spines['top'].set_visible(False)
ax_rfm.spines['right'].set_visible(False)
ax_rfm.set_facecolor(CARD_BG)

# ── Line Chart — Monthly Revenue ────────────────────
ax_line = fig.add_subplot(gs[2, :3])
ax_line.set_facecolor(CARD_BG)
monthly_sorted = monthly.sort_values('InvoiceDate').reset_index(drop=True)
x_vals = range(len(monthly_sorted))
ax_line.plot(x_vals, monthly_sorted['Revenue'], color=ACCENT,
             linewidth=2.5, marker='o', markersize=4)
ax_line.fill_between(x_vals, monthly_sorted['Revenue'],
                     alpha=0.12, color=ACCENT)
ax_line.set_title('Monthly Revenue Trend', fontsize=12,
                  fontweight='bold', color=TITLE_C)
ax_line.set_xlabel('Month', fontsize=9, color=TEXT_C)
ax_line.set_ylabel('Revenue ($)', fontsize=9, color=TEXT_C)
step = max(1, len(monthly_sorted)//10)
ax_line.set_xticks(list(x_vals)[::step])
ax_line.set_xticklabels(monthly_sorted['InvoiceDate'].iloc[::step], rotation=35, fontsize=7)
ax_line.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M'))
ax_line.tick_params(labelsize=8)
ax_line.spines['top'].set_visible(False)
ax_line.spines['right'].set_visible(False)
ax_line.set_facecolor(CARD_BG)

# ── AOV by Segment ───────────────────────────────────
ax_aov = fig.add_subplot(gs[2, 3])
ax_aov.set_facecolor(CARD_BG)
aov = rfm.groupby('Segment')['Monetary'].mean().sort_values(ascending=True)
aov_colors = [COLORS.get(s, '#888') for s in aov.index]
bars2 = ax_aov.barh(aov.index, aov.values, color=aov_colors,
                    edgecolor='white', height=0.55)
for bar, val in zip(bars2, aov.values):
    ax_aov.text(bar.get_width() + aov.max()*0.01,
                bar.get_y() + bar.get_height()/2,
                f'${val:,.0f}', va='center', fontsize=9,
                fontweight='bold', color=TEXT_C)
ax_aov.set_title('Avg Order Value (AOV)\nby Segment', fontsize=12,
                 fontweight='bold', color=TITLE_C)
ax_aov.set_xlabel('AOV ($)', fontsize=9, color=TEXT_C)
ax_aov.tick_params(labelsize=8)
ax_aov.spines['top'].set_visible(False)
ax_aov.spines['right'].set_visible(False)
ax_aov.set_facecolor(CARD_BG)

# ── Save ────────────────────────────────────────────
os.makedirs('../data', exist_ok=True)
plt.savefig('../data/powerbi_dashboard.png', dpi=150,
            bbox_inches='tight', facecolor=BG)
print('Dashboard saved: data/powerbi_dashboard.png')
plt.show()
