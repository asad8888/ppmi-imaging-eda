#!/usr/bin/env python3
"""
Generate all 10 PPMI Imaging EDA notebooks.
Run from the working/ directory:
    source venv/bin/activate && python generate_notebooks.py
"""

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from pathlib import Path

WORKING_DIR = Path(__file__).parent

def md(text):  return new_markdown_cell(text)
def code(src): return new_code_cell(src)

def save_nb(cells, name):
    nb = new_notebook()
    nb.cells = cells
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3 (ipykernel)", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3", "version": "3.11.0"},
    }
    with open(WORKING_DIR / name, "w") as f:
        nbformat.write(nb, f)
    print(f"  {name}")

SETUP = """\
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

sns.set_theme(style='whitegrid', palette='colorblind')
plt.rcParams.update({'figure.figsize': (12, 5), 'axes.titlesize': 14,
                     'axes.labelsize': 12, 'xtick.labelsize': 10,
                     'ytick.labelsize': 10, 'figure.dpi': 120})
DATA_DIR = Path('../Imaging')
print(f'Data directory: {DATA_DIR.resolve()}')"""

VISIT_HELPER = """\
VISIT_ORDER = ['SC', 'BL', 'V04', 'V06', 'V08', 'V10', 'V12', 'V14', 'V16', 'PW']
VISIT_LABELS = {'SC': 'Screening', 'BL': 'Baseline', 'PW': 'Withdrawal',
                'V04': 'Yr 1', 'V06': 'Yr 2', 'V08': 'Yr 3',
                'V10': 'Yr 4', 'V12': 'Yr 5', 'V14': 'Yr 6', 'V16': 'Yr 7'}
def ordered_visits(series):
    present = series.dropna().unique().tolist()
    ordered = [v for v in VISIT_ORDER if v in present]
    return ordered + sorted([v for v in present if v not in VISIT_ORDER])"""

# ─────────────────────────────────────────────────────────────────────────────
def make_00():
    cells = [
        md("# 00 · PPMI Imaging — Study Overview & Cohort\n> *Start here. No neuroscience background required.*"),
        md("""## What is Parkinson's Disease?

Parkinson's Disease (PD) is a progressive brain disorder that affects ~10 million people worldwide.

**Root cause:** Neurons that produce **dopamine** — a chemical messenger that coordinates smooth movement — gradually die off in a brain region called the **Substantia Nigra**.

By the time the first tremor or stiffness appears, **60–80% of dopamine neurons are already gone**. This makes early detection and biomarker research critical.

**Non-motor symptoms often appear years before movement problems:** loss of smell (anosmia), REM sleep disorder, constipation, depression.

---

## What is PPMI?

The **Parkinson's Progression Markers Initiative (PPMI)** is one of the most comprehensive PD studies ever conducted. Launched in 2010, it tracks thousands of participants across international sites with detailed clinical and biological measurements over many years.

**Goal:** Find reliable, objective markers that can detect PD early and track its progression.

**Three participant groups:**

| Cohort | Description |
|--------|-------------|
| **PD** | Confirmed Parkinson's diagnosis (recently diagnosed, < 2 years) |
| **Prodromal** | Pre-diagnostic: show early warning signs (REM sleep disorder, smell loss) but no PD yet |
| **Healthy Control (HC)** | Age-matched healthy volunteers for comparison |

---

## What is "Imaging Data"?

This dataset contains **processed measurements** extracted from brain scans — not the raw images themselves. Think of it as: MRI machine → computer analysis → numbers in a spreadsheet.

Each row in a file typically represents one scan session for one participant at one visit."""),
        code(SETUP),
        code(VISIT_HELPER),
        md("## File Inventory\nLet's count what we have across all imaging files."),
        code("""\
files = {
    'DaTSCAN Scan Log': 'Dopamine_Imaging_12Nov2026.csv',
    'DaTSCAN Quant SBR': 'Xing_Core_Lab_-_Quant_SBR_12Nov2026.csv',
    'DaTSCAN Visual Read': 'Xing_Core_Lab_-_Visual_Read_12Nov2026.csv',
    'MRI Core Log': 'Magnetic_Resonance_Imaging__MRI__12Nov2026.csv',
    'MRIQC (MRI Quality)': 'MRIQC_12Nov2026.csv',
    'Grey Matter Volume': 'Grey_Matter_Volume_12Nov2026.csv',
    'FreeSurfer Thickness': 'FS7_APARC_CTH_12Nov2026.csv',
    'FreeSurfer SA': 'FS7_APARC_SA_12Nov2026.csv',
    'FreeSurfer Vol': 'FS7_ASEG_VOL_12Nov2026.csv',
    'DTI Regions': 'DTI_Regions_of_Interest_12Nov2026.csv',
    'PET AV-133 Metadata': 'PET_Acquisition_Metadata_12Nov2026.csv',
    'PET AV-133 SBR': 'PET_SBR_Analysis_12Nov2026.csv',
    'TAU PET Analysis': 'TAU_PET_Analysis_12Nov2026.csv',
    'SV2A PET SUVR': 'SV2A_PET_SUVR_Analysis_12Nov2026.csv',
    'Safety CT': 'Safety_Head_CT_Scan_12Nov2026.csv',
}
rows = []
for label, fname in files.items():
    p = DATA_DIR / fname
    if p.exists():
        df = pd.read_csv(p)
        rows.append({'File': label, 'Rows': f'{len(df):,}',
                     'Participants': df['PATNO'].nunique() if 'PATNO' in df.columns else '—',
                     'Visits': df['EVENT_ID'].nunique() if 'EVENT_ID' in df.columns else '—'})
summary = pd.DataFrame(rows)
print(summary.to_string(index=False))"""),
        md("## Participant Count per Modality"),
        code("""\
numeric = [(r['File'], r['Participants']) for _, r in summary.iterrows()
           if isinstance(r['Participants'], (int, np.integer))]
numeric.sort(key=lambda x: x[1])
labels, counts = zip(*numeric)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(labels, counts, color=sns.color_palette('colorblind', len(labels)))
ax.set_xlabel('Unique Participants')
ax.set_title('Coverage by Imaging File')
for b, v in zip(bars, counts):
    ax.text(b.get_width() + 3, b.get_y() + b.get_height()/2, f'{v:,}', va='center', fontsize=9)
ax.set_xlim(0, max(counts) * 1.2)
plt.tight_layout(); plt.show()"""),
        md("## Visit Schedule\n\n| Code | Meaning |\n|------|--------|\n| SC | Screening — first contact |\n| BL | Baseline — start of study |\n| V04–V16 | Annual follow-up visits (every 2 years) |\n| PW | Premature Withdrawal |\n| U01, U02 | Unscheduled visits |"),
        code("""\
datscan = pd.read_csv(DATA_DIR / 'Dopamine_Imaging_12Nov2026.csv')
visits = ordered_visits(datscan['EVENT_ID'])
vc = datscan.groupby('EVENT_ID')['PATNO'].nunique().reindex(visits).dropna()

fig, ax = plt.subplots(figsize=(13, 5))
bars = ax.bar(range(len(vc)), vc.values, color=sns.color_palette('colorblind')[0])
ax.set_xticks(range(len(vc)))
ax.set_xticklabels([f'{VISIT_LABELS.get(v,v)}\\n({v})' for v in vc.index], rotation=45, ha='right')
ax.set_ylabel('Unique Participants'); ax.set_title('Participants per Visit (DaTSCAN file)')
for b, v in zip(bars, vc.values):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+8, str(int(v)), ha='center', fontsize=9)
plt.tight_layout(); plt.show()"""),
        md("""## Key Takeaways

- **DaTSCAN SPECT** is the flagship modality — largest N, longest follow-up
- **Structural MRI + FreeSurfer** provides anatomical measures (~700 participants processed)
- **DTI** targets the Substantia Nigra specifically — the PD-critical region
- **PET substudies** (Tau, SV2A, AV-133) are smaller, cutting-edge biomarker pilots
- All files share `PATNO` and `EVENT_ID` as merge keys
- Proceed to **01_DaTSCAN_SPECT_EDA** for the richest dataset"""),
    ]
    save_nb(cells, "00_Overview_and_Cohort.ipynb")


