# PPMI Imaging — Exploratory Data Analysis

Jupyter notebooks for exploratory data analysis of imaging-derived data from the **Parkinson's Progression Markers Initiative (PPMI)** study. One notebook per modality, designed to be readable by anyone — no neuroscience background required.

---

## Background

**Parkinson's Disease (PD)** is a progressive neurodegenerative disorder caused by the death of dopamine-producing neurons in the Substantia Nigra. By the time motor symptoms appear, 60–80% of these neurons are already gone — making early biomarkers critical.

**PPMI** (Parkinson's Progression Markers Initiative) is one of the largest PD biomarker studies ever conducted, tracking thousands of participants (PD patients, prodromal individuals, and healthy controls) across international sites with deep longitudinal follow-up.

This repository contains EDA notebooks for the **imaging arm** of PPMI — derived measurements from DaTSCAN, MRI, FreeSurfer, DTI, and multiple PET tracers.

---

## Notebooks

| # | Notebook | Modality | Key questions answered |
|---|----------|----------|----------------------|
| 00 | `00_Overview_and_Cohort` | Study overview | What is PPMI? How many participants? What data exists? |
| 01 | `01_DaTSCAN_SPECT_EDA` | DaTSCAN / SPECT | How does dopamine transporter binding vary? Left/right asymmetry? Longitudinal decline? |
| 02 | `02_MRI_Structural_EDA` | Structural MRI | Which sequences were acquired? Image quality metrics? Grey matter volume? |
| 03 | `03_FreeSurfer_EDA` | FreeSurfer morphometry | Cortical thickness and surface area by region? Subcortical volumes (caudate, putamen, hippocampus)? |
| 04 | `04_DTI_EDA` | Diffusion Tensor Imaging | White matter integrity in the Substantia Nigra? FA distributions? |
| 05 | `05_PET_AV133_EDA` | AV-133 PET (VMAT2) | Dopamine vesicular transporter binding? SBR by region? |
| 06 | `06_PET_Tau_EDA` | Tau PET | Tau SUVR by brain region? Braak staging pattern? |
| 07 | `07_PET_SV2A_EDA` | SV2A PET | Synaptic density across brain regions? Left/right symmetry? |
| 08 | `08_PET_Other_Tracers_EDA` | Pilot PET tracers | What pilot substudies exist? (DPA-714, FD4, MNI1008, C05-05) |
| 09 | `09_Safety_CT_EDA` | Safety CT | CT scan completion rates? Used as LP safety screen. |

Each notebook follows a consistent structure:
1. **Background** — plain-English explanation of the modality and its relevance to PD
2. **Column reference table** — every CSV column explained before it is used
3. **EDA sections** — visualisations with interpretation notes
4. **Key takeaways** — 3–5 bullet summary

---

## Data

Data is from the PPMI study and must be downloaded separately from the [LONI IDA portal](https://ida.loni.usc.edu). Access requires a free account and data use agreement.

**Download path:** IDA → Download → Study Data → Imaging

The notebooks expect data files in `../Imaging/` relative to this directory (i.e., one level up in a folder called `Imaging`).

**Files used:**

| File | Modality |
|------|----------|
| `Dopamine_Imaging_*.csv` | DaTSCAN scan log |
| `Xing_Core_Lab_-_DATSCAN_acquisition_metadata_*.csv` | DaTSCAN acquisition |
| `Xing_Core_Lab_-_Quant_SBR_*.csv` | DaTSCAN quantitative SBR |
| `Xing_Core_Lab_-_Visual_Read_*.csv` | DaTSCAN visual read |
| `Magnetic_Resonance_Imaging__MRI__*.csv` | MRI log |
| `Xing_Core_Lab_-_MRI_acquisition_metadata_*.csv` | MRI acquisition |
| `MRIQC_*.csv` | MRI quality metrics |
| `Grey_Matter_Volume_*.csv` | Grey matter volume |
| `FS7_APARC_CTH_*.csv` | FreeSurfer cortical thickness |
| `FS7_APARC_SA_*.csv` | FreeSurfer surface area |
| `FS7_ASEG_VOL_*.csv` | FreeSurfer subcortical volumes |
| `DTI_Regions_of_Interest_*.csv` | DTI Substantia Nigra ROIs |
| `PET_Acquisition_Metadata_*.csv` | AV-133 PET metadata |
| `PET_SBR_Analysis_*.csv` | AV-133 SBR analysis |
| `TAU_PET_*.csv` | Tau PET |
| `SV2A_PET_*.csv` | SV2A PET |
| `Safety_Head_CT_Scan_*.csv` | Safety CT |

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/asad8888/ppmi-imaging-eda.git
cd ppmi-imaging-eda
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Register the kernel

```bash
python -m ipykernel install --user --name ppmi-imaging --display-name "PPMI Imaging (venv)"
```

### 5. Place data files

Download the PPMI imaging CSVs from LONI and place them in `../Imaging/` (one directory above this repo).

### 6. Run all notebooks (headless)

```bash
for nb in *.ipynb; do
  jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.kernel_name=ppmi-imaging \
    --ExecutePreprocessor.timeout=300 "$nb"
done
```

Or open interactively:

```bash
jupyter notebook
```

Then select **Kernel → Change Kernel → PPMI Imaging (venv)** and **Kernel → Restart & Run All**.

---

## Dependencies

```
pandas >= 2.0
numpy >= 1.24
matplotlib >= 3.7
seaborn >= 0.12
scipy >= 1.10
jupyter >= 1.0
nbformat >= 5.9
ipywidgets >= 8.0
openpyxl >= 3.1
```

---

## Acknowledgements

Data used in the preparation of this repository were obtained from the Parkinson's Progression Markers Initiative (PPMI) database (www.ppmi-info.org/access-data-specimens/download-data), RRID:SCR_006431. For up-to-date information on the study, visit www.ppmi-info.org.

PPMI — a public-private partnership — is funded by the Michael J. Fox Foundation for Parkinson's Research and funding partners, including [full list of sponsors at ppmi-info.org](https://www.ppmi-info.org/about-ppmi/who-we-are/study-sponsors).
