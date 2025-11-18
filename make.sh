rm dist -r
python -m build
python -m pip install dist/*.whl --force-reinstall