# ─────────────────────────────────────────────────────────────────────────────
def make_01():
    cells = [
        md("# 01 · DaTSCAN / SPECT Dopamine Imaging EDA\n> *The primary biomarker in PPMI — measuring how much dopamine transporter is left in the brain.*"),
        md("""## Background: What is DaTSCAN?

**DaTSCAN** uses a radioactive tracer (¹²³I-ioflupane) that binds to **Dopamine Transporter (DAT)** proteins on dopamine neurons.

1. Tracer injected → travels to brain → binds to DAT proteins
2. SPECT camera detects radiation → creates a map of DAT density
3. More binding = more dopamine neurons = healthier dopamine system

**Why it matters for PD:** As dopamine neurons die, DAT binding decreases. DaTSCAN can detect this *before* motor symptoms are severe enough for a clinical diagnosis.

**Key measurement — Striatal Binding Ratio (SBR):**
> SBR = (tracer uptake in brain region) / (tracer uptake in white matter) − 1

White matter has no DAT, so it's the reference. An SBR of 2.0 means the region has 3× more tracer than white matter.
- **Healthy controls:** SBR typically > 1.5 in putamen
- **PD patients:** SBR can drop to < 1.0 in putamen

**Brain regions measured:**
- **Striatum** = Caudate + Putamen (combined)
- **Caudate nucleus** = involved in learning/motivation; less affected early in PD
- **Putamen** = most affected early in PD; the most sensitive region for diagnosis
- **L_ / R_ prefixes** = left / right hemisphere"""),
        code(SETUP), code(VISIT_HELPER),
        md("## Load Data Files"),
        code("""\
scan_log = pd.read_csv(DATA_DIR / 'Dopamine_Imaging_12Nov2026.csv')
acq_meta = pd.read_csv(DATA_DIR / 'Xing_Core_Lab_-_DATSCAN_acquisition_metadata_12Nov2026.csv')
sbr      = pd.read_csv(DATA_DIR / 'Xing_Core_Lab_-_Quant_SBR_12Nov2026.csv')
vis_read = pd.read_csv(DATA_DIR / 'Xing_Core_Lab_-_Visual_Read_12Nov2026.csv')
for name, df in [('Scan Log', scan_log), ('Acquisition Metadata', acq_meta),
                 ('Quant SBR', sbr), ('Visual Read', vis_read)]:
    print(f'{name:30s}: {len(df):>6,} rows | {df["PATNO"].nunique()} participants')"""),
        md("""## Column Reference

### Scan Log (`Dopamine_Imaging`)
| Column | Meaning |
|--------|---------|
| `PATNO` | Participant ID |
| `EVENT_ID` | Visit code |
| `DATSCAN` | Scan completed? 1=Yes 0=No |
| `DATSCANTRC` | Tracer: 1=¹²³I-DaTscan, 2=⁹⁹mTc-TRODAT-1 |
| `VSINTRPT` | Visual interpretation: 1=Normal, 2=Abnormal |
| `INFODT` | Date info recorded (MM/YYYY) |

### Acquisition Metadata (`Xing_Core_Lab_-_DATSCAN_acquisition_metadata`)
| Column | Meaning |
|--------|---------|
| `DATSCAN_LIGAND` | Radiopharmaceutical name |
| `DATSCAN_TOTAL_DOSE_CALC` | Injected dose in MBq (radioactivity amount) |
| `DATSCAN_IMAGE_ACCEPTABLE` | QC pass: Yes/No |
| `DATSCAN_START_TIME` | When SPECT scan began |

### Quantitative SBR (`Xing_Core_Lab_-_Quant_SBR`)
| Column | Meaning |
|--------|---------|
| `DATSCAN_ANALYZED` | Was scan analyzable? Yes/No |
| `STRIATUM_REF_CWM` | Bilateral striatum SBR (vs cerebral white matter) |
| `CAUDATE_REF_CWM` | Bilateral caudate SBR |
| `PUTAMEN_REF_CWM` | Bilateral putamen SBR |
| `*_L_REF_CWM` | Left hemisphere version |
| `*_R_REF_CWM` | Right hemisphere version |
| `*_PRECAUDATE_*` | Anterior part of caudate |
| `*_ANTPUTAMEN_*` | Anterior putamen (most sensitive to PD) |
| `*_POSTPUTAMEN_*` | Posterior putamen |

### Visual Read (`Xing_Core_Lab_-_Visual_Read`)
| Column | Meaning |
|--------|---------|
| `DATSCAN_VISINTRP` | Radiologist overall interpretation: "positive"=abnormal, "negative"=normal |"""),
        md("## 1 · Scan Completion per Visit"),
        code("""\
completed = scan_log[scan_log['DATSCAN'] == 1]
visits = ordered_visits(scan_log['EVENT_ID'])
vc = completed.groupby('EVENT_ID')['PATNO'].nunique().reindex(visits).dropna()

fig, ax = plt.subplots(figsize=(13, 5))
bars = ax.bar(range(len(vc)), vc.values, color=sns.color_palette('colorblind')[0])
ax.set_xticks(range(len(vc)))
ax.set_xticklabels([f'{VISIT_LABELS.get(v,v)}\\n({v})' for v in vc.index], rotation=45, ha='right')
ax.set_ylabel('Participants with Completed DaTSCAN')
ax.set_title('DaTSCAN Completion per Visit')
for b, v in zip(bars, vc.values):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+5, str(int(v)), ha='center', fontsize=9)
plt.tight_layout(); plt.show()
print(f'Total scan records: {len(scan_log):,} | Completed: {len(completed):,}')"""),
        md("## 2 · Radiotracer Used"),
        code("""\
lig = acq_meta['DATSCAN_LIGAND'].value_counts()
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
lig.plot(kind='bar', ax=axes[0], color=sns.color_palette('colorblind', len(lig)), edgecolor='white')
axes[0].set_title('Tracer Used'); axes[0].set_ylabel('Scans'); axes[0].tick_params(axis='x', rotation=30)
axes[1].pie(lig.values, labels=lig.index, autopct='%1.1f%%',
            colors=sns.color_palette('colorblind', len(lig)), startangle=90)
axes[1].set_title('Tracer Proportion')
plt.tight_layout(); plt.show(); print(lig.to_string())"""),
        md("## 3 · Image Quality Acceptance Rate\n\nEvery scan is reviewed by the Xing Core Lab. Only 'acceptable' scans are used for analysis."),
        code("""\
qc = acq_meta['DATSCAN_IMAGE_ACCEPTABLE'].value_counts()
colors = ['#2ecc71' if 'Yes' in str(k) else '#e74c3c' for k in qc.index]
fig, axes = plt.subplots(1, 2, figsize=(10, 5))
qc.plot(kind='bar', ax=axes[0], color=colors, edgecolor='white')
axes[0].set_title('QC Results'); axes[0].set_ylabel('Scans'); axes[0].tick_params(axis='x', rotation=0)
axes[1].pie(qc.values, labels=[f'{k} ({v:,})' for k,v in qc.items()],
            colors=colors, autopct='%1.1f%%', startangle=90)
axes[1].set_title('Pass Rate')
plt.tight_layout(); plt.show()
print(f'Acceptance rate: {qc.get("Yes",0)/len(acq_meta)*100:.1f}%')"""),
        md("## 4 · Injected Dose Distribution\n\nDose in MBq (megabecquerels). Should fall within a protocol range to ensure consistent imaging."),
        code("""\
dose = acq_meta['DATSCAN_TOTAL_DOSE_CALC'].dropna()
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
dose.hist(bins=40, ax=axes[0], edgecolor='black', alpha=0.8, color=sns.color_palette('colorblind')[0])
axes[0].axvline(dose.mean(), color='red', linestyle='--', label=f'Mean: {dose.mean():.1f} MBq')
axes[0].set_title('Injected Dose Distribution'); axes[0].set_xlabel('Dose (MBq)'); axes[0].legend()
axes[1].boxplot(dose.values, patch_artist=True,
                boxprops=dict(facecolor=sns.color_palette('colorblind')[0]))
axes[1].set_title('Dose Box Plot'); axes[1].set_ylabel('Dose (MBq)'); axes[1].set_xticks([])
plt.tight_layout(); plt.show()
print(dose.describe().round(2))"""),
        md("## 5 · SBR Distributions by Brain Region\n\nThis is the core result. Higher SBR = more dopamine transporters = healthier dopamine system. The putamen is most sensitive to early PD changes."),
        code("""\
sbr_valid = sbr[sbr['DATSCAN_ANALYZED'] == 'Yes'].copy()
key_cols = {c: c.replace('_REF_CWM','').replace('_',' ').title()
            for c in ['STRIATUM_REF_CWM','CAUDATE_REF_CWM','PUTAMEN_REF_CWM']
            if c in sbr_valid.columns}

plot_data = pd.concat([sbr_valid[c].rename(label) for c, label in key_cols.items()], axis=1)
melted = plot_data.melt(var_name='Region', value_name='SBR').dropna()

fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=melted, x='Region', y='SBR', palette='colorblind', ax=ax, inner='box', cut=0)
ax.axhline(1.0, color='red', linestyle='--', alpha=0.6, label='SBR = 1.0')
ax.set_title('Striatal Binding Ratio by Region (analyzed scans)')
ax.set_ylabel('SBR (higher = more dopamine transporters)')
ax.legend(); plt.tight_layout(); plt.show()
print(melted.groupby('Region')['SBR'].describe().round(3))"""),
        md("## 6 · Left vs Right Hemisphere Asymmetry\n\nPD often starts asymmetrically — one side more affected than the other. Points off the diagonal indicate asymmetry."),
        code("""\
sbr_valid = sbr[sbr['DATSCAN_ANALYZED'] == 'Yes'].copy()
pairs = [c for c in [('CAUDATE_L_REF_CWM','CAUDATE_R_REF_CWM','Caudate'),
                      ('PUTAMEN_L_REF_CWM','PUTAMEN_R_REF_CWM','Putamen')]
         if c[0] in sbr_valid.columns]

fig, axes = plt.subplots(1, len(pairs), figsize=(6*len(pairs), 5))
if len(pairs) == 1: axes = [axes]
for ax, (lc, rc, name) in zip(axes, pairs):
    sub = sbr_valid[[lc, rc]].dropna()
    mn, mx = sub.min().min()*0.9, sub.max().max()*1.05
    ax.scatter(sub[lc], sub[rc], alpha=0.3, s=15, color=sns.color_palette('colorblind')[0])
    ax.plot([mn,mx],[mn,mx],'r--', label='Perfect symmetry')
    ax.set_xlabel(f'Left {name} SBR'); ax.set_ylabel(f'Right {name} SBR')
    ax.set_title(f'{name}: L vs R'); ax.legend(fontsize=9)
plt.suptitle('Hemispheric Asymmetry', y=1.02); plt.tight_layout(); plt.show()"""),
        md("## 7 · Longitudinal SBR Trends\n\nSBR should decline over time in PD patients. Here we plot the mean across all participants — the trend reflects the mixed cohort (PD + prodromal + healthy controls)."),
        code("""\
sbr_valid = sbr[sbr['DATSCAN_ANALYZED'] == 'Yes'].copy()
lon_cols = [c for c in ['CAUDATE_REF_CWM','PUTAMEN_REF_CWM'] if c in sbr_valid.columns]
visits = ordered_visits(sbr_valid['EVENT_ID'])

if lon_cols:
    fig, axes = plt.subplots(1, len(lon_cols), figsize=(7*len(lon_cols), 5))
    if len(lon_cols) == 1: axes = [axes]
    for ax, col in zip(axes, lon_cols):
        stats = sbr_valid.groupby('EVENT_ID')[col].agg(['mean','sem']).reindex(visits).dropna()
        x = range(len(stats))
        ax.errorbar(x, stats['mean'], yerr=stats['sem'], marker='o', linewidth=2, capsize=4,
                    color=sns.color_palette('colorblind')[0])
        ax.set_xticks(list(x))
        ax.set_xticklabels([VISIT_LABELS.get(v,v) for v in stats.index], rotation=45, ha='right')
        ax.set_ylabel('Mean SBR ± SEM')
        ax.set_title(col.split('_')[0] + ' SBR over Time')
    plt.suptitle('Longitudinal SBR (all participants, mean ± SEM)', fontsize=13)
    plt.tight_layout(); plt.show()"""),
        md("## 8 · Visual Interpretation: Positive vs Negative\n\nAn expert radiologist reviewed every scan and gave a binary judgment: does the uptake pattern look abnormal (positive = likely PD-like)?"),
        code("""\
vr = vis_read['DATSCAN_VISINTRP'].str.strip().str.lower().value_counts()
colors = ['#e74c3c' if 'pos' in k else '#2ecc71' for k in vr.index]
fig, axes = plt.subplots(1, 2, figsize=(10, 5))
vr.plot(kind='bar', ax=axes[0], color=colors, edgecolor='white')
axes[0].set_title('Visual Read Results'); axes[0].set_ylabel('Scans')
axes[0].tick_params(axis='x', rotation=30)
axes[1].pie(vr.values, labels=[f'{k.title()} ({v:,})' for k,v in vr.items()],
            colors=colors, autopct='%1.1f%%', startangle=90)
axes[1].set_title('Positive vs Negative Rate')
plt.tight_layout(); plt.show(); print(vr)"""),
        md("## 9 · SBR Region Correlation Heatmap\n\nHow correlated are measurements across different brain regions? We expect left-right pairs to be highly correlated, and caudate/putamen to be moderately correlated."),
        code("""\
sbr_valid = sbr[sbr['DATSCAN_ANALYZED'] == 'Yes'].copy()
sbr_num = sbr_valid.select_dtypes(include='number').drop(columns=['PATNO','PROTOCOL'], errors='ignore')
sbr_num = sbr_num.dropna(axis=1, thresh=len(sbr_num)//2)
short = {c: c.replace('_REF_CWM','').replace('STRIATUM','STR').replace('CAUDATE','CAU')
              .replace('PUTAMEN','PUT').replace('PRECAUDATE','PRECAU')
              .replace('POSTCAUDATE','POSCAU').replace('ANTPUTAMEN','ANTPUT')
              .replace('POSTPUTAMEN','POSPUT') for c in sbr_num.columns}
corr = sbr_num.rename(columns=short).corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
fig, ax = plt.subplots(figsize=(14, 11))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn', vmin=0, vmax=1,
            ax=ax, linewidths=0.3, annot_kws={'size': 7})
ax.set_title('SBR Region Correlations'); plt.tight_layout(); plt.show()"""),
        md("""## Key Takeaways

- **Putamen SBR is the most sensitive DaTSCAN measure** for early PD — it declines first and most steeply
- **High image quality acceptance rate** ensures data reliability
- **L/R asymmetry** is a PD hallmark — expect asymmetric SBR loss in PD patients
- **Longitudinal decline** is the core signal to track over time in this dataset
- **Visual read** provides a binary clinical judgment; quantitative SBR is continuous and more precise
- Next: compare by cohort (PD vs HC) once you merge in the participants file"""),
    ]
    save_nb(cells, "01_DaTSCAN_SPECT_EDA.ipynb")


