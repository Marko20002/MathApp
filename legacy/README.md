# Archived prototype

These files are preserved from the original repository for reference. The active
application is `../backend` plus `../frontend`. Nothing in the active application
imports this directory.

The old `django/`, OCR scripts, normalization code and CLI pipeline have Windows
paths and optional dependencies. They are not a supported alternate application
entry point. Their former PDF/image/JSON samples are in `../data/samples/`.

The commented JSON-prompt experiment remains in `deepseek/mathsolver.py` for
historical reference. New classifier code is in `../ml/src/mathapp_ml/`.
