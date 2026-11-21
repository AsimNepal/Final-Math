# Braess's Paradox: Interactive Website and Reproducible Applied Mathematics Study

Independent mathematics portfolio by Asim Nepal (SUNY Brockport, November 2026).

## Contents

- `index.html`, `style.css`, `script.js`: static Netlify-ready interactive website.
- `project.pdf`, `main.tex`: original mathematical portfolio and its LaTeX source.
- `RESEARCH_REPORT.md`: expanded derivations, computational design, limitations, and background reading.
- `traffic.py`: reusable network equilibrium and system-optimum solver.
- `run_experiments.py`: demand, road-capacity, and larger-network experiments.
- `test_traffic.py`: numerical tests against known four-node results.
- `*.csv`: reproducible numerical results.
- `*.png`: generated charts used by the website.

## Run the code

Requires Python 3.10+.

```bash
python -m pip install -r requirements.txt
python run_experiments.py
cd research
python -m unittest -v test_traffic
```

## Deploy to Netlify from GitHub

Upload **the extracted contents** of this ZIP into the **root** of your GitHub repository, preserving the `research`, `results`, and `figures` folders. `index.html` must be in the repository root. Netlify requires no build command; publish the repository root (`.`). All generated figures and CSVs are included, so visitors do not need Python.

## Scientific caution

The larger-network experiments use synthetic edge times and intentionally include a family with an embedded Braess motif. The reported frequencies are sample-specific, not representative of actual road networks. The PDF is the original portfolio; the new research extension is documented in `RESEARCH_REPORT.md` and on the website.


All files in this distribution are in a single directory, without subfolders.