# ─────────────────────────────────────────────────────────────────────────────
def make_02():
    cells = [
        md("# 02 · Structural MRI EDA\n> *MRI gives us a detailed picture of brain structure — which sequences were acquired, their quality, and overall grey matter volume.*"),
        md("""## Background: What is Structural MRI?

**MRI (Magnetic Resonance Imaging)** uses magnetic fields and radio waves to produce detailed images of the brain without radiation.

**Key sequences acquired in PPMI:**

| Sequence | Purpose |
|----------|---------|
| **T1-weighted** | High-resolution anatomical brain structure — gold standard for measuring brain volumes and cortical thickness |
| **T2-weighted / FLAIR** | Highlights fluid; good for detecting lesions and white matter abnormalities |
| **DTI (Diffusion Tensor)** | Measures direction of water diffusion along white matter tracts |
| **Resting-state fMRI** | Captures brain activity at rest via blood oxygenation changes |
| **NM-MRI (Neuromelanin)** | Specifically images the Substantia Nigra — the PD-affected region |

**Why MRI in PD?** PD causes measurable structural changes:
- Shrinkage of striatum, hippocampus, cortex
- White matter tract disruption
- Substantia Nigra changes visible on NM-MRI

**What we measure:** Not the raw scan — but derived numbers: volumes, thicknesses, quality metrics."""),
        code(SETUP), code(VISIT_HELPER),
        md("## Load Data Files"),
        code("""\
mri_log  = pd.read_csv(DATA_DIR / 'Magnetic_Resonance_Imaging__MRI__12Nov2026.csv')
mri_meta = pd.read_csv(DATA_DIR / 'Xing_Core_Lab_-_MRI_acquisition_metadata_12Nov2026.csv')
mriqc    = pd.read_csv(DATA_DIR / 'MRIQC_12Nov2026.csv')
gmvol    = pd.read_csv(DATA_DIR / 'Grey_Matter_Volume_12Nov2026.csv')
for name, df in [('MRI Log', mri_log), ('Acquisition Metadata', mri_meta),
                 ('MRIQC', mriqc), ('Grey Matter Volume', gmvol)]:
    print(f'{name:30s}: {len(df):>6,} rows | {df["PATNO"].nunique()} participants')"""),
        md("""## Column Reference

### MRI Log (`Magnetic_Resonance_Imaging__MRI__`)
| Column | Meaning |
|--------|---------|
| `MRICMPLT` | MRI scan completed: 1=Yes, 0=No |
| `MRIWDTI` | DTI sequences included: 1=Yes, 0=No |
| `MRIWRSS` | Resting-state fMRI sequences included: 1=Yes, 0=No |
| `MRIRSLT` | MRI result code |

### Acquisition Metadata (`Xing_Core_Lab_-_MRI_acquisition_metadata`)
| Column | Meaning |
|--------|---------|
| `MRI_SEQ_T1_WEIGHTED` | T1-weighted sequence acquired: Yes/No |
| `MRI_SEQ_T2_WEIGHTED` | T2-weighted / FLAIR sequence acquired: Yes/No |
| `MRI_SEQ_DTI` | DTI sequence acquired: Yes/No |
| `MRI_SEQ_RS` | Resting-state fMRI acquired: Yes/No |
| `MRI_SEQ_NM_MT` | Neuromelanin sequence acquired: Yes/No |
| `MRI_IMAGE_ACCEPTABLE` | Overall image quality: Yes/No |

### MRIQC (Quality Control Metrics)
These are automated image quality measures. They tell you if a scan is worth using for analysis.

| Column | Meaning | Good direction |
|--------|---------|---------------|
| `cjv` | Coefficient of Joint Variation — tissue intensity uniformity | Lower = better |
| `cnr` | Contrast-to-Noise Ratio — how well GM/WM are differentiated | Higher = better |
| `efc` | Entropy Focus Criterion — sharpness, low = less motion | Lower = better |
| `fber` | Foreground-to-Background Energy Ratio | Higher = better |
| `snr_total` | Overall Signal-to-Noise Ratio | Higher = better |
| `snr_gm` | SNR in grey matter | Higher = better |
| `snr_wm` | SNR in white matter | Higher = better |
| `fwhm_avg` | Full-Width Half-Maximum — spatial smoothness in mm | Lower = sharper |
| `icvs_gm` | Grey matter as fraction of intracranial volume | — |
| `icvs_wm` | White matter as fraction of intracranial volume | — |
| `icvs_csf` | CSF as fraction of intracranial volume | — |

### Grey Matter Volume
| Column | Meaning |
|--------|---------|
| `GM_VOLUME` | Total grey matter volume in mm³ |
| `IMAGEID` | Unique identifier for the scan image |
| `MRIDATE` | Date of MRI scan |"""),
        md("## 1 · MRI Scan Completion per Visit"),
        code("""\
completed = mri_log[mri_log['MRICMPLT'] == 1]
visits = ordered_visits(mri_log['EVENT_ID'])
vc = completed.groupby('EVENT_ID')['PATNO'].nunique().reindex(visits).dropna()

fig, ax = plt.subplots(figsize=(13, 5))
bars = ax.bar(range(len(vc)), vc.values, color=sns.color_palette('colorblind')[1])
ax.set_xticks(range(len(vc)))
ax.set_xticklabels([f'{VISIT_LABELS.get(v,v)}\\n({v})' for v in vc.index], rotation=45, ha='right')
ax.set_ylabel('Participants with MRI'); ax.set_title('MRI Scan Completion per Visit')
for b, v in zip(bars, vc.values):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+3, str(int(v)), ha='center', fontsize=9)
plt.tight_layout(); plt.show()"""),
        md("## 2 · Which MRI Sequences Were Acquired?\n\nNot every participant gets every sequence. This shows what fraction had each sequence type."),
        code("""\
seq_cols = {'T1-Weighted': 'MRI_SEQ_T1_WEIGHTED', 'T2/FLAIR': 'MRI_SEQ_T2_WEIGHTED',
            'DTI': 'MRI_SEQ_DTI', 'Resting fMRI': 'MRI_SEQ_RS', 'Neuromelanin': 'MRI_SEQ_NM_MT'}
seq_cols = {k: v for k, v in seq_cols.items() if v in mri_meta.columns}

yes_pct = {k: (mri_meta[v] == 'Yes').mean()*100 for k, v in seq_cols.items()}
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(yes_pct.keys(), yes_pct.values(),
              color=sns.color_palette('colorblind', len(yes_pct)))
ax.set_ylabel('% Scans with Sequence'); ax.set_title('MRI Sequence Availability')
ax.set_ylim(0, 115)
for b, (k, v) in zip(bars, yes_pct.items()):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+1, f'{v:.1f}%', ha='center', fontsize=10)
plt.tight_layout(); plt.show()"""),
        md("## 3 · Image Quality Acceptance Rate"),
        code("""\
if 'MRI_IMAGE_ACCEPTABLE' in mri_meta.columns:
    qc = mri_meta['MRI_IMAGE_ACCEPTABLE'].value_counts()
    colors = ['#2ecc71' if 'Yes' in str(k) else '#e74c3c' for k in qc.index]
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    qc.plot(kind='bar', ax=axes[0], color=colors, edgecolor='white')
    axes[0].set_title('MRI QC Results'); axes[0].set_ylabel('Scans')
    axes[0].tick_params(axis='x', rotation=0)
    axes[1].pie(qc.values, labels=[f'{k} ({v:,})' for k,v in qc.items()],
                colors=colors, autopct='%1.1f%%', startangle=90)
    axes[1].set_title('Pass Rate')
    plt.tight_layout(); plt.show()
    print(f'Acceptance: {qc.get("Yes",0)/len(mri_meta)*100:.1f}%')"""),
        md("## 4 · MRIQC — Automated Image Quality Metrics\n\nMRIQC is a tool that automatically extracts quality metrics from T1-weighted MRI. We plot the four most important summary metrics."),
        code("""\
key_metrics = {'CJV\\n(lower=better)': 'cjv', 'CNR\\n(higher=better)': 'cnr',
               'EFC\\n(lower=better)': 'efc', 'FBER\\n(higher=better)': 'fber'}
key_metrics = {k: v for k, v in key_metrics.items() if v in mriqc.columns}

fig, axes = plt.subplots(1, len(key_metrics), figsize=(14, 5))
for ax, (label, col) in zip(axes, key_metrics.items()):
    data = mriqc[col].dropna()
    data.hist(bins=35, ax=ax, edgecolor='black', alpha=0.8, color=sns.color_palette('colorblind')[2])
    ax.axvline(data.mean(), color='red', linestyle='--', linewidth=1.5)
    ax.set_title(f'{label}\\nMean={data.mean():.3f}')
    ax.set_xlabel('Value'); ax.set_ylabel('Count')
plt.suptitle('MRIQC Key Quality Metrics', fontsize=14, y=1.02)
plt.tight_layout(); plt.show()
print(mriqc[list(key_metrics.values())].describe().round(4))"""),
        md("## 5 · SNR by Tissue Type\n\nSignal-to-Noise Ratio broken down by brain tissue: Grey Matter (GM), White Matter (WM), and CSF."),
        code("""\
snr_cols = {'Grey Matter': 'snr_gm', 'White Matter': 'snr_wm', 'Total': 'snr_total'}
snr_cols = {k: v for k, v in snr_cols.items() if v in mriqc.columns}

if snr_cols:
    fig, ax = plt.subplots(figsize=(10, 5))
    data = [mriqc[v].dropna().values for v in snr_cols.values()]
    bp = ax.boxplot(data, patch_artist=True, boxprops=dict(alpha=0.7))
    ax.set_xticks(range(1, len(snr_cols)+1))
    ax.set_xticklabels(list(snr_cols.keys()))
    colors = sns.color_palette('colorblind', len(snr_cols))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    ax.set_title('Signal-to-Noise Ratio by Tissue Type (MRIQC)')
    ax.set_ylabel('SNR (higher = better)')
    plt.tight_layout(); plt.show()"""),
        md("## 6 · Grey Matter Volume Distribution\n\nTotal grey matter volume in mm³, extracted from T1 MRI. Normal adult GM volume is roughly 500,000–1,000,000 mm³."),
        code("""\
gm = gmvol['GM_VOLUME'].dropna()
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
gm.hist(bins=30, ax=axes[0], edgecolor='black', alpha=0.8, color=sns.color_palette('colorblind')[3])
axes[0].axvline(gm.mean(), color='red', linestyle='--', label=f'Mean: {gm.mean():,.0f}')
axes[0].set_title('Grey Matter Volume Distribution')
axes[0].set_xlabel('GM Volume (mm³)'); axes[0].legend()
# KDE overlay
from scipy.stats import gaussian_kde
kde = gaussian_kde(gm)
x = np.linspace(gm.min(), gm.max(), 200)
axes[1].plot(x, kde(x), color=sns.color_palette('colorblind')[3], linewidth=2)
axes[1].fill_between(x, kde(x), alpha=0.3, color=sns.color_palette('colorblind')[3])
axes[1].set_title('GM Volume — Density Estimate')
axes[1].set_xlabel('GM Volume (mm³)'); axes[1].set_ylabel('Density')
plt.tight_layout(); plt.show()
print(gm.describe().round(0))"""),
        md("## 7 · Grey Matter Volume by Visit"),
        code("""\
if 'EVENT_ID' in gmvol.columns:
    visits = ordered_visits(gmvol['EVENT_ID'])
    present = [v for v in visits if v in gmvol['EVENT_ID'].unique()]
    fig, ax = plt.subplots(figsize=(10, 5))
    data = [gmvol[gmvol['EVENT_ID']==v]['GM_VOLUME'].dropna().values for v in present]
    bp = ax.boxplot(data, patch_artist=True)
    ax.set_xticks(range(1, len(present)+1))
    ax.set_xticklabels([VISIT_LABELS.get(v,v) for v in present])
    colors = sns.color_palette('colorblind', len(present))
    for patch, c in zip(bp['boxes'], colors): patch.set_facecolor(c)
    ax.set_ylabel('Grey Matter Volume (mm³)')
    ax.set_title('GM Volume by Visit')
    ax.tick_params(axis='x', rotation=30)
    plt.tight_layout(); plt.show()"""),
        md("""## Key Takeaways

- **T1-weighted MRI is near-universal** in PPMI; DTI and resting fMRI are available for subsets
- **High QC acceptance rate** means most MRI data is usable
- **MRIQC metrics** let you filter out poor-quality scans before analysis — CJV and CNR are the most useful
- **Grey matter volume** is a global measure of brain atrophy — expect subtle decline in PD over years
- **Next step:** FreeSurfer EDA digs into regional cortical and subcortical structure"""),
    ]
    save_nb(cells, "02_MRI_Structural_EDA.ipynb")


# ─────────────────────────────────────────────────────────────────────────────
def make_03():
    cells = [
        md("# 03 · FreeSurfer Brain Morphometry EDA\n> *Cortical thickness, surface area, and subcortical volumes — derived from T1 MRI using FreeSurfer 7.*"),
        md("""## Background: What is FreeSurfer?

**FreeSurfer** is a software tool that automatically segments a T1 MRI into ~70 cortical regions and ~40 subcortical structures, then measures their size.

**Three types of measurements:**

| Measure | File | Unit | What it tells you |
|---------|------|------|-------------------|
| **Cortical Thickness (CTH)** | FS7_APARC_CTH | mm | How thick the cortex (grey matter outer layer) is in each region |
| **Surface Area (SA)** | FS7_APARC_SA | mm² | How large each cortical region is on the brain surface |
| **Subcortical Volume** | FS7_ASEG_VOL | mm³ | Volume of deep brain structures |

**Why this matters for PD:**
- **Putamen and caudate** (basal ganglia) shrink early in PD
- **Hippocampus and amygdala** shrink in PD with cognitive changes
- **Cortical thinning** appears in frontal/parietal regions in advanced PD
- These changes are subtle but detectable with enough participants

**Column naming convention:**
- `lh_` prefix = left hemisphere
- `rh_` prefix = right hemisphere
- Region names are from the Desikan-Killiany atlas (a standard brain parcellation)"""),
        code(SETUP), code(VISIT_HELPER),
        md("## Load Data Files"),
        code("""\
cth  = pd.read_csv(DATA_DIR / 'FS7_APARC_CTH_12Nov2026.csv')
sa   = pd.read_csv(DATA_DIR / 'FS7_APARC_SA_12Nov2026.csv')
aseg = pd.read_csv(DATA_DIR / 'FS7_ASEG_VOL_12Nov2026.csv')
for name, df in [('Cortical Thickness (CTH)', cth), ('Surface Area (SA)', sa),
                 ('Subcortical Volumes (ASEG)', aseg)]:
    print(f'{name:35s}: {len(df):>5,} rows | {df["PATNO"].nunique()} participants | {df.shape[1]} columns')"""),
        md("""## Column Reference

### Cortical Thickness / Surface Area (APARC)
Columns follow the pattern `{hemisphere}_{region}`:
- `lh_` = left hemisphere, `rh_` = right hemisphere
- `lh_MeanThickness` / `rh_WhiteSurfArea` = whole-hemisphere summary
- 34 cortical regions per hemisphere (see list below)

**Key cortical regions in PD research:**
| Region | Why it matters |
|--------|---------------|
| `precentral` | Motor cortex — controls voluntary movement |
| `postcentral` | Somatosensory cortex |
| `superiorfrontal`, `rostralmiddlefrontal` | Frontal executive function |
| `entorhinal`, `parahippocampal` | Memory/hippocampal circuit |
| `insula` | Autonomic regulation, emotion |
| `transversetemporal` | Primary auditory cortex |

### Subcortical Volumes (ASEG)
**PD-critical structures:**
| Column | Structure | PD Relevance |
|--------|-----------|-------------|
| `Left-Caudate`, `Right-Caudate` | Caudate nucleus | Dopamine target; shrinks in PD |
| `Left-Putamen`, `Right-Putamen` | Putamen | Most-affected basal ganglia in PD |
| `Left-Hippocampus`, `Right-Hippocampus` | Hippocampus | Memory; affected in PD-dementia |
| `Left-Amygdala`, `Right-Amygdala` | Amygdala | Emotion/autonomic; affected in PD |
| `Brain-Stem` | Brainstem | Contains SN; affected early |
| `Left-Thalamus`, `Right-Thalamus` | Thalamus | Relay station |
| `EstimatedTotalIntraCranialVol` | eTIV | Head size — used for normalization |
| `BrainSegVol` | Total brain segment volume | Overall brain size |
| `TotalGrayVol` | Total grey matter | Overall atrophy measure |"""),
        md("## 1 · Mean Cortical Thickness by Region\n\nAverage cortical thickness across all participants for each region. The cortex is typically 2–4 mm thick."),
        code("""\
cth_cols = [c for c in cth.columns if c.startswith('lh_') and c != 'lh_MeanThickness']
rh_cols  = [c.replace('lh_','rh_') for c in cth_cols if c.replace('lh_','rh_') in cth.columns]

lh_means = cth[cth_cols].mean().rename(lambda c: c.replace('lh_',''))
rh_means = cth[rh_cols].mean().rename(lambda c: c.replace('rh_',''))
both = pd.DataFrame({'Left': lh_means, 'Right': rh_means}).sort_values('Left')

fig, ax = plt.subplots(figsize=(8, 14))
y = range(len(both))
ax.barh([i-0.2 for i in y], both['Left'], height=0.4,
        color=sns.color_palette('colorblind')[0], label='Left hemisphere')
ax.barh([i+0.2 for i in y], both['Right'], height=0.4,
        color=sns.color_palette('colorblind')[1], label='Right hemisphere')
ax.set_yticks(list(y)); ax.set_yticklabels(both.index, fontsize=8)
ax.set_xlabel('Mean Cortical Thickness (mm)'); ax.set_title('Mean CTH by Region — All Participants')
ax.legend(); ax.axvline(2.5, color='grey', linestyle=':', alpha=0.5)
plt.tight_layout(); plt.show()"""),
        md("## 2 · Left vs Right Hemisphere Thickness Asymmetry\n\nIs the brain symmetric? Each dot is one participant. Points off the diagonal indicate hemispheric asymmetry."),
        code("""\
if 'lh_MeanThickness' in cth.columns and 'rh_MeanThickness' in cth.columns:
    sub = cth[['lh_MeanThickness','rh_MeanThickness']].dropna()
    mn = sub.min().min()*0.98; mx = sub.max().max()*1.02
    fig, ax = plt.subplots(figsize=(6,6))
    ax.scatter(sub['lh_MeanThickness'], sub['rh_MeanThickness'],
               alpha=0.3, s=15, color=sns.color_palette('colorblind')[0])
    ax.plot([mn,mx],[mn,mx],'r--', label='Perfect symmetry')
    ax.set_xlabel('Left Mean Thickness (mm)'); ax.set_ylabel('Right Mean Thickness (mm)')
    ax.set_title('Bilateral Cortical Thickness Symmetry'); ax.legend()
    plt.tight_layout(); plt.show()
    asym = (sub['lh_MeanThickness'] - sub['rh_MeanThickness'])
    print(f'Mean L-R asymmetry: {asym.mean():.4f} mm | Std: {asym.std():.4f} mm')"""),
        md("## 3 · Subcortical Volumes — PD-Relevant Structures\n\nThese deep brain structures are affected in PD. Volumes are in mm³."),
        code("""\
pd_structs = ['Left-Putamen','Right-Putamen','Left-Caudate','Right-Caudate',
              'Left-Hippocampus','Right-Hippocampus','Left-Amygdala','Right-Amygdala']
pd_structs = [c for c in pd_structs if c in aseg.columns]

if pd_structs:
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    axes = axes.flatten()
    for ax, col in zip(axes, pd_structs):
        data = aseg[col].dropna()
        data.hist(bins=25, ax=ax, color=sns.color_palette('colorblind')[4],
                  edgecolor='black', alpha=0.8)
        ax.axvline(data.mean(), color='red', linestyle='--', linewidth=1.2)
        ax.set_title(f'{col}\\n({data.mean():,.0f} mm³)', fontsize=9)
        ax.set_xlabel('Volume (mm³)', fontsize=8); ax.set_ylabel('', fontsize=8)
    plt.suptitle('PD-Relevant Subcortical Structure Volumes', fontsize=14)
    plt.tight_layout(); plt.show()
    print(aseg[pd_structs].describe().round(0).T[['mean','std','min','max']])"""),
        md("## 4 · eTIV-Normalised Subcortical Volumes\n\nLarger heads have larger brains. We normalise volumes by eTIV (Estimated Total Intracranial Volume) to compare fairly across people."),
        code("""\
etiv_col = 'EstimatedTotalIntraCranialVol'
if etiv_col in aseg.columns and pd_structs:
    norm = aseg[pd_structs].div(aseg[etiv_col], axis=0) * 1000  # per 1000 mm³ eTIV
    means = norm.mean().sort_values()
    fig, ax = plt.subplots(figsize=(10, 5))
    means.plot(kind='barh', ax=ax, color=sns.color_palette('colorblind', len(means)))
    ax.set_xlabel('Volume / eTIV × 1000')
    ax.set_title('eTIV-Normalised Subcortical Volumes')
    plt.tight_layout(); plt.show()"""),
        md("## 5 · Global Brain Measures"),
        code("""\
global_cols = ['BrainSegVol','TotalGrayVol','CortexVol','EstimatedTotalIntraCranialVol']
global_cols = [c for c in global_cols if c in aseg.columns]

fig, axes = plt.subplots(1, len(global_cols), figsize=(14, 4))
for ax, col in zip(axes, global_cols):
    data = aseg[col].dropna()
    data.hist(bins=25, ax=ax, color=sns.color_palette('colorblind')[5],
              edgecolor='black', alpha=0.8)
    ax.axvline(data.mean(), color='red', linestyle='--', linewidth=1.2)
    ax.set_title(col.replace('Estimated','Est.'), fontsize=9)
    ax.set_xlabel('Volume (mm³)'); ax.set_ylabel('Count')
plt.suptitle('Global Brain Volume Measures', fontsize=13)
plt.tight_layout(); plt.show()"""),
        md("## 6 · Subcortical Volume Correlations\n\nAre the two hemispheres correlated? Are caudate and putamen correlated with each other?"),
        code("""\
if len(pd_structs) >= 4:
    short = {c: c.replace('Left-','L-').replace('Right-','R-').replace('Hippocampus','Hipp') for c in pd_structs}
    corr = aseg[pd_structs].rename(columns=short).corr()
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlGn', vmin=0, vmax=1,
                ax=ax, linewidths=0.5)
    ax.set_title('Subcortical Volume Correlations')
    plt.tight_layout(); plt.show()"""),
        md("""## Key Takeaways

- **Putamen and caudate** are the most PD-relevant subcortical structures — atrophy here is a key PD biomarker
- **High L/R symmetry** at the group level; individual asymmetry may be clinically meaningful
- **eTIV normalisation** is essential when comparing volumes across people of different head sizes
- **~1,700 participants** have FreeSurfer data — a large enough sample for group comparisons
- These morphometric measures complement DaTSCAN: anatomy vs. function"""),
    ]
    save_nb(cells, "03_FreeSurfer_EDA.ipynb")


# ─────────────────────────────────────────────────────────────────────────────
def make_04():
    cells = [
        md("# 04 · DTI — Diffusion Tensor Imaging EDA\n> *DTI measures water diffusion in white matter tracts, targeting the Substantia Nigra — the brain region most affected in PD.*"),
        md("""## Background: What is DTI?

Water molecules in the brain don't move randomly — in white matter tracts (bundles of nerve fibres), water diffuses **preferentially along** the fibre direction. **Diffusion Tensor Imaging (DTI)** measures this directed diffusion.

**Key DTI metrics:**

| Metric | Full Name | Meaning | In PD/damage |
|--------|-----------|---------|-------------|
| **FA** | Fractional Anisotropy | How *directional* diffusion is (0=random, 1=perfectly aligned) | **Decreases** when fibres are damaged or lost |
| **E1** | First Eigenvalue (axial diffusivity) | Diffusion *along* the fibre axis | Increases when axons degenerate |
| **E2** | Second Eigenvalue | Diffusion perpendicular to fibres | Increases when myelin is damaged |
| **E3** | Third Eigenvalue | Diffusion perpendicular to fibres | Increases when myelin is damaged |

**FA is the most commonly reported metric** — a high FA indicates intact, well-organised white matter.

---

## What is the Substantia Nigra?

The **Substantia Nigra** (SN) is a small but critical region in the midbrain. It contains the **dopamine-producing neurons** that degenerate in PD.

In this dataset, DTI measurements are taken in 6 ROIs (Regions of Interest) within the SN:

| Column | Location |
|--------|---------|
| `ROI1` | Left Rostral SN (front part) |
| `ROI2` | Left Middle SN |
| `ROI3` | Left Caudal SN (back part) |
| `ROI4` | Right Rostral SN |
| `ROI5` | Right Middle SN |
| `ROI6` | Right Caudal SN |
| `REF1` | Left reference white matter (healthy tract for comparison) |
| `REF2` | Right reference white matter |"""),
        code(SETUP), code(VISIT_HELPER),
        md("## Load Data File"),
        code("""\
dti = pd.read_csv(DATA_DIR / 'DTI_Regions_of_Interest_12Nov2026.csv')
print(f'Shape: {dti.shape}')
print(f'Participants: {dti["PATNO"].nunique()}')
print(f'Measures: {dti["Measure"].unique()}')
print(f'Tissues: {dti["Tissue"].unique()}')
print(f'Rows per measure: {dti.groupby("Measure").size().to_dict()}')
dti.head(8)"""),
        md("""## Column Reference

| Column | Meaning |
|--------|---------|
| `PATNO` | Participant ID |
| `PAG_NAME` | Form name (always "DTIROI") |
| `INFODT` | Date of data entry (MM/YYYY) |
| `Measure` | DTI metric: FA, E1, E2, or E3 |
| `Tissue` | Brain region (SN = Substantia Nigra) |
| `ROI1` | Left Rostral SN |
| `ROI2` | Left Middle SN |
| `ROI3` | Left Caudal SN |
| `ROI4` | Right Rostral SN |
| `ROI5` | Right Middle SN |
| `ROI6` | Right Caudal SN |
| `REF1` | Left reference white matter |
| `REF2` | Right reference white matter |
| `RUNDATE` | Date the analysis was run |

**Value ranges:**
- FA: 0–1 (typical SN values: 0.2–0.5)
- E1/E2/E3: very small numbers ~0.0005–0.002 (units: mm²/s)"""),
        md("## 1 · FA Distribution Across All 6 SN ROIs\n\nFA tells us how intact the white matter is. Lower FA in the SN is associated with dopamine neuron loss."),
        code("""\
fa = dti[dti['Measure'] == 'FA'].copy()
roi_cols = [c for c in ['ROI1','ROI2','ROI3','ROI4','ROI5','ROI6'] if c in fa.columns]
roi_labels = {
    'ROI1': 'L Rostral', 'ROI2': 'L Middle', 'ROI3': 'L Caudal',
    'ROI4': 'R Rostral', 'ROI5': 'R Middle', 'ROI6': 'R Caudal'
}
fa_melt = fa[roi_cols].rename(columns=roi_labels).melt(var_name='ROI', value_name='FA').dropna()

fig, ax = plt.subplots(figsize=(12, 6))
sns.violinplot(data=fa_melt, x='ROI', y='FA', palette='colorblind', ax=ax, inner='box', cut=0)
ax.set_title('Fractional Anisotropy (FA) in Substantia Nigra — 6 ROIs')
ax.set_ylabel('FA (0=random diffusion, 1=perfectly aligned)')
ax.set_xlabel('Region of Interest (L=Left, R=Right)')
plt.tight_layout(); plt.show()
print(fa_melt.groupby('ROI')['FA'].describe().round(4))"""),
        md("## 2 · Left vs Right SN Comparison\n\nAre the two sides of the SN symmetric? PD often starts asymmetrically."),
        code("""\
fa = dti[dti['Measure'] == 'FA'].copy()
sides = [('ROI2','ROI5','Middle SN')]  # middle is most reliable
sides = [(l,r,n) for l,r,n in sides if l in fa.columns and r in fa.columns]

for lcol, rcol, name in sides:
    sub = fa[[lcol, rcol]].dropna()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    mn = sub.min().min()*0.95; mx = sub.max().max()*1.05
    axes[0].scatter(sub[lcol], sub[rcol], alpha=0.4, s=20,
                    color=sns.color_palette('colorblind')[0])
    axes[0].plot([mn,mx],[mn,mx],'r--', label='Symmetry line')
    axes[0].set_xlabel(f'Left {name} FA'); axes[0].set_ylabel(f'Right {name} FA')
    axes[0].set_title(f'{name}: L vs R FA'); axes[0].legend()

    diff = sub[lcol] - sub[rcol]
    diff.hist(bins=25, ax=axes[1], color=sns.color_palette('colorblind')[1],
              edgecolor='black', alpha=0.8)
    axes[1].axvline(0, color='red', linestyle='--')
    axes[1].set_title('L - R FA Asymmetry')
    axes[1].set_xlabel('Left minus Right FA')
    plt.tight_layout(); plt.show()
    print(f'Mean L-R diff: {diff.mean():.4f} | Std: {diff.std():.4f}')"""),
        md("## 3 · Rostral vs Middle vs Caudal SN\n\nThe SN has distinct sub-regions. PD pathology may preferentially affect certain parts."),
        code("""\
fa = dti[dti['Measure'] == 'FA'].copy()
groups = {
    'L Rostral': 'ROI1', 'L Middle': 'ROI2', 'L Caudal': 'ROI3',
    'R Rostral': 'ROI4', 'R Middle': 'ROI5', 'R Caudal': 'ROI6'
}
groups = {k: v for k, v in groups.items() if v in fa.columns}
plot_data = pd.concat([fa[v].rename(k) for k, v in groups.items()], axis=1)
melted = plot_data.melt(var_name='ROI', value_name='FA').dropna()

fig, ax = plt.subplots(figsize=(12, 5))
sns.boxplot(data=melted, x='ROI', y='FA', palette='colorblind', ax=ax)
ax.set_title('FA by SN Sub-Region and Hemisphere')
ax.set_ylabel('FA'); ax.set_xlabel('')
plt.tight_layout(); plt.show()"""),
        md("## 4 · All 4 DTI Measures Side by Side\n\nComparing FA, E1, E2, E3 across the middle SN (most common reference point)."),
        code("""\
measures = ['FA', 'E1', 'E2', 'E3']
middle_col = 'ROI2'  # Left middle SN

fig, axes = plt.subplots(1, 4, figsize=(16, 5))
for ax, measure in zip(axes, measures):
    sub = dti[dti['Measure'] == measure][middle_col].dropna()
    if len(sub) > 0:
        sub.hist(bins=25, ax=ax, color=sns.color_palette('colorblind')[measures.index(measure)],
                 edgecolor='black', alpha=0.8)
        ax.axvline(sub.mean(), color='red', linestyle='--', linewidth=1.5)
        ax.set_title(f'{measure}\\nMean={sub.mean():.5f}')
        ax.set_xlabel('Value')
        if measure == 'FA':
            ax.set_xlabel('FA (0–1 scale)')
        else:
            ax.set_xlabel('Diffusivity (mm²/s)')
plt.suptitle('DTI Measures — Left Middle Substantia Nigra', fontsize=13)
plt.tight_layout(); plt.show()"""),
        md("## 5 · ROI vs Reference White Matter\n\nWe compare SN FA against the reference white matter tract. Healthy white matter (REF) should have higher FA than SN."),
        code("""\
fa = dti[dti['Measure'] == 'FA'].copy()
if 'ROI2' in fa.columns and 'REF1' in fa.columns:
    sub = fa[['ROI2','REF1']].dropna()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(sub['REF1'], sub['ROI2'], alpha=0.3, s=15,
               color=sns.color_palette('colorblind')[0])
    mn = sub.min().min()*0.9; mx = sub.max().max()*1.05
    ax.plot([mn,mx],[mn,mx],'r--', label='Equal FA')
    ax.set_xlabel('Reference White Matter FA'); ax.set_ylabel('Left Middle SN FA')
    ax.set_title('SN vs Reference White Matter — FA')
    ax.legend(); plt.tight_layout(); plt.show()
    print(f'REF1 mean FA: {sub["REF1"].mean():.4f}')
    print(f'ROI2 (L Mid SN) mean FA: {sub["ROI2"].mean():.4f}')
    print(f'SN is {(sub["ROI2"].mean()/sub["REF1"].mean()*100):.1f}% of reference WM FA')"""),
        md("""## Key Takeaways

- **FA in the Substantia Nigra is the key measure** — lower FA indicates white matter disruption associated with dopamine neuron loss
- **SN FA is lower than reference white matter** — expected, as the SN has complex architecture
- **L/R asymmetry in SN FA** may correlate with the side that develops symptoms first in PD
- **Small sample size (~300 participants)** compared to DaTSCAN — DTI was not acquired for everyone
- **E1 (axial diffusivity) increases** when axons degenerate; **E2/E3 (radial diffusivity) increases** when myelin is lost"""),
    ]
    save_nb(cells, "04_DTI_EDA.ipynb")


# ─────────────────────────────────────────────────────────────────────────────
def make_05():
    cells = [
        md("# 05 · PET Imaging — AV-133 (VMAT2) EDA\n> *AV-133 is a PET tracer that labels dopamine storage vesicles — complementary to DaTSCAN but measuring a different aspect of the dopamine system.*"),
        md("""## Background: What is AV-133 PET?

**AV-133** (also called Florbetapir or ¹⁸F-Fluorodeoxyglucose... actually AV-133 = ¹⁸F-AV-133 / DTBZ analogue) is a radioactive tracer that binds to **VMAT2** — Vesicular Monoamine Transporter Type 2.

**VMAT2** is a protein that packages dopamine into storage vesicles inside the neuron.

**Comparison with DaTSCAN:**

| Property | DaTSCAN (DAT) | AV-133 (VMAT2) |
|----------|--------------|-----------------|
| What it labels | Dopamine **transporter** on cell surface | Dopamine **storage vesicles** inside cell |
| Sensitivity to PD | High | High |
| Affected by drugs | Yes (e.g., stimulants block DAT) | Less so |
| Available in PPMI | 10,000+ scans | ~257 scans |

**Key measurement — Striatal Binding Ratio (SBR):**
Same concept as DaTSCAN: (region uptake) / (reference region) − 1.

Regions measured:
- `PET_RCAUD_S` / `PET_LCAUD_S` = Right/Left Caudate SBR
- `PET_RPUTANT_S` / `PET_LPUTANT_S` = Right/Left Anterior Putamen SBR
- `PET_RPUTPOST_S` / `PET_LPUTPOST_S` = Right/Left Posterior Putamen SBR"""),
        code(SETUP), code(VISIT_HELPER),
        md("## Load Data Files"),
        code("""\
acq_meta = pd.read_csv(DATA_DIR / 'PET_Acquisition_Metadata_12Nov2026.csv')
sbr_pet  = pd.read_csv(DATA_DIR / 'PET_SBR_Analysis_12Nov2026.csv')
early    = pd.read_csv(DATA_DIR / 'Early_Imaging_Substudy_AV-133_PET_Imaging_12Nov2026.csv')
prodromal= pd.read_csv(DATA_DIR / 'AV-133_Prodromal_Imaging_Substudy_AV-133_PET_Imaging_12Nov2026.csv')
dual_pd  = pd.read_csv(DATA_DIR / 'Dual_PET_AV-133_in_PD_Imaging_Substudy_AV-133_PET_Imaging_12Nov2026.csv')
dual_pi  = pd.read_csv(DATA_DIR / 'Dual_PET_AV133_in_PI_Substudy_AV-133_NX_PET_Imaging_12Nov2026.csv')
for name, df in [('Acquisition Metadata', acq_meta), ('SBR Analysis', sbr_pet),
                 ('Early Imaging Substudy', early), ('Prodromal Substudy', prodromal),
                 ('Dual PET PD', dual_pd), ('Dual PET PI', dual_pi)]:
    print(f'{name:30s}: {len(df):>4} rows | {df["PATNO"].nunique()} participants')"""),
        md("""## Column Reference

### Acquisition Metadata
| Column | Meaning |
|--------|---------|
| `PET_LIGAND` | Tracer: 18F-AV-133 |
| `PET_WEIGHT` | Participant body weight (for dose calculation) |
| `PET_TOTAL_DOSE_CALC` | Administered radioactive dose |
| `PET_PASS_QC` | Did scan pass QC? Yes/No |
| `PET_IMAGE_ACCEPTABLE` | Was image usable? Yes/No |
| `PET_SCANNER` | Scanner model used |
| `PET_SCAN_QUALITY_RATING` | Quality rating: 1=best, 2=acceptable, 3=poor |

### SBR Analysis
| Column | Meaning |
|--------|---------|
| `PET_RCAUD_S` | Right Caudate SBR (striatal binding ratio) |
| `PET_LCAUD_S` | Left Caudate SBR |
| `PET_RPUTANT_S` | Right Anterior Putamen SBR |
| `PET_LPUTANT_S` | Left Anterior Putamen SBR |
| `PET_RPUTPOST_S` | Right Posterior Putamen SBR |
| `PET_LPUTPOST_S` | Left Posterior Putamen SBR |
| `PET_ANALYZED` | Was scan analyzable? |

### Clinical Substudy Files
| Column | Meaning |
|--------|---------|
| `SYSSUPBF` / `SYSSUPAF` | Systolic blood pressure before/after injection (mmHg) |
| `DIASUPBF` / `DIASUPAF` | Diastolic blood pressure before/after injection |
| `HRSUPBF` / `HRSUPAF` | Heart rate before/after injection (bpm) |
| `PETCMPLT` | PET scan completed: 1=Yes |"""),
        md("## 1 · Scanner Distribution"),
        code("""\
if 'PET_SCANNER' in acq_meta.columns:
    sc = acq_meta['PET_SCANNER'].value_counts()
    fig, ax = plt.subplots(figsize=(9, 5))
    sc.plot(kind='bar', ax=ax, color=sns.color_palette('colorblind', len(sc)), edgecolor='white')
    ax.set_title('PET Scanner Types Used'); ax.set_ylabel('Number of Scans')
    ax.tick_params(axis='x', rotation=30)
    for i, v in enumerate(sc.values):
        ax.text(i, v+0.3, str(v), ha='center', fontsize=10)
    plt.tight_layout(); plt.show()"""),
        md("## 2 · QC Acceptance Rate"),
        code("""\
qc_col = 'PET_IMAGE_ACCEPTABLE' if 'PET_IMAGE_ACCEPTABLE' in acq_meta.columns else 'PET_PASS_QC'
if qc_col in acq_meta.columns:
    qc = acq_meta[qc_col].value_counts()
    colors = ['#2ecc71' if 'Yes' in str(k) or k == True else '#e74c3c' for k in qc.index]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    qc.plot(kind='bar', ax=axes[0], color=colors, edgecolor='white')
    axes[0].set_title('PET QC Results'); axes[0].tick_params(axis='x', rotation=0)
    axes[1].pie(qc.values, labels=[f'{k} ({v})' for k,v in qc.items()],
                colors=colors, autopct='%1.1f%%', startangle=90)
    axes[1].set_title('Pass Rate')
    plt.tight_layout(); plt.show()"""),
        md("## 3 · Scan Quality Ratings\n\nQuality rated 1–3: 1=excellent, 2=acceptable, 3=poor."),
        code("""\
if 'PET_SCAN_QUALITY_RATING' in acq_meta.columns:
    qr = acq_meta['PET_SCAN_QUALITY_RATING'].value_counts().sort_index()
    labels = {1: 'Excellent (1)', 2: 'Acceptable (2)', 3: 'Poor (3)'}
    colors = ['#2ecc71','#f39c12','#e74c3c']
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([labels.get(k, str(k)) for k in qr.index], qr.values,
           color=colors[:len(qr)], edgecolor='white')
    ax.set_title('PET Scan Quality Ratings'); ax.set_ylabel('Count')
    plt.tight_layout(); plt.show()"""),
        md("## 4 · AV-133 SBR Distributions\n\nStriatal binding ratios by region. Compare to DaTSCAN SBR values — same brain regions, different biological target."),
        code("""\
sbr_valid = sbr_pet[sbr_pet.get('PET_ANALYZED', pd.Series(['Yes']*len(sbr_pet))) == 'Yes'].copy() \
            if 'PET_ANALYZED' in sbr_pet.columns else sbr_pet.copy()
sbr_region_cols = {c: c.replace('PET_','').replace('_S','').replace('RPUT','R Put').replace('LPUT','L Put')
                      .replace('RCAUD','R Caud').replace('LCAUD','L Caud')
                      .replace('ANT',' Ant').replace('POST',' Post')
                   for c in sbr_valid.columns if c.startswith('PET_') and
                   sbr_valid[c].dtype in [np.float64, float]}
sbr_region_cols = {k: v for k, v in sbr_region_cols.items() if sbr_valid[k].dropna().shape[0] > 5}

if sbr_region_cols:
    melt = sbr_valid[list(sbr_region_cols.keys())].rename(columns=sbr_region_cols).melt(
        var_name='Region', value_name='SBR').dropna()
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.violinplot(data=melt, x='Region', y='SBR', palette='colorblind', ax=ax,
                   inner='box', cut=0)
    ax.set_title('AV-133 PET — SBR by Brain Region')
    ax.set_ylabel('Striatal Binding Ratio'); ax.tick_params(axis='x', rotation=30)
    plt.tight_layout(); plt.show()
    print(melt.groupby('Region')['SBR'].describe().round(3))"""),
        md("## 5 · Substudy Participant Counts"),
        code("""\
substudies = {
    'Early Imaging': early, 'Prodromal': prodromal,
    'Dual PET (PD)': dual_pd, 'Dual PET (PI)': dual_pi
}
counts = {name: df['PATNO'].nunique() for name, df in substudies.items()}
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(counts.keys(), counts.values(), color=sns.color_palette('colorblind', len(counts)))
ax.set_title('AV-133 Substudy Participant Counts'); ax.set_ylabel('Unique Participants')
for i, (k, v) in enumerate(counts.items()):
    ax.text(i, v+0.3, str(v), ha='center', fontsize=11)
plt.tight_layout(); plt.show()"""),
        md("## 6 · Pre vs Post-Injection Vital Signs\n\nBlood pressure and heart rate are recorded before and after the radiotracer injection as a safety check."),
        code("""\
vital_pairs = [('SYSSUPBF','SYSSUPAF','Systolic BP (mmHg)'),
               ('DIASUPBF','DIASUPAF','Diastolic BP (mmHg)'),
               ('HRSUPBF','HRSUPAF','Heart Rate (bpm)')]
vital_pairs = [(a,b,n) for a,b,n in vital_pairs if a in early.columns and b in early.columns]

if vital_pairs:
    fig, axes = plt.subplots(1, len(vital_pairs), figsize=(5*len(vital_pairs), 5))
    if len(vital_pairs) == 1: axes = [axes]
    for ax, (pre, post, name) in zip(axes, vital_pairs):
        sub = early[[pre, post]].dropna()
        ax.scatter(sub[pre], sub[post], alpha=0.5, s=20,
                   color=sns.color_palette('colorblind')[0])
        mn = min(sub.min()); mx = max(sub.max())
        ax.plot([mn,mx],[mn,mx],'r--', alpha=0.7, label='No change')
        ax.set_xlabel(f'Pre-injection {name}'); ax.set_ylabel(f'Post-injection {name}')
        ax.set_title(name); ax.legend(fontsize=8)
    plt.suptitle('Vital Signs: Before vs After Injection', fontsize=13)
    plt.tight_layout(); plt.show()"""),
        md("""## Key Takeaways

- **AV-133 measures VMAT2** (dopamine vesicular transporter) — complementary to DaTSCAN's DAT measure
- **Smaller dataset (~257 scans)** than DaTSCAN; collected in specific substudies
- **High image quality** expected given the careful QC process
- **Anterior putamen SBR** is most sensitive — consistent with DaTSCAN findings
- **Vital signs** show only minor changes pre/post injection — tracer is well-tolerated"""),
    ]
    save_nb(cells, "05_PET_AV133_EDA.ipynb")


# ─────────────────────────────────────────────────────────────────────────────
def make_06():
    cells = [
        md("# 06 · Tau PET Imaging EDA\n> *Tau is a protein that forms toxic aggregates in brain diseases. Tau PET is an emerging biomarker being evaluated in PD/Parkinsonism.*"),
        md("""## Background: What is Tau PET?

**Tau** is a protein that normally stabilises microtubules inside neurons. In several neurodegenerative diseases, tau becomes abnormally phosphorylated, detaches from microtubules, and forms **neurofibrillary tangles** that damage and kill neurons.

**Tau pathology in PD:** Unlike Alzheimer's disease where tau is a primary driver, in PD tau pathology is **secondary** — but it appears to accelerate disease progression and cognitive decline in a subset of patients.

**Two tracers used in PPMI:**

| Tracer | Full Name | Notes |
|--------|----------|-------|
| **PI-2620** | ¹⁸F-PI-2620 | Also called florzolotau; selective for tau tangles |
| **MK-6240** | ¹⁸F-MK-6240 | High affinity for tau, low off-target binding |

**Measurement — SUVR (Standardised Uptake Value Ratio):**
> SUVR = (tracer uptake in target region) / (tracer uptake in reference region)

Reference region: **cerebellum** (assumed tau-free in most PD patients).
An SUVR > 1.0 indicates elevated tau deposition relative to the reference.

**Braak Staging Regions:**
Tau spreads in a predictable pattern through the brain (Braak stages 1–6). PET regions aligned to these stages track where tau has spread.

> ⚠️ **Small sample size warning:** Only ~23 participants have tau PET data. This is a pilot substudy — statistical interpretation requires caution."""),
        code(SETUP), code(VISIT_HELPER),
        md("## Load Data Files"),
        code("""\
tau_meta = pd.read_csv(DATA_DIR / 'TAU_PET_Metadata_12Nov2026.csv')
tau_anal = pd.read_csv(DATA_DIR / 'TAU_PET_Analysis_12Nov2026.csv')
mk6240   = pd.read_csv(DATA_DIR / 'Tau_Substudy_MK-6240_PET_Imaging_12Nov2026.csv')
pi2620   = pd.read_csv(DATA_DIR / 'NX_PI-2620_Tau_Imaging_Substudy_Imaging_12Nov2026.csv')
for name, df in [('TAU PET Metadata', tau_meta), ('TAU PET Analysis', tau_anal),
                 ('MK-6240 Substudy', mk6240), ('PI-2620 Substudy (NX)', pi2620)]:
    print(f'{name:30s}: {len(df):>4} rows | {df["PATNO"].nunique()} participants | {df.shape[1]} cols')"""),
        md("""## Column Reference

### TAU PET Analysis
| Column | Meaning |
|--------|---------|
| `PET_LIGAND` | Tracer name (PI-2620 or MK-6240) |
| `TAU_SUVR_CBM` | SUVR in cerebellum (reference region — should be ~1.0) |
| Braak region columns | SUVR in regions corresponding to Braak tau staging |

### SUVR Interpretation
| SUVR Range | Interpretation |
|-----------|---------------|
| ~1.0 | Background — tau level similar to reference |
| 1.1–1.3 | Mild elevation |
| > 1.3 | Moderate-to-high tau deposition |

### Key Column Patterns
Columns ending in `_SUVR` or starting with `TAU_SUVR_` or `BRAAK_` represent regional SUVR values."""),
        md("## 1 · Small Sample Size Caveat"),
        code("""\
print("=" * 60)
print("IMPORTANT: Small Sample Size Notice")
print("=" * 60)
print(f"TAU PET Analysis participants: {tau_anal['PATNO'].nunique()}")
print(f"MK-6240 substudy participants: {mk6240['PATNO'].nunique()}")
print(f"PI-2620 substudy participants: {pi2620['PATNO'].nunique()}")
print()
print("Tau PET in PPMI is a PILOT substudy.")
print("N ~23 is insufficient for robust statistical inference.")
print("Use these results for exploration and hypothesis generation only.")"""),
        md("## 2 · Tracer Distribution"),
        code("""\
if 'PET_LIGAND' in tau_meta.columns:
    lig = tau_meta['PET_LIGAND'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 4))
    lig.plot(kind='bar', ax=ax, color=sns.color_palette('colorblind', len(lig)))
    ax.set_title('Tau PET Tracers Used'); ax.set_ylabel('Scans')
    ax.tick_params(axis='x', rotation=30)
    plt.tight_layout(); plt.show(); print(lig)"""),
        md("## 3 · SUVR Distributions by Region\n\nAll SUVR values should hover near 1.0 in regions without tau; values > 1.1 suggest tau accumulation."),
        code("""\
suvr_cols = [c for c in tau_anal.columns if 'SUVR' in c.upper() or 'BRAAK' in c.upper()]
suvr_cols = [c for c in suvr_cols if tau_anal[c].dtype in [np.float64, float]]

if suvr_cols:
    fig, ax = plt.subplots(figsize=(12, 5))
    data = [tau_anal[c].dropna().values for c in suvr_cols]
    bp = ax.boxplot(data, patch_artist=True)
    ax.set_xticks(range(1, len(suvr_cols)+1))
    ax.set_xticklabels([c.replace('TAU_SUVR_','').replace('_SUVR','') for c in suvr_cols], rotation=30, ha='right')
    colors = sns.color_palette('colorblind', len(suvr_cols))
    for patch, c in zip(bp['boxes'], colors): patch.set_facecolor(c)
    ax.axhline(1.0, color='red', linestyle='--', alpha=0.7, label='SUVR = 1.0 (reference level)')
    ax.set_title('Tau SUVR by Brain Region (N~23)')
    ax.set_ylabel('SUVR'); ax.legend()
    ax.tick_params(axis='x', rotation=30)
    plt.tight_layout(); plt.show()
    print(tau_anal[suvr_cols].describe().round(3))"""),
        md("## 4 · Individual Participant Profiles\n\nWith N=23, we can plot every individual — something impossible with larger datasets."),
        code("""\
if suvr_cols:
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(suvr_cols))
    colors_p = sns.color_palette('tab20', n_colors=min(len(tau_anal), 20))
    for i, (_, row) in enumerate(tau_anal[suvr_cols].dropna().iterrows()):
        ax.plot(x, row.values, alpha=0.4, linewidth=1, color=colors_p[i % len(colors_p)])
    mean_vals = tau_anal[suvr_cols].mean()
    ax.plot(x, mean_vals.values, 'k-', linewidth=3, label='Group mean')
    ax.axhline(1.0, color='red', linestyle='--', alpha=0.5)
    ax.set_xticks(list(x))
    ax.set_xticklabels([c.replace('TAU_SUVR_','').replace('_SUVR','') for c in suvr_cols],
                       rotation=30, ha='right')
    ax.set_ylabel('SUVR'); ax.set_title('Individual Tau SUVR Profiles (each line = one participant)')
    ax.legend(); plt.tight_layout(); plt.show()"""),
        md("## 5 · Acquisition Metadata Summary"),
        code("""\
print("TAU PET Acquisition Metadata Summary:")
print(f"Total scans: {len(tau_meta)}")
print(f"Participants: {tau_meta['PATNO'].nunique()}")
print()
num_cols = tau_meta.select_dtypes(include='number').columns.difference(['PATNO'])
if len(num_cols) > 0:
    print(tau_meta[num_cols].describe().round(2))
cat_cols = tau_meta.select_dtypes(include='object').columns.difference(['EVENT_ID','INFODT','ORIG_ENTRY','LAST_UPDATE'])
for col in cat_cols[:5]:
    vc = tau_meta[col].value_counts()
    if 1 < len(vc) <= 10:
        print(f"\\n{col}:"); print(vc.to_string())"""),
        md("""## Key Takeaways

- **Very small pilot dataset (N~23)** — treat findings as hypothesis-generating only
- **Two tracers used:** PI-2620 and MK-6240 — both target tau tangles but differ in pharmacokinetics
- **SUVR values cluster near 1.0** — expected in a PD cohort (tau is secondary; primary in Alzheimer's)
- **Individual profiles** are visible at this small N — useful for case-by-case exploration
- **Tau PET is a growing area** — expect more data as the PPMI-3 protocol expands substudy enrolment"""),
    ]
    save_nb(cells, "06_PET_Tau_EDA.ipynb")


# ─────────────────────────────────────────────────────────────────────────────
def make_07():
    cells = [
        md("# 07 · SV2A PET Imaging EDA\n> *SV2A PET measures synaptic density — how many synapses survive in PD. A novel marker of neurodegeneration.*"),
        md("""## Background: What is SV2A PET?

**SV2A (Synaptic Vesicle Glycoprotein 2A)** is a protein present on nearly all synaptic vesicles (the packages that store neurotransmitters at synapses).

**Why measure it?** The number of synapses is closely correlated with neuronal health. As neurons die, their synapses disappear — SV2A provides a **direct measure of synaptic density**.

**Tracer used:** ¹⁸F-SynVesT-1 (also called [¹⁸F]UCB-H or ¹⁸F-SV2A ligand)

**Measurement — SUVR:**
- SV2A_SUVR_CS: SUVR normalised to **centrum semiovale** (white matter reference — no synapses)
- Other columns: SUVR for different brain regions

**Why it matters for PD:**
- Striatal synapse loss parallels dopamine neuron loss
- Cortical synapse loss may explain cognitive symptoms
- SV2A could serve as a marker of disease spread and severity

> ⚠️ **Small sample:** Only 18 participants, but 1,584 rows because multiple brain regions are measured per participant."""),
        code(SETUP), code(VISIT_HELPER),
        md("## Load Data Files"),
        code("""\
sv2a_sub  = pd.read_csv(DATA_DIR / 'SV2A_PET_Imaging_Substudy_SV2A_PET_Imaging_12Nov2026.csv')
sv2a_meta = pd.read_csv(DATA_DIR / 'SV2A_PET_Acquisition_Metadata_12Nov2026.csv')
sv2a_suvr = pd.read_csv(DATA_DIR / 'SV2A_PET_SUVR_Analysis_12Nov2026.csv')
for name, df in [('SV2A Substudy', sv2a_sub), ('SV2A Metadata', sv2a_meta), ('SV2A SUVR', sv2a_suvr)]:
    print(f'{name:25s}: {len(df):>5,} rows | {df["PATNO"].nunique()} participants | {df.shape[1]} cols')
print()
print('SUVR file columns:', sv2a_suvr.columns.tolist())"""),
        md("""## Column Reference

### SV2A Acquisition Metadata
| Column | Meaning |
|--------|---------|
| `PET_LIGAND` | Tracer: [18F]SynVesT-1 |
| `PET_TOTAL_DOSE_CALC` | Injected dose |
| `PET_IMAGE_ACCEPTABLE` | QC pass: Yes/No |
| `PET_SCANNER` | Scanner model |

### SV2A SUVR Analysis
| Column | Meaning |
|--------|---------|
| `SV2A_SUVR_CS` | SUVR in centrum semiovale (white matter — reference region, expected ~1.0) |
| Region columns | SUVR in various cortical and subcortical regions |

**Region abbreviations** in column names:
- `FL_` = Frontal Lobe
- `TL_` = Temporal Lobe
- `PL_` = Parietal Lobe
- `OL_` = Occipital Lobe
- `_L` / `_R` = Left / Right"""),
        md("## 1 · Data Structure Overview"),
        code("""\
print(f'Participants: {sv2a_suvr["PATNO"].nunique()}')
print(f'Total rows: {len(sv2a_suvr):,}')
print(f'Rows per participant: {len(sv2a_suvr)/sv2a_suvr["PATNO"].nunique():.0f}')
suvr_cols = [c for c in sv2a_suvr.columns
             if sv2a_suvr[c].dtype in [np.float64, float] and c != 'PATNO']
print(f'Numeric SUVR columns: {len(suvr_cols)}')
print('\\nFirst few columns:', suvr_cols[:8])"""),
        md("## 2 · SUVR Distribution Across All Regions\n\nValues > 1.0 mean more tracer (more synapses) than white matter reference."),
        code("""\
if suvr_cols:
    means = sv2a_suvr[suvr_cols].mean().sort_values(ascending=False)
    stds  = sv2a_suvr[suvr_cols].std()

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    # Mean SUVR bar chart
    top = means.head(20)
    axes[0].bar(range(len(top)), top.values,
                color=sns.color_palette('colorblind', min(len(top), 10))*3,
                edgecolor='white')
    axes[0].set_xticks(range(len(top)))
    axes[0].set_xticklabels(top.index, rotation=45, ha='right', fontsize=8)
    axes[0].axhline(1.0, color='red', linestyle='--', label='SUVR=1.0 (reference)')
    axes[0].set_title('Top 20 Regions by Mean SV2A SUVR'); axes[0].legend()
    axes[0].set_ylabel('Mean SUVR')

    # Distribution of all SUVR values
    all_vals = sv2a_suvr[suvr_cols].values.flatten()
    all_vals = all_vals[~np.isnan(all_vals)]
    axes[1].hist(all_vals, bins=50, color=sns.color_palette('colorblind')[0],
                 edgecolor='black', alpha=0.8)
    axes[1].axvline(np.median(all_vals), color='red', linestyle='--',
                    label=f'Median={np.median(all_vals):.2f}')
    axes[1].set_title('Distribution of All SV2A SUVR Values')
    axes[1].set_xlabel('SUVR'); axes[1].set_ylabel('Count'); axes[1].legend()
    plt.tight_layout(); plt.show()"""),
        md("## 3 · Left vs Right Regional Symmetry\n\nAre matching left and right regions symmetric in SV2A signal?"),
        code("""\
# Find left-right pairs by naming convention
l_cols = [c for c in suvr_cols if c.endswith('_L') and c[:-2]+'_R' in suvr_cols]
r_cols = [c[:-2]+'_R' for c in l_cols]

if l_cols:
    n_pairs = min(len(l_cols), 6)
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()
    for i, (lc, rc) in enumerate(zip(l_cols[:n_pairs], r_cols[:n_pairs])):
        sub = sv2a_suvr[[lc, rc]].dropna()
        if len(sub) < 2: continue
        mn = sub.min().min()*0.9; mx = sub.max().max()*1.05
        axes[i].scatter(sub[lc], sub[rc], alpha=0.6, s=30,
                        color=sns.color_palette('colorblind')[i%6])
        axes[i].plot([mn,mx],[mn,mx],'r--', alpha=0.7)
        region = lc.replace('_L','').replace('SV2A_SUVR_','')
        axes[i].set_xlabel(f'{region} Left'); axes[i].set_ylabel(f'{region} Right')
        axes[i].set_title(region, fontsize=9)
    plt.suptitle('SV2A SUVR: Left vs Right Hemisphere', fontsize=13)
    plt.tight_layout(); plt.show()"""),
        md("## 4 · Acquisition Metadata"),
        code("""\
print('Acquisition summary:')
print(f'  Participants: {sv2a_meta["PATNO"].nunique()}')
for col in sv2a_meta.columns:
    vc = sv2a_meta[col].value_counts()
    if 1 < len(vc) <= 8 and col not in ['PATNO','EVENT_ID']:
        print(f'\\n{col}:'); print(vc.to_string())
num_meta = sv2a_meta.select_dtypes(include='number').columns.difference(['PATNO'])
if len(num_meta) > 0:
    print('\\nNumeric metadata summary:')
    print(sv2a_meta[num_meta].describe().round(2))"""),
        md("""## Key Takeaways

- **SV2A measures synaptic density** — a marker of neurodegeneration independent of dopamine
- **Only 18 participants** in this pilot substudy — findings are exploratory
- **SUVR > 1.0 everywhere** because cortical grey matter is synapse-rich (much more than white matter)
- **High left-right symmetry** at the group level
- **Striatal and cortical SV2A** are the most PD-relevant targets — reduced in areas with neuronal loss
- **SV2A may detect neurodegeneration earlier than volumetry** — synapses are lost before neurons die"""),
    ]
    save_nb(cells, "07_PET_SV2A_EDA.ipynb")


# ─────────────────────────────────────────────────────────────────────────────
def make_08():
    cells = [
        md("# 08 · PET — Other Tracers (Pilot Substudies)\n> *Small-N exploratory PET substudies: neuroinflammation (DPA-714), and novel experimental tracers (FD4, MNI1008, C05-05).*"),
        md("""## Background: What Are These Tracers?

PPMI includes several very small **pilot PET substudies** testing novel tracers that target different aspects of PD biology.

| Tracer | Target | Mechanism | Why it matters |
|--------|--------|-----------|---------------|
| **DPA-714** (¹⁸F) | TSPO | Binds to Translocator Protein on activated microglia | **Neuroinflammation** — microglia become activated in PD; may drive disease progression |
| **FD4** (¹⁸F) | Unknown/Novel | Experimental tracer | Under evaluation — specific target being characterised |
| **MNI1008** (¹⁸F) | Likely α-synuclein related | Novel compound from Montreal Neurological Institute | **Alpha-synuclein** (the protein that forms Lewy bodies in PD) is the ultimate PD biomarker target |
| **C05-05** (¹⁸F) | Novel | Experimental | Under evaluation |

**Key context:**
- These are **feasibility/safety studies** — the goal is to show the tracer works in humans, not to establish clinical utility yet
- **N = 6–16 participants** — not suitable for statistical analysis
- Data is primarily acquisition metadata and completion records

> ⚠️ All findings from these substudies should be treated as **hypothesis-generating pilot data only.**"""),
        code(SETUP), code(VISIT_HELPER),
        md("## Load All Four Files"),
        code("""\
dpa714  = pd.read_csv(DATA_DIR / 'Dual_PET_DPA-714_Imaging_Substudy_DPA-714_NX_PET_Imaging_12Nov2026.csv')
fd4     = pd.read_csv(DATA_DIR / 'FD4_Tracer_Substudy_FD4_PET_Imaging_12Nov2026.csv')
mni1008 = pd.read_csv(DATA_DIR / 'MNI1008_PET_Imaging_Substudy_MNI_PET_Imaging_12Nov2026.csv')
c05     = pd.read_csv(DATA_DIR / 'C05-05_PET_Imaging_Substudy_Imaging_12Nov2026.csv')

dfs = {'DPA-714 (Neuroinflammation)': dpa714, 'FD4 (Novel)': fd4,
       'MNI1008 (Novel)': mni1008, 'C05-05 (Novel)': c05}
for name, df in dfs.items():
    print(f'{name:35s}: {len(df):>3} rows | {df["PATNO"].nunique()} participants | {df.shape[1]} cols')"""),
        md("## Participant and Visit Summary"),
        code("""\
fig, ax = plt.subplots(figsize=(9, 4))
names = list(dfs.keys())
counts = [df['PATNO'].nunique() for df in dfs.values()]
colors = sns.color_palette('colorblind', len(names))
bars = ax.bar(names, counts, color=colors)
ax.set_title('Participants per Pilot PET Substudy')
ax.set_ylabel('Unique Participants')
ax.tick_params(axis='x', rotation=15)
for b, v in zip(bars, counts):
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.1, str(v), ha='center', fontsize=12)
ax.set_ylim(0, max(counts)*1.3)
plt.tight_layout(); plt.show()"""),
        md("## Column Overview — What Data Is Available?\n\nSince these are small substudies, we inspect available columns and completion flags rather than analysing distributions."),
        code("""\
for name, df in dfs.items():
    print(f'\\n{"="*60}')
    print(f'{name}')
    print(f'{"="*60}')
    print(f'Shape: {df.shape}')
    print('\\nColumns and types:')
    for col in df.columns:
        dtype = df[col].dtype
        n_unique = df[col].nunique()
        sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else 'NaN'
        print(f'  {col:35s} {str(dtype):10s} nunique={n_unique:3d}  sample={str(sample)[:30]}')"""),
        md("## Scan Completion Summary"),
        code("""\
complete_flags = ['PETCMPLT','AVNEXCMPLT','AVCONVCMPLT','CMPLT','COMPLETE']

fig, ax = plt.subplots(figsize=(10, 5))
summary_rows = []
for name, df in dfs.items():
    for flag in complete_flags:
        if flag in df.columns:
            pct = (df[flag] == 1).mean() * 100 if df[flag].dtype in [int, np.int64] else \
                  (df[flag].astype(str).str.lower().isin(['yes','1','true'])).mean() * 100
            summary_rows.append({'Substudy': name.split('(')[0].strip(),
                                  'Flag': flag, 'Complete%': pct})
            break

if summary_rows:
    summ_df = pd.DataFrame(summary_rows)
    bars = ax.bar(summ_df['Substudy'], summ_df['Complete%'],
                  color=sns.color_palette('colorblind', len(summ_df)))
    ax.set_title('Scan Completion Rates by Substudy')
    ax.set_ylabel('% Completed'); ax.set_ylim(0, 115)
    ax.tick_params(axis='x', rotation=15)
    for b, v in zip(bars, summ_df['Complete%']):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+1, f'{v:.0f}%', ha='center')
    plt.tight_layout(); plt.show()
else:
    print('No standard completion flag found — checking raw column values:')
    for name, df in dfs.items():
        print(f'\\n{name}:'); print(df.dtypes.to_string())"""),
        md("## Vital Signs (where available)\n\nLarger substudy files (FD4, MNI1008) collect multiple timepoints of vital signs."),
        code("""\
vital_map = {
    'Systolic BP': ['SYSSUPBF','SYSSUPAF','SYS_SUP_BL','SYS_BL'],
    'Diastolic BP': ['DIASUPBF','DIASUPAF','DIAS_SUP_BL'],
    'Heart Rate': ['HRSUPBF','HRSUPAF','HR_SUP_BL'],
}
for name, df in [('FD4', fd4), ('MNI1008', mni1008)]:
    found = [(vname, [c for c in alts if c in df.columns])
             for vname, alts in vital_map.items()]
    found = [(vname, cols) for vname, cols in found if cols]
    if found:
        print(f'\\n{name} vital signs:')
        for vname, cols in found:
            print(f'  {vname}: {df[cols].describe().round(1).loc["mean"].to_dict()}')"""),
        md("""## Key Takeaways

- **All four substudies are pilot studies** — small N (6–16 participants), unsuitable for independent statistical analysis
- **DPA-714** targets neuroinflammation (microglial activation via TSPO) — highly relevant to PD disease mechanisms
- **MNI1008** likely targets alpha-synuclein — the definitive PD pathological protein; if validated, would be the most disease-specific PD PET tracer ever
- **FD4 and C05-05** are under characterisation — their exact clinical utility is being established
- **These substudies represent the frontier** of PD biomarker research — their data is precious precisely because it's rare
- **For analysis:** combine with DaTSCAN/clinical data for context, treat as case series rather than cohort studies"""),
    ]
    save_nb(cells, "08_PET_Other_Tracers_EDA.ipynb")


# ─────────────────────────────────────────────────────────────────────────────
def make_09():
    cells = [
        md("# 09 · Safety Head CT Scan EDA\n> *CT scans performed as a safety check before lumbar punctures — a routine procedural requirement in PPMI.*"),
        md("""## Background: Why CT Scans for Safety?

PPMI collects **cerebrospinal fluid (CSF)** via lumbar puncture (spinal tap) as part of its biomarker program. CSF contains valuable protein markers (alpha-synuclein, tau, etc.) that complement the imaging data.

Before performing a lumbar puncture, clinicians must ensure there is **no raised intracranial pressure** — a condition where the CT scan shows brain swelling or herniation risk. If there's a problem, the LP is contraindicated.

**The CT scan here is not for brain analysis** — it's a standard safety screening tool.

**What is a CT scan?**
CT (Computed Tomography) uses X-rays from multiple angles to create cross-sectional images of the brain. It's faster and cheaper than MRI but provides less soft-tissue detail.

---

## Column Reference

| Column | Meaning |
|--------|---------|
| `PATNO` | Participant ID |
| `EVENT_ID` | Visit code when CT was done |
| `CTSCAN` | CT scan completed: 1=Yes, 0=No |
| `CTDT` | Date of CT scan (MM/DD/YYYY or MM/YYYY) |
| `PAG_NAME` | Form identifier (always "CT") |
| `REC_ID` | Unique record identifier |
| `ORIG_ENTRY` | Date data was first entered into the system |
| `LAST_UPDATE` | Date data was most recently updated |"""),
        code(SETUP), code(VISIT_HELPER),
        md("## Load Data File"),
        code("""\
ct = pd.read_csv(DATA_DIR / 'Safety_Head_CT_Scan_12Nov2026.csv')
print(f'Shape: {ct.shape}')
print(f'Participants: {ct["PATNO"].nunique()}')
print(f'Completion (1=Yes, 0=No):')
print(ct['CTSCAN'].value_counts())
ct.head()"""),
        md("## 1 · CT Scan Completion Rate by Visit"),
        code("""\
visits = ordered_visits(ct['EVENT_ID'])
done = ct[ct['CTSCAN'] == 1]
vc = done.groupby('EVENT_ID')['PATNO'].nunique().reindex(visits).dropna()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
# Completed count
bars = axes[0].bar(range(len(vc)), vc.values, color=sns.color_palette('colorblind')[0])
axes[0].set_xticks(range(len(vc)))
axes[0].set_xticklabels([f'{VISIT_LABELS.get(v,v)}\\n({v})' for v in vc.index], rotation=45, ha='right')
axes[0].set_ylabel('Participants'); axes[0].set_title('CT Scan Completions per Visit')
for b, v in zip(bars, vc.values):
    axes[0].text(b.get_x()+b.get_width()/2, b.get_height()+1, str(int(v)), ha='center', fontsize=9)

# Overall completion rate
total_per_visit = ct.groupby('EVENT_ID')['PATNO'].nunique().reindex(visits).dropna()
rate = (vc / total_per_visit * 100).dropna()
axes[1].bar(range(len(rate)), rate.values, color=sns.color_palette('colorblind')[1])
axes[1].set_xticks(range(len(rate)))
axes[1].set_xticklabels([VISIT_LABELS.get(v,v) for v in rate.index], rotation=45, ha='right')
axes[1].set_ylabel('% Completed'); axes[1].set_title('CT Completion Rate per Visit (%)')
axes[1].set_ylim(0, 115)
plt.tight_layout(); plt.show()"""),
        md("## 2 · CT Completion Over Calendar Time"),
        code("""\
ct_done = ct[ct['CTSCAN'] == 1].copy()
if 'ORIG_ENTRY' in ct_done.columns:
    ct_done['ENTRY_DATE'] = pd.to_datetime(ct_done['ORIG_ENTRY'], errors='coerce', format='%m/%Y')
    if ct_done['ENTRY_DATE'].isna().mean() > 0.5:
        ct_done['ENTRY_DATE'] = pd.to_datetime(ct_done['ORIG_ENTRY'], errors='coerce')

    ct_done = ct_done.dropna(subset=['ENTRY_DATE'])
    if len(ct_done) > 10:
        ct_done['Year'] = ct_done['ENTRY_DATE'].dt.year
        yearly = ct_done.groupby('Year').size()

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.bar(yearly.index, yearly.values, color=sns.color_palette('colorblind')[2])
        ax.set_title('CT Scans Completed by Year of Entry')
        ax.set_xlabel('Year'); ax.set_ylabel('CT Scans Completed')
        ax.set_xticks(yearly.index)
        plt.tight_layout(); plt.show()"""),
        md("## 3 · Missing Data Analysis"),
        code("""\
missing = (ct.isnull().sum() / len(ct) * 100).round(1)
missing = missing[missing > 0].sort_values(ascending=False)
print('Columns with missing data:')
print(missing.to_string())
print(f'\\nTotal records: {len(ct):,}')
print(f'Records with CT completed: {(ct["CTSCAN"]==1).sum():,} ({(ct["CTSCAN"]==1).mean()*100:.1f}%)')
print(f'Records with CT not done: {(ct["CTSCAN"]==0).sum():,}')
print(f'Records with missing CT date (CTDT): {ct["CTDT"].isna().sum():,}')"""),
        md("""## Key Takeaways

- **Safety CT is a procedural requirement** for lumbar puncture, not a brain imaging biomarker
- **Most records (~958) represent screening visits** — LP safety check is typically done early
- **High completion rate** where CT was scheduled — consistent with the safety-critical nature
- **Missing CTDT** likely reflects records where CT was not required or was done previously
- **This dataset is best used** as a flag: which participants underwent LP (and therefore have CSF biomarker data available)?"""),
    ]
    save_nb(cells, "09_Safety_CT_EDA.ipynb")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating PPMI EDA notebooks...")
    make_00()
    make_01()
    make_02()
    make_03()
    make_04()
    make_05()
    make_06()
    make_07()
    make_08()
    make_09()
    print("\nAll done! Open Jupyter with:")
    print("  source venv/bin/activate")
    print("  jupyter notebook")
